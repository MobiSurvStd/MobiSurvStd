from datetime import datetime

import polars as pl

from mobisurvstd.common.trips import add_intermodality_column
from mobisurvstd.schema import (
    CAR_SCHEMA,
    HOUSEHOLD_SCHEMA,
    LEG_SCHEMA,
    MOTORCYCLE_SCHEMA,
    PERSON_SCHEMA,
    TRIP_SCHEMA,
)
from mobisurvstd.utils import SurveyData


def clean(
    households: pl.LazyFrame,
    persons: pl.LazyFrame,
    trips: pl.LazyFrame,
    legs: pl.LazyFrame,
    cars: pl.LazyFrame,
    motorcycles: pl.LazyFrame,
    survey_type: str,
    main_insee: str,
):
    households = count_nb_persons(households, persons)
    persons = count_nb_trips(persons, trips)
    trips = count_nb_legs(trips, legs)
    trips = add_main_mode(trips, legs)
    trips = add_access_egress_modes(trips, legs)
    # Select only the column in the schema and add the missing columns with null values.
    data = dict()
    for name, lf, schema in (
        ("households", households, HOUSEHOLD_SCHEMA),
        ("persons", persons, PERSON_SCHEMA),
        ("trips", trips, TRIP_SCHEMA),
        ("legs", legs, LEG_SCHEMA),
        ("cars", cars, CAR_SCHEMA),
        ("motorcycles", motorcycles, MOTORCYCLE_SCHEMA),
    ):
        print(f"Collecting {name}...")
        # `short_name` is the name without the "s"
        short_name = name[:-1]
        existing_columns = lf.collect_schema().names()
        columns = [
            cast_column(col, dtype)
            if col in existing_columns
            else pl.lit(None, dtype=dtype).alias(col)
            for col, dtype in schema.items()
        ]
        data[name] = lf.select(columns).sort(f"{short_name}_id").collect()
    data["metadata"] = create_metadata(survey_type, main_insee, data)
    return SurveyData.from_dict(data)


def count_zones(prefix: str, data: dict):
    """Count the number of unique zones observed."""
    return len(
        set(data["households"][f"home_{prefix}"].drop_nulls())
        .union(set(data["persons"][f"work_{prefix}"].drop_nulls()))
        .union(set(data["persons"][f"study_{prefix}"].drop_nulls()))
        .union(set(data["trips"][f"origin_{prefix}"].drop_nulls()))
        .union(set(data["trips"][f"destination_{prefix}"].drop_nulls()))
        .union(set(data["legs"][f"start_{prefix}"].drop_nulls()))
        .union(set(data["legs"][f"end_{prefix}"].drop_nulls()))
    )


def create_metadata(survey_type: str, main_insee: str, data: dict):
    # Find survey metadata.
    survey_methods = data["households"]["survey_method"].unique()
    if len(survey_methods) == 1:
        survey_method = survey_methods[0]
    else:
        assert len(survey_methods) == 2
        survey_method = "mixed"
    nb_insee_zones = count_zones("insee", data)
    start_date: datetime = data["households"]["interview_date"].min()  # type: ignore
    end_date: datetime = data["households"]["interview_date"].max()  # type: ignore
    metadata = {
        "type": survey_type,
        "survey_method": survey_method,
        "nb_households": len(data["households"]),
        "nb_cars": len(data["cars"]),
        "nb_motorcycles": len(data["motorcycles"]),
        "nb_persons": len(data["persons"]),
        "nb_trips": len(data["trips"]),
        "nb_legs": len(data["legs"]),
        "nb_special_locations": 0,  # TODO
        "nb_detailed_zones": 0,  # TODO
        "nb_draw_zones": 0,  # TODO
        "nb_insee_zones": nb_insee_zones,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "insee": main_insee,
    }
    print(metadata)
    return metadata


def cast_column(col: str, dtype: pl.DataType):
    if dtype == pl.Struct:
        # The struct fields are unspecified so the column is not cast.
        return pl.col(col).alias(col)
    else:
        return pl.col(col).cast(dtype).alias(col)


def count_nb_persons(households: pl.LazyFrame, persons: pl.LazyFrame):
    has_age = "age" in persons.collect_schema().names()
    person_counts = persons.group_by("household_id").agg(
        nb_persons=pl.len(),
        nb_persons_5plus=pl.col("age").is_not_null().all() & pl.col("age").gt(5).sum()
        if has_age
        else None,
        nb_majors=pl.col("age").is_not_null().all() & pl.col("age").ge(18).sum()
        if has_age
        else None,
        nb_minors=pl.col("age").is_not_null().all() & pl.col("age").lt(18).sum()
        if has_age
        else None,
    )
    households = households.join(person_counts, on="household_id", how="left", coalesce=True)
    return households


def count_nb_trips(persons: pl.LazyFrame, trips: pl.LazyFrame):
    trip_counts = trips.group_by("person_id").agg(nb_trips=pl.len())
    persons = persons.join(trip_counts, on="person_id", how="left", coalesce=True)
    # Set nb_trips = 0 for surveyed persons.
    persons = persons.with_columns(
        nb_trips=pl.when("is_surveyed").then(pl.col("nb_trips").fill_null(0)).otherwise("nb_trips")
    )
    return persons


def count_nb_legs(trips: pl.LazyFrame, legs: pl.LazyFrame):
    """Add column `nb_legs` to the trips.

    Also add columns `nb_legs_{mode_group}` and `intermodality` if leg's `mode_group` are known.
    """
    agg_cols = [pl.len().alias("nb_legs")]
    has_mode_group = "mode_group" in legs.collect_schema().names()
    if has_mode_group:
        agg_cols.extend(
            [
                pl.col("mode_group").eq(mode_group).sum().alias(f"nb_legs_{mode_group}")
                for mode_group in LEG_SCHEMA["mode_group"].categories
            ]
        )
    leg_counts = legs.group_by("trip_id").agg(agg_cols)
    trips = trips.join(leg_counts, on="trip_id", how="left", coalesce=True)
    if has_mode_group:
        trips = add_intermodality_column(trips)
    return trips


def add_main_mode(trips: pl.LazyFrame, legs: pl.LazyFrame):
    """Identify the main mode and main mode group of each trip, given the modes and mode groups of
    the trips' legs.

    If the column `main_mode_group` already exists in `trips`, the function does nothing (even if
    the column `main_mode` does not exist).

    If the column `mode_group` does not exist in `legs`, the function does nothing.

    If the column `mode_group` exists in `legs` but the column `mode` does not, then the main mode
    groups are identified but not the groups.

    The most used modes of a trip are identified using the legs' travel time (if column
    `leg_travel_time` exists), or using the legs' euclidean distance (if column
    `leg_euclidean_distance_km` exists). If neither column is available, the function does nothing.
    """
    trip_columns = trips.collect_schema().names()
    if "main_mode_group" in trip_columns:
        # Note. It is possible that the `main_mode` column does not exist and that we would like to
        # add it but that would require a different function.
        return trips
    leg_columns = legs.collect_schema().names()
    if "mode_group" not in leg_columns:
        assert "mode" not in leg_columns, "Legs have `mode` but no `mode_group`"
        return trips
    has_modes = "mode" in leg_columns
    # === Step A ===
    # Find the column used to identify the most used mode over legs.
    agg_column = None
    if "leg_travel_time" in leg_columns:
        agg_column = "leg_travel_time"
    elif "leg_euclidean_distance_km" in leg_columns:
        agg_column = "leg_euclidean_distance_km"
    if agg_column is None:
        # There is no way to find the main mode.
        return trips
    # === Step B ===
    # Find the `main_mode_group`: the mode group that is the most used over the legs.
    main_modes = (
        # Exclude walking legs (unless it is the only mode_group used in the leg).
        legs.filter(
            pl.col("mode_group").ne("walking")
            | pl.col("mode_group").eq("walking").all().over("trip_id")
        )
        # Exclude trips where the agg_column is NULL for at least one non-walking leg (unless
        # the trip as at most 1 mode / mode group).
        .filter(
            pl.col(agg_column).is_not_null().all().over("trip_id")
            | pl.col("mode" if has_modes else "mode_group").n_unique().over("trip_id").eq(1)
        )
        # Compute the agg_column sum by `mode_group` and `mode`, for each trip.
        .with_columns(
            mode_group_total=pl.col(agg_column).sum().over("trip_id", "mode_group"),
            # The `mode_total` column is None if the `mode` column does not exist.
            mode_total=pl.col(agg_column).sum().over("trip_id", "mode") if has_modes else None,
        )
        .group_by("trip_id")
        .agg(
            # Find the `mode_group` with the largest total for each trip.
            main_mode_group=pl.col("mode_group").sort_by("mode_group_total").last(),
            # Find the `mode` with the largest total, among the modes in the `main_mode_group`,
            # for each trip.
            main_mode=pl.col("mode").sort_by("mode_group_total", "mode_total").last()
            if has_modes
            else None,
        )
    )
    # Add the `main_mode_group` and `mode_group` columns to the trips.
    trips = trips.join(main_modes, on="trip_id", how="left", coalesce=True)
    # Remove the `main_mode` column if the legs modes are unknown.
    if not has_modes:
        trips = trips.drop("main_mode")
    return trips


def add_access_egress_modes(trips: pl.LazyFrame, legs: pl.LazyFrame):
    trip_columns = trips.collect_schema().names()
    leg_columns = legs.collect_schema().names()
    if "main_mode_group" not in trip_columns and "mode_group" not in leg_columns:
        # Access and egress modes cannot be identified.
        return trips
    has_modes = "mode" in leg_columns
    # Find first and last mode / mode group of each trip's legs.
    first_last_leg_modes = (
        legs.sort("trip_id", "leg_index")
        .group_by("trip_id")
        .agg(
            first_mode_group=pl.col("mode_group").first(),
            first_mode=pl.col("mode").first() if has_modes else None,
            last_mode_group=pl.col("mode_group").last(),
            last_mode=pl.col("mode").last() if has_modes else None,
        )
    )
    # Access mode is the mode of the first leg if the trip's `main_mode_group` is "public_transit"
    # and the first leg's `mode_group` is not "public_transit", otherwise it is NULL.
    # Egress mode is the mode of the last leg if the trip's `main_mode_group` is "public_transit"
    # and the last leg's `mode_group` is not "public_transit", otherwise it is NULL.
    is_pt_trip = pl.col("main_mode_group") == "public_transit"
    trips = trips.join(first_last_leg_modes, on="trip_id", how="left", coalesce=True).with_columns(
        public_transit_access_mode=pl.when(
            is_pt_trip & pl.col("first_mode_group").ne("public_transit")
        ).then("first_mode"),
        public_transit_access_mode_group=pl.when(
            is_pt_trip & pl.col("first_mode_group").ne("public_transit")
        ).then("first_mode_group"),
        public_transit_egress_mode=pl.when(
            is_pt_trip & pl.col("last_mode_group").ne("public_transit")
        ).then("last_mode"),
        public_transit_egress_mode_group=pl.when(
            is_pt_trip & pl.col("last_mode_group").ne("public_transit")
        ).then("last_mode_group"),
    )
    return trips

from datetime import date

import geopandas as gpd
import polars as pl
from loguru import logger

from mobisurvstd.classes import SurveyData
from mobisurvstd.common.trips import add_intermodality_column
from mobisurvstd.schema import (
    CAR_SCHEMA,
    HOUSEHOLD_SCHEMA,
    LEG_SCHEMA,
    MOTORCYCLE_SCHEMA,
    PERSON_SCHEMA,
    TRIP_SCHEMA,
)


def clean(
    households: pl.LazyFrame,
    persons: pl.LazyFrame,
    trips: pl.LazyFrame,
    legs: pl.LazyFrame,
    cars: pl.LazyFrame,
    motorcycles: pl.LazyFrame,
    survey_type: str,
    survey_name: str,
    main_insee: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    special_locations: gpd.GeoDataFrame | None = None,
    detailed_zones: gpd.GeoDataFrame | None = None,
    draw_zones: gpd.GeoDataFrame | None = None,
):
    households = count_nb_persons(households, persons)
    households = add_household_type(households, persons)
    persons = count_nb_trips(persons, trips)
    persons = add_worked_during_surveyed_day(persons, trips)
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
        logger.debug(f"Collecting {name}")
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
    if special_locations is not None:
        data["special_locations"] = special_locations
    if detailed_zones is not None:
        data["detailed_zones"] = detailed_zones
    if draw_zones is not None:
        data["draw_zones"] = draw_zones
    data["metadata"] = create_metadata(
        data, survey_type, survey_name, main_insee, start_date, end_date
    )
    return SurveyData.from_dict(data)


def create_metadata(
    data: dict,
    survey_type: str,
    survey_name: str,
    main_insee: str | None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    # Find survey method.
    survey_methods = data["households"]["survey_method"].unique()
    if len(survey_methods) == 1:
        survey_method = survey_methods[0]
    else:
        assert len(survey_methods) == 2
        survey_method = "mixed"
    # Count number of zones and add zone counts.
    if "special_locations" in data:
        nb_special_locations = len(data["special_locations"])
        data["special_locations"] = add_zone_counts(
            data["special_locations"], "special_location", data
        )
    else:
        nb_special_locations = 0
    if "detailed_zones" in data:
        nb_detailed_zones = len(data["detailed_zones"])
        data["detailed_zones"] = add_zone_counts(data["detailed_zones"], "detailed_zone", data)
    else:
        nb_detailed_zones = 0
    if "draw_zones" in data:
        nb_draw_zones = len(data["draw_zones"])
        data["draw_zones"] = add_zone_counts(data["draw_zones"], "draw_zone", data)
    else:
        nb_draw_zones = 0
    # Find start and end date of survey.
    if start_date is None:
        start_date: date = data["households"]["interview_date"].min()  # type: ignore
    if end_date is None:
        end_date: date = data["households"]["interview_date"].max()  # type: ignore
    metadata = {
        "name": survey_name,
        "type": survey_type,
        "survey_method": survey_method,
        "nb_households": len(data["households"]),
        "nb_cars": len(data["cars"]),
        "nb_motorcycles": len(data["motorcycles"]),
        "nb_persons": len(data["persons"]),
        "nb_trips": len(data["trips"]),
        "nb_legs": len(data["legs"]),
        "nb_special_locations": nb_special_locations,
        "nb_detailed_zones": nb_detailed_zones,
        "nb_draw_zones": nb_draw_zones,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "insee": main_insee,
    }
    return metadata


def cast_column(col: str, dtype: pl.DataType):
    if dtype == pl.Struct:
        # The struct fields are unspecified so the column is not cast.
        return pl.col(col).alias(col)
    else:
        return pl.col(col).cast(dtype).alias(col)


def count_nb_persons(households: pl.LazyFrame, persons: pl.LazyFrame):
    has_age = "age" in persons.collect_schema().names()
    has_age_class = "age_class_code" in persons.collect_schema().names()
    person_counts = persons.group_by("household_id").agg(
        nb_persons=pl.len(),
        nb_persons_5plus=pl.when(pl.col("age").is_not_null().all()).then(pl.col("age").gt(5).sum())
        if has_age
        else None,
        nb_majors=pl.when(pl.col("age_class_code").is_not_null().all()).then(
            pl.col("age_class_code").gt(1).sum()
        )
        if has_age_class
        else None,
        nb_minors=pl.when(pl.col("age_class_code").is_not_null().all()).then(
            pl.col("age_class_code").eq(1).sum()
        )
        if has_age_class
        else None,
    )
    households = households.join(person_counts, on="household_id", how="left", coalesce=True)
    return households


def add_household_type(households: pl.LazyFrame, persons: pl.LazyFrame):
    household_columns = households.collect_schema().names()
    person_columns = persons.collect_schema().names()
    if (
        "household_type" in household_columns
        or "reference_person_link" not in person_columns
        or "woman" not in person_columns
    ):
        return households
    households = households.join(
        persons.group_by("household_id").agg(
            nb_men=pl.col("woman").not_().sum(),
            nb_women=pl.col("woman").sum(),
            nb_spouses=pl.col("reference_person_link").eq("spouse").sum(),
            nb_children=pl.col("reference_person_link").eq("child").sum(),
            nb_refs=pl.col("reference_person_link").eq("reference_person").sum(),
            only_family=pl.col("reference_person_link")
            .is_in(("reference_person", "spouse", "child"))
            .all(),
            ref_is_man=pl.col("reference_person_link")
            .eq("reference_person")
            .and_(pl.col("woman").not_())
            .any(),
            ref_is_woman=pl.col("reference_person_link").eq("reference_person").and_("woman").any(),
        ),
        on="household_id",
        how="left",
        coalesce=True,
    )
    households = households.with_columns(
        household_type=pl.when(nb_persons=1, nb_men=1)
        .then(pl.lit("single:man"))
        .when(nb_persons=1, nb_women=1)
        .then(pl.lit("single:woman"))
        .when(nb_persons=2, nb_spouses=1, nb_refs=1)
        .then(pl.lit("couple:no_child"))
        .when("only_family", pl.col("nb_children") > 0, nb_refs=1, nb_spouses=1)
        .then(pl.lit("couple:children"))
        .when("only_family", "ref_is_man", pl.col("nb_children") > 0, nb_refs=1, nb_spouses=0)
        .then(pl.lit("singleparent:father"))
        .when("only_family", "ref_is_woman", pl.col("nb_children") > 0, nb_refs=1, nb_spouses=0)
        .then(pl.lit("singleparent:mother"))
        .when(pl.col("only_family").not_())
        .then(pl.lit("other"))
    )
    return households


def count_nb_trips(persons: pl.LazyFrame, trips: pl.LazyFrame):
    trip_counts = trips.group_by("person_id").agg(nb_trips=pl.len())
    persons = persons.join(trip_counts, on="person_id", how="left", coalesce=True)
    # Set nb_trips = 0 for surveyed persons.
    persons = persons.with_columns(
        nb_trips=pl.when("is_surveyed").then(pl.col("nb_trips").fill_null(0)).otherwise("nb_trips")
    )
    # Add `traveled_during_surveyed_day` if needed.
    if "traveled_during_surveyed_day" not in persons.collect_schema().names():
        persons = persons.with_columns(
            traveled_during_surveyed_day=pl.when(pl.col("nb_trips") > 0)
            .then(pl.lit("yes"))
            .otherwise(pl.lit("no"))
        )
    return persons


def add_worked_during_surveyed_day(persons: pl.LazyFrame, trips: pl.LazyFrame):
    persons_cols = persons.collect_schema().names()
    persons = persons.join(
        trips.group_by("person_id").agg(
            has_work_activity=pl.col("destination_purpose")
            .is_in(("work:declared", "work:secondary", "work:other", "work:professional_tour"))
            .any(),
            has_telework_activity=pl.col("destination_purpose").eq("work:telework").any(),
        ),
        on="person_id",
        how="left",
        coalesce=True,
    )
    persons = persons.with_columns(
        worked_during_surveyed_day=pl.when("has_work_activity")
        .then(pl.lit("yes:outside"))
        .when(
            "work_only_at_home" if "work_only_at_home" in persons_cols else False,
            "has_telework_activity",
        )
        .then(pl.lit("yes:home:usual"))
        .when(
            pl.col("work_only_at_home").not_() if "work_only_at_home" in persons_cols else False,
            "has_telework_activity",
        )
        .then(pl.lit("yes:home:telework"))
        .when("work_only_at_home" not in persons_cols, "has_telework_activity")
        .then(pl.lit("yes:home:other"))
        .when("is_surveyed", pl.col("professional_occupation").eq("worker"))
        .then(pl.lit("no:unspecified"))
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
    if "main_mode_group" not in trip_columns or "mode_group" not in leg_columns:
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


def add_zone_counts(gdf: gpd.GeoDataFrame, prefix: str, data: dict):
    # Add nb_homes.
    gdf = gdf.merge(
        data["households"]
        .group_by(pl.col(f"home_{prefix}").alias(f"{prefix}_id"))
        .agg(nb_homes=pl.len())
        .to_pandas(),
        on=f"{prefix}_id",
        how="left",
    )
    gdf["nb_homes"] = gdf["nb_homes"].fillna(0).astype("UInt32")
    # Add nb_work_locations.
    gdf = gdf.merge(
        data["persons"]
        .group_by(pl.col(f"work_{prefix}").alias(f"{prefix}_id"))
        .agg(nb_work_locations=pl.len())
        .to_pandas(),
        on=f"{prefix}_id",
        how="left",
    )
    gdf["nb_work_locations"] = gdf["nb_work_locations"].fillna(0).astype("UInt32")
    # Add nb_study_locations.
    gdf = gdf.merge(
        data["persons"]
        .group_by(pl.col(f"study_{prefix}").alias(f"{prefix}_id"))
        .agg(nb_study_locations=pl.len())
        .to_pandas(),
        on=f"{prefix}_id",
        how="left",
    )
    gdf["nb_study_locations"] = gdf["nb_study_locations"].fillna(0).astype("UInt32")
    # Add nb_trip_origins.
    gdf = gdf.merge(
        data["trips"]
        .group_by(pl.col(f"origin_{prefix}").alias(f"{prefix}_id"))
        .agg(nb_trip_origins=pl.len())
        .to_pandas(),
        on=f"{prefix}_id",
        how="left",
    )
    gdf["nb_trip_origins"] = gdf["nb_trip_origins"].fillna(0).astype("UInt32")
    # Add nb_trip_destinations.
    gdf = gdf.merge(
        data["trips"]
        .group_by(pl.col(f"destination_{prefix}").alias(f"{prefix}_id"))
        .agg(nb_trip_destinations=pl.len())
        .to_pandas(),
        on=f"{prefix}_id",
        how="left",
    )
    gdf["nb_trip_destinations"] = gdf["nb_trip_destinations"].fillna(0).astype("UInt32")
    # Add nb_leg_starts.
    gdf = gdf.merge(
        data["legs"]
        .group_by(pl.col(f"start_{prefix}").alias(f"{prefix}_id"))
        .agg(nb_leg_starts=pl.len())
        .to_pandas(),
        on=f"{prefix}_id",
        how="left",
    )
    gdf["nb_leg_starts"] = gdf["nb_leg_starts"].fillna(0).astype("UInt32")
    # Add nb_leg_stops.
    gdf = gdf.merge(
        data["legs"]
        .group_by(pl.col(f"end_{prefix}").alias(f"{prefix}_id"))
        .agg(nb_leg_ends=pl.len())
        .to_pandas(),
        on=f"{prefix}_id",
        how="left",
    )
    gdf["nb_leg_ends"] = gdf["nb_leg_ends"].fillna(0).astype("UInt32")
    return gdf

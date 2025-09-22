from collections import defaultdict

import polars as pl
from loguru import logger

from .schema import (
    CAR_SCHEMA,
    HOUSEHOLD_SCHEMA,
    LEG_SCHEMA,
    MOTORCYCLE_SCHEMA,
    PERSON_SCHEMA,
    TRIP_SCHEMA,
)
from .schema.guarantees import AutoFixed, Invalid, Valid


def validate(data):
    is_valid = True

    # === Zones ===
    spatial_ids = defaultdict(lambda: None)
    if data.special_locations is not None:
        spatial_ids["special_location"] = data.special_locations["special_location_id"].tolist()
    if data.detailed_zones is not None:
        spatial_ids["detailed_zone"] = data.detailed_zones["detailed_zone_id"].tolist()
    if data.draw_zones is not None:
        spatial_ids["draw_zone"] = data.draw_zones["draw_zone_id"].tolist()

    # === Households ===
    is_valid &= validate_spatial_ids(data.households, spatial_ids, "home")
    is_valid &= validate_households(data)
    for variable in HOUSEHOLD_SCHEMA:
        result = variable.check_guarantees(data.households)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.households = df
            case Invalid():
                is_valid = False

    # === Persons ===
    is_valid &= validate_spatial_ids(data.persons, spatial_ids, "work")
    is_valid &= validate_spatial_ids(data.persons, spatial_ids, "study")
    is_valid &= validate_persons(data)
    for variable in PERSON_SCHEMA:
        result = variable.check_guarantees(data.persons)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.persons = df
            case Invalid():
                is_valid = False

    # === Trips ===
    is_valid &= validate_spatial_ids(data.trips, spatial_ids, "origin")
    is_valid &= validate_spatial_ids(data.trips, spatial_ids, "destination")
    is_valid &= validate_trips(data)
    for variable in TRIP_SCHEMA:
        result = variable.check_guarantees(data.trips)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.trips = df
            case Invalid():
                is_valid = False

    # === Legs ===
    is_valid &= validate_spatial_ids(data.legs, spatial_ids, "start")
    is_valid &= validate_spatial_ids(data.legs, spatial_ids, "end")
    is_valid &= validate_legs(data)
    for variable in LEG_SCHEMA:
        result = variable.check_guarantees(data.legs)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.legs = df
            case Invalid():
                is_valid = False

    for variable in CAR_SCHEMA:
        result = variable.check_guarantees(data.cars)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.cars = df
            case Invalid():
                is_valid = False

    for variable in MOTORCYCLE_SCHEMA:
        result = variable.check_guarantees(data.motorcycles)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.motorcycles = df
            case Invalid():
                is_valid = False

    return is_valid


def validate_spatial_ids(df: pl.DataFrame, spatial_ids: dict, prefix: str):
    is_valid = True
    for name in ("special_location", "detailed_zone", "draw_zone"):
        if spatial_ids[name] is not None:
            col = f"{prefix}_{name}"
            invalid_ids = df.filter(pl.col(col).is_in(spatial_ids[name]).not_())[col]
            if len(invalid_ids) == len(df):
                # All ids are invalid.
                logger.error(f"All values of `{col}` are not valid {name} ids")
                is_valid = False
            elif invalid_ids.n_unique() > 1:
                # We allow at most 1 id to be invalid (usually there is an id for "undefined zone",
                # e.g., 999999).
                # We just send a warning: there are two many missing spatial ids in the CEREMA
                # because the spatial files are incomplete.
                n = len(invalid_ids)
                first_invalids = invalid_ids.unique()[:5].sort().to_list()
                logger.warning(f"{n} values of `{col}` are not valid {name} ids ({first_invalids})")
    return is_valid


def validate_households(data):
    is_valid = True
    # Note that the NUTS correspondence guarantees and the `household_type` guarantees are not
    # validated because these variables are computed automatically by MobiSurvStd so the guarantees
    # are always satisfied by definition.
    # Guarantee that `trip_weekday` is equal to the household's `trips_weekday` (when defined).
    invalid_households = set(
        (
            data.trips.select("trip_id", "household_id", "trip_weekday")
            .join(data.households.select("household_id", "trips_weekday"), on="household_id")
            .filter(
                pl.col("trips_weekday").is_not_null(),
                pl.col("trip_weekday").is_not_null(),
                pl.col("trip_weekday") != pl.col("trips_weekday"),
            )
        )["household_id"]
    )
    if invalid_households:
        n = len(invalid_households)
        logger.warning(
            f"{n} households have `trips_weekday` != `trip_weekday` for at least one trip. "
            "The `trips_weekday` value is set to null."
        )
        data.households = data.households.with_columns(
            trips_weekday=pl.when(pl.col("household_id").is_in(invalid_households))
            .then(None)
            .otherwise("trips_weekday")
        )
    # Guarantee that `nb_cars` is not smaller than the number of cars in `cars.parquet`.
    nb_cars = data.cars.group_by("household_id").len()
    invalid_households = set(
        data.households.filter(
            pl.col("nb_cars")
            < pl.col("household_id").replace_strict(
                nb_cars["household_id"], nb_cars["len"], default=0
            )
        )["household_id"]
    )
    if invalid_households:
        n = len(invalid_households)
        logger.warning(
            f"{n} households have more cars listed in `cars.parquet` than the value of `nb_cars`. "
            "The `nb_cars` values are automatically set to the number of known cars."
        )
        data.households = data.households.with_columns(
            nb_cars=pl.max_horizontal(
                "nb_cars",
                pl.col("household_id").replace_strict(
                    nb_cars["household_id"], nb_cars["len"], default=0
                ),
            )
        )
    # Guarantee that `nb_motorcycles` is not smaller than the number of motorcycles in
    # `motorcycles.parquet`.
    nb_motorcycles = data.motorcycles.group_by("household_id").len()
    invalid_households = set(
        data.households.filter(
            pl.col("nb_motorcycles")
            < pl.col("household_id").replace_strict(
                nb_motorcycles["household_id"], nb_motorcycles["len"], default=0
            )
        )["household_id"]
    )
    if invalid_households:
        n = len(invalid_households)
        logger.warning(
            f"{n} households have more motorcycles listed in `motorcycles.parquet` than the value "
            "of `nb_motorcycles`. "
            "The `nb_motorcycles` values are automatically set to the number of known motorcycles."
        )
        data.households = data.households.with_columns(
            nb_motorcycles=pl.max_horizontal(
                "nb_motorcycles",
                pl.col("household_id").replace_strict(
                    nb_motorcycles["household_id"], nb_motorcycles["len"], default=0
                ),
            )
        )
    # Guarantee that `nb_persons` matches the actual number of persons.
    nb_persons = data.persons.group_by("household_id").len()
    invalid_households = set(
        data.households.filter(
            pl.col("nb_persons")
            != pl.col("household_id").replace_strict(
                nb_persons["household_id"], nb_persons["len"], default=0
            )
        )["household_id"]
    )
    if invalid_households:
        n = len(invalid_households)
        logger.error(
            f"{n} households have a different number of persons in `persons.parquet` than the "
            "value of `nb_persons`."
        )
        is_valid = False
    # Guarantee that `nb_persons_5plus` is compatible with the persons characteristics.
    nb_persons = data.persons.group_by("household_id").agg(
        nb_persons_5plus_lb=pl.col("age").ge(5).sum(),
        nb_persons_5plus_ub=pl.col("age").ge(5).or_(pl.col("age").is_null()).sum(),
    )
    invalid_households = set(
        data.households.join(nb_persons, on="household_id", how="left").filter(
            (pl.col("nb_persons_5plus") < pl.col("nb_persons_5plus_lb"))
            | (pl.col("nb_persons_5plus") > pl.col("nb_persons_5plus_ub"))
        )["household_id"]
    )
    if invalid_households:
        n = len(invalid_households)
        logger.error(
            f"{n} households have persons'`age` that are incompatible with the value of "
            "`nb_persons_5plus`"
        )
        is_valid = False
    # Guarantee that `nb_majors` is compatible with the persons characteristics.
    nb_majors = data.persons.group_by("household_id").agg(
        nb_majors_lb=pl.col("age").ge(18).or_(pl.col("age_class") != "17-").sum(),
        nb_majors_ub=pl.col("age")
        .ge(18)
        .or_(pl.col("age_class") != "17-")
        .or_(pl.col("age").is_null() & pl.col("age_class").is_null())
        .sum(),
    )
    invalid_households = set(
        data.households.join(nb_majors, on="household_id", how="left").filter(
            (pl.col("nb_majors") < pl.col("nb_majors_lb"))
            | (pl.col("nb_majors") > pl.col("nb_majors_ub"))
            | (pl.col("nb_majors").is_null() & pl.col("nb_majors_lb").eq(pl.col("nb_majors_ub")))
        )["household_id"]
    )
    if invalid_households:
        n = len(invalid_households)
        logger.error(
            f"{n} households have persons'`age` that are incompatible with the value of `nb_majors`"
        )
        is_valid = False
    # Guarantee that `nb_minors` is compatible with the persons characteristics.
    nb_minors = data.persons.group_by("household_id").agg(
        nb_minors_lb=pl.col("age").lt(18).or_(pl.col("age_class") == "17-").sum(),
        nb_minors_ub=pl.col("age")
        .lt(18)
        .or_(pl.col("age_class") == "17-")
        .or_(pl.col("age").is_null() & pl.col("age_class").is_null())
        .sum(),
    )
    invalid_households = set(
        data.households.join(nb_minors, on="household_id", how="left").filter(
            (pl.col("nb_minors") < pl.col("nb_minors_lb"))
            | (pl.col("nb_minors") > pl.col("nb_minors_ub"))
            | (pl.col("nb_minors").is_null() & pl.col("nb_minors_lb").eq(pl.col("nb_minors_ub")))
        )["household_id"]
    )
    if invalid_households:
        n = len(invalid_households)
        logger.error(
            f"{n} households have persons'`age` that are incompatible with the value of `nb_minors`"
        )
        is_valid = False
    return is_valid


def validate_persons(data):
    is_valid = True
    # Guarantee that the household_id exists.
    invalid_persons = data.persons.select("person_id", "household_id").join(
        data.households, on="household_id", how="anti"
    )
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        logger.error(f"{n} persons have an invalid `household_id`:\n{invalid_persons}")
        is_valid = False
    # Guarantee that `nb_trips` matches the actual number of trips.
    nb_trips = data.trips.group_by("person_id").len()
    invalid_persons = set(
        data.persons.filter(
            (
                pl.col("nb_trips")
                != pl.col("person_id").replace_strict(
                    nb_trips["person_id"], nb_trips["len"], default=0
                )
            )
            | (
                pl.col("nb_trips").is_null()
                & pl.col("person_id").is_in(data.trips["person_id"].to_list())
            )
        )["person_id"]
    )
    if invalid_persons:
        n = len(invalid_persons)
        logger.error(
            f"{n} persons have a different number of trips in `trips.parquet` than the value of "
            "`nb_trips`."
        )
        is_valid = False
    # The guarantee that `is_surveyed` is false when there is no trip is satisfied because we just
    # checked that `nb_trips` cannot be positive when there is no trip and there is another
    # guarantee that `nb_trips` is null if and only if `is_surveyed` is false.
    # Persons who have been surveyed, said that they traveled but do not have any trip, have not
    # really been surveyed...
    invalid_persons = set(
        data.persons.filter(
            pl.col("traveled_during_surveyed_day").eq("yes") & pl.col("nb_trips").eq(0)
        )["person_id"]
    )
    if invalid_persons:
        n = len(invalid_persons)
        logger.warning(
            f"{n} persons indicated having traveled during the surveyed day but do not have any "
            "trip. These persons are assumed to not have been surveyed for trips."
        )
        filter = pl.col("person_id").is_in(invalid_persons)
        data.persons = data.persons.with_columns(
            is_surveyed=pl.when(filter).then(False).otherwise("is_surveyed"),
            *(
                pl.when(filter).then(None).otherwise(col).alias(col)
                for col in (
                    "traveled_during_surveyed_day",
                    "worked_during_surveyed_day",
                    "nb_trips",
                    "sample_weight_surveyed",
                )
            ),
        )
    # Guarantee that there is no trip with work purpose when `worked_during_surveyed_day` is
    # "no:weekday".
    persons_with_work_trip = set(
        data.trips.filter(
            pl.col("destination_purpose_group").eq("work")
            | pl.col("origin_purpose_group").eq("work")
        )["person_id"]
    )
    invalid_persons = set(
        data.persons.filter(
            pl.col("person_id").is_in(persons_with_work_trip),
            worked_during_surveyed_day="no:weekday",
        )["person_id"]
    )
    if invalid_persons:
        n = len(invalid_persons)
        logger.warning(
            f"{n} persons have a work trip although they indicated having not worked because they "
            "never work on that weekday. The value of `worked_during_surveyed_day` is set to null."
        )
        data.persons = data.persons.with_columns(
            worked_during_surveyed_day=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(None)
            .otherwise("worked_during_surveyed_day")
        )
    # Guarantee that there is at least one trip with work purpose when `worked_during_surveyed_day`
    # is "yes:outside".
    invalid_persons = set(
        data.persons.filter(
            pl.col("person_id").is_in(persons_with_work_trip).not_(),
            worked_during_surveyed_day="yes:outside",
        )["person_id"]
    )
    if invalid_persons:
        n = len(invalid_persons)
        logger.warning(
            f"{n} persons do not have a work trip although they indicated having worked outside "
            "during the surveyed day. The value of `worked_during_surveyed_day` is set to null."
        )
        data.persons = data.persons.with_columns(
            worked_during_surveyed_day=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(None)
            .otherwise("worked_during_surveyed_day")
        )
    return is_valid


def validate_trips(data):
    is_valid = True
    # The guarantees for `home_sequence_index`, `main_mode_group`, `intermodality`,
    # `public_transit_acces_mode`, `public_transit_acces_mode_group`, `public_transit_egress_mode`,
    # `public_transit_egress_mode_group`, `nb_legs`, and `nb_legs_*` are satisfied by definition
    # because these variables are always generated by MobiSurvStd.
    # Guarantee that the person_id and household_id exist and are consistent.
    invalid_trips = data.trips.select("trip_id", "person_id", "household_id").join(
        data.persons, on=["person_id", "household_id"], how="anti"
    )
    if not invalid_trips.is_empty():
        n = len(invalid_trips)
        logger.error(f"{n} trips have invalid `person_id` / `household_id`:\n{invalid_trips}")
        is_valid = False
    # Guarantee that the household_id exists.
    invalid_trips = data.trips.select("trip_id", "household_id").join(
        data.households, on="household_id", how="anti"
    )
    if not invalid_trips.is_empty():
        n = len(invalid_trips)
        logger.error(f"{n} trips have an invalid `household_id`:\n{invalid_trips}")
        is_valid = False
    # Try to fix departure / arrival time wrap-around at midnight:
    # if departure times are 08:00, 20:00, 02:00, 04:00, then they are set to 08:00, 20:00, 26:00,
    # 28:00.
    recompute_durs = False
    invalid_trips = set(
        data.trips.filter(pl.col("departure_time").diff().cum_sum().over("person_id") < 0)[
            "trip_id"
        ]
    )
    if invalid_trips:
        n = len(invalid_trips)
        logger.warning(
            f"{n} trips have a departure time that is earlier than a previous trip. "
            "These trips are assumed to be departing the next day."
        )
        data.trips = data.trips.with_columns(
            departure_time=pl.when(pl.col("trip_id").is_in(invalid_trips))
            .then(pl.col("departure_time") + 24 * 60)
            .otherwise("departure_time"),
            # Arrival time also needs to be shifted.
            arrival_time=pl.when(pl.col("trip_id").is_in(invalid_trips))
            .then(pl.col("arrival_time") + 24 * 60)
            .otherwise("arrival_time"),
        )
        recompute_durs = True
    invalid_trips = set(
        data.trips.filter(pl.col("arrival_time").diff().cum_sum().over("person_id") < 0)["trip_id"]
    )
    if invalid_trips:
        n = len(invalid_trips)
        logger.warning(
            f"{n} trips have a arrival time that is earlier than a previous trip. "
            "These trips are assumed to be arriving the next day."
        )
        data.trips = data.trips.with_columns(
            arrival_time=pl.when(pl.col("trip_id").is_in(invalid_trips))
            .then(pl.col("arrival_time") + 24 * 60)
            .otherwise("arrival_time")
        )
        recompute_durs = True
    invalid_persons = set(
        data.trips.filter(pl.col("arrival_time") < pl.col("departure_time"))["person_id"]
    )
    if invalid_persons:
        n = len(invalid_persons)
        logger.warning(
            f"{n} persons have at least one trip with `arrival_time` smaller than `departure_time`."
            " The `departure_time`, `arrival_time`, and `travel_time` values for these persons "
            "are automatically set to null."
        )
        data.trips = data.trips.with_columns(
            pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit(None))
            .otherwise(col)
            .alias(col)
            for col in (
                "departure_time",
                "arrival_time",
                "travel_time",
                "origin_activity_duration",
                "destination_activity_duration",
            )
        )
    invalid_persons = set(
        data.trips.filter(
            pl.col("arrival_time") > pl.col("departure_time").shift(-1).over("person_id")
        )["person_id"]
    )
    if invalid_persons:
        n = len(invalid_persons)
        logger.warning(
            f"{n} persons have at least one trip that starts before the previous trip ended. "
            "The `departure_time`, `arrival_time`, and `travel_time` values for these persons "
            "are automatically set to null."
        )
        data.trips = data.trips.with_columns(
            pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit(None))
            .otherwise(col)
            .alias(col)
            for col in (
                "departure_time",
                "arrival_time",
                "travel_time",
                "origin_activity_duration",
                "destination_activity_duration",
            )
        )
    invalid_persons = set(
        data.trips.filter(
            pl.col("departure_time").is_null().any().over("person_id")
            | pl.col("arrival_time").is_null().any().over("person_id"),
            pl.col("departure_time").is_not_null().any().over("person_id")
            | pl.col("arrival_time").is_not_null().any().over("person_id"),
        )["person_id"]
    )
    if invalid_persons:
        n = len(invalid_persons)
        logger.warning(
            f"{n} persons have at least one trip with NULL departure or arrival time. "
            "The `departure_time`, `arrival_time`, and `travel_time` values for these persons "
            "are all automatically set to null."
        )
        data.trips = data.trips.with_columns(
            pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit(None))
            .otherwise(col)
            .alias(col)
            for col in (
                "departure_time",
                "arrival_time",
                "travel_time",
                "origin_activity_duration",
                "destination_activity_duration",
            )
        )
    if recompute_durs:
        # Durations need to be recomputed due to changes of deparure / arrival times.
        # The previous check ensure that all durations will be positive.
        data.trips = data.trips.with_columns(
            travel_time=pl.col("arrival_time") - pl.col("departure_time"),
            origin_activity_duration=pl.col("departure_time")
            - pl.col("arrival_time").shift(1).over("person_id"),
            destination_activity_duration=pl.col("departure_time").shift(-1).over("person_id")
            - pl.col("arrival_time"),
        )
    # Guarantee that the `trip_date` is not later than the `interview_date`.
    invalid_trips = set(
        data.trips.select("trip_id", "household_id", "trip_date")
        .join(data.households.select("household_id", "interview_date"), on="household_id")
        .filter(pl.col("trip_date") >= pl.col("interview_date"))["trip_id"]
    )
    if invalid_trips:
        n = len(invalid_trips)
        logger.warning(
            f"{n:,} trips have `trip_date` that is not earlier than the household's "
            "`interview_date`. The `trip_date` values are set to null."
        )
        data.trips = data.trips.with_columns(
            trip_date=pl.when(pl.col("trip_id").is_in(invalid_trips))
            .then(None)
            .otherwise("trip_date")
        )
    return is_valid


def validate_legs(data):
    is_valid = True
    # Guarantee that the trip_id, person_id, and household_id exist and are consistent.
    invalid_legs = data.legs.select("leg_id", "trip_id", "person_id", "household_id").join(
        data.trips, on=["trip_id", "person_id", "household_id"], how="anti"
    )
    if not invalid_legs.is_empty():
        n = len(invalid_legs)
        logger.error(
            f"{n} legs have invalid `trip_id` / `person_id` / `household_id`:\n{invalid_legs}"
        )
        is_valid = False
    # Guarantee that the sum of `leg_travel_time` is not longer than trip `travel_time`.
    leg_tts = data.legs.group_by("trip_id").agg(tot_leg_travel_time=pl.col("leg_travel_time").sum())
    invalid_trips = set(
        data.trips.filter(
            pl.col("travel_time")
            < pl.col("trip_id").replace_strict(
                leg_tts["trip_id"], leg_tts["tot_leg_travel_time"], default=0
            )
        )["trip_id"]
    )
    if invalid_trips:
        n = len(invalid_trips)
        logger.warning(
            f"{n} trips have a sum of `leg_travel_time` that is larger than `travel_time`. "
            "The `leg_travel_time` values are set to null."
        )
        data.legs = data.legs.with_columns(
            leg_travel_time=pl.when(pl.col("trip_id").is_in(invalid_trips))
            .then(None)
            .otherwise("leg_travel_time")
        )
    # Guarantee that the household must have extra cars when `car_type` is "other_household".
    households_with_extra_cars = set(
        data.households.select("household_id", "nb_cars")
        .join(data.cars["household_id"].value_counts(), on="household_id", how="left")
        .filter(pl.col("nb_cars") > pl.col("count").fill_null(0))["household_id"]
    )
    invalid_legs = set(
        data.legs.filter(
            pl.col("car_type").eq("other_household"),
            pl.col("household_id").is_in(households_with_extra_cars).not_(),
        )["leg_id"]
    )
    if invalid_legs:
        n = len(invalid_legs)
        logger.warning(
            f'{n} legs have `car_type` = "other_household" but the household has no extra car. '
            "The `car_type` value is set to null."
        )
        data.legs = data.legs.with_columns(
            car_type=pl.when(pl.col("leg_id").is_in(invalid_legs)).then(None).otherwise("car_type")
        )
    # Guarantee that `car_id` values are valid.
    invalid_legs = (
        data.legs.filter(pl.col("car_id").is_not_null())
        .select("leg_id", "household_id", "car_id")
        .join(data.cars, on=["household_id", "car_id"], how="anti")
    )
    if not invalid_legs.is_empty():
        n = len(invalid_legs)
        logger.error(f"{n} legs have invalid `car_id`:\n{invalid_legs}")
        is_valid = False
    # Guarantee that the household must have extra motorcycles when `motorcycle_type` is
    # "other_household".
    households_with_extra_motorcycles = set(
        data.households.select("household_id", "nb_motorcycles")
        .join(data.motorcycles["household_id"].value_counts(), on="household_id", how="left")
        .filter(pl.col("nb_motorcycles") > pl.col("count").fill_null(0))["household_id"]
    )
    invalid_legs = set(
        data.legs.filter(
            pl.col("motorcycle_type").eq("other_household"),
            pl.col("household_id").is_in(households_with_extra_motorcycles).not_(),
        )["leg_id"]
    )
    if invalid_legs:
        n = len(invalid_legs)
        logger.warning(
            f'{n} legs have `motorcycle_type` = "other_household" but the household has no extra '
            "motorcycle. The `motorcycle_type` value is set to null."
        )
        data.legs = data.legs.with_columns(
            motorcycle_type=pl.when(pl.col("leg_id").is_in(invalid_legs))
            .then(None)
            .otherwise("motorcycle_type")
        )
    # Guarantee that `motorcycle_id` values are valid.
    invalid_legs = set(
        data.legs.select("leg_id", "household_id", "motorcycle_id").join(
            data.motorcycles, on=["household_id", "motorcycle_id"], how="anti"
        )["leg_id"]
    )
    if not invalid_legs:
        n = len(invalid_legs)
        logger.error(f"{n} legs have invalid `motorcycle_id`:\n{invalid_legs}")
        is_valid = False
    # Guarantee that `nb_persons_in_vehicle` is at least 1 one `mode` is passenger related.
    invalid_legs = set(
        data.legs.filter(
            pl.col("mode").cast(pl.String).str.contains("passenger"),
            pl.col("nb_persons_in_vehicle") <= 1,
        )["leg_id"]
    )
    if invalid_legs:
        n = len(invalid_legs)
        logger.warning(
            f"{n} legs have `nb_persons_in_vehicle` <= 1 when `mode` is passenger related."
            "The values are set to null."
        )
        # All `nb_*_in_vehicles` variables are invalidated.
        data.legs = data.legs.with_columns(
            pl.when(pl.col("leg_id").is_in(invalid_legs))
            .then(pl.lit(None))
            .otherwise(col)
            .alias(col)
            for col in (
                "nb_persons_in_vehicle",
                "nb_majors_in_vehicle",
                "nb_minors_in_vehicle",
                "nb_household_members_in_vehicle",
                "nb_non_household_members_in_vehicle",
                "in_vehicle_person_ids",
            )
        )
    # Guarantee that `nb_majors_in_vehicle` is at least one when the person is major.
    major_persons = set(data.persons.filter(pl.col("age_class") != "17-")["person_id"])
    invalid_legs = set(
        data.legs.filter(
            pl.col("nb_majors_in_vehicle") == 0, pl.col("person_id").is_in(major_persons)
        )["leg_id"]
    )
    if invalid_legs:
        n = len(invalid_legs)
        logger.warning(
            f"{n} legs have `nb_majors_in_vehicle` = 0 when the person is major themself. "
            "The `nb_majors_in_vehicle` value is set to null."
        )
        data.legs = data.legs.with_columns(
            nb_majors_in_vehicle=pl.when(pl.col("leg_id").is_in(invalid_legs))
            .then(None)
            .otherwise("nb_majors_in_vehicle")
        )
    # Guarantee that `nb_minors_in_vehicle` is at least one when the person is minor.
    minor_persons = set(data.persons.filter(pl.col("age_class") == "17-")["person_id"])
    invalid_legs = set(
        data.legs.filter(
            pl.col("nb_minors_in_vehicle") == 0, pl.col("person_id").is_in(minor_persons)
        )["leg_id"]
    )
    if invalid_legs:
        n = len(invalid_legs)
        logger.warning(
            f"{n} legs have `nb_minors_in_vehicle` = 0 when the person is minor themself. "
            "The `nb_minors_in_vehicle` value is set to null."
        )
        data.legs = data.legs.with_columns(
            nb_minors_in_vehicle=pl.when(pl.col("leg_id").is_in(invalid_legs))
            .then(None)
            .otherwise("nb_minors_in_vehicle")
        )
    return is_valid

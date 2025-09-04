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

    # === Persons ===
    # Persons who have been surveyed, said that they traveled but do not have any trip, have not
    # really been surveyed...
    invalid_persons = set(
        data.persons.filter(
            pl.col("is_surveyed")
            & pl.col("traveled_during_surveyed_day").eq("yes")
            & pl.col("nb_trips").eq(0)
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

    # === Trips ===
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

    # === Legs ===
    invalid_legs = set(
        data.legs.filter(
            pl.col("mode").cast(pl.String).str.contains("passenger"),
            pl.col("nb_persons_in_vehicle") <= 1,
        )["leg_id"]
    )
    if invalid_legs:
        n = len(invalid_legs)
        logger.warning(
            f"{n} legs have `nb_persons_in_vehicle` <= 1 when `mode` is passenger related"
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

    for variable in HOUSEHOLD_SCHEMA:
        result = variable.check_guarantees(data.households)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.households = df
            case Invalid():
                is_valid = False

    for variable in PERSON_SCHEMA:
        result = variable.check_guarantees(data.persons)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.persons = df
            case Invalid():
                is_valid = False

    for variable in TRIP_SCHEMA:
        result = variable.check_guarantees(data.trips)
        match result:
            case Valid():
                pass
            case AutoFixed(df=df):
                data.trips = df
            case Invalid():
                is_valid = False

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

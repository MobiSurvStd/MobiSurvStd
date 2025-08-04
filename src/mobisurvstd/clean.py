import polars as pl
from loguru import logger


def clean(data):
    # === Trips ===
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
            for col in ("departure_time", "arrival_time", "travel_time")
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
            for col in ("departure_time", "arrival_time", "travel_time")
        )
    assert (
        data.trips["travel_time"]
        .cast(pl.Int32)
        .eq_missing(
            data.trips["arrival_time"].cast(pl.Int32) - data.trips["departure_time"].cast(pl.Int32)
        )
        .all()
    ), "`travel_time` is not equal to `arrival_time - departure_time`"

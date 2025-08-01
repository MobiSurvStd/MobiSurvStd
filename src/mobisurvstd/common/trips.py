import polars as pl

from mobisurvstd.common.modes import MODE_TO_GROUP
from mobisurvstd.common.zones import add_lng_lat_columns
from mobisurvstd.resources.admin_express import find_insee
from mobisurvstd.resources.insee_data import add_insee_data
from mobisurvstd.resources.nuts import add_nuts_data
from mobisurvstd.schema import TRIP_SCHEMA

from . import DEBUG


def clean(
    lf: pl.LazyFrame,
    year: int,
    perimeter_insees: list[str] | None = None,
    perimeter_deps: list[str] | None = None,
    special_locations: pl.DataFrame | None = None,
    detailed_zones: pl.DataFrame | None = None,
):
    existing_cols = lf.collect_schema().names()
    lf = lf.sort("original_trip_id")
    lf = add_indexing(lf, existing_cols)
    lf = add_purpose_groups(lf, existing_cols)
    lf = add_home_sequence_index(lf)
    lf = add_durations(lf, existing_cols)
    lf = add_weekdays(lf, existing_cols)
    lf = add_lng_lat(lf, existing_cols, special_locations, detailed_zones)
    lf = add_insee_columns(lf, existing_cols)
    lf = add_insee_data_columns(lf, existing_cols, year)
    lf = add_nuts_columns(lf, existing_cols)
    lf = add_intra_zones(lf, existing_cols)
    lf = add_main_mode_groups(lf, existing_cols)
    lf = add_trip_perimeter(lf, existing_cols, perimeter_insees, perimeter_deps)
    if DEBUG:
        # Try to collect the schema to check if it is valid.
        lf.collect_schema()
        lf.collect()
    return lf


def add_indexing(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add columns `trip_id`, `trip_index`, `first_trip`, `last_trip` to a trip LazyFrame."""
    if "trip_id" not in existing_cols:
        lf = lf.with_columns(trip_id=pl.int_range(1, pl.len() + 1, dtype=TRIP_SCHEMA["trip_id"]))
        existing_cols.append("trip_id")
    if "trip_index" not in existing_cols:
        lf = lf.with_columns(
            trip_index=pl.int_range(1, pl.len() + 1, dtype=TRIP_SCHEMA["trip_index"]).over(
                "person_id"
            )
        )
        existing_cols.append("trip_index")
    if "first_trip" not in existing_cols:
        lf = lf.with_columns(first_trip=pl.col("trip_index").eq(1))
        existing_cols.append("first_trip")
    if "last_trip" not in existing_cols:
        lf = lf.with_columns(
            last_trip=pl.col("trip_index").eq(pl.col("trip_index").last().over("person_id"))
        )
        existing_cols.append("last_trip")
    return lf


def add_durations(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add columns `travel_time`, `origin_activity_duration`, `destination_activity_duration` to a
    trip LazyFrame.
    """
    if "departure_time" in existing_cols and "arrival_time" in existing_cols:
        lf = lf.with_columns(
            travel_time=pl.col("arrival_time") - pl.col("departure_time"),
            origin_activity_duration=pl.col("departure_time")
            - pl.col("arrival_time").shift(1).over("person_id"),
            destination_activity_duration=pl.col("departure_time").shift(-1).over("person_id")
            - pl.col("arrival_time"),
        )
    return lf


WEEKDAY_MAP = {
    1: "monday",
    2: "tuesday",
    3: "wednesday",
    4: "thursday",
    5: "friday",
    6: "saturday",
    7: "sunday",
}


def add_weekdays(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add columns `trip_weekday` to the trip LazyFrame if column `trip_date` exists."""
    if "trip_date" in existing_cols and "trip_weekay" not in existing_cols:
        lf = lf.with_columns(
            trip_weekday=pl.col("trip_date").dt.weekday().replace_strict(WEEKDAY_MAP)
        )
    return lf


def add_purpose_groups(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add all `*_purpose_group` columns (if the `*_purpose` column exists)."""
    for col in (
        "origin_purpose",
        "origin_escort_purpose",
        "destination_purpose",
        "destination_escort_purpose",
    ):
        if col in existing_cols:
            group_col = f"{col}_group"
            lf = lf.with_columns(
                pl.col(col).cast(pl.String).str.extract(r"(\w+):?").alias(group_col)
            )
    return lf


def add_home_sequence_index(lf: pl.LazyFrame):
    """Add `home_sequence_index` column."""
    return lf.with_columns(
        home_sequence_index=pl.col("origin_purpose_group").eq("home").cum_sum().over("person_id")
    )


def add_lng_lat(
    lf: pl.LazyFrame,
    existing_cols: list[str],
    special_locations: pl.DataFrame | None,
    detailed_zones: pl.DataFrame | None,
):
    for coords, name in (
        (special_locations, "special_location"),
        (detailed_zones, "detailed_zone"),
    ):
        if coords is not None and (
            f"origin_{name}" in existing_cols or f"destination_{name}" in existing_cols
        ):
            lf = add_lng_lat_columns(lf, existing_cols, coords, prefix="origin", name=name)
            lf = add_lng_lat_columns(lf, existing_cols, coords, prefix="destination", name=name)
    return lf


def add_insee_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add `origin_insee` and `destination_insee` columns (if they do not exist already), by reading
    the origin and destination longitudes and latitudes.
    """
    for prefix in ("origin", "destination"):
        if (
            f"{prefix}_insee" in existing_cols
            or f"{prefix}_lng" not in existing_cols
            or f"{prefix}_lat" not in existing_cols
        ):
            continue
        lf = find_insee(lf, prefix, "trip_id")
        existing_cols.append(f"{prefix}_insee")
    return lf


def add_insee_data_columns(lf: pl.LazyFrame, existing_cols: list[str], year: int):
    """Add all insee data for the origin and destination municipalities."""
    for prefix in ("origin", "destination"):
        if f"{prefix}_insee" in existing_cols:
            # If the corresponding `*_dep` column already exists, then it is not added again.
            lf = add_insee_data(lf, prefix, year=year, skip_dep=f"{prefix}_dep" in existing_cols)
            existing_cols.append(f"{prefix}_insee_name")
            existing_cols.append(f"{prefix}_dep")
            if year is not None:
                existing_cols.append(f"{prefix}_aav")
    return lf


def add_nuts_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add all département and NUTS-related columns."""
    for prefix in ("origin", "destination"):
        if f"{prefix}_dep" in existing_cols:
            lf = add_nuts_data(lf, prefix)
    return lf


def add_intra_zones(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add `intra_municipality`, `intra_aav`, and `intra_dep` columns (if possible)."""
    for suffix, col in (
        ("insee", "intra_municipality"),
        ("aav", "intra_aav"),
        ("dep", "intra_dep"),
    ):
        orig_col = f"origin_{suffix}"
        dest_col = f"destination_{suffix}"
        if orig_col in existing_cols and dest_col in existing_cols:
            lf = lf.with_columns((pl.col(orig_col) == pl.col(dest_col)).alias(col))
    return lf


def add_main_mode_groups(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add `main_mode_group` columns (if the `main_mode` column exists)."""
    if "main_mode" in existing_cols:
        lf = lf.with_columns(main_mode_group=pl.col("main_mode").replace_strict(MODE_TO_GROUP))
        existing_cols.append("main_mode_group")
    return lf


def add_intermodality_column(lf: pl.LazyFrame):
    # A trip is intermodal if there is at least two legs from different mode groups (excluding all
    # walking legs).
    lf = lf.with_columns(
        intermodality=sum(
            pl.col(f"nb_legs_{mode_group}") > 0
            for mode_group in TRIP_SCHEMA["main_mode_group"].categories
            if mode_group != "walking"
        )
        >= 2
    )
    return lf


def add_trip_perimeter(
    lf: pl.LazyFrame,
    existing_cols: list[str],
    perimeter_insees: list[str] | None = None,
    perimeter_deps: list[str] | None = None,
):
    if perimeter_insees is None and perimeter_deps is None:
        # Perimeter is not defined.
        return lf
    if perimeter_insees is not None:
        assert perimeter_deps is None, (
            "Only one of `perimeter_insees` and `perimeter_deps` should be given"
        )
        if "origin_insee" not in existing_cols and "destination_insee" not in existing_cols:
            # Cannot identify trip perimeters.
            return lf
        lf = lf.with_columns(
            origin_in_perimeter=pl.col("origin_insee").is_in(perimeter_insees),
            destination_in_perimeter=pl.col("destination_insee").is_in(perimeter_insees),
        )
    else:
        if "origin_dep" not in existing_cols and "destination_dep" not in existing_cols:
            # Cannot identify trip perimeters.
            return lf
        lf = lf.with_columns(
            origin_in_perimeter=pl.col("origin_dep").is_in(perimeter_deps),
            destination_in_perimeter=pl.col("destination_dep").is_in(perimeter_deps),
        )
    lf = lf.with_columns(
        trip_perimeter=pl.when(
            pl.col("origin_in_perimeter").is_null() | pl.col("destination_in_perimeter").is_null()
        )
        .then(None)
        .when("origin_in_perimeter", "destination_in_perimeter")
        .then(pl.lit("internal"))
        .when(pl.col("origin_in_perimeter") | pl.col("destination_in_perimeter"))
        .then(pl.lit("crossing"))
        .otherwise(pl.lit("external"))
    )
    return lf

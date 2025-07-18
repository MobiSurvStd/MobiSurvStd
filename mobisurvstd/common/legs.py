import polars as pl

from mobisurvstd.common.modes import MODE_TO_GROUP
from mobisurvstd.common.zones import add_lng_lat_columns
from mobisurvstd.resources.admin_express import find_insee
from mobisurvstd.resources.insee_data import add_insee_data
from mobisurvstd.resources.nuts import add_nuts_data
from mobisurvstd.schema import LEG_SCHEMA

from . import DEBUG


def clean(
    lf: pl.LazyFrame,
    special_locations: pl.DataFrame | None = None,
    detailed_zones: pl.DataFrame | None = None,
):
    existing_cols = lf.collect_schema().names()
    lf = lf.sort("original_leg_id")
    lf = add_indexing(lf, existing_cols)
    lf = add_nb_persons_in_vehicle(lf, existing_cols)
    lf = add_mode_groups(lf, existing_cols)
    lf = add_lng_lat(lf, existing_cols, special_locations, detailed_zones)
    lf = add_insee_columns(lf, existing_cols)
    lf = add_insee_data_columns(lf, existing_cols)
    lf = add_nuts_columns(lf, existing_cols)
    if DEBUG:
        # Try to collect the schema to check if it is valid.
        lf.collect_schema()
        lf.collect()
    return lf


def add_indexing(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add columns `leg_index`, `first_leg`, `last_leg` to a leg LazyFrame."""
    if "leg_id" not in existing_cols:
        lf = lf.with_columns(leg_id=pl.int_range(1, pl.len() + 1, dtype=LEG_SCHEMA["trip_id"]))
        existing_cols.append("leg_id")
    if "leg_index" not in existing_cols:
        lf = lf.with_columns(
            leg_index=pl.int_range(1, pl.len() + 1, dtype=LEG_SCHEMA["leg_index"]).over("trip_id")
        )
        existing_cols.append("leg_index")
    if "first_leg" not in existing_cols:
        lf = lf.with_columns(first_leg=pl.col("leg_index").eq(1))
        existing_cols.append("first_leg")
    if "last_leg" not in existing_cols:
        lf = lf.with_columns(
            last_leg=pl.col("leg_index").eq(pl.col("leg_index").last().over("trip_id"))
        )
        existing_cols.append("last_leg")
    return lf


def add_nb_persons_in_vehicle(lf: pl.LazyFrame, existing_cols: list[str]):
    if (
        "nb_household_members_in_vehicle" in existing_cols
        and "nb_non_household_members_in_vehicle" in existing_cols
        and "nb_persons_in_vehicle" not in existing_cols
    ):
        lf = lf.with_columns(
            nb_persons_in_vehicle=pl.col("nb_household_members_in_vehicle")
            + pl.col("nb_non_household_members_in_vehicle")
        )
        existing_cols.append("nb_persons_in_vehicle")
    if (
        "nb_majors_in_vehicle" in existing_cols
        and "nb_minors_in_vehicle" in existing_cols
        and "nb_persons_in_vehicle" not in existing_cols
    ):
        lf = lf.with_columns(
            nb_persons_in_vehicle=pl.col("nb_majors_in_vehicle") + pl.col("nb_minors_in_vehicle")
        )
        existing_cols.append("nb_persons_in_vehicle")
    return lf


def add_mode_groups(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add `mode_group` columns (if the `mode` column exists)."""
    if "mode" in existing_cols:
        lf = lf.with_columns(mode_group=pl.col("mode").replace_strict(MODE_TO_GROUP))
        existing_cols.append("mode_group")
    return lf


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
            f"start_{name}" in existing_cols or f"end_{name}" in existing_cols
        ):
            lf = add_lng_lat_columns(lf, existing_cols, coords, prefix="start", name=name)
            lf = add_lng_lat_columns(lf, existing_cols, coords, prefix="end", name=name)
    return lf


def add_insee_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add `start_insee` and `end_insee` columns (if they do not exist already), by reading the
    start and end longitudes and latitudes.
    """
    for prefix in ("start", "end"):
        if (
            f"{prefix}_insee" in existing_cols
            or f"{prefix}_lng" not in existing_cols
            or f"{prefix}_lat" not in existing_cols
        ):
            continue
        lf = find_insee(lf, prefix, "leg_id")
        existing_cols.append(f"{prefix}_insee")
    return lf


def add_insee_data_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add all insee data for the origin and destination municipalities."""
    for prefix in ("start", "end"):
        if f"{prefix}_insee" in existing_cols:
            # If the corresponding `*_dep` column already exists, then it is not added again.
            lf = add_insee_data(lf, prefix, skip_dep=f"{prefix}_dep" in existing_cols)
            existing_cols.append(f"{prefix}_insee_name")
            existing_cols.append(f"{prefix}_dep")
    return lf


def add_nuts_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add all département and NUTS-related columns."""
    for prefix in ("start", "end"):
        if f"{prefix}_dep" in existing_cols:
            lf = add_nuts_data(lf, prefix)
    return lf

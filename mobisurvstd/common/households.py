import polars as pl

from mobisurvstd.common.admin_express import find_insee
from mobisurvstd.common.insee_data import add_insee_data
from mobisurvstd.common.nuts import add_nuts_data
from mobisurvstd.schema import HOUSEHOLD_SCHEMA


def clean(lf: pl.LazyFrame):
    existing_cols = lf.collect_schema().names()
    lf = indexing(lf)
    lf = add_bicycle_counts(lf, existing_cols)
    lf = add_insee_columns(lf, existing_cols)
    if "home_dep" in existing_cols:
        lf = add_nuts_data(lf, "home")
    return lf


def indexing(lf: pl.LazyFrame):
    lf = lf.with_columns(
        household_id=pl.int_range(1, pl.len() + 1, dtype=HOUSEHOLD_SCHEMA["household_id"])
    )
    return lf


def add_bicycle_counts(lf: pl.LazyFrame, existing_cols: list[str]):
    has_nb = "nb_bicycles" in existing_cols
    has_nb_std = "nb_standard_bicycles" in existing_cols
    has_nb_elec = "nb_electric_bicycles" in existing_cols
    if has_nb + has_nb_std + has_nb_elec == 2:
        # The third column (missing) can be deduced from the first two.
        if not has_nb:
            lf = lf.with_columns(
                nb_bicycles=pl.col("nb_standard_bicycles") + pl.col("nb_electric_bicycles")
            )
        if not has_nb_std:
            lf = lf.with_columns(
                nb_standard_bicycles=pl.col("nb_bicycles") - pl.col("nb_electric_bicycles")
            )
        if not has_nb_elec:
            lf = lf.with_columns(
                nb_electric_bicycles=pl.col("nb_bicycles") - pl.col("nb_standard_bicycles")
            )
    return lf


def add_insee_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add `home_insee`column (if it does not exist already), by reading the home longitudes and
    latitudes.
    """
    if (
        "home_insee" in existing_cols
        or "home_lng" not in existing_cols
        or "home_lat" not in existing_cols
    ):
        return lf
    lf = find_insee(lf, "home", "household_id")
    existing_cols.append("home_insee")
    return lf


def add_insee_data_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add insee name and département code for the home municipality."""
    if "home_insee" in existing_cols:
        # If the `home_dep` column already exists, then it is not added again.
        lf = add_insee_data(lf, "home", year=None, skip_dep="home_dep" in existing_cols)
        existing_cols.append("home_dep")
    return lf

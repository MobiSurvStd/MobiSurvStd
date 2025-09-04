import polars as pl

from mobisurvstd.schema import MOTORCYCLE_SCHEMA

from . import DEBUG


def clean(lf: pl.LazyFrame, extra_cols: list[str] | None = None):
    existing_cols = lf.collect_schema().names()
    columns = [variable.name for variable in MOTORCYCLE_SCHEMA if variable.name in existing_cols]
    if extra_cols is not None:
        columns.extend(extra_cols)
    lf = lf.select(columns).sort("original_motorcycle_id").collect().lazy()
    lf = indexing(lf, existing_cols)
    lf = add_mileage_bounds(lf, existing_cols)
    if DEBUG:
        # Try to collect the schema to check if it is valid.
        lf.collect_schema()
        lf.collect()
    return lf.collect().lazy()


def indexing(lf: pl.LazyFrame, existing_cols: list[str]):
    if "motorcycle_id" not in existing_cols:
        lf = lf.with_columns(motorcycle_id=pl.int_range(1, pl.len() + 1))
        existing_cols.append("motorcycle_id")
    if "motorcycle_index" not in existing_cols:
        lf = lf.with_columns(motorcycle_index=pl.int_range(1, pl.len() + 1).over("household_id"))
        existing_cols.append("motorcycle_index")
    return lf


def add_mileage_bounds(lf: pl.LazyFrame, existing_cols: list[str]):
    col = "annual_mileage"
    lb_col = f"{col}_lower_bound"
    ub_col = f"{col}_upper_bound"
    if col in existing_cols and lb_col not in existing_cols and ub_col not in existing_cols:
        lf = lf.with_columns(pl.col(col).alias(lb_col), pl.col(col).alias(ub_col))
        existing_cols.append(lb_col)
        existing_cols.append(ub_col)
    return lf

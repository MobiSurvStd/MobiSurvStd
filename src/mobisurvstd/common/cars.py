import polars as pl

from mobisurvstd.schema import CAR_SCHEMA

from . import DEBUG


def clean(lf: pl.LazyFrame):
    existing_cols = lf.collect_schema().names()
    lf = lf.sort("original_car_id")
    lf = indexing(lf, existing_cols)
    lf = add_fuel_type_group(lf, existing_cols)
    lf = add_mileage_bounds(lf, existing_cols)
    lf = add_critair_column(lf, existing_cols)
    if DEBUG:
        # Try to collect the schema to check if it is valid.
        lf.collect_schema()
        lf.collect()
    return lf


def indexing(lf: pl.LazyFrame, existing_cols: list[str]):
    if "car_id" not in existing_cols:
        lf = lf.with_columns(car_id=pl.int_range(1, pl.len() + 1, dtype=CAR_SCHEMA["car_id"]))
        existing_cols.append("car_id")
    if "car_index" not in existing_cols:
        lf = lf.with_columns(
            car_index=pl.int_range(1, pl.len() + 1, dtype=CAR_SCHEMA["car_index"]).over(
                "household_id"
            )
        )
        existing_cols.append("car_index")
    return lf


def add_fuel_type_group(lf: pl.LazyFrame, existing_cols: list[str]):
    if "fuel_type" in existing_cols:
        lf = lf.with_columns(
            fuel_type_group=pl.col("fuel_type").cast(pl.String).str.extract(r"(\w+):?")
        )
        existing_cols.append("fuel_type_group")
    return lf


def add_mileage_bounds(lf: pl.LazyFrame, existing_cols: list[str]):
    for col in ("total_mileage", "annual_mileage"):
        lb_col = f"{col}_lower_bound"
        ub_col = f"{col}_upper_bound"
        if col in existing_cols and lb_col not in existing_cols and ub_col not in existing_cols:
            lf = lf.with_columns(pl.col(col).alias(lb_col), pl.col(col).alias(ub_col))
            existing_cols.append(lb_col)
            existing_cols.append(ub_col)
    return lf


def is_essence():
    return pl.col("fuel_type").is_in(("thermic:petrol", "hybrid:regular:petrol"))


def is_diesel():
    return pl.col("fuel_type").is_in(("thermic:diesel", "hybrid:regular:diesel"))


def is_critair_e():
    return pl.col("fuel_type").eq("electric")


def is_critair_1():
    return (
        pl.col("fuel_type").eq("thermic:gas")
        | pl.col("fuel_type").eq("hybrid:plug-in")
        | is_essence().and_(pl.col("year") >= 2011)
    )


def is_critair_2():
    return is_essence().and_(pl.col("year").is_between(2006, 2010)) | is_diesel().and_(
        pl.col("year") >= 2011
    )


def is_critair_3():
    return is_essence().and_(pl.col("year").is_between(1997, 2005)) | is_diesel().and_(
        pl.col("year").is_between(2006, 2010)
    )


def is_critair_4():
    return is_diesel().and_(pl.col("year").is_between(2001, 2005))


def is_critair_5():
    return is_diesel().and_(pl.col("year").is_between(1997, 2000))


def is_critair_unclassified():
    return pl.col("year") <= 1996


def add_critair_column(lf: pl.LazyFrame, existing_cols: list[str]):
    if "critair" not in existing_cols and "year" in existing_cols and "fuel_type" in existing_cols:
        lf = lf.with_columns(
            critair=pl.when(is_critair_e())
            .then(pl.lit("E"))
            .when(is_critair_1())
            .then(pl.lit("1"))
            .when(is_critair_2())
            .then(pl.lit("2"))
            .when(is_critair_3())
            .then(pl.lit("3"))
            .when(is_critair_4())
            .then(pl.lit("4"))
            .when(is_critair_5())
            .then(pl.lit("5"))
            .when(is_critair_unclassified())
            .then(pl.lit("N"))
            .otherwise(pl.lit(None))
        )
        existing_cols.append("critair")
    return lf

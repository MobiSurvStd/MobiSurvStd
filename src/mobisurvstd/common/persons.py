import polars as pl

from mobisurvstd.common.zones import add_lng_lat_columns
from mobisurvstd.resources.admin_express import find_insee
from mobisurvstd.resources.insee_data import add_insee_data
from mobisurvstd.resources.nuts import add_nuts_data
from mobisurvstd.schema import AGE_CLASS_TO_CODE, PCS_CODES, PERSON_SCHEMA, STUDENT_GROUP_MAP

from . import DEBUG


def clean(
    lf: pl.LazyFrame,
    special_locations: pl.DataFrame | None = None,
    detailed_zones: pl.DataFrame | None = None,
    extra_cols: list[str] | None = None,
):
    existing_cols = lf.collect_schema().names()
    columns = [variable.name for variable in PERSON_SCHEMA if variable.name in existing_cols]
    if extra_cols is not None:
        columns.extend(extra_cols)
    lf = lf.select(columns).collect().lazy()
    lf = indexing(lf, existing_cols)
    lf = add_age_class(lf, existing_cols)
    lf = add_pcs_group(lf, existing_cols)
    lf = add_professional_occupation(lf, existing_cols)
    lf = add_student_group(lf, existing_cols)
    lf = add_has_pt_subscription(lf, existing_cols)
    lf = add_work_only_at_home(lf, existing_cols)
    lf = add_lng_lat(lf, existing_cols, special_locations, detailed_zones)
    lf = add_insee_columns(lf, existing_cols)
    lf = add_insee_data_columns(lf, existing_cols)
    lf = add_nuts_columns(lf, existing_cols)
    if DEBUG:
        # Try to collect the schema to check if it is valid.
        lf.collect_schema()
        lf.collect()
    return lf.collect().lazy()


def indexing(lf: pl.LazyFrame, existing_cols: list[str]):
    if "person_id" not in existing_cols:
        lf = lf.with_columns(person_id=pl.int_range(1, pl.len() + 1))
        existing_cols.append("person_id")
    if "person_index" not in existing_cols:
        lf = lf.with_columns(person_index=pl.int_range(1, pl.len() + 1).over("household_id"))
        existing_cols.append("person_index")
    return lf


def age_to_age_class(expr: pl.Expr):
    return (
        pl.when(expr < 18)
        .then(pl.lit("17-"))
        .when(expr < 25)
        .then(pl.lit("18-24"))
        .when(expr < 35)
        .then(pl.lit("25-34"))
        .when(expr < 50)
        .then(pl.lit("35-49"))
        .when(expr < 65)
        .then(pl.lit("50-64"))
        .when(expr < 75)
        .then(pl.lit("65-74"))
        .otherwise(pl.lit("75+"))
    )


def add_age_class(lf: pl.LazyFrame, existing_cols: list[str]):
    if "age" in existing_cols and "age_class" not in existing_cols:
        lf = lf.with_columns(age_class=age_to_age_class(pl.col("age")))
        existing_cols.append("age_class")
    if "age_class" in existing_cols:
        assert "age_class_code" not in existing_cols
        lf = lf.with_columns(age_class_code=pl.col("age_class").replace_strict(AGE_CLASS_TO_CODE))
        existing_cols.append("age_class_code")
    return lf


def add_professional_occupation(lf: pl.LazyFrame, existing_cols: list[str]):
    if (
        "detailed_professional_occupation" in existing_cols
        and "professional_occupation" not in existing_cols
    ):
        lf = lf.with_columns(
            professional_occupation=pl.col("detailed_professional_occupation").str.extract(
                r"(\w+):?"
            )
        )
        existing_cols.append("professional_occupation")
    return lf


def add_pcs_group(lf: pl.LazyFrame, existing_cols: list[str]):
    if "pcs_group_code" in existing_cols and "pcs_group" not in existing_cols:
        lf = lf.with_columns(pcs_group=pl.col("pcs_group_code").replace_strict(PCS_CODES))
        existing_cols.append("pcs_group")
    return lf


def add_student_group(lf: pl.LazyFrame, existing_cols: list[str]):
    if "student_category" in existing_cols and "student_group" not in existing_cols:
        lf = lf.with_columns(
            student_group=pl.col("student_category").replace_strict(STUDENT_GROUP_MAP)
        )
    return lf


def add_has_pt_subscription(lf: pl.LazyFrame, existing_cols: list[str]):
    if (
        "public_transit_subscription" in existing_cols
        and "has_public_transit_subscription" not in existing_cols
    ):
        lf = lf.with_columns(
            has_public_transit_subscription=pl.col("public_transit_subscription").str.starts_with(
                "yes:"
            )
        )
        existing_cols.append("has_public_transit_subscription")
    return lf


def add_work_only_at_home(lf: pl.LazyFrame, existing_cols: list[str]):
    if "workplace_singularity" in existing_cols and "work_only_at_home" not in existing_cols:
        lf = lf.with_columns(work_only_at_home=pl.col("workplace_singularity").eq("unique:home"))
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
            f"work_{name}" in existing_cols or f"study_{name}" in existing_cols
        ):
            lf = add_lng_lat_columns(lf, existing_cols, coords, prefix="work", name=name)
            lf = add_lng_lat_columns(lf, existing_cols, coords, prefix="study", name=name)
    return lf


def add_insee_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add `work_insee` and `study_insee` columns (if they do not exist already), by reading
    the work and study longitudes and latitudes.
    """
    for prefix in ("work", "study"):
        if (
            f"{prefix}_insee" in existing_cols
            or f"{prefix}_lng" not in existing_cols
            or f"{prefix}_lat" not in existing_cols
        ):
            continue
        lf = find_insee(lf, prefix, "person_id")
        existing_cols.append(f"{prefix}_insee")
    return lf


def add_insee_data_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    for prefix in ("work", "study"):
        insee_col = f"{prefix}_insee"
        dep_col = f"{prefix}_dep"
        if insee_col in existing_cols:
            lf = add_insee_data(lf, prefix, year=None, skip_dep=dep_col in existing_cols)
            existing_cols.append(dep_col)
    return lf


def add_nuts_columns(lf: pl.LazyFrame, existing_cols: list[str]):
    """Add all département and NUTS-related columns."""
    for prefix in ("work", "study"):
        if f"{prefix}_dep" in existing_cols:
            lf = add_nuts_data(lf, prefix)
    return lf

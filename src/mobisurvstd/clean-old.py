import itertools

import geopandas as gpd
import polars as pl

from .common.modes import MODE_TO_GROUP
from .common.persons import PCS_CODES

# Regular expression to match INSEE municipality codes.
INSEE_REGEX = "^[0-9][0-9AB][0-9][0-9][0-9]$"
# Minimum authorized age between a parent and their child.
CHILD_AGE_THRS = 14
# Check if the origin (purpose, location) matches the destination of the previous trip: "yes",
# "warn", or "no".
CHECK_ORIGIN_MATCHES_PREV_DEST = "warn"
# Check if the origin special location matches the destination special location of the previous leg:
# "yes", "warn", or "no".
CHECK_START_MATCHED_PREV_END = "warn"
PCS2020_CODES = (
    10,
    21,
    22,
    23,
    31,
    33,
    34,
    35,
    37,
    38,
    42,
    43,
    44,
    45,
    46,
    47,
    47,
    52,
    53,
    54,
    55,
    56,
    62,
    63,
    64,
    65,
    67,
    68,
    69,
)
PCS2003_CODES = (
    10,
    21,
    22,
    23,
    31,
    32,
    36,
    41,
    46,
    47,
    48,
    51,
    54,
    55,
    56,
    61,
    66,
    69,
    71,
    72,
    73,
    76,
    81,
    82,
)


def all_null_or_all_defined(s: pl.Series, msg: str):
    assert s.is_null().all() or s.is_not_null().all(), msg


def all_defined(df: pl.DataFrame, col: str):
    assert df[col].is_not_null().all(), f"Column `{col}` is not always non-null"


def all_null_for(df: pl.DataFrame, col: str, cond: pl.Expr, cond_str: str, force=False):
    mask = cond & pl.col(col).is_not_null()
    n = df.filter(mask).select(pl.len()).item()
    if n == 0:
        return
    if force:
        print(f"Warning. For {n} {cond_str}, value of `{col}` is not null.")
        print(f"The `{col}` value is automatically changed to null.")
        df = df.with_columns(pl.when(mask).then(pl.lit(None)).otherwise(pl.col(col)).alias(col))
    else:
        raise AssertionError(f"There are some {cond_str} with a non-null value for `{col}`")


def all_defined_for(df: pl.DataFrame, col: str, cond: pl.Expr, cond_str: str):
    assert df.select((cond & pl.col(col).is_null()).any().not_()).item(), (
        f"There are some {cond_str} with a null value for `{col}`"
    )


def is_sorted(df: pl.DataFrame, col: str):
    assert df[col].is_sorted(), f"Values of `{col}` are not sorted in increasing order"


def valid_insee_codes(df: pl.DataFrame, col: str):
    assert df[col].str.contains(INSEE_REGEX).all(), (
        f"Column `{col}` contains invalid INSEE municipalities"
    )


def same_as_next_in_group(
    df: pl.DataFrame, col_prev: str, col_next: str, group_col: str, warn_only=False
):
    # We use `ne_missing` to handle cases where prev is null or next is defined (or the reverse).
    # The second condition means that we don't consider the last row in the group (where next is by
    # definition null).
    nb_invalids = df.select(
        (
            pl.col(col_prev).ne_missing(pl.col(col_next).shift(-1).over(group_col))
            & (pl.int_range(1, pl.len() + 1) != pl.len()).over(group_col)
        ).sum()
    ).item()
    if nb_invalids == 0:
        return
    if warn_only:
        print(
            f"Warning. `{col_prev}` does not match the next `{col_next}` over `{group_col}` for "
            f"{nb_invalids} values"
        )
    else:
        raise AssertionError(f"`{col_prev}` does not match the next `{col_next}`")


def perimeter_check(trips: pl.DataFrame, ids: set, zone: str):
    n = (
        trips.filter(
            pl.col("trip_perimeter") == "internal",
            (
                pl.col(f"origin_{zone}_zone").is_in(ids)
                & pl.col(f"destination_{zone}_zone").is_in(ids)
            ).not_(),
        )
        .select(pl.len())
        .item()
    )
    if n > 0:
        print(
            f"Warning. For {n} trips, origin or destination is not in the survey's {zone} zone ids "
            'with `trip_perimeter` equal to "internal"'
        )
    n = (
        trips.filter(
            pl.col("trip_perimeter") == "crossing",
            (
                pl.col(f"origin_{zone}_zone").is_in(ids)
                | pl.col(f"destination_{zone}_zone").is_in(ids)
            ).not_(),
        )
        .select(pl.len())
        .item()
    )
    if n > 0:
        print(
            f"Warning. For {n} trips, origin and destination are both not in the survey's {zone} "
            'zone ids with `trip_perimeter` equal to "crossing"'
        )
    n = (
        trips.filter(
            pl.col("trip_perimeter") == "crossing",
            pl.col(f"origin_{zone}_zone").is_in(ids),
            pl.col(f"destination_{zone}_zone").is_in(ids),
        )
        .select(pl.len())
        .item()
    )
    if n > 0:
        print(
            f"Warning. For {n} trips, origin and destination are both in the survey's {zone} zone "
            'ids with `trip_perimeter` equal to "crossing"'
        )
    n = (
        trips.filter(
            pl.col("trip_perimeter") == "external",
            pl.col(f"origin_{zone}_zone").is_in(ids)
            | pl.col(f"destination_{zone}_zone").is_in(ids),
        )
        .select(pl.len())
        .item()
    )
    if n > 0:
        print(
            f"Warning. For {n} trips, origin or destination is in the survey's {zone} zone ids "
            'with `trip_perimeter` equal to "external"'
        )


def intersect_check(
    df: pl.DataFrame,
    intersect_df: pl.DataFrame,
    col_prefix: str,
    zone1: str,
    zone2: str,
    id_col: str,
):
    invalids = (
        df.select(id_col, f"{col_prefix}_{zone1}", f"{col_prefix}_{zone2}")
        # Only run the check for the rows were both columns correspond to zones whose intersection
        # is observed.
        .filter(
            pl.col(f"{col_prefix}_{zone1}").is_in(intersect_df[f"{zone1}_id"]),
            pl.col(f"{col_prefix}_{zone2}").is_in(intersect_df[f"{zone2}_id"]),
        )
        .join(
            intersect_df,
            left_on=[f"{col_prefix}_{zone1}", f"{col_prefix}_{zone2}"],
            right_on=[f"{zone1}_id", f"{zone2}_id"],
            how="anti",
        )
    )
    if not invalids.is_empty():
        n = len(invalids)
        print(
            f"Warning. {n} values of `{col_prefix}_{zone1}` correspond to zones which do not "
            f"intersect with the zone from `{col_prefix}_{zone2}`"
        )
        matching_zones = intersect_df.filter(
            pl.col(f"{zone1}_id").is_in(invalids[f"{col_prefix}_{zone1}"])
        )
        assert (
            matching_zones[f"{zone1}_id"].n_unique() == invalids[f"{col_prefix}_{zone1}"].n_unique()
        ), "Cannot reconcile bad zone intersections"
        # Note. The `default=None` in the `replace_strict` is only here to provide some value for
        # the rows not matched in the `pl.when`. For the matched value, the default should not be
        # used.
        df = df.with_columns(
            pl.when(pl.col(id_col).is_in(invalids[id_col]))
            .then(
                pl.col(f"{col_prefix}_{zone1}").replace_strict(
                    matching_zones[f"{zone1}_id"], matching_zones[f"{zone2}_id"], default=None
                )
            )
            .otherwise(f"{col_prefix}_{zone2}")
            .alias(f"{col_prefix}_{zone2}")
        )
        print("The values have been automatically fixed")
    return df


def clean(
    households: pl.DataFrame,
    cars: pl.DataFrame,
    motorcycles: pl.DataFrame,
    persons: pl.DataFrame,
    trips: pl.DataFrame,
    legs: pl.DataFrame,
    special_locations: gpd.GeoDataFrame | None,
    detailed_zones: gpd.GeoDataFrame | None,
    draw_zones: gpd.GeoDataFrame | None,
    insee_zones: gpd.GeoDataFrame | None,
):
    trips_with_persons = trips.lazy().join(persons.lazy(), on="person_id", how="left")
    legs_with_trips = legs.lazy().join(trips.lazy(), on="trip_id", how="left")
    legs_with_persons = legs.lazy().join(persons.lazy(), on="person_id", how="left")

    # === Households ===
    # Some columns have values that are either all null or all defined.
    for col in (
        "survey_method",
        "sample_weight",
        "home_detailed_zone",
        "home_draw_zone",
        "home_insee",
    ):
        all_null_or_all_defined(households[col], "Column `col` is null for some values")
    all_defined(households, "household_id")
    assert households["household_id"].min() == 1, "Column `household_id` does not start at 1"
    assert households["household_id"].max() == len(households), (
        "Column `household_id` does not end at the number of households"
    )
    is_sorted(households, "household_id")
    assert households["sample_weight"].ge(0).all(), (
        "Column `sample_weight` is negative for some values"
    )
    if detailed_zones is not None:
        assert households["home_detailed_zone"].is_in(detailed_zones["detailed_zone_id"]).all(), (
            "Some values in `home_detailed_zone` are not valid detailed zone ids"
        )
    if draw_zones is not None:
        assert households["home_draw_zone"].is_in(draw_zones["draw_zone_id"]).all(), (
            "Some values in `home_draw_zone` are not valid draw zone ids"
        )
    valid_insee_codes(households, "home_insee")
    if insee_zones is not None:
        n = households["home_insee"].is_in(insee_zones["insee_id"]).not_().sum()
        if n > 0:
            print(f"Warning. `home_insee` is not in the defined INSEE zones for {n} households")
    car_counts = cars["household_id"].value_counts()
    assert (
        households.lazy()
        .join(car_counts.lazy(), on="household_id")
        .select((pl.col("nb_cars") >= pl.col("count")).all())
        .collect()
        .item()
    ), "Some households have more cars defined than the value of `nb_cars`"
    motorcycle_counts = motorcycles["household_id"].value_counts()
    assert (
        households.lazy()
        .join(motorcycle_counts.lazy(), on="household_id")
        .select((pl.col("nb_motorcycles") >= pl.col("count")).all())
        .collect()
        .item()
    ), "Some households have more motorcycles defined than the value of `nb_motorcycles`"
    assert households.select(
        (
            pl.col("nb_standard_bicycles").is_null()
            | pl.col("nb_electric_bicycles").is_null()
            | (
                (
                    pl.col("nb_standard_bicycles") + pl.col("nb_electric_bicycles")
                    == pl.col("nb_bicycles")
                )
                & pl.col("nb_bicycles").is_not_null()
            )
        ).all()
    ).item(), (
        "The property `nb_bicycles = nb_standard_bicycles + nb_electric_bicycles` is not always "
        "verified"
    )
    # The test below ensures that (i) `nb_persons` is not null, (ii) `nb_persons` is positive,
    # (iii) `nb_persons` matches the number of persons for this household.
    person_counts = persons.group_by("household_id").agg(nb_persons=pl.len())
    assert households.join(
        person_counts, on=["household_id", "nb_persons"], how="anti"
    ).is_empty(), (
        "Column `nb_persons` does not match the actual number of persons for some households"
    )

    # === Persons ===
    all_defined(persons, "person_id")
    assert persons["person_id"].min() == 1, "Column `person_id` does not start at 1"
    assert persons["person_id"].max() == len(persons), (
        "Column `person_id` does not end at the number of persons"
    )
    is_sorted(persons, "person_id")
    all_defined(persons, "household_id")
    assert persons["household_id"].is_in(households["household_id"]).all(), (
        "Column `household_id` does not match a valid household id"
    )
    is_sorted(persons, "household_id")
    all_defined(persons, "person_index")
    # The test below ensures that `person_index` values are sorted within a household.
    assert persons.select(
        (pl.col("person_index") == pl.int_range(1, pl.len() + 1).over("household_id")).all()
    ).item(), (
        "Column `person_index` does not range from 1 to the number of persons within a household"
    )
    # Check: at least one reference person per household.
    invalid_household_ids = (
        persons.group_by("household_id")
        .agg(
            is_valid=pl.col("reference_person_link").is_null().all()
            | pl.col("reference_person_link").eq("reference_person").any()
        )
        .filter(pl.col("is_valid").not_())["household_id"]
    )
    if not invalid_household_ids.is_empty():
        n = len(invalid_household_ids)
        print(f"Warning. There is no reference person defined for {n} households.")
        print("The reference person is automatically set to the first person.")
        persons = persons.with_columns(
            reference_person_link=pl.when(
                pl.col("household_id").is_in(invalid_household_ids) & pl.col("person_index") == 1
            )
            .then(pl.lit("reference_person"))
            .otherwise(pl.col("reference_person_link"))
        )
    # Check: exactly one reference person per household.
    invalid_household_ids = (
        persons.group_by("household_id")
        .agg(
            is_valid=pl.col("reference_person_link").is_null().all()
            | pl.col("reference_person_link").eq("reference_person").sum().eq(1)
        )
        .filter(pl.col("is_valid").not_())["household_id"]
    )
    if not invalid_household_ids.is_empty():
        n = len(invalid_household_ids)
        print(f"Warning. There is more than one reference person defined for {n} households.")
        print(
            "The `reference_person_link` value is automatically set to null for the extra "
            "reference persons."
        )
        persons = persons.with_columns(
            reference_person_link=pl.when(
                pl.col("household_id").is_in(invalid_household_ids)
                & (pl.col("reference_person_link") == "reference_person")
                & (
                    (pl.col("reference_person_link") == "reference_person")
                    .cum_sum()
                    .over("household_id")
                    > 1
                )
            )
            .then(pl.lit(None))
            .otherwise(pl.col("reference_person_link"))
        )
    # Maximum age is 125.
    if persons["age"].max() > 125:
        n = (persons["age"] > 125).sum()
        print(f"Warning. There are {n} persons with a age larger than 125.")
        print("The age is automatically capped to 125.")
        persons = persons.with_columns(pl.min_horizontal(pl.col("age"), 125))
    # Check: Age difference between parents and children.
    invalid_person_ids = persons.with_columns(
        parent_max_age=pl.col("age")
        .filter(pl.col("reference_person_link").is_in(("reference_person", "spouse")))
        .max()
        .over("household_id"),
    ).filter(
        pl.col("reference_person_link").eq("child")
        & (pl.col("parent_max_age") - pl.col("age") < CHILD_AGE_THRS)
    )["person_id"]
    if not invalid_person_ids.is_empty():
        n = len(invalid_person_ids)
        print(
            "Warning. The age difference to the oldest parent is less than "
            f"{CHILD_AGE_THRS} years for {n} children."
        )
        # If there is no spouse and there is only one child with invalid age, then the child's link
        # is changed to spouse.
        # Example: reference_person (37 y.o.), child (37 y.o.), child (3 y.o.)
        new_spouses = persons.filter(
            # The person has an age problem.
            pl.col("person_id").is_in(invalid_person_ids)
            # There is no spouse in the household.
            & pl.col("reference_person_link").ne("spouse").all().over("household_id")
            # There is only one person in the household with an age problem.
            & pl.col("person_id").is_in(invalid_person_ids).sum().over("household_id").eq(1)
        )["person_id"]
        n1 = len(new_spouses)
        if n1 > 0:
            print(f"For {n1} persons the status is automatically changed from child to spouse.")
            persons = persons.with_columns(
                reference_person_link=pl.when(pl.col("person_id").is_in(new_spouses))
                .then(pl.lit("spouse"))
                .otherwise(pl.col("reference_person_link"))
            )
        # If (i) there are two spouses (= 3 parents), (ii) the youngest parent is a spouse,
        # (iii) the age difference between the youngest parent and the second-youngest parent is not
        # less than # CHILD_AGE_THRS years, and (iv) the age difference between the second-youngest
        # parent and # the oldest is less than CHILD_AGE_THRS years, then the youngest parent can be
        # changed to a # child while satisfying all age constraints.
        # Example: reference_person (56 y.o.), spouse (55 y.o.), spouse (23 y.o.), child (22 y.o.).
        new_children = persons.with_columns(
            parent_min_age=pl.col("age")
            .filter(pl.col("reference_person_link").is_in(("reference_person", "spouse")))
            .min()
            .over("household_id"),
            parent_median_age=pl.col("age")
            .filter(pl.col("reference_person_link").is_in(("reference_person", "spouse")))
            .median()
            .over("household_id"),
            parent_max_age=pl.col("age")
            .filter(pl.col("reference_person_link").is_in(("reference_person", "spouse")))
            .max()
            .over("household_id"),
        ).filter(
            # There is exactly one person with an age problem in the household.
            pl.col("person_id").is_in(invalid_person_ids).sum().over("household_id").eq(1)
            # There are two spouses in the household.
            & pl.col("reference_person_link").eq("spouse").sum().over("household_id").eq(2)
            # The youngest parent is younger by more than CHILD_AGE_THRS years to the other parents.
            & (pl.col("parent_median_age") - pl.col("parent_min_age") >= CHILD_AGE_THRS)
            # The two oldest parents have less than CHILD_AGE_THRS age difference.
            & (pl.col("parent_max_age") - pl.col("parent_median_age") < CHILD_AGE_THRS)
            # The current person is the youngest parent.
            & pl.col("age").eq(pl.col("parent_min_age"))
            # The current person is a spouse.
            & pl.col("reference_person_link").eq("spouse")
        )["person_id"]
        n2 = len(new_children)
        if n2 > 0:
            print(f"For {n2} persons the status is automatically changed from spouse to child.")
            persons = persons.with_columns(
                reference_person_link=pl.when(pl.col("person_id").is_in(new_children))
                .then(pl.lit("child"))
                .otherwise(pl.col("reference_person_link"))
            )
        if n > n1 + n2:
            m = n - n1 - n2
            print(
                f"For {m} persons, the `reference_person_link` value is automatically set to null "
                'instead of "child".'
            )
            persons = persons.with_columns(
                reference_person_link=pl.when(
                    pl.col("person_id").is_in(invalid_person_ids)
                    & pl.col("person_id").is_in(new_spouses).not_()
                    & pl.col("person_id").is_in(new_children).not_()
                )
                .then(pl.lit(None))
                .otherwise(pl.col("reference_person_link"))
            )
    invalid_persons = persons.filter(
        pl.col("education_level").is_not_null() | pl.col("detailed_education_level").is_not_null(),
        pl.col("professional_occupation").eq("student"),
    )["person_id"]
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(
            f"Warning. {n} students have a non-null `education_level` or `detailed_education_level"
        )
        print("The values are automatically set to null")
        persons = persons.with_columns(
            education_level=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit(None))
            .otherwise(pl.col("education_level")),
            detailed_education_level=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit(None))
            .otherwise(pl.col("detailed_education_level")),
        )
    assert persons.select(
        (pl.col("education_level").is_not_null() & pl.col("professional_occupation").eq("student"))
        .not_()
        .all()
    ).item(), (
        "The value of `education_level` is incompatible with the value of "
        "`professional_occupation` for some persons"
    )
    assert persons.select(
        (
            pl.col("professional_occupation").ne("worker")
            | pl.col("detailed_professional_occupation").is_in(
                ("worker:full_time", "worker:part_time", "worker:unspecified")
            )
        ).all()
    ).item(), "Some workers have a `detailed_professional_occupation` that is not work-related"
    assert persons.select(
        (
            pl.col("professional_occupation").ne("student")
            | pl.col("detailed_professional_occupation").is_in(
                ("student:primary_or_secondary", "student:higher", "student:apprenticeship")
            )
        ).all()
    ).item(), "Some students have a `detailed_professional_occupation` that is not student-related"
    assert persons.select(
        (
            pl.col("professional_occupation").ne("other")
            | pl.col("detailed_professional_occupation").is_in(
                ("other:unemployed", "other:retired", "other:homemaker", "other:unspecified")
            )
        ).all()
    ).item(), (
        'Some persons with `professional_occupation` "other" have a '
        "`detailed_professional_occupation` that is work or study related"
    )
    assert persons.select(
        (
            (pl.col("professional_occupation") == "worker")
            & (pl.col("secondary_professional_occupation") == "work")
        )
        .any()
        .not_()
    ).item(), 'Some workers have a `secondary_professional_occupation` equal to "work"'
    assert persons.select(
        (
            (pl.col("professional_occupation") == "student")
            & (pl.col("secondary_professional_occupation") == "education")
        )
        .any()
        .not_()
    ).item(), 'Some students have a `secondary_professional_occupation` equal to "education"'
    is_nonworking_student = pl.col("professional_occupation").eq("student") & pl.col(
        "secondary_professional_occupation"
    ).ne_missing("work")
    invalid_persons = (
        persons.filter(is_nonworking_student & pl.col("pcs_group").is_not_null())
        .select("person_id")
        .to_series()
    )
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(f"Warning. {n} students have a non-null `pcs_group`")
        print('The `secondary_professional_occupation` value is automatically set to "work"')
        persons = persons.with_columns(
            secondary_professional_occupation=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit("work"))
            .otherwise(pl.col("secondary_professional_occupation"))
        )
    # The test below check the 3 guarantees for `pcs_group_code`.
    assert persons.select(
        pl.col("pcs_group_code")
        .replace_strict(PCS_CODES, return_dtype=pl.String)
        .eq_missing(pl.col("pcs_group"))
        .all()
    ).item(), "Columns `pcs_group` and `pcs_group_code` have inconsistencies"
    invalid_persons = persons.filter(pl.col("pcs_category_code2020").is_in(PCS2020_CODES).not_())[
        "person_id"
    ]
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(f"Warning. {n} persons have an invalid `pcs_category_code2020`")
        print("The value is automatically set to null")
        persons = persons.with_columns(
            pcs_category_code2020=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit(None))
            .otherwise(pl.col("pcs_category_code2020"))
        )
    all_defined_for(
        persons,
        "pcs_group_code",
        pl.col("pcs_category_code2020").is_not_null(),
        "non-null `pcs_category_code2020`",
    )
    assert (persons["pcs_category_code2020"] // 10 == persons["pcs_group_code"]).all(), (
        "Columns `pcs_category_code2020` and `pcs_group_code have inconsistencies"
    )
    invalid_persons = persons.filter(pl.col("pcs_category_code2003").is_in(PCS2003_CODES).not_())[
        "person_id"
    ]
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(f"Warning. {n} persons have an invalid `pcs_category_code2003`")
        print("The value is automatically set to null")
        persons = persons.with_columns(
            pcs_category_code2003=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit(None))
            .otherwise(pl.col("pcs_category_code2003"))
        )
    all_defined_for(
        persons,
        "pcs_group_code",
        pl.col("pcs_category_code2003").is_not_null(),
        "non-null `pcs_category_code2003`",
    )
    assert (persons["pcs_category_code2003"] // 10 == persons["pcs_group_code"]).all(), (
        "Columns `pcs_category_code2003` and `pcs_group_code have inconsistencies"
    )
    valid_insee_codes(persons, "work_insee")
    assert persons["work_commute_euclidean_distance_km"].ge(0).all(), (
        "Column `work_commute_euclidean_distance_km` is negative for some values"
    )
    is_not_worker = pl.col("professional_occupation").ne("worker") & pl.col(
        "secondary_professional_occupation"
    ).ne("work")
    mask = pl.col("work_commute_euclidean_distance_km").is_not_null() & is_not_worker
    if persons.select(mask.any()).item():
        if not (persons.filter(mask)["work_commute_euclidean_distance_km"] == 0.0).all():
            # When all distances are 0, we can silently set them to null.
            n = persons.select(mask.sum()).item()
            print(
                f"Warning. The `work_commute_euclidean_distance_km` variable is set for {n} "
                "non-worker persons."
            )
            print("The value is automatically set to null.")
        persons = persons.with_columns(
            work_commute_euclidean_distance_km=pl.when(is_not_worker)
            .then(pl.lit(None))
            .otherwise(pl.col("work_commute_euclidean_distance_km"))
        )
    for col in (
        "work_only_at_home",
        "work_special_location",
        "work_detailed_zone",
        "work_draw_zone",
        "work_insee",
        "has_car_for_work_commute",
        "telework",
        "work_car_parking",
        "work_bicycle_parking",
    ):
        all_null_for(persons, col, is_not_worker, "non-workers")
        if col not in ("work_only_at_home", "worked_during_surveyed_day"):
            all_null_for(persons, col, pl.col("work_only_at_home"), "workers working only at home")
    invalid_persons = (
        persons.filter(
            is_not_worker
            & pl.col("secondary_professional_occupation").ne_missing("work")
            & pl.col("worked_during_surveyed_day").is_in(
                (
                    "yes:outside",
                    "yes:home:usual",
                    "yes:home:telework",
                    "yes:home:other",
                    "yes:unspecified",
                )
            )
        )
        .select("person_id")
        .to_series()
    )
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(f"Warning. {n} non-workers have indicating having worked during the surveyed day")
        print('Their `secondary_professional_occupation` value is automatically set to "work"')
        persons = persons.with_columns(
            secondary_professional_occupation=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit("work"))
            .otherwise(pl.col("secondary_professional_occupation"))
        )
    invalid_persons = (
        persons.filter(
            is_not_worker
            & pl.col("secondary_professional_occupation").ne_missing("work")
            & pl.col("worked_during_surveyed_day").is_in(
                ("no:weekday", "no:reason", "no:unspecified")
            )
        )
        .select("person_id")
        .to_series()
    )
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(f"Warning. {n} non-workers have indicating having not worked during the surveyed day")
        print("The `worked_during_surveyed_day` value is automatically set to null")
        persons = persons.with_columns(
            worked_during_surveyed_day=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit(None))
            .otherwise(pl.col("worked_during_surveyed_day"))
        )
    all_null_for(
        persons,
        "worked_during_surveyed_day",
        is_not_worker & pl.col("secondary_professional_occupation").ne_missing("work"),
        "non-wokers",
    )
    assert persons.select(
        (pl.col("work_only_at_home") & (pl.col("work_commute_euclidean_distance_km") > 0.0))
        .any()
        .not_()
    ).item(), (
        "Column `work_commute_euclidean_distance_km` is positive for some persons working only at "
        "home"
    )
    is_not_student = pl.col("professional_occupation").ne("student")
    for col in (
        "student_group",
        "student_category",
        "study_only_at_home",
        "study_special_location",
        "study_detailed_zone",
        "study_draw_zone",
        "study_insee",
        "has_car_for_study_commute",
        "study_car_parking",
        "study_bicycle_parking",
    ):
        all_null_for(persons, col, is_not_student, "non-students")
        if col not in ("student_group", "student_category", "study_only_at_home"):
            all_null_for(
                persons, col, pl.col("study_only_at_home"), "persons studying only at home"
            )
    student_constraints = (
        ("student:primary_or_secondary", ("primaire", "collège", "lycée")),
        ("student:apprenticeship", ("lycée", "supérieur")),
        ("student:higher", ("supérieur",)),
    )
    for occ, groups in student_constraints:
        assert persons.select(
            (
                pl.col("detailed_professional_occupation").eq(occ)
                & pl.col("student_group").is_in(groups).not_()
            )
            .any()
            .not_()
        ).item(), (
            "Columns `student_group` and `detailed_professional_occupation` have inconsistencies"
        )
    student_constraints = (
        ("primaire", ("maternelle", "primaire")),
        ("collège", ("collège:6e", "collège:5e", "collège:4e", "collège:3e", "collège:SEGPA")),
        ("lycée", ("lycée:seconde", "lycée:première", "lycée:terminale", "lycée:CAP")),
        (
            "supérieur",
            (
                "supérieur:technique",
                "supérieur:prépa1",
                "supérieur:prépa2",
                "supérieur:BAC+1",
                "supérieur:BAC+2",
                "supérieur:BAC+3",
                "supérieur:BAC+4",
                "supérieur:BAC+5",
                "supérieur:BAC+6&+",
            ),
        ),
    )
    for group, cats in student_constraints:
        assert persons.select(
            (pl.col("student_group").eq(group) & pl.col("student_category").is_in(cats).not_())
            .any()
            .not_()
        ).item(), "Columns `student_group` and `student_category` have inconsistencies"
    valid_insee_codes(persons, "study_insee")
    assert persons["study_commute_euclidean_distance_km"].ge(0).all(), (
        "Column `study_commute_euclidean_distance_km` is negative for some values"
    )
    mask = pl.col("study_commute_euclidean_distance_km").is_not_null() & is_not_student
    if persons.select(mask.any()).item():
        if not (persons.filter(mask)["study_commute_euclidean_distance_km"] == 0.0).all():
            # When all distances are 0, we can silently set them to null.
            n = persons.select(mask.sum()).item()
            print(
                f"Warning. The `study_commute_euclidean_distance_km` variable is set for {n} "
                "non-student persons."
            )
            print("The value is automatically set to null.")
        persons = persons.with_columns(
            study_commute_euclidean_distance_km=pl.when(is_not_student)
            .then(pl.lit(None))
            .otherwise(pl.col("study_commute_euclidean_distance_km"))
        )
    assert persons.select(
        (pl.col("study_only_at_home") & (pl.col("study_commute_euclidean_distance_km") > 0.0))
        .any()
        .not_()
    ).item(), (
        "Column `study_commute_euclidean_distance_km` is positive for some persons studying only "
        "at home"
    )
    invalid_persons = persons.filter(
        pl.col("has_driving_license").eq("yes") & pl.col("age").is_between(15, 17)
    )["person_id"]
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(
            f"Warning. {n} persons indicated having a driving license but are between 15 and 17 "
            "year old"
        )
        print('Their `has_driving_license` value is automatically set to "in_progress"')
        persons = persons.with_columns(
            has_driving_license=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit("in_progress"))
            .otherwise("has_driving_license")
        )
    assert persons.select(
        (pl.col("has_driving_license").eq("yes") & pl.col("age").lt(17)).any().not_()
    ).item(), "Some persons have a driving license and are younger than 17"
    assert persons.select(
        (pl.col("has_driving_license").eq("in_progress") & pl.col("age").lt(15)).any().not_()
    ).item(), "Some persons are taking driving lessons and are younger than 15"
    assert persons.select(
        (pl.col("has_public_transit_subscription") & pl.col("public_transit_subscription").eq("no"))
        .any()
        .not_()
    ).item(), (
        "Columns `has_public_transit_subscription` and public_transit_subscription` have some inconsistencies"
    )
    all_defined(persons, "is_surveyed")
    assert trips_with_persons.select(pl.col("is_surveyed").all()).collect().item(), (
        "Column `is_surveyed` is false for some persons with reported trips"
    )
    all_null_for(
        persons,
        "traveled_during_surveyed_day",
        pl.col("is_surveyed").not_(),
        "persons not surveyed for trips",
    )
    all_defined_for(
        persons, "traveled_during_surveyed_day", pl.col("is_surveyed"), "persons surveyed for trips"
    )
    assert persons.select(
        (pl.col("traveled_during_surveyed_day").eq("yes") & pl.col("nb_trips").eq(0)).any().not_()
    ).item(), (
        'Some persons with `traveled_during_surveyed_day` equal to "yes" have no reported trip'
    )
    assert persons.select(
        (pl.col("traveled_during_surveyed_day").is_in(("no", "away")) & pl.col("nb_trips").ne(0))
        .any()
        .not_()
    ).item(), (
        'Some persons with `traveled_during_surveyed_day` equal to "no" or "away" have at least '
        "one reported trip"
    )
    invalid_persons = persons.filter(
        pl.col("worked_during_surveyed_day").eq("yes:home:usual")
        & pl.col("work_only_at_home").not_()
    )["person_id"]
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(
            f"Warning. {n} persons indicated that they worked at home as usual during the surveyed "
            "day but the value `work_only_at_home` is not true"
        )
        print('The `worked_during_surveyed_day` value is automatically set to "yes:home:telework"')
        persons = persons.with_columns(
            worked_during_surveyed_day=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit("yes:home:telework"))
            .otherwise(pl.col("worked_during_surveyed_day"))
        )
    assert (
        trips_with_persons.select(
            (
                pl.col("worked_during_surveyed_day").eq("no:weekday")
                & pl.col("destination_purpose_group").eq("work")
            )
            .any()
            .not_()
        )
        .collect()
        .item()
    ), (
        'Some persons have `worked_during_surveyed_day` equal to "no:weekday" but did at least one '
        "trip to work"
    )
    invalid_persons = (
        trips_with_persons.filter(pl.col("worked_during_surveyed_day") == "yes:outside")
        .group_by("person_id")
        .agg(
            is_valid=pl.col("origin_purpose_group")
            .eq("work")
            .any()
            .or_(pl.col("destination_purpose_group").eq("work").any())
        )
        .filter(pl.col("is_valid").not_())
        .select("person_id")
        .collect()
        .to_series()
    )
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(
            f"Warning. {n} persons reported having work outside during the surveyed day but did "
            "not actually report any trip to work"
        )
        print(
            'Their `worked_during_surveyed_day` value is automatically changed to "no:unspecified"'
        )
        persons = persons.with_columns(
            worked_during_surveyed_day=pl.when(pl.col("person_id").is_in(invalid_persons))
            .then(pl.lit("no:unspecified"))
            .otherwise(pl.col("worked_during_surveyed_day"))
        )
    all_null_for(persons, "nb_trips", pl.col("is_surveyed").not_(), "non-surveyed persons")
    all_defined_for(persons, "nb_trips", pl.col("is_surveyed"), "surveyed persons")
    trip_counts = trips.group_by("person_id").agg(count=pl.len())
    assert (
        persons.lazy()
        .join(trip_counts.lazy(), on="person_id", how="full")
        .filter(pl.col("nb_trips") != pl.col("count"))
        .collect()
        .is_empty()
    ), "column `nb_trips` does not match the actual number of trips for some persons"
    assert persons["sample_weight_all"].ge(0).all(), (
        "Column `sample_weight_all` is negative for some values"
    )
    assert persons["sample_weight_surveyed"].ge(0).all(), (
        "Column `sample_weight_surveyed` is negative for some values"
    )
    all_null_for(
        persons,
        "sample_weight_surveyed",
        pl.col("is_surveyed").not_(),
        "non-surveyed persons",
        force=True,
    )

    # === Trips ===
    all_defined(trips, "trip_id")
    assert trips["trip_id"].min() == 1, "Column `trip_id` does not start at 1"
    assert trips["trip_id"].max() == len(trips), (
        "Column `trip_id` does not end at the number of trips"
    )
    is_sorted(trips, "trip_id")
    all_defined(trips, "person_id")
    assert trips["person_id"].is_in(persons["person_id"]).all(), (
        "Column `person_id` does not match a valid person id"
    )
    is_sorted(trips, "person_id")
    all_defined(trips, "household_id")
    assert (
        trips.lazy()
        .join(
            persons.select("person_id", "household_id").lazy(),
            on=["person_id", "household_id"],
            how="anti",
        )
        .collect()
        .is_empty()
    ), "Incompatible combination for `person_id` and `household_id` in trips"
    all_defined(trips, "trip_index")
    # The test below ensures that `trip_index` values are sorted within a person.
    assert trips.select(
        (pl.col("trip_index") == pl.int_range(1, pl.len() + 1).over("person_id")).all()
    ).item(), "Column `trip_index` does not range from 1 to the number of trips within a person"
    all_defined(trips, "first_trip")
    all_defined(trips, "last_trip")
    assert trips.select(
        (pl.col("trip_index").eq(1) & pl.col("first_trip").not_()).any().not_()
    ).item(), "`trip_index` is 1 but `first_trip` is false"
    assert trips.select((pl.col("trip_index").ne(1) & pl.col("first_trip")).any().not_()).item(), (
        "`first_trip` is true but `trip_index` is not 1"
    )
    assert (
        trips_with_persons.select(
            (pl.col("origin_purpose").eq("work:declared") & is_not_worker).any().not_()
        )
        .collect()
        .item()
    ), '`origin_purpose` is "work:declared" for a non-worker person'
    education_purposes = (
        "education:primary",
        "education:middle_school",
        "education:high_school",
        "education:higher",
    )
    assert (
        trips_with_persons.select(
            (pl.col("origin_purpose").is_in(education_purposes) & is_not_student).any().not_()
        )
        .collect()
        .item()
    ), "`origin_purpose` is education-related for a non-student person"
    assert trips.select(
        (
            pl.col("origin_purpose").cast(pl.String).str.extract(r"(\w+):?")
            == pl.col("origin_purpose_group")
        ).all()
    ).item(), "Columns `origin_purpose` and `origin_purpose_group` have some inconsistencies"
    all_defined_for(
        trips,
        "origin_purpose_group",
        pl.col("origin_purpose").is_not_null(),
        "trips with non-null `origin_purpose`",
    )
    assert (
        trips_with_persons.select(
            (pl.col("destination_purpose").eq("work:declared") & is_not_worker).any().not_()
        )
        .collect()
        .item()
    ), '`destination_purpose` is "work:declared" for a non-worker person'
    assert (
        trips_with_persons.select(
            (pl.col("destination_purpose").is_in(education_purposes) & is_not_student).any().not_()
        )
        .collect()
        .item()
    ), "`destination_purpose` is education-related for a non-student person"
    assert trips.select(
        (
            pl.col("destination_purpose").cast(pl.String).str.extract(r"(\w+):?")
            == pl.col("destination_purpose_group")
        ).all()
    ).item(), (
        "Columns `destination_purpose` and `destination_purpose_group` have some inconsistencies"
    )
    all_defined_for(
        trips,
        "destination_purpose_group",
        pl.col("destination_purpose").is_not_null(),
        "trips with non-null `destination_purpose`",
    )
    if CHECK_ORIGIN_MATCHES_PREV_DEST != "no":
        same_as_next_in_group(
            trips,
            "destination_purpose",
            "origin_purpose",
            "person_id",
            CHECK_ORIGIN_MATCHES_PREV_DEST == "warn",
        )
        same_as_next_in_group(
            trips,
            "destination_purpose_group",
            "origin_purpose_group",
            "person_id",
            CHECK_ORIGIN_MATCHES_PREV_DEST == "warn",
        )
    all_null_for(
        trips,
        "origin_escort_purpose",
        pl.col("origin_purpose_group").ne_missing("escort"),
        "non-escort trips",
    )
    assert trips.select(
        (
            pl.col("origin_escort_purpose").cast(pl.String).str.extract(r"(\w+):?")
            == pl.col("origin_escort_purpose_group")
        ).all()
    ).item(), (
        "Columns `origin_escort_purpose` and `origin_escort_purpose_group` have some inconsistencies"
    )
    all_defined_for(
        trips,
        "origin_escort_purpose_group",
        pl.col("origin_escort_purpose").is_not_null(),
        "trips with non-null `origin_escort_purpose`",
    )
    assert (trips["origin_escort_purpose_group"] != "escort").all(), (
        'Some trips have "escort" as `origin_escort_purpose_group`'
    )
    all_null_for(
        trips,
        "destination_escort_purpose",
        pl.col("destination_purpose_group").ne_missing("escort"),
        "non-escort trips",
    )
    assert trips.select(
        (
            pl.col("destination_escort_purpose").cast(pl.String).str.extract(r"(\w+):?")
            == pl.col("destination_escort_purpose_group")
        ).all()
    ).item(), (
        "Columns `destination_escort_purpose` and `destination_escort_purpose_group` have some inconsistencies"
    )
    all_defined_for(
        trips,
        "destination_escort_purpose_group",
        pl.col("destination_escort_purpose").is_not_null(),
        "trips with non-null `destination_escort_purpose`",
    )
    assert (trips["destination_escort_purpose_group"] != "escort").all(), (
        'Some trips have "escort" as `destination_escort_purpose_group`'
    )
    if CHECK_ORIGIN_MATCHES_PREV_DEST != "no":
        same_as_next_in_group(
            trips,
            "destination_escort_purpose",
            "origin_escort_purpose",
            "person_id",
            CHECK_ORIGIN_MATCHES_PREV_DEST == "warn",
        )
        same_as_next_in_group(
            trips,
            "destination_escort_purpose_group",
            "origin_escort_purpose_group",
            "person_id",
            CHECK_ORIGIN_MATCHES_PREV_DEST == "warn",
        )
    valid_insee_codes(trips, "origin_insee")
    valid_insee_codes(trips, "destination_insee")
    if CHECK_ORIGIN_MATCHES_PREV_DEST != "no":
        for zone in ("special_location", "detailed_zone", "draw_zone", "insee"):
            same_as_next_in_group(
                trips,
                f"destination_{zone}",
                f"origin_{zone}",
                "person_id",
                CHECK_ORIGIN_MATCHES_PREV_DEST == "warn",
            )
    assert trips.select(pl.col("departure_time").diff().over("person_id").min()).item() > 0, (
        "Column `departure_time` is not increasing over persons"
    )
    invalid_persons = trips.filter(pl.col("arrival_time") < pl.col("departure_time"))[
        "person_id"
    ].unique()
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(
            f"Warning. {n} persons have at least one trip with `arrival_time` smaller than "
            "`departure_time`"
        )
        print(
            "The `departure_time`, `arrival_time`, and `travel_time` values for these persons are "
            "automatically set to null."
        )
        trips = trips.with_columns(
            pl.when(pl.col("person_id").is_in(invalid_person_ids))
            .then(pl.lit(None))
            .otherwise(col)
            .alias(col)
            for col in ("departure_time", "arrival_time", "travel_time")
        )
    invalid_persons = trips.filter(
        pl.col("arrival_time") > pl.col("departure_time").shift(-1).over("person_id")
    )["person_id"].unique()
    if not invalid_persons.is_empty():
        n = len(invalid_persons)
        print(
            f"Warning. {n} persons have at least one trip that starts before the previous trip "
            "ended"
        )
        print(
            "The `departure_time`, `arrival_time`, and `travel_time` values for these persons are "
            "automatically set to null."
        )
        trips = trips.with_columns(
            pl.when(pl.col("person_id").is_in(invalid_person_ids))
            .then(pl.lit(None))
            .otherwise(col)
            .alias(col)
            for col in ("departure_time", "arrival_time", "travel_time")
        )
    assert trips["travel_time"].eq_missing(trips["arrival_time"] - trips["departure_time"]).all(), (
        "`travel_time` is not equal to `arrival_time - departure_time`"
    )
    assert (
        legs_with_trips.select(
            ((pl.col("main_mode") == pl.col("mode")).any() | pl.col("main_mode").is_null().all())
            .over("trip_id")
            .all()
        )
        .collect()
        .item()
    ), "Some trips have no leg whose `mode` matches the trip's `main_mode`"
    assert trips.select(
        (pl.col("main_mode").replace_strict(MODE_TO_GROUP) == pl.col("main_mode_group")).all()
    ).item(), "Columns `main_mode` and `main_mode_group` have some inconsistencies"
    all_defined_for(
        trips,
        "main_mode_group",
        pl.col("main_mode").is_not_null(),
        "trips with non-null `main_mode`",
    )
    assert trips["trip_euclidean_distance_km"].ge(0).all(), (
        "Column `trip_euclidean_distance_km` is negative for some values"
    )
    assert trips["trip_travel_distance_km"].ge(0).all(), (
        "Column `trip_travel_distance_km` is negative for some values"
    )
    assert (trips["trip_travel_distance_km"] >= trips["trip_euclidean_distance_km"]).all(), (
        "`trip_travel_distance_km` is smaller than `trip_euclidean_distance_km` for some values"
    )
    if detailed_zones is not None:
        zone_ids = set(detailed_zones["detailed_zone_id"])
        perimeter_check(trips, zone_ids, "detailed")
    if draw_zones is not None:
        zone_ids = set(draw_zones["draw_zone_id"])
        perimeter_check(trips, zone_ids, "draw")
    if insee_zones is not None:
        zone_ids = set(insee_zones["insee_id"])
        perimeter_check(trips, zone_ids, "insee")
    tour_purposes = ("work:professional_tour", "shopping:tour_no_purchase")
    all_null_for(
        trips,
        "nb_tour_stops",
        (
            pl.col("origin_purpose").is_in(tour_purposes)
            | pl.col("destination_purpose").is_in(tour_purposes)
        ).not_(),
        "non-tour purposes",
    )
    # The test below ensures that (i) `nb_legs` is not null, (ii) `nb_legs` is positive,
    # (iii) `nb_legs` matches the number of legs for this trip.
    leg_counts = legs.group_by("trip_id").agg(nb_legs=pl.len())
    assert trips.join(leg_counts, on=["trip_id", "nb_legs"], how="anti").is_empty(), (
        "Column `nb_legs` does not match the actual number of legs for some trips"
    )

    # === Legs ===
    all_defined(legs, "leg_id")
    assert legs["leg_id"].min() == 1, "Column `leg_id` does not start at 1"
    assert legs["leg_id"].max() == len(legs), "Column `leg_id` does not end at the number of legs"
    is_sorted(legs, "leg_id")
    all_defined(legs, "trip_id")
    assert legs["trip_id"].is_in(trips["trip_id"]).all(), (
        "Column `trip_id` does not match a valid trip id"
    )
    is_sorted(legs, "trip_id")
    all_defined(legs, "person_id")
    assert (
        legs.lazy()
        .join(
            trips.lazy().select("trip_id", "person_id"),
            on=["trip_id", "person_id"],
            how="anti",
        )
        .collect()
        .is_empty()
    ), "Incompatible combination for `trip_id` and `person_id` in legs"
    all_defined(legs, "household_id")
    assert (
        legs.lazy()
        .join(
            persons.lazy().select("person_id", "household_id"),
            on=["person_id", "household_id"],
            how="anti",
        )
        .collect()
        .is_empty()
    ), "Incompatible combination for `person_id` and `household_id` in legs"
    all_defined(legs, "leg_index")
    # The test below ensures that `leg_index` values are sorted within a trip.
    assert legs.select(
        (pl.col("leg_index") == pl.int_range(1, pl.len() + 1).over("trip_id")).all()
    ).item(), "Column `leg_index` does not range from 1 to the number of legs within a trip"
    all_defined(legs, "first_leg")
    all_defined(legs, "last_leg")
    assert legs.select(
        (pl.col("leg_index").eq(1) & pl.col("first_leg").not_()).any().not_()
    ).item(), "`leg_index` is 1 but `first_leg` is false"
    assert legs.select((pl.col("leg_index").ne(1) & pl.col("first_leg")).any().not_()).item(), (
        "`first_leg` is true but `leg_index` is not 1"
    )
    assert legs.select(
        (pl.col("mode").replace_strict(MODE_TO_GROUP) == pl.col("mode_group")).all()
    ).item(), "Columns `mode` and `mode_group` have some inconsistencies"
    valid_insee_codes(legs, "start_insee")
    valid_insee_codes(legs, "end_insee")
    if CHECK_START_MATCHED_PREV_END != "no":
        for zone in ("special_location", "detailed_zone", "draw_zone", "insee"):
            same_as_next_in_group(
                legs,
                f"end_{zone}",
                f"start_{zone}",
                "trip_id",
                CHECK_START_MATCHED_PREV_END == "warn",
            )
    # When we observe this:
    # start1: a ; end1: a
    # start2: b ; end2: c
    # we switch `end1` to `start2` to satisfy the constraint
    legs_to_fix = (
        legs.filter(
            pl.col("end_detailed_zone").ne_missing(
                pl.col("start_detailed_zone").shift(-1).over("trip_id")
            )
            & (pl.int_range(1, pl.len() + 1) != pl.len()).over("trip_id")
            & pl.col("start_detailed_zone").eq_missing(pl.col("end_detailed_zone"))
        )
        .select("leg_id")
        .to_series()
    )
    if not legs_to_fix.is_empty():
        n = len(legs_to_fix)
        print(
            f"Warning. {n} legs have `end_detailed_zone` that does not match "
            "`start_detailed_zone` of the next leg but it matches `start_detailed_zone` of the "
            "current leg"
        )
        print(
            "Their `end_detailed_zone` value is automatically changed to `start_detailed_zone` "
            "of the current leg"
        )
        legs = legs.with_columns(
            end_detailed_zone=pl.when(pl.col("leg_id").is_in(legs_to_fix))
            .then(pl.col("start_detailed_zone").shift(-1).over("trip_id"))
            .otherwise(pl.col("end_detailed_zone"))
        )
    n = (
        legs_with_trips.group_by("trip_id")
        .agg(
            leg_tt=pl.col("leg_travel_time").fill_null(0).sum(),
            trip_tt=pl.col("travel_time").first(),
        )
        .filter(pl.col("leg_tt") > pl.col("trip_tt"))
        .select(pl.len())
        .collect()
        .item()
    )
    if n > 0:
        print(
            f"Warning. The sum of the legs' `leg_travel_time is larger than the trip's "
            f"`travel_time` for {n} trips."
        )
    assert legs["leg_euclidean_distance_km"].ge(0).all(), (
        "Column `leg_euclidean_distance_km` is negative for some values"
    )
    assert legs["leg_travel_distance_km"].ge(0).all(), (
        "Column `leg_travel_distance_km` is negative for some values"
    )
    assert (legs["leg_travel_distance_km"] >= legs["leg_euclidean_distance_km"]).all(), (
        "`leg_travel_distance_km` is smaller than `leg_euclidean_distance_km` for some values"
    )
    is_non_car_leg = pl.col("mode").is_in(("car:driver", "car:passenger")).not_()
    all_null_for(
        legs,
        "car_type",
        is_non_car_leg,
        "non-car legs",
    )
    all_null_for(
        legs, "car_id", pl.col("car_type").ne("household"), "legs with a non-household car"
    )
    invalid_legs = legs.filter(pl.col("car_type").eq("household") & pl.col("car_id").is_null())[
        "leg_id"
    ]
    if not invalid_legs.is_empty():
        n = len(invalid_legs)
        print(f'For {n} legs `car_type` is "household" but `car_id` is null')
        print('The value of `car_type` is automatically changed to "other_household"')
        legs = legs.with_columns(
            car_type=pl.when(pl.col("leg_id").is_in(invalid_legs))
            .then(pl.lit("other_household"))
            .otherwise(pl.col("car_type"))
        )
    all_defined_for(legs, "car_id", pl.col("car_type").eq("household"), "legs with a household car")
    extra_cars_households = (
        households.lazy()
        .join(car_counts.lazy(), on="household_id")
        .filter(pl.col("nb_cars") > pl.col("count"))
        .select("household_id")
        .collect()
        .to_series()
    )
    invalid_legs = legs.filter(
        pl.col("car_type").eq("other_household")
        & pl.col("household_id").is_in(extra_cars_households).not_()
    )["leg_id"]
    if not invalid_legs.is_empty():
        n = len(invalid_legs)
        print(
            f'Warning. {n} legs have `car_type` equal to "other_household" but there is no extra '
            "car in the household"
        )
        print('The `car_type` value is automatically changed to "other"')
        legs = legs.with_columns(
            car_type=pl.when(pl.col("leg_id").is_in(invalid_legs))
            .then(pl.lit("other"))
            .otherwise(pl.col("car_type"))
        )
    # The test below ensure that `car_id` is a valid id and that it matches a car from the
    # household.
    assert (
        legs.lazy()
        .filter(pl.col("car_id").is_not_null())
        .select("car_id", leg_household_id="household_id")
        .join(cars.lazy(), on="car_id", how="left")
        .select("leg_household_id", car_household_id="household_id")
        .select(pl.col("car_household_id").eq_missing(pl.col("leg_household_id")).all())
        .collect()
        .item()
    ), "`car_id` does not match a valid car from the household"
    all_null_for(legs, "nolicense_car", pl.col("mode").ne("car:driver"), "non car-driver legs")
    is_vehicle_mode = pl.col("mode_group").is_in(
        ("car_driver", "motorcycle", "bicycle", "car_passenger")
    ) | pl.col("mode").is_in(
        (
            "truck:driver",
            "truck:passenger",
            "personal_transporter:non_motorized",
            "personal_transporter:motorized",
            "personal_transporter:unspecified",
        )
    )
    for col in (
        "nb_persons_in_vehicle",
        "nb_majors_in_vehicle",
        "nb_minors_in_vehicle",
        "parking_location",
        "parking_search_time",
    ):
        all_null_for(legs, col, is_vehicle_mode.not_(), "non-vehicle mode")
    assert legs["nb_persons_in_vehicle"].ge(1).all(), (
        "Column `nb_persons_in_vehicle` is non-positive for some values"
    )
    assert legs.select(
        (
            (
                pl.col("mode_group").eq("car_passenger")
                | pl.col("mode").is_in(
                    (
                        "motorcycle:passenger",
                        "motorcycle:passenger:moped",
                        "motorcycle:passenger:moto",
                        "bicycle:passenger",
                        "truck:passenger",
                    )
                )
            )
            & pl.col("nb_persons_in_vehicle").eq(1)
        )
        .any()
        .not_()
    ).item(), "`nb_persons_in_vehicle` is 1 for passenger legs"
    assert (legs["nb_persons_in_vehicle"] >= legs["nb_majors_in_vehicle"]).all(), (
        "`nb_majors_in_vehicle` is larger than `nb_persons_in_vehicle` for some legs"
    )
    assert (legs["nb_persons_in_vehicle"] >= legs["nb_minors_in_vehicle"]).all(), (
        "`nb_minors_in_vehicle` is larger than `nb_persons_in_vehicle` for some legs"
    )
    is_major = pl.col("age").ge(18)
    assert (
        legs_with_persons.select((pl.col("nb_majors_in_vehicle").eq(0) & is_major).any().not_())
        .collect()
        .item()
    ), "`nb_majors_in_vehicle` is 0 but the person is major"
    assert (
        legs_with_persons.select(
            (pl.col("nb_minors_in_vehicle").eq(0) & is_major.not_()).any().not_()
        )
        .collect()
        .item()
    ), "`nb_minors_in_vehicle` is 0 but the person is minor"
    all_defined_for(
        legs,
        "nb_persons_in_vehicle",
        pl.col("nb_majors_in_vehicle").is_not_null() & pl.col("nb_minors_in_vehicle").is_not_null(),
        "non-null `nb_majors_in_vehicle` and `nb_minors_in_vehicle`",
    )
    assert (
        legs["nb_majors_in_vehicle"] + legs["nb_minors_in_vehicle"] == legs["nb_persons_in_vehicle"]
    ).all(), "`nb_persons_in_vehicle` is not equal to `nb_majors_in_vehicle + nb_minors_in_vehicle`"
    is_non_motorcycle_leg = pl.col("mode_group").ne("motorcycle")
    all_null_for(
        legs,
        "motorcycle_type",
        is_non_motorcycle_leg,
        "non-motorcycle legs",
    )
    all_null_for(
        legs,
        "motorcycle_id",
        pl.col("motorcycle_type").ne("household"),
        "legs with a non-household motorcycle",
    )
    all_defined_for(
        legs,
        "motorcycle_id",
        pl.col("motorcycle_type").eq("household"),
        "legs with a household motorcycle",
    )
    extra_motorcycles_households = (
        households.lazy()
        .join(motorcycle_counts.lazy(), on="household_id")
        .filter(pl.col("nb_motorcycles") > pl.col("count"))
        .select("household_id")
        .collect()
        .to_series()
    )
    invalid_legs = legs.filter(
        pl.col("motorcycle_type").eq("other_household")
        & pl.col("household_id").is_in(extra_motorcycles_households).not_()
    )["leg_id"]
    if not invalid_legs.is_empty():
        n = len(invalid_legs)
        print(
            'Warning. {n} legs have `motorcycle_type` equal to "other_household" but there is no '
            "extra motorcycle in the household"
        )
        print('The `motorcycle_type` value is automatically changed to "other"')
        legs = legs.with_columns(
            motorcycle_type=pl.when(pl.col("leg_id").is_in(invalid_legs))
            .then(pl.lit("other"))
            .otherwise(pl.col("motorcycle_type"))
        )
    # The test below ensure that `motorcycle_id` is a valid id and that it matches a motorcycle from
    # the household.
    assert (
        legs.lazy()
        .filter(pl.col("motorcycle_id").is_not_null())
        .select("motorcycle_id", leg_household_id="household_id")
        .join(motorcycles.lazy(), on="motorcycle_id", how="left")
        .select("leg_household_id", motorcycle_household_id="household_id")
        .select(pl.col("motorcycle_household_id").eq_missing(pl.col("leg_household_id")).all())
        .collect()
        .item()
    ), "`motorcycle_id` does not match a valid motorcycle from the household"
    all_null_for(
        legs,
        "parking_type",
        pl.col("parking_location").is_null()
        | pl.col("parking_location").is_in(("stop_only", "none")),
        "legs without valid parking location",
        force=True,
    )

    # === Cars ===
    all_defined(cars, "car_id")
    assert cars["car_id"].min() == 1, "Column `car_id` does not start at 1"
    assert cars["car_id"].max() == len(cars), "Column `car_id` does not end at the number of cars"
    is_sorted(cars, "car_id")
    all_defined(cars, "household_id")
    assert cars["household_id"].is_in(households["household_id"]).all(), (
        "Column `household_id` does not match a valid household id"
    )
    is_sorted(cars, "household_id")
    all_defined(cars, "car_index")
    # The test below ensures that `car_index` values are sorted within a household.
    assert cars.select(
        (pl.col("car_index") == pl.int_range(1, pl.len() + 1).over("household_id")).all()
    ).item(), "Column `car_index` does not range from 1 to the number of cars within a household"
    assert cars["year"].min() >= 1900, "Some cars are older than 1900"
    assert cars["year"].max() <= persons["interview_date"].max().year, (
        "Some cars have a initial year in the future"
    )
    all_null_for(
        cars,
        "parking_type",
        pl.col("parking_location").is_null(),
        "cars with null parking location",
    )

    # === Motorcycles ===
    all_defined(motorcycles, "motorcycle_id")
    assert motorcycles["motorcycle_id"].min() == 1, "Column `motorcycle_id` does not start at 1"
    assert motorcycles["motorcycle_id"].max() == len(motorcycles), (
        "Column `motorcycle_id` does not end at the number of motorcycles"
    )
    is_sorted(motorcycles, "motorcycle_id")
    all_defined(motorcycles, "household_id")
    assert motorcycles["household_id"].is_in(households["household_id"]).all(), (
        "Column `household_id` does not match a valid household id"
    )
    is_sorted(motorcycles, "household_id")
    all_defined(motorcycles, "motorcycle_index")
    # The test below ensures that `motorcycle_index` values are sorted within a household.
    assert motorcycles.select(
        (pl.col("motorcycle_index") == pl.int_range(1, pl.len() + 1).over("household_id")).all()
    ).item(), (
        "Column `motorcycle_index` does not range from 1 to the number of motorcycles within a household"
    )
    all_null_for(
        motorcycles,
        "parking_type",
        pl.col("parking_location").is_null(),
        "motorcycles with null parking location",
    )
    for col in ("thermic_engine_type", "cm3_lower_bound", "cm3_upper_bound"):
        all_null_for(
            motorcycles,
            col,
            pl.col("fuel_type").ne("thermic"),
            "non-thermic motorcycles",
            force=True,
        )
    assert (motorcycles["cm3_upper_bound"] >= motorcycles["cm3_lower_bound"]).all(), (
        "Some motorocycles have `cm3_upper_bound` smaller than `cm3_lower_bound`"
    )
    for col in ("kw_lower_bound", "kw_upper_bound"):
        all_null_for(
            motorcycles,
            col,
            pl.col("fuel_type").ne("electric"),
            "non-electric motorcycles",
        )
    assert (motorcycles["kw_upper_bound"] >= motorcycles["kw_lower_bound"]).all(), (
        "Some motorocycles have `kw_upper_bound` smaller than `kw_lower_bound`"
    )

    # === Zone intersects ===
    zones = (
        (special_locations, "special_location"),
        (detailed_zones, "detailed_zone"),
        (draw_zones, "draw_zone"),
        (insee_zones, "insee"),
    )
    for (gdf1, z1), (gdf2, z2) in itertools.combinations(zones, 2):
        if gdf1 is None or gdf2 is None:
            continue
        intersects = pl.from_pandas(
            gpd.sjoin(
                gdf1.loc[:, ["geometry", f"{z1}_id"]],
                gdf2.loc[:, ["geometry", f"{z2}_id"]].to_crs(gdf1.crs),
                predicate="intersects",
            ).loc[:, [f"{z1}_id", f"{z2}_id"]]
        )
        households = intersect_check(households, intersects, "home", z1, z2, "household_id")
        persons = intersect_check(persons, intersects, "work", z1, z2, "person_id")
        persons = intersect_check(persons, intersects, "study", z1, z2, "person_id")
        trips = intersect_check(trips, intersects, "origin", z1, z2, "trip_id")
        trips = intersect_check(trips, intersects, "destination", z1, z2, "trip_id")
        legs = intersect_check(legs, intersects, "start", z1, z2, "leg_id")
        legs = intersect_check(legs, intersects, "end", z1, z2, "leg_id")

    return dict(
        households=households,
        cars=cars,
        motorcycles=motorcycles,
        persons=persons,
        trips=trips,
        legs=legs,
        special_locations=special_locations,
        detailed_zones=detailed_zones,
        draw_zones=draw_zones,
        insee_zones=insee_zones,
    )

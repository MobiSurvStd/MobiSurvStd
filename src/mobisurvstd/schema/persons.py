import polars as pl

from .common import Variable
from .guarantees import (
    Defined,
    DefinedIfAndOnlyIf,
    EqualTo,
    EqualToMapping,
    ExactlyOneOf,
    Indexed,
    InseeConsistentWithDep,
    NonDecreasing,
    NonNegative,
    Null,
    SmallerThan,
    UpperBounded,
    ValidDepCode,
    ValidInsee,
    ValueInSet,
    ValueIs,
    ValueIsNot,
)

COMMUTE_CAR_ENUM = pl.Enum(
    [
        "yes:full_commute",
        "yes:partial_commute",
        "yes:not_used",
        "yes:partial_or_not_used",
        "yes:full_or_partial",
        "no",
    ]
)

CAR_PARKING_ENUM = pl.Enum(
    [
        "yes:reserved",
        "yes:many_spots",
        "yes:compatible_schedule",
        "yes:unspecified",
        "no",
        "dont_know",
    ]
)

BICYCLE_PARKING_ENUM = pl.Enum(
    [
        "yes:on_site:sheltered",
        "yes:on_site:unsheltered",
        "yes:on_site",
        "yes:nearby:sheltered",
        "yes:nearby:unsheltered",
        "yes:nearby",
        "no",
    ]
)

FREQUENCY_ENUM = pl.Enum(["each_week", "each_month", "occasionally", "never"])

IS_NOT_WORKER_EXPR = (
    pl.col("professional_occupation").ne("worker")
    & pl.col("secondary_professional_occupation").ne_missing("work")
    & pl.col("detailed_professional_occupation").ne("student:apprenticeship")
)

AGE_CLASS_TO_CODE = {
    "17-": 1,
    "18-24": 2,
    "25-34": 3,
    "35-49": 4,
    "50-64": 5,
    "65-74": 6,
    "75+": 7,
}


PCS_CODES = {
    1: "agriculteurs_exploitants",
    2: "artisans_commerçants_chefs_d'entreprise",
    3: "cadres_et_professions_intellectuelles_supérieures",
    4: "professions_intermédiaires",
    5: "employés",
    6: "ouvriers",
    7: "retraités",
    8: "autres_personnes_sans_activité_professionnelle",
}

STUDENT_GROUP_MAP = {
    "maternelle": "primaire",
    "primaire": "primaire",
    "collège:6e": "collège",
    "collège:5e": "collège",
    "collège:4e": "collège",
    "collège:3e": "collège",
    "collège:SEGPA": "collège",
    "lycée:seconde": "lycée",
    "lycée:première": "lycée",
    "lycée:terminale": "lycée",
    "lycée:CAP": "lycée",
    "supérieur:technique": "supérieur",
    "supérieur:prépa1": "supérieur",
    "supérieur:prépa2": "supérieur",
    "supérieur:BAC+1": "supérieur",
    "supérieur:BAC+2": "supérieur",
    "supérieur:BAC+3": "supérieur",
    "supérieur:BAC+4": "supérieur",
    "supérieur:BAC+5": "supérieur",
    "supérieur:BAC+6&+": "supérieur",
}

PERSON_SCHEMA = [
    # Identifier of the person.
    Variable("person_id", pl.UInt32, [Indexed()]),
    # Identifier of the household the person belongs to.
    Variable("household_id", pl.UInt32, [Defined(), NonDecreasing()]),
    # Index of the person within the household's persons.
    Variable("person_index", pl.UInt8, [Defined(), Indexed(over=pl.col("household_id"))]),
    # Identifier of the person in the original survey data.
    Variable("original_person_id", pl.Struct),
    # Link of the person relative to the reference person of the household.
    Variable(
        "reference_person_link",
        pl.Enum(
            [
                "reference_person",
                "spouse",
                "child",
                "roommate_or_tenant",
                "other:relative",
                "other:non_relative",
            ]
        ),
        [
            ExactlyOneOf(
                "reference_person",
                over=pl.col("household_id"),
                when=pl.col("reference_person_link").is_not_null().all().over("household_id"),
                when_alias='"reference_person_link" is not null for all household\'s persons',
            )
        ],
    ),
    # Whether the person is living in the household home for most of the year.
    Variable(
        "resident_type", pl.Enum(["permanent_resident", "mostly_weekends", "mostly_weekdays"])
    ),
    # Whether the person is a woman.
    Variable("woman", pl.Boolean),
    # Age of the person.
    Variable(
        "age",
        pl.UInt8,
        [
            UpperBounded(125),
            SmallerThan(
                pl.col("age")
                .filter(pl.col("reference_person_link").eq("reference_person"))
                .first()
                .over("household_id"),
                alias="age of the reference person",
                when=pl.col("reference_person_link") == "child",
            ),
        ],
    ),
    # Age class of the person, in 7 classes.
    Variable(
        "age_class",
        pl.Enum(list(AGE_CLASS_TO_CODE.keys())),
        [
            Defined(when=pl.col("age").is_not_null()),
            ValueIs("17-", when=pl.col("age") < 18),
            ValueIs("18-24", when=pl.col("age").is_between(18, 24)),
            ValueIs("25-34", when=pl.col("age").is_between(25, 34)),
            ValueIs("35-49", when=pl.col("age").is_between(35, 49)),
            ValueIs("50-64", when=pl.col("age").is_between(50, 64)),
            ValueIs("65-74", when=pl.col("age").is_between(65, 74)),
            ValueIs("75+", when=pl.col("age") >= 75),
        ],
    ),
    # Code of the age class.
    Variable(
        "age_class_code",
        pl.UInt8,
        [
            Defined(when=pl.col("age").is_not_null()),
            DefinedIfAndOnlyIf(pl.col("age_class").is_not_null()),
            EqualToMapping(pl.col("age_class"), "`age_class`", AGE_CLASS_TO_CODE),
        ],
    ),
    # Education level reached by the person, in detailed categories.
    Variable(
        "detailed_education_level",
        pl.Enum(
            [
                "no_studies",
                "no_diploma",
                "primary:unspecified",
                "primary:CEP",
                "secondary:no_bac:college",
                "secondary:no_bac:CAP/BEP",
                "secondary:bac:techno_or_pro",
                "secondary:bac:general",
                "secondary:bac:unspecified",
                "higher:at_most_bac+2:paramedical_social",
                "higher:at_most_bac+2:BTS/DUT",
                "higher:at_most_bac+2:DEUG",
                "higher:at_most_bac+2:unspecified",
                "higher:at_least_bac+3:ecole",
                "higher:at_least_bac+3:universite",
                "higher:at_least_bac+3:unspecified",
                "higher:bac+3_or_+4",
                "higher:at_least_bac+5",
            ]
        ),
        [Null(when=pl.col("professional_occupation") == "student")],
    ),
    # Education level reached by the person.
    Variable(
        "education_level",
        pl.Enum(
            [
                "no_studies_or_no_diploma",
                "primary",
                "secondary:no_bac",
                "secondary:bac",
                "higher:at_most_bac+2",
                "higher:at_least_bac+3",
            ]
        ),
        [
            Null(when=pl.col("professional_occupation") == "student"),
            Defined(when=pl.col("detailed_education_level").is_not_null()),
            ValueIs(
                "no_studies_or_no_diploma",
                when=pl.col("detailed_education_level").is_in(("no_studies", "no_diploma")),
            ),
            ValueIs(
                "primary",
                when=pl.col("detailed_education_level").is_in(
                    ("primary:unspecified", "primary:CEP")
                ),
            ),
            ValueIs(
                "secondary:no_bac",
                when=pl.col("detailed_education_level").is_in(
                    ("secondary:no_bac:college", "secondary:no_bac:CAP/BEP")
                ),
            ),
            ValueIs(
                "secondary:bac",
                when=pl.col("detailed_education_level").is_in(
                    (
                        "secondary:bac:techno_or_pro",
                        "secondary:bac:general",
                        "secondary:bac:unspecified",
                    )
                ),
            ),
            ValueIs(
                "higher:at_most_bac+2",
                when=pl.col("detailed_education_level").is_in(
                    (
                        "higher:at_most_bac+2:DEUG",
                        "higher:at_most_bac+2:BTS/DUT",
                        "higher:at_most_bac+2:paramedical_social",
                        "higher:at_most_bac+2:unspecified",
                    )
                ),
            ),
            ValueIs(
                "higher:at_least_bac+3",
                when=pl.col("detailed_education_level").is_in(
                    (
                        "higher:at_least_bac+3:universite",
                        "higher:at_least_bac+3:ecole",
                        "higher:at_least_bac+3:unspecified",
                        "higher:bac+3_or_+4",
                        "higher:at_least_bac+5",
                    )
                ),
            ),
        ],
    ),
    # Detailed professional status of the person.
    Variable(
        "detailed_professional_occupation",
        pl.Enum(
            [
                "worker:full_time",
                "worker:part_time",
                "worker:unspecified",
                "student:apprenticeship",
                "student:higher",
                "student:primary_or_secondary",
                "student:unspecified",
                "other:unemployed",
                "other:retired",
                "other:homemaker",
                "other:unspecified",
            ]
        ),
    ),
    # Professional status of the person.
    Variable(
        "professional_occupation",
        pl.Enum(["worker", "student", "other"]),
        [
            Defined(when=pl.col("detailed_professional_occupation").is_not_null()),
            EqualTo(
                pl.col("detailed_professional_occupation").cast(pl.String).str.extract(r"(\w+):"),
                alias="`detailed_professional_occupation`",
            ),
        ],
    ),
    # Secondary professional occupation of the person.
    Variable(
        "secondary_professional_occupation",
        pl.Enum(["work", "education"]),
        [
            ValueIsNot("work", when=pl.col("professional_occupation") == "worker"),
            ValueIsNot(
                "education",
                when=pl.col("professional_occupation").eq("student")
                & pl.col("detailed_professional_occupation").ne_missing("student:apprenticeship"),
            ),
        ],
    ),
    # Code of the category of "Professions et Catégories Socioprofessionnelles" the person belongs
    # to (2020 version).
    Variable(
        "pcs_category_code2020",
        pl.UInt8,
        [
            Null(
                when=pl.col("professional_occupation").eq("student")
                & pl.col("detailed_professional_occupation").ne("student:apprenticeship")
                & pl.col("secondary_professional_occupation").ne("work")
            ),
            ValueInSet(
                {
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
                    48,
                    52,
                    53,
                    54,
                    55,
                    56,
                    62,
                    64,
                    65,
                    67,
                    68,
                    69,
                }
            ),
        ],
    ),
    # Code of the category of "Professions et Catégories Socioprofessionnelles" the person belongs
    # to (2003 version).
    Variable(
        "pcs_category_code2003",
        pl.UInt8,
        [
            Null(
                when=pl.col("professional_occupation").eq("student")
                & pl.col("detailed_professional_occupation").ne("student:apprenticeship")
                & pl.col("secondary_professional_occupation").ne("work")
            ),
            ValueInSet(
                {
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
                }
            ),
        ],
    ),
    # Code of the group of "Professions et Catégories Socioprofessionnelles" the person belongs to.
    Variable(
        "pcs_group_code",
        pl.UInt8,
        [
            Null(
                when=pl.col("professional_occupation").eq("student")
                & pl.col("detailed_professional_occupation").ne("student:apprenticeship")
                & pl.col("secondary_professional_occupation").ne("work")
            ),
            Defined(when=pl.col("pcs_category_code2020").is_not_null()),
            Defined(when=pl.col("pcs_category_code2003").is_not_null()),
            EqualTo(
                pl.col("pcs_category_code2020") // 10,
                alias="first digit of `pcs_category_code2020`",
                when=pl.col("pcs_category_code2020").is_not_null(),
            ),
            EqualTo(
                pl.col("pcs_category_code2003") // 10,
                alias="first digit of `pcs_category_code2003`",
                when=pl.col("pcs_category_code2003").is_not_null(),
            ),
        ],
    ),
    # Group of "Professions et Catégories Socioprofessionnelles" the person belongs to.
    Variable(
        "pcs_group",
        pl.Enum(list(PCS_CODES.values())),
        [
            Null(
                when=pl.col("professional_occupation").eq("student")
                & pl.col("detailed_professional_occupation").ne("student:apprenticeship")
                & pl.col("secondary_professional_occupation").ne("work")
            ),
            Defined(when=pl.col("pcs_group_code").is_not_null()),
            EqualToMapping(pl.col("pcs_group_code"), "`pcs_group_code`", PCS_CODES),
        ],
    ),
    # Whether the person work only at home.
    Variable(
        "work_only_at_home",
        pl.Boolean,
        [Null(when=IS_NOT_WORKER_EXPR)],
    ),
    # Whether the person has a unique, fixed workplace location.
    Variable(
        "workplace_singularity",
        pl.Enum(["unique:outside", "unique:home", "variable"]),
        [
            Null(when=IS_NOT_WORKER_EXPR),
            ValueIs("unique:home", when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Longitude of usual workplace.
    Variable(
        "work_lng",
        pl.Float64,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Latitude of usual workplace.
    Variable(
        "work_lat",
        pl.Float64,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Special location of the usual work location of the person.
    Variable(
        "work_special_location",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Detailed zone of the usual work location of the person.
    Variable(
        "work_detailed_zone",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Draw zone of the usual work location.
    Variable(
        "work_draw_zone",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # INSEE code of the municipality where the usual work location is.
    Variable(
        "work_insee",
        pl.String,
        [
            ValidInsee(),
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
            InseeConsistentWithDep("work_dep"),
        ],
    ),
    # Name of the municipality where the usual work location is.
    Variable(
        "work_insee_name",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Département code of the usual work location.
    Variable(
        "work_dep",
        pl.String,
        [
            ValidDepCode(),
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Département name of the usual work location.
    Variable(
        "work_dep_name",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # NUTS 2 code of the usual work location.
    Variable(
        "work_nuts2",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # NUTS 2 name of the usual work location.
    Variable(
        "work_nuts2_name",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # NUTS 1 code of the usual work location.
    Variable(
        "work_nuts1",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # NUTS 1 name of the usual work location.
    Variable(
        "work_nuts1_name",
        pl.String,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Euclidean distance between the person's home location and usual work location.
    Variable(
        "work_commute_euclidean_distance_km",
        pl.Float64,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            ValueIs(0.0, when=pl.col("work_only_at_home").eq(True)),
            NonNegative(),
        ],
    ),
    # Whether the person has a vehicle he/she can use to commute to work.
    Variable(
        "has_car_for_work_commute",
        COMMUTE_CAR_ENUM,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Frequency of telework for the person.
    Variable(
        "telework",
        pl.Enum(["yes:weekly", "yes:monthly", "yes:occasionally", "no"]),
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Whether the person has access to a car parking spot at work location.
    Variable(
        "work_car_parking",
        CAR_PARKING_ENUM,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Whether the person has access to a bicycle parking spot at work location.
    Variable(
        "work_bicycle_parking",
        BICYCLE_PARKING_ENUM,
        [
            Null(when=IS_NOT_WORKER_EXPR),
            Null(when=pl.col("work_only_at_home").eq(True)),
        ],
    ),
    # Category indicating the detailed current education level for students.
    Variable(
        "student_category",
        pl.Enum(list(STUDENT_GROUP_MAP.keys())),
        [Null(when=pl.col("professional_occupation") != "student")],
    ),
    # Group indicating the current education level for students.
    Variable(
        "student_group",
        pl.Enum(["primaire", "collège", "lycée", "supérieur"]),
        [
            Null(when=pl.col("professional_occupation") != "student"),
            EqualToMapping(pl.col("student_category"), "`student_category`", STUDENT_GROUP_MAP),
            ValueInSet(
                {"primaire", "collège", "lycée"},
                when=pl.col("detailed_professional_occupation").eq("student:primary_or_secondary"),
            ),
            ValueIs(
                "supérieur", when=pl.col("detailed_professional_occupation").eq("student:higher")
            ),
            ValueInSet(
                {"lycée", "supérieur"},
                when=pl.col("detailed_professional_occupation").eq("student:apprenticeship"),
            ),
        ],
    ),
    # Whether the person study only at home.
    Variable(
        "study_only_at_home",
        pl.Boolean,
        [Null(when=pl.col("professional_occupation") != "student")],
    ),
    # Longitude of usual study location.
    Variable(
        "study_lng",
        pl.Float64,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Latitude of usual study location.
    Variable(
        "study_lat",
        pl.Float64,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Special location of the usual study location of the person.
    Variable(
        "study_special_location",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Detailed zone of the usual study location of the person.
    Variable(
        "study_detailed_zone",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Draw zone of the usual study location.
    Variable(
        "study_draw_zone",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # INSEE code of the municipality where the usual study location is.
    Variable(
        "study_insee",
        pl.String,
        [
            ValidInsee(),
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
            InseeConsistentWithDep("study_dep"),
        ],
    ),
    # Name of the municipality where the usual study location is.
    Variable(
        "study_insee_name",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Département code of the usual study location.
    Variable(
        "study_dep",
        pl.String,
        [
            ValidDepCode(),
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Département name of the usual study location.
    Variable(
        "study_dep_name",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # NUTS 2 code of the usual study location.
    Variable(
        "study_nuts2",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # NUTS 2 name of the usual study location.
    Variable(
        "study_nuts2_name",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # NUTS 1 code of the usual study location.
    Variable(
        "study_nuts1",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # NUTS 1 name of the usual study location.
    Variable(
        "study_nuts1_name",
        pl.String,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Euclidean distance between the person's home location and usual study location.
    Variable(
        "study_commute_euclidean_distance_km",
        pl.Float64,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            ValueIs(0.0, when=pl.col("study_only_at_home").eq(True)),
            NonNegative(),
        ],
    ),
    # Whether the person has a vehicle he/she can use to commute to study.
    Variable(
        "has_car_for_study_commute",
        COMMUTE_CAR_ENUM,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Whether the person has access to a car parking spot at study location.
    Variable(
        "study_car_parking",
        CAR_PARKING_ENUM,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Whether the person has access to a bicycle parking spot at study location.
    Variable(
        "study_bicycle_parking",
        BICYCLE_PARKING_ENUM,
        [
            Null(when=pl.col("professional_occupation") != "student"),
            Null(when=pl.col("study_only_at_home").eq(True)),
        ],
    ),
    # Whether the person has a driving license.
    Variable(
        "has_driving_license",
        pl.Enum(["yes", "no", "in_progress"]),
        [
            ValueIsNot(
                "yes", when=pl.col("age") < 17, when_alias='"age" < 17', fix_value="in_progress"
            ),
            ValueIsNot(
                "in_progress", when=pl.col("age") < 15, when_alias='"age" < 15', fix_value="no"
            ),
        ],
    ),
    # Whether the person has a driving license for motorcycles.
    Variable(
        "has_motorcycle_driving_license",
        pl.Enum(["yes", "no", "in_progress"]),
        [
            ValueIsNot(
                "yes", when=pl.col("age") < 17, when_alias='"age" < 17', fix_value="in_progress"
            ),
            ValueIsNot(
                "in_progress", when=pl.col("age") < 15, when_alias='"age" < 15', fix_value="no"
            ),
        ],
    ),
    # Type of public-transit subscription the person had.
    Variable(
        "public_transit_subscription",
        pl.Enum(
            [
                "yes:free",
                "yes:paid:with_employer_contribution",
                "yes:paid:without_employer_contribution",
                "yes:paid",
                "yes:unspecified",
                "no",
            ]
        ),
    ),
    # Whether the person had a valid public-transit subscription the day before the interview.
    Variable(
        "has_public_transit_subscription",
        pl.Boolean,
        [
            Defined(when=pl.col("public_transit_subscription").is_not_null()),
            ValueIs(False, when=pl.col("public_transit_subscription").eq("no")),
            ValueIsNot(False, when=pl.col("public_transit_subscription").ne("no")),
        ],
    ),
    # Type of car-sharing service subscription the person has.
    Variable(
        "car_sharing_subscription",
        pl.Enum(["yes:organized", "yes:peer_to_peer", "yes:unspecified", "no"]),
    ),
    # Whether the person has a subscription for a car-sharing service.
    Variable(
        "has_car_sharing_subscription",
        pl.Boolean,
        [
            Defined(when=pl.col("car_sharing_subscription").is_not_null()),
            ValueIs(False, when=pl.col("car_sharing_subscription").eq("no")),
            ValueIsNot(False, when=pl.col("car_sharing_subscription").ne("no")),
        ],
    ),
    # Whether the person has a subscription for a bike-sharing service.
    Variable("has_bike_sharing_subscription", pl.Boolean),
    # Whether the person has reported having travel inconveniences.
    Variable("has_travel_inconvenience", pl.Boolean),
    # Whether the person was surveyed for his/her trips of previous day.
    Variable("is_surveyed", pl.Boolean, [Defined()]),
    # Whether the person performed at least one trip during the day before the interview.
    Variable(
        "traveled_during_surveyed_day",
        pl.Enum(["yes", "no", "away"]),
        [DefinedIfAndOnlyIf(pl.col("is_surveyed").eq(True))],
    ),
    # Whether the person worked during the day before the interview.
    Variable(
        "worked_during_surveyed_day",
        pl.Enum(
            [
                "yes:outside",
                "yes:home:usual",
                "yes:home:telework",
                "yes:home:other",
                "yes:unspecified",
                "no:weekday",
                "no:reason",
                "no:unspecified",
            ]
        ),
        [
            Null(when=pl.col("is_surveyed").eq(False)),
            ValueIsNot("yes:home:usual", when=pl.col("work_only_at_home").eq(False)),
        ],
    ),
    # Number of trips that this person performed.
    Variable(
        "nb_trips",
        pl.UInt8,
        [
            DefinedIfAndOnlyIf(pl.col("is_surveyed").eq(True)),
            ValueIs(
                0,
                when=pl.col("traveled_during_surveyed_day").is_in(("no", "away")),
                when_alias='"traveled_during_surveyed_day" is "no" or "away"',
            ),
            ValueIsNot(0, when=pl.col("traveled_during_surveyed_day") == "yes"),
        ],
    ),
    # Sample weight of the person among all the persons interviewed.
    Variable("sample_weight_all", pl.Float64, [NonNegative()]),
    # Sample weight of the person among all the persons whose trips were surveyed.
    Variable(
        "sample_weight_surveyed",
        pl.Float64,
        [NonNegative(), Null(when=pl.col("is_surveyed").eq(False))],
    ),
]

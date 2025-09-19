import polars as pl

from .common import Variable
from .guarantees import (
    AllDefinedOrAllNull,
    Defined,
    EqualTo,
    Indexed,
    InseeConsistentWithDep,
    LargerThan,
    NonNegative,
    Positive,
    Unique,
    ValidDepCode,
    ValidInsee,
)

HOUSEHOLD_SCHEMA = [
    # Identifier of the household.
    Variable("household_id", pl.UInt32, [Indexed()]),
    # Identifier of the household in the original survey data.
    Variable("original_household_id", pl.Struct, [Unique()]),
    # Method used to survey the household.
    Variable("survey_method", pl.Enum(["face_to_face", "phone"]), [AllDefinedOrAllNull()]),
    # Date at which the interview took place.
    Variable("interview_date", pl.Date),
    # Day of the week when the reported trips took place.
    Variable(
        "trips_weekday",
        pl.Enum(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]),
    ),
    # Sample weight of the household.
    Variable("sample_weight", pl.Float64, [AllDefinedOrAllNull(), NonNegative()]),
    # Longitude of home coordinates.
    Variable("home_lng", pl.Float64),
    # Latitude of home coordinates.
    Variable("home_lat", pl.Float64),
    # Special location where the household is located.
    Variable("home_special_location", pl.String),
    # Detailed zone where the household is located.
    Variable("home_detailed_zone", pl.String, []),
    # Draw zone where the household is located.
    Variable("home_draw_zone", pl.String, []),
    # INSEE code of the municipality where the household is located.
    Variable("home_insee", pl.String, [ValidInsee(), InseeConsistentWithDep("home_dep")]),
    # Name of the municipality where the household is located.
    Variable("home_insee_name", pl.String),
    # Département code of the household home.
    Variable("home_dep", pl.String, [ValidDepCode()]),
    # Département name of the household home.
    Variable("home_dep_name", pl.String),
    # NUTS 2 code of the household home.
    Variable("home_nuts2", pl.String),
    # NUTS 2 name of the household home.
    Variable("home_nuts2_name", pl.String),
    # NUTS 1 code of the household home.
    Variable("home_nuts1", pl.String),
    # NUTS 1 name of the household home.
    Variable("home_nuts1_name", pl.String),
    # Type of household structure.
    Variable(
        "household_type",
        pl.Enum(
            [
                "single:man",
                "single:woman",
                "couple:no_child",
                "couple:children",
                "singleparent:father",
                "singleparent:mother",
                "other",
            ]
        ),
    ),
    # Lower bound for the net income of the household, in euros.
    Variable("income_lower_bound", pl.UInt16),
    # Upper bound for the net income of the household, in euros.
    Variable(
        "income_upper_bound",
        pl.UInt16,
        [LargerThan(pl.col("income_lower_bound"), strict=False)],
    ),
    # Type of the housing the household is living in.
    Variable("housing_type", pl.Enum(["house", "apartment", "other"])),
    # Type of ownership / renting for the housing.
    Variable(
        "housing_status",
        pl.Enum(
            [
                "owner:ongoing_loan",
                "owner:fully_repaid",
                "owner:usufructuary",
                "owner:unspecified",
                "tenant:public_housing",
                "tenant:private",
                "tenant:unspecified",
                "rent_free",
                "university_resident",
                "other",
            ]
        ),
    ),
    # Whether the household has internet access at home.
    Variable("has_internet", pl.Boolean),
    # Number of cars owned by the household.
    Variable("nb_cars", pl.UInt8),
    # Number of motorcycles (or similar) owned by the household.
    Variable("nb_motorcycles", pl.UInt8),
    # Number of bicycles (standard or electric) owned by the household.
    Variable(
        "nb_bicycles",
        pl.UInt8,
        [
            Defined(
                when=pl.col("nb_standard_bicycles").is_not_null()
                & pl.col("nb_electric_bicycles").is_not_null()
            ),
            EqualTo(
                pl.col("nb_standard_bicycles") + pl.col("nb_electric_bicycles"),
                when=pl.col("nb_standard_bicycles").is_not_null()
                & pl.col("nb_electric_bicycles").is_not_null(),
            ),
        ],
    ),
    # Number of standard bicycles (non-electric) owned by the household.
    Variable(
        "nb_standard_bicycles",
        pl.UInt8,
        [
            Defined(
                when=pl.col("nb_bicycles").is_not_null()
                & pl.col("nb_electric_bicycles").is_not_null()
            )
        ],
    ),
    # Number of electric bicycles owned by the household.
    Variable(
        "nb_electric_bicycles",
        pl.UInt8,
        [
            Defined(
                when=pl.col("nb_bicycles").is_not_null()
                & pl.col("nb_standard_bicycles").is_not_null()
            )
        ],
    ),
    # Whether the household can park bicycles at home.
    Variable("has_bicycle_parking", pl.Boolean),
    # Number of persons in the household.
    Variable(
        "nb_persons",
        pl.UInt8,
        [
            Positive(),
            Defined(),
            EqualTo(
                pl.col("nb_majors") + pl.col("nb_minors"),
                when=pl.col("nb_majors").is_not_null() & pl.col("nb_minors").is_not_null(),
            ),
        ],
    ),
    # Number of persons in the household whose age is 6 or more.
    Variable("nb_persons_5plus", pl.UInt8),
    # Number of persons in the household whose age is 18 or more.
    Variable("nb_majors", pl.UInt8, [Defined(when=pl.col("nb_minors").is_not_null())]),
    # Number of persons in the household whose age is 17 or less.
    Variable("nb_minors", pl.UInt8, [Defined(when=pl.col("nb_majors").is_not_null())]),
]

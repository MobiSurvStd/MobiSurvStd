import polars as pl

from .common import MODE_ENUM, MODE_GROUP_ENUM, MODE_TO_GROUP, PARKING_TYPE_ENUM, Variable
from .guarantees import (
    AtMostOneOf,
    Defined,
    DefinedIfAndOnlyIf,
    EqualTo,
    EqualToMapping,
    Indexed,
    InseeConsistentWithDep,
    ListContains,
    ListLengthIs,
    LowerBounded,
    NonDecreasing,
    NonNegative,
    Null,
    Positive,
    SmallerThan,
    ValidDepCode,
    ValidInsee,
    ValueIs,
)

LEG_PARKING_LOCATION_ENUM = pl.Enum(
    [
        "stop_only",
        "garage",
        "street",
        "parking_lot",
        "parking_lot:unsheltered",
        "parking_lot:sheltered",
        "P+R",
        "other",
    ]
)

LEG_SCHEMA = [
    # Identifier of the leg.
    Variable("leg_id", pl.UInt32, [Indexed()]),
    # Identifier of the trip that the leg belongs to.
    Variable("trip_id", pl.UInt32, [Defined(), NonDecreasing()]),
    # Identifier of the person that performed the leg.
    Variable("person_id", pl.UInt32, [Defined(), NonDecreasing()]),
    # Identifier of the household in which the person who performed the leg belongs.
    Variable("household_id", pl.UInt32, [Defined(), NonDecreasing()]),
    # Index of the leg among the trip's legs.
    Variable("leg_index", pl.UInt8, [Defined(), Indexed(over=pl.col("trip_id"))]),
    # Whether the leg is the first one of the trip.
    Variable(
        "first_leg",
        pl.Boolean,
        [
            Defined(),
            ValueIs(True, when=pl.col("leg_index") == 1),
            AtMostOneOf(True, over="trip_id"),
        ],
    ),
    # Whether the leg is the last one of the trip.
    Variable(
        "last_leg",
        pl.Boolean,
        [
            Defined(),
            ValueIs(True, when=pl.col("leg_index") == pl.col("leg_index").max().over("trip_id")),
            AtMostOneOf(True, over="trip_id"),
        ],
    ),
    # Identifier of the leg in the original survey data.
    Variable("original_leg_id", pl.Struct),
    # Mode of transportation used to perform the leg.
    Variable("mode", MODE_ENUM),
    # Mode group of the mode of transportation used.
    Variable(
        "mode_group",
        MODE_GROUP_ENUM,
        [
            Defined(when=pl.col("mode").is_not_null()),
            EqualToMapping(pl.col("mode"), "`mode` group", MODE_TO_GROUP),
        ],
    ),
    # Name of the public-transit line taken.
    Variable(
        "public_transit_line", pl.String, [Null(when=pl.col("mode_group") != "public_transit")]
    ),
    # Longitude of the leg's start point.
    Variable("start_lng", pl.Float64),
    # Latitude of the leg's start point.
    Variable("start_lat", pl.Float64),
    # Special location from which the leg started (after walking).
    Variable("start_special_location", pl.String),
    # Detailed zone from which the leg started (after walking).
    Variable("start_detailed_zone", pl.String),
    # Draw zone from which the leg started (after walking).
    Variable("start_draw_zone", pl.String),
    # INSEE code of the municipality from which the leg started (after walking).
    Variable("start_insee", pl.String, [ValidInsee(), InseeConsistentWithDep("start_dep")]),
    # Name of the municipality from which the leg started (after walking).
    Variable("start_insee_name", pl.String),
    # Département code of the leg's start point.
    Variable("start_dep", pl.String, [ValidDepCode()]),
    # Département name of the leg's start point.
    Variable("start_dep_name", pl.String),
    # NUTS 2 code of the leg's start point.
    Variable("start_nuts2", pl.String),
    # NUTS 2 name of the leg's start point.
    Variable("start_nuts2_name", pl.String),
    # NUTS 1 code of the leg's start point.
    Variable("start_nuts1", pl.String),
    # NUTS 1 name of the leg's start point.
    Variable("start_nuts1_name", pl.String),
    # Longitude of the leg's end point.
    Variable("end_lng", pl.Float64),
    # Latitude of the leg's end point.
    Variable("end_lat", pl.Float64),
    # Special location at which the leg stopped (before walking).
    Variable("end_special_location", pl.String),
    # Detailed zone at which the leg stopped (before walking).
    Variable("end_detailed_zone", pl.String),
    # Draw zone at which the leg stopped (before walking).
    Variable("end_draw_zone", pl.String),
    # INSEE code of the municipality at which the leg stopped (before walking).
    Variable("end_insee", pl.String, [ValidInsee(), InseeConsistentWithDep("end_dep")]),
    # Name of the municipality at which the leg stopped (after walking).
    Variable("end_insee_name", pl.String),
    # Département code of the leg's end point.
    Variable("end_dep", pl.String, [ValidDepCode()]),
    # Département name of the leg's end point.
    Variable("end_dep_name", pl.String),
    # NUTS 2 code of the leg's end point.
    Variable("end_nuts2", pl.String),
    # NUTS 2 name of the leg's end point.
    Variable("end_nuts2_name", pl.String),
    # NUTS 1 code of the leg's end point.
    Variable("end_nuts1", pl.String),
    # NUTS 1 name of the leg's end point.
    Variable("end_nuts1_name", pl.String),
    # Travel time between start and stop points, in minutes.
    Variable("leg_travel_time", pl.UInt16),
    # Euclidean distance between start and stop points, in kilometers.
    Variable("leg_euclidean_distance_km", pl.Float64, [NonNegative()]),
    # Travel distance between start and stop points, in kilometers.
    Variable("leg_travel_distance_km", pl.Float64, [NonNegative()]),
    # Type of car used for the leg.
    Variable(
        "car_type",
        pl.Enum(["household", "other_household", "rental", "company", "shared", "other"]),
        [Null(when=pl.col("mode_group").is_in(("car_driver", "car_passenger")).not_())],
    ),
    # Identifier of the car used to perform the leg.
    Variable("car_id", pl.UInt32, [DefinedIfAndOnlyIf(pl.col("car_type").eq("household"))]),
    # Whether the car used was a no-license car.
    Variable(
        "nolicense_car",
        pl.Boolean,
        [Null(when=pl.col("mode_group").is_in(("car_driver", "car_passenger")).not_())],
    ),
    # Type of motorcycle used for the leg.
    Variable(
        "motorcycle_type",
        pl.Enum(["household", "other_household", "rental", "company", "shared", "other"]),
        [Null(when=pl.col("mode_group") != "motorcycle")],
    ),
    # Identifier of the motorcycle used to perform the leg.
    Variable(
        "motorcycle_id", pl.UInt32, [DefinedIfAndOnlyIf(pl.col("motorcycle_type").eq("household"))]
    ),
    # Number of persons that were present in the vehicle used.
    Variable(
        "nb_persons_in_vehicle",
        pl.UInt8,
        [
            Positive(),
            Null(when=pl.col("mode_group").is_in(("walking", "public_transit"))),
            LowerBounded(
                2,
                when=pl.col("mode").cast(pl.String).str.contains("passenger"),
                when_alias="`mode` is passenger related",
            ),
        ],
    ),
    # Ids of the person that were in the vehicle.
    Variable(
        "in_vehicle_person_ids",
        pl.List(pl.UInt32),
        [
            Null(when=pl.col("mode_group").is_in(("walking", "public_transit"))),
            ListContains(
                pl.col("person_id"),
                alias="the leg' `person_id`",
                when=pl.col("in_vehicle_person_ids").is_not_null(),
            ),
            ListLengthIs(
                pl.col("nb_household_members_in_vehicle"),
                when=pl.col("in_vehicle_person_ids").is_not_null(),
            ),
        ],
    ),
    # Number of majors that were present in the vehicle used.
    Variable(
        "nb_majors_in_vehicle",
        pl.UInt8,
        [
            Null(when=pl.col("mode_group").is_in(("walking", "public_transit"))),
            SmallerThan(pl.col("nb_persons_in_vehicle"), strict=False),
        ],
    ),
    # Number of minors that were present in the vehicle used.
    Variable(
        "nb_minors_in_vehicle",
        pl.UInt8,
        [
            Null(when=pl.col("mode_group").is_in(("walking", "public_transit"))),
            SmallerThan(pl.col("nb_persons_in_vehicle"), strict=False),
            EqualTo(
                pl.col("nb_persons_in_vehicle") - pl.col("nb_majors_in_vehicle"),
                when=pl.col("nb_persons_in_vehicle").is_not_null()
                & pl.col("nb_majors_in_vehicle").is_not_null(),
            ),
            Defined(
                when=pl.col("nb_persons_in_vehicle").is_not_null()
                & pl.col("nb_majors_in_vehicle").is_not_null()
            ),
        ],
    ),
    # Number of persons from the household that were present in the vehicle.
    Variable(
        "nb_household_members_in_vehicle",
        pl.UInt8,
        [
            Null(when=pl.col("mode_group").is_in(("walking", "public_transit"))),
            SmallerThan(pl.col("nb_persons_in_vehicle"), strict=False),
            Defined(when=pl.col("in_vehicle_person_ids").is_not_null()),
        ],
    ),
    # Number of persons not from the household that were present in the vehicle.
    Variable(
        "nb_non_household_members_in_vehicle",
        pl.UInt8,
        [
            Null(when=pl.col("mode_group").is_in(("walking", "public_transit"))),
            SmallerThan(pl.col("nb_persons_in_vehicle"), strict=False),
            EqualTo(
                pl.col("nb_persons_in_vehicle") - pl.col("nb_household_members_in_vehicle"),
                when=pl.col("nb_persons_in_vehicle").is_not_null()
                & pl.col("nb_household_members_in_vehicle").is_not_null(),
            ),
            Defined(
                when=pl.col("nb_persons_in_vehicle").is_not_null()
                & pl.col("nb_household_members_in_vehicle").is_not_null()
            ),
        ],
    ),
    # Location type where the car was parked at the end of the leg.
    Variable(
        "parking_location",
        LEG_PARKING_LOCATION_ENUM,
        [Null(when=pl.col("mode_group").is_in(("walking", "public_transit")))],
    ),
    # Type of parking (paid or free) used to park the car.
    Variable(
        "parking_type",
        PARKING_TYPE_ENUM,
        [Null(when=pl.col("mode_group").is_in(("walking", "public_transit")))],
    ),
    # Time spent searching for a parking spot.
    Variable(
        "parking_search_time",
        pl.UInt32,
        [Null(when=pl.col("mode_group").is_in(("walking", "public_transit")))],
    ),
]

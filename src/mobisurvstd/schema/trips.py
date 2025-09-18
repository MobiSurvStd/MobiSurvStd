import polars as pl

from .common import MODE_ENUM, MODE_GROUP_ENUM, MODE_TO_GROUP, Variable
from .guarantees import (
    AtMostOneOf,
    Bounded,
    Defined,
    EqualTo,
    EqualToMapping,
    Indexed,
    InseeConsistentWithDep,
    LargerThan,
    NonDecreasing,
    NonNegative,
    Null,
    Positive,
    Sorted,
    ValidDepCode,
    ValidInsee,
    ValueInSet,
    ValueIs,
)

PURPOSE_ENUM = pl.Enum(
    [
        "home:main",
        "home:secondary",
        "work:usual",
        "work:telework",
        "work:secondary",
        "work:business_meal",
        "work:other",
        "work:professional_tour",
        "education:childcare",
        "education:usual",
        "education:other",
        "shopping:daily",
        "shopping:weekly",
        "shopping:specialized",
        "shopping:unspecified",
        "shopping:pickup",
        "shopping:no_purchase",
        "shopping:tour_no_purchase",
        "task:healthcare",
        "task:healthcare:hospital",
        "task:healthcare:doctor",
        "task:procedure",
        "task:job_search",
        "task:other",
        "leisure:sport_or_culture",
        "leisure:walk_or_driving_lesson",
        "leisure:lunch_break",
        "leisure:restaurant",
        "leisure:visiting",
        "leisure:visiting:parents",
        "leisure:visiting:friends",
        "leisure:other",
        "escort:activity:drop_off",
        "escort:activity:pick_up",
        "escort:transport:drop_off",
        "escort:transport:pick_up",
        "escort:unspecified:drop_off",
        "escort:unspecified:pick_up",
        "other",
    ]
)

SHOP_TYPE_ENUM = pl.Enum(
    [
        "small_shop",
        "supermarket",
        "hypermarket",
        "supermarket_or_hypermarket",
        "mall",
        "market",
        "drive_in",
        "private",
        "other",
    ]
)

PURPOSE_GROUP_ENUM = pl.Enum(
    ["home", "work", "education", "shopping", "task", "leisure", "escort", "other"]
)

TRIP_SCHEMA = [
    # Identifier of the trip.
    Variable("trip_id", pl.UInt32, [Indexed()]),
    # Identifier of the person who performed the trip.
    Variable("person_id", pl.UInt32, [Defined(), NonDecreasing()]),
    # Identifier of the household in which the person who performed the trip belongs.
    Variable("household_id", pl.UInt32, [Defined(), NonDecreasing()]),
    # Index of the trip among the person's trips.
    Variable("trip_index", pl.UInt8, [Defined(), Indexed(over=pl.col("person_id"))]),
    # Whether the trip is the first one of the person.
    Variable(
        "first_trip",
        pl.Boolean,
        [
            Defined(),
            ValueIs(True, when=pl.col("trip_index") == 1),
            AtMostOneOf(True, over="person_id"),
        ],
    ),
    # Whether the trip is the last one of the person.
    Variable(
        "last_trip",
        pl.Boolean,
        [
            Defined(),
            ValueIs(
                True, when=pl.col("trip_index") == pl.col("trip_index").max().over("person_id")
            ),
            AtMostOneOf(True, over="person_id"),
        ],
    ),
    # Cumulative number of times that the person started a trip from their main home.
    Variable("home_sequence_index", pl.UInt8),
    # Identifier of the trip in the original survey data.
    Variable("original_trip_id", pl.Struct),
    # Purpose of the activity performed at the trip's origin.
    Variable("origin_purpose", PURPOSE_ENUM),
    # Purpose group of the activity performed at the trip's origin.
    Variable(
        "origin_purpose_group",
        PURPOSE_GROUP_ENUM,
        [
            EqualTo(
                pl.col("origin_purpose").cast(pl.String).str.extract(r"(\w+):?"),
                '"origin_purpose" group',
            ),
            Defined(when=pl.col("origin_purpose").is_not_null()),
        ],
    ),
    # Duration at the activity performed at the trip's origin, in minutes.
    Variable(
        "origin_activity_duration",
        pl.UInt16,
        [
            Null(when=pl.col("first_trip")),
            EqualTo(
                pl.col("departure_time") - pl.col("arrival_time").shift(1).over("person_id"),
                "difference between departure time and previous arrival time",
            ),
        ],
    ),
    # Purpose of the activity performed at the trip's destination.
    Variable("destination_purpose", PURPOSE_ENUM),
    # Purpose group of the activity performed at the trip's destination.
    Variable(
        "destination_purpose_group",
        PURPOSE_GROUP_ENUM,
        [
            EqualTo(
                pl.col("destination_purpose").cast(pl.String).str.extract(r"(\w+):?"),
                '"destination_purpose" group',
            ),
            Defined(when=pl.col("destination_purpose").is_not_null()),
        ],
    ),
    # Duration at the activity performed at the trip's destination, in minutes.
    Variable(
        "destination_activity_duration",
        pl.UInt16,
        [
            Null(when=pl.col("last_trip")),
            EqualTo(
                pl.col("departure_time").shift(-1).over("person_id") - pl.col("arrival_time"),
                "difference between next departure time and arrival time",
            ),
        ],
    ),
    # Purpose of the activity performed at the trip's origin by the person who is escorted.
    Variable(
        "origin_escort_purpose",
        PURPOSE_ENUM,
        [Null(when=pl.col("origin_purpose_group") != "escort")],
    ),
    # Purpose group of the activity performed at the trip's origin by the person who is escorted.
    Variable(
        "origin_escort_purpose_group",
        PURPOSE_GROUP_ENUM,
        [
            Null(when=pl.col("origin_purpose_group") != "escort"),
            EqualTo(
                pl.col("origin_escort_purpose").cast(pl.String).str.extract(r"(\w+):?"),
                '"origin_escort_purpose" group',
            ),
            Defined(when=pl.col("origin_escort_purpose").is_not_null()),
        ],
    ),
    # Purpose of the activity performed at the trip's destination by the person who is escorted.
    Variable(
        "destination_escort_purpose",
        PURPOSE_ENUM,
        [Null(when=pl.col("destination_purpose_group") != "escort")],
    ),
    # Purpose group of the activity performed at the trip's destination by the person who is
    # escorted.
    Variable(
        "destination_escort_purpose_group",
        PURPOSE_GROUP_ENUM,
        [
            Null(when=pl.col("destination_purpose_group") != "escort"),
            EqualTo(
                pl.col("destination_escort_purpose").cast(pl.String).str.extract(r"(\w+):?"),
                '"destination_escort_purpose" group',
            ),
            Defined(when=pl.col("destination_escort_purpose").is_not_null()),
        ],
    ),
    # Type of shop where the activity at origin was performed.
    Variable(
        "origin_shop_type",
        SHOP_TYPE_ENUM,
        [Null(when=pl.col("origin_purpose_group") != "shopping")],
    ),
    # Type of shop where the activity at destination was performed.
    Variable(
        "destination_shop_type",
        SHOP_TYPE_ENUM,
        [Null(when=pl.col("destination_purpose_group") != "shopping")],
    ),
    # Longitude of the trip's origin.
    Variable("origin_lng", pl.Float64),
    # Latitude of the trip's origin.
    Variable("origin_lat", pl.Float64),
    # Special location of the trip's origin.
    Variable("origin_special_location", pl.String),
    # Detailed zone of the trip's origin.
    Variable("origin_detailed_zone", pl.String),
    # Draw zone of the trip's origin.
    Variable("origin_draw_zone", pl.String),
    # INSEE code of the municipality of trip's origin.
    Variable("origin_insee", pl.String, [ValidInsee(), InseeConsistentWithDep("origin_dep")]),
    # Name of the municipality of trip's origin.
    Variable("origin_insee_name", pl.String),
    # Density category of the origin INSEE municipality.
    Variable("origin_insee_density", pl.UInt8, [Bounded(1, 7)]),
    # Category of the origin INSEE municipality within the AAV.
    Variable("origin_insee_aav_type", pl.UInt8, [ValueInSet({11, 12, 13, 20, 30})]),
    # Code of the AAV of the trip's origin.
    Variable("origin_aav", pl.String),
    # Name of the AAV of the trip's origin.
    Variable("origin_aav_name", pl.String),
    # Category of the AAV of the trip's origin.
    Variable("origin_aav_category", pl.UInt8, [Bounded(1, 5)]),
    # Département code of the trip's origin.
    Variable("origin_dep", pl.String, [ValidDepCode()]),
    # Département name of the trip's origin.
    Variable("origin_dep_name", pl.String),
    # NUTS 2 code of the trip's origin.
    Variable("origin_nuts2", pl.String),
    # NUTS 2 name of the trip's origin.
    Variable("origin_nuts2_name", pl.String),
    # NUTS 1 code of the trip's origin.
    Variable("origin_nuts1", pl.String),
    # NUTS 1 name of the trip's origin.
    Variable("origin_nuts1_name", pl.String),
    # Longitude of the trip's destination.
    Variable("destination_lng", pl.Float64),
    # Latitude of the trip's destination.
    Variable("destination_lat", pl.Float64),
    # Special location of the trip's destination.
    Variable("destination_special_location", pl.String),
    # Detailed zone of the trip's destination.
    Variable("destination_detailed_zone", pl.String),
    # Draw zone of the trip's destination.
    Variable("destination_draw_zone", pl.String),
    # INSEE code of the municipality of trip's destination.
    Variable(
        "destination_insee", pl.String, [ValidInsee(), InseeConsistentWithDep("destination_dep")]
    ),
    # Name of the municipality of trip's destination.
    Variable("destination_insee_name", pl.String),
    # Density category of the destination INSEE municipality.
    Variable("destination_insee_density", pl.UInt8, [Bounded(1, 7)]),
    # Category of the destination INSEE municipality within the AAV.
    Variable("destination_insee_aav_type", pl.UInt8, [ValueInSet({11, 12, 13, 20, 30})]),
    # Code of the AAV of the trip's destination.
    Variable("destination_aav", pl.String),
    # Name of the AAV of the trip's destination.
    Variable("destination_aav_name", pl.String),
    # Category of the AAV of the trip's destination.
    Variable("destination_aav_category", pl.UInt8, [Bounded(1, 5)]),
    # Département code of the trip's destination.
    Variable("destination_dep", pl.String, [ValidDepCode()]),
    # Département name of the trip's destination.
    Variable("destination_dep_name", pl.String),
    # NUTS 2 code of the trip's destination.
    Variable("destination_nuts2", pl.String),
    # NUTS 2 name of the trip's destination.
    Variable("destination_nuts2_name", pl.String),
    # NUTS 1 code of the trip's destination.
    Variable("destination_nuts1", pl.String),
    # NUTS 1 name of the trip's destination.
    Variable("destination_nuts1_name", pl.String),
    # Departure time from origin, in number of minutes after midnight.
    Variable("departure_time", pl.UInt16, [Sorted(over="person_id")]),
    # Arrival time at destination, in number of minutes after midnight.
    Variable(
        "arrival_time",
        pl.UInt16,
        [Sorted(over="person_id"), LargerThan(pl.col("departure_time"), strict=False)],
    ),
    # Trip travel time, in minutes.
    Variable(
        "travel_time", pl.UInt16, [EqualTo(pl.col("arrival_time") - pl.col("departure_time"))]
    ),
    # Date at which the trip took place.
    Variable("trip_date", pl.Date),
    # Day of the week when the trip took place.
    Variable(
        "trip_weekday",
        pl.Enum(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]),
        [
            EqualTo(
                pl.col("trip_date")
                .dt.weekday()
                .replace_strict(
                    {
                        1: "monday",
                        2: "tuesday",
                        3: "wednesday",
                        4: "thursday",
                        5: "friday",
                        6: "saturday",
                        7: "sunday",
                    }
                ),
                alias='"trip_date" weekday',
            )
        ],
    ),
    # Main mode of transportation used for the trip.
    Variable("main_mode", MODE_ENUM),
    # Mode group of the main mode of transportation used for the trip.
    Variable(
        "main_mode_group",
        MODE_GROUP_ENUM,
        [
            Defined(when=pl.col("main_mode").is_not_null()),
            EqualToMapping(pl.col("main_mode"), "`main_mode` group", MODE_TO_GROUP),
        ],
    ),
    # Whether the trip involved using two different transportation modes.
    Variable("intermodality", pl.Boolean),
    # Mode of transportation used for the access part of the trips.
    Variable(
        "public_transit_access_mode",
        MODE_ENUM,
        [Null(when=pl.col("main_mode_group") != "public_transit")],
    ),
    # Mode group of the transportation mode used for the access part of the trips.
    Variable(
        "public_transit_access_mode_group",
        MODE_GROUP_ENUM,
        [
            Null(when=pl.col("main_mode_group") != "public_transit"),
            Defined(when=pl.col("public_transit_access_mode").is_not_null()),
            EqualToMapping(
                pl.col("public_transit_access_mode"),
                "`public_transit_access_mode` group",
                MODE_TO_GROUP,
            ),
        ],
    ),
    # Mode of transportation used for the egress part of the trips.
    Variable(
        "public_transit_egress_mode",
        MODE_ENUM,
        [Null(when=pl.col("main_mode_group") != "public_transit")],
    ),
    # Mode group of the transportation mode used for the egress part of the trips.
    Variable(
        "public_transit_egress_mode_group",
        MODE_GROUP_ENUM,
        [
            Null(when=pl.col("main_mode_group") != "public_transit"),
            Defined(when=pl.col("public_transit_egress_mode").is_not_null()),
            EqualToMapping(
                pl.col("public_transit_egress_mode"),
                "`public_transit_egress_mode` group",
                MODE_TO_GROUP,
            ),
        ],
    ),
    # Euclidean distance between the trip's origin and destination, in kilometers.
    Variable("trip_euclidean_distance_km", pl.Float64, [NonNegative()]),
    # Travel distance of the trip, in kilometers.
    Variable("trip_travel_distance_km", pl.Float64, [NonNegative()]),
    # Whether the INSEE origin equals the INSEE destination.
    Variable(
        "intra_municipality",
        pl.Boolean,
        [EqualTo(pl.col("origin_insee") == pl.col("destination_insee"))],
    ),
    # Whether the origin AAV equals the destination AAV.
    Variable("intra_aav", pl.Boolean, [EqualTo(pl.col("origin_aav") == pl.col("destination_aav"))]),
    # Whether the origin département equals the destination département.
    Variable("intra_dep", pl.Boolean, [EqualTo(pl.col("origin_dep") == pl.col("destination_dep"))]),
    # Trip type with respect to the survey's perimiter.
    Variable("trip_perimeter", pl.Enum(["internal", "crossing", "external", "unknown"])),
    # Number of stops for trips representing tours.
    Variable(
        "nb_tour_stops",
        pl.UInt8,
        [
            Null(
                when=pl.col("origin_purpose")
                .is_in(("work:professional_tour", "shopping:tour_no_purchase"))
                .not_()
                & pl.col("destination_purpose")
                .is_in(("work:professional_tour", "shopping:tour_no_purchase"))
                .not_(),
                when_alias='origin / destination purpose is not "work:professional_tour" or "shopping:tour_no_purchase"',
            )
        ],
    ),
    # Number of legs in the trip.
    Variable("nb_legs", pl.UInt8, [Defined(when=pl.col("main_mode").is_not_null()), Positive()]),
    # Number of walking legs in the trip.
    Variable(
        "nb_legs_walking",
        pl.UInt8,
        [
            Defined(when=pl.col("main_mode").is_not_null()),
            Positive(when=pl.col("main_mode_group") == "walking"),
        ],
    ),
    # Number of bicycle legs in the trip.
    Variable(
        "nb_legs_bicycle",
        pl.UInt8,
        [
            Defined(when=pl.col("main_mode").is_not_null()),
            Positive(when=pl.col("main_mode_group") == "bicycle"),
        ],
    ),
    # Number of motorcycle legs in the trip.
    Variable(
        "nb_legs_motorcycle",
        pl.UInt8,
        [
            Defined(when=pl.col("main_mode").is_not_null()),
            Positive(when=pl.col("main_mode_group") == "motorcycle"),
        ],
    ),
    # Number of car_driver legs in the trip.
    Variable(
        "nb_legs_car_driver",
        pl.UInt8,
        [
            Defined(when=pl.col("main_mode").is_not_null()),
            Positive(when=pl.col("main_mode_group") == "car_driver"),
        ],
    ),
    # Number of car_passenger legs in the trip.
    Variable(
        "nb_legs_car_passenger",
        pl.UInt8,
        [
            Defined(when=pl.col("main_mode").is_not_null()),
            Positive(when=pl.col("main_mode_group") == "car_passenger"),
        ],
    ),
    # Number of public_transit legs in the trip.
    Variable(
        "nb_legs_public_transit",
        pl.UInt8,
        [
            Defined(when=pl.col("main_mode").is_not_null()),
            Positive(when=pl.col("main_mode_group") == "public_transit"),
        ],
    ),
    # Number of other legs in the trip.
    Variable(
        "nb_legs_other",
        pl.UInt8,
        [
            Defined(when=pl.col("main_mode").is_not_null()),
            Positive(when=pl.col("main_mode_group") == "other"),
        ],
    ),
]

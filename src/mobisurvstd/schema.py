import polars as pl

HOUSEHOLD_SCHEMA = {
    # Identifier of the household.
    "household_id": pl.UInt32,
    # Identifier of the household in the original survey data.
    "original_household_id": pl.Struct,
    # Method used to survey the household.
    "survey_method": pl.Enum(["face_to_face", "phone"]),
    # Date at which the interview took place.
    "interview_date": pl.Date,
    # Sample weight of the household.
    "sample_weight": pl.Float64,
    # Longitude of home coordinates.
    "home_lng": pl.Float64,
    # Latitude of home coordinates.
    "home_lat": pl.Float64,
    # Special location where the household is located.
    "home_special_location": pl.String,
    # Detailed zone where the household is located.
    "home_detailed_zone": pl.String,
    # Draw zone where the household is located.
    "home_draw_zone": pl.String,
    # INSEE code of the municipality where the household is located.
    "home_insee": pl.String,
    # Name of the municipality where the household is located.
    "home_insee_name": pl.String,
    # Département code of the household home.
    "home_dep": pl.String,
    # Département name of the household home.
    "home_dep_name": pl.String,
    # NUTS 2 code of the household home.
    "home_nuts2": pl.String,
    # NUTS 2 name of the household home.
    "home_nuts2_name": pl.String,
    # NUTS 1 code of the household home.
    "home_nuts1": pl.String,
    # NUTS 1 name of the household home.
    "home_nuts1_name": pl.String,
    # Type of household structure.
    "household_type": pl.Enum(
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
    # Lower bound for the net income of the household, in euros.
    "income_lower_bound": pl.UInt16,
    # Upper bound for the net income of the household, in euros.
    "income_upper_bound": pl.UInt16,
    # Type of the housing the household is living in.
    "housing_type": pl.Enum(["house", "apartment", "other"]),
    # Type of ownership / renting for the housing.
    "housing_status": pl.Enum(
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
    # Whether the household has internet access at home.
    "has_internet": pl.Boolean,
    # Number of cars owned by the household.
    "nb_cars": pl.UInt8,
    # Number of motorcycles (or similar) owned by the household.
    "nb_motorcycles": pl.UInt8,
    # Number of bicycles (standard or electric) owned by the household.
    "nb_bicycles": pl.UInt8,
    # Number of standard bicycles (non-electric) owned by the household.
    "nb_standard_bicycles": pl.UInt8,
    # Number of electric bicycles owned by the household.
    "nb_electric_bicycles": pl.UInt8,
    # Whether the household can park bicycles at home.
    "has_bicycle_parking": pl.Boolean,
    # Number of persons in the household.
    "nb_persons": pl.UInt8,
    # Number of persons in the household whose age is 6 or more.
    "nb_persons_5plus": pl.UInt8,
    # Number of persons in the household whose age is 18 or more.
    "nb_majors": pl.UInt8,
    # Number of persons in the household whose age is 17 or less.
    "nb_minors": pl.UInt8,
}

PARKING_LOCATION_ENUM = pl.Enum(["garage", "street", "parking_lot", "other"])

PARKING_TYPE_ENUM = pl.Enum(["forbidden", "free", "paid", "paid_by_other", "other"])

CAR_SCHEMA = {
    # Identifier of the car.
    "car_id": pl.UInt32,
    # Identifier of the household the car belongs to.
    "household_id": pl.UInt32,
    # Index of the car within the household's cars.
    "car_index": pl.UInt8,
    # Identifier of the car in the original survey data.
    "original_car_id": pl.Struct,
    # Type of the car.
    "type": pl.Enum(
        ["passenger_car", "recreational_vehicle", "utility_vehicle", "license_free_car"]
    ),
    # Fuel type of the car.
    "fuel_type": pl.Enum(
        [
            "thermic:petrol",
            "thermic:diesel",
            "thermic:gas",
            "electric",
            "hybrid:regular",
            "hybrid:regular:petrol",
            "hybrid:regular:diesel",
            "hybrid:plug-in",
            "hybrid:unspecified",
            "other",
        ]
    ),
    # Fuel type of the car in groups.
    "fuel_type_group": pl.Enum(["thermic", "electric", "hybrid", "other"]),
    # Year the car was first used.
    "year": pl.UInt16,
    # Tax horsepower of the car.
    "tax_horsepower": pl.UInt16,
    # Crit'Air vignette of the vehicle.
    "critair": pl.Enum(["E", "1", "2", "3", "4", "5", "N"]),
    # Total mileage of the car in kilometers.
    "total_mileage": pl.UInt32,
    # Lower bound for the total mileage of the car in kilometers.
    "total_mileage_lower_bound": pl.UInt32,
    # Upper bound for the total mileage of the car in kilometers.
    "total_mileage_upper_bound": pl.UInt32,
    # Annual mileage of the car in kilometers.
    "annual_mileage": pl.UInt32,
    # Lower bound for the annual mileage of the car in kilometers.
    "annual_mileage_lower_bound": pl.UInt32,
    # Upper bound for the annual mileage of the car in kilometers.
    "annual_mileage_upper_bound": pl.UInt32,
    # Type of ownership of the car.
    "ownership": pl.Enum(
        [
            "personal",
            "employer:full_availability",
            "employer:limited_availability",
            "leasing",
            "shared",
            "other",
        ]
    ),
    # Type of location used to park the car overnight.
    "parking_location": PARKING_LOCATION_ENUM,
    # Type of parking (paid or free) used to park the car overnight.
    "parking_type": PARKING_TYPE_ENUM,
}

MOTORCYCLE_SCHEMA = {
    # Identifier of the motorcycle.
    "motorcycle_id": pl.UInt32,
    # Identifier of the household the motorcycle belongs to.
    "household_id": pl.UInt32,
    # Index of the motorcycle within the household's motorcycles.
    "motorcycle_index": pl.UInt8,
    # Identifier of the motorcycle in the original survey data.
    "original_motorcycle_id": pl.Struct,
    # Type of the motorcycle.
    "type": pl.Enum(["moped", "scooter", "motorbike", "motorized_tricycle", "other"]),
    # Fuel type used by the motorcycle.
    "fuel_type": pl.Enum(["thermic", "electric", "other"]),
    # Year the motorcycle was first used.
    "year": pl.UInt16,
    # Type of engine for the motorcycle (if thermic).
    "thermic_engine_type": pl.Enum(["two_stroke", "four_stroke"]),
    # Lower bound for the cubic capacity of the motorcycle in cm3 (if thermic).
    "cm3_lower_bound": pl.UInt16,
    # Upper bound for the cubic capacity of the motorcycle in cm3 (if thermic).
    "cm3_upper_bound": pl.UInt16,
    # Lower bound for the energy power of the motorcycle in kw (if electric).
    "kw_lower_bound": pl.UInt16,
    # Upper bound for the energy power of the motorcycle in kw (if electric).
    "kw_upper_bound": pl.UInt16,
    # Annual mileage of the car in kilometers.
    "annual_mileage": pl.UInt32,
    # Lower bound for the annual mileage of the car in kilometers.
    "annual_mileage_lower_bound": pl.UInt32,
    # Upper bound for the annual mileage of the car in kilometers.
    "annual_mileage_upper_bound": pl.UInt32,
    # Type of location used to park the motorcycle overnight.
    "parking_location": PARKING_LOCATION_ENUM,
    # Type of parking (paid or free) used to park the motorcycle overnight.
    "parking_type": PARKING_TYPE_ENUM,
}

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

PERSON_SCHEMA = {
    # Identifier of the person.
    "person_id": pl.UInt32,
    # Identifier of the household the person belongs to.
    "household_id": pl.UInt32,
    # Index of the person within the household's persons.
    "person_index": pl.UInt8,
    # Identifier of the person in the original survey data.
    "original_person_id": pl.Struct,
    # Link of the person relative to the reference person of the household.
    "reference_person_link": pl.Enum(
        [
            "reference_person",
            "spouse",
            "child",
            "roommate_or_tenant",
            "other:relative",
            "other:non_relative",
        ]
    ),
    # Whether the person is living in the household home for most of the year.
    "resident_type": pl.Enum(["permanent_resident", "mostly_weekends", "mostly_weekdays"]),
    # Whether the person is a woman.
    "woman": pl.Boolean,
    # Age of the person.
    "age": pl.UInt8,
    # Age class of the person, in 7 classes.
    "age_class": pl.Enum(["17-", "18-24", "25-34", "35-49", "50-64", "65-74", "75+"]),
    # Code of the age class.
    "age_class_code": pl.UInt8,
    # Education level reached by the person.
    "education_level": pl.Enum(
        [
            "no_studies_or_no_diploma",
            "primary",
            "secondary:no_bac",
            "secondary:bac",
            "higher:at_most_bac+2",
            "higher:at_least_bac+3",
        ]
    ),
    # Education level reached by the person, in detailed categories.
    "detailed_education_level": pl.Enum(
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
    # Professional status of the person.
    "professional_occupation": pl.Enum(["worker", "student", "other"]),
    # Detailed professional status of the person.
    "detailed_professional_occupation": pl.Enum(
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
    # Secondary professional occupation of the person.
    "secondary_professional_occupation": pl.Enum(["work", "education"]),
    # Group of "Professions et Catégories Socioprofessionnelles" the person belongs to.
    "pcs_group": pl.Enum(
        [
            "agriculteurs_exploitants",
            "artisans_commerçants_chefs_d'entreprise",
            "cadres_et_professions_intellectuelles_supérieures",
            "professions_intermédiaires",
            "employés",
            "ouvriers",
            "retraités",
            "autres_personnes_sans_activité_professionnelle",
        ]
    ),
    # Code of the group of "Professions et Catégories Socioprofessionnelles" the person belongs to.
    "pcs_group_code": pl.UInt8,
    # Code of the category of "Professions et Catégories Socioprofessionnelles" the person belongs
    # to (2020 version).
    "pcs_category_code2020": pl.UInt8,
    # Code of the category of "Professions et Catégories Socioprofessionnelles" the person belongs
    # to (2003 version).
    "pcs_category_code2003": pl.UInt8,
    # Whether the person work only at home.
    "work_only_at_home": pl.Boolean,
    # Whether the person has a unique, fixed workplace location.
    "workplace_singularity": pl.Enum(["unique:outside", "unique:home", "variable"]),
    # Longitude of usual workplace.
    "work_lng": pl.Float64,
    # Latitude of usual workplace.
    "work_lat": pl.Float64,
    # Special location of the usual work location of the person.
    "work_special_location": pl.String,
    # Detailed zone of the usual work location of the person.
    "work_detailed_zone": pl.String,
    # Draw zone of the usual work location.
    "work_draw_zone": pl.String,
    # INSEE code of the municipality where the usual work location is.
    "work_insee": pl.String,
    # Name of the municipality where the usual work location is.
    "work_insee_name": pl.String,
    # Département code of the usual work location.
    "work_dep": pl.String,
    # Département name of the usual work location.
    "work_dep_name": pl.String,
    # NUTS 2 code of the usual work location.
    "work_nuts2": pl.String,
    # NUTS 2 name of the usual work location.
    "work_nuts2_name": pl.String,
    # NUTS 1 code of the usual work location.
    "work_nuts1": pl.String,
    # NUTS 1 name of the usual work location.
    "work_nuts1_name": pl.String,
    # Euclidean distance between the person's home location and usual work location.
    "work_commute_euclidean_distance_km": pl.Float64,
    # Whether the person has a vehicle he/she can use to commute to work.
    "has_car_for_work_commute": COMMUTE_CAR_ENUM,
    # Frequency of telework for the person.
    "telework": pl.Enum(["yes:weekly", "yes:monthly", "yes:occasionally", "no"]),
    # Whether the person has access to a car parking spot at work location.
    "work_car_parking": CAR_PARKING_ENUM,
    # Whether the person has access to a bicycle parking spot at work location.
    "work_bicycle_parking": BICYCLE_PARKING_ENUM,
    # Group indicating the current education level for students.
    "student_group": pl.Enum(["primaire", "collège", "lycée", "supérieur"]),
    # Category indicating the detailed current education level for students.
    "student_category": pl.Enum(
        [
            "maternelle",
            "primaire",
            "collège:6e",
            "collège:5e",
            "collège:4e",
            "collège:3e",
            "collège:SEGPA",
            "lycée:seconde",
            "lycée:première",
            "lycée:terminale",
            "lycée:CAP",
            "supérieur:technique",
            "supérieur:prépa1",
            "supérieur:prépa2",
            "supérieur:BAC+1",
            "supérieur:BAC+2",
            "supérieur:BAC+3",
            "supérieur:BAC+4",
            "supérieur:BAC+5",
            "supérieur:BAC+6&+",
        ]
    ),
    # Whether the person study only at home.
    "study_only_at_home": pl.Boolean,
    # Longitude of usual study location.
    "study_lng": pl.Float64,
    # Latitude of usual study location.
    "study_lat": pl.Float64,
    # Special location of the usual study location of the person.
    "study_special_location": pl.String,
    # Detailed zone of the usual study location of the person.
    "study_detailed_zone": pl.String,
    # Draw zone of the usual study location.
    "study_draw_zone": pl.String,
    # INSEE code of the municipality where the usual study location is.
    "study_insee": pl.String,
    # Name of the municipality where the usual study location is.
    "study_insee_name": pl.String,
    # Département code of the usual study location.
    "study_dep": pl.String,
    # Département name of the usual study location.
    "study_dep_name": pl.String,
    # NUTS 2 code of the usual study location.
    "study_nuts2": pl.String,
    # NUTS 2 name of the usual study location.
    "study_nuts2_name": pl.String,
    # NUTS 1 code of the usual study location.
    "study_nuts1": pl.String,
    # NUTS 1 name of the usual study location.
    "study_nuts1_name": pl.String,
    # Euclidean distance between the person's home location and usual study location.
    "study_commute_euclidean_distance_km": pl.Float64,
    # Whether the person has a vehicle he/she can use to commute to study.
    "has_car_for_study_commute": COMMUTE_CAR_ENUM,
    # Whether the person has access to a car parking spot at study location.
    "study_car_parking": CAR_PARKING_ENUM,
    # Whether the person has access to a bicycle parking spot at study location.
    "study_bicycle_parking": BICYCLE_PARKING_ENUM,
    # Whether the person has a driving license.
    "has_driving_license": pl.Enum(["yes", "no", "in_progress"]),
    # Whether the person has a driving license for motorcycles.
    "has_motorcycle_driving_license": pl.Enum(["yes", "no", "in_progress"]),
    # Whether the person had a valid public-transit subscription the day before the interview.
    "has_public_transit_subscription": pl.Boolean,
    # Type of public-transit subscription the person had.
    "public_transit_subscription": pl.Enum(
        [
            "yes:free",
            "yes:paid:with_employer_contribution",
            "yes:paid:without_employer_contribution",
            "yes:paid",
            "yes:unspecified",
            "no",
        ]
    ),
    # Whether the person has a subscription for a car-sharing service.
    "has_car_sharing_subscription": pl.Boolean,
    # Type of car-sharing service subscription the person has.
    "car_sharing_subscription": pl.Enum(
        ["yes:organized", "yes:peer_to_peer", "yes:unspecified", "no"]
    ),
    # Whether the person has a subscription for a bike-sharing service.
    "has_bike_sharing_subscription": pl.Boolean,
    # Whether the person has reported having travel inconveniences.
    "has_travel_inconvenience": pl.Boolean,
    # Whether the person was surveyed for his/her trips of previous day.
    "is_surveyed": pl.Boolean,
    # Whether the person performed at least one trip during the day before the interview.
    "traveled_during_surveyed_day": pl.Enum(["yes", "no", "away"]),
    # Whether the person worked during the day before the interview.
    "worked_during_surveyed_day": pl.Enum(
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
    # Number of trips that this person performed.
    "nb_trips": pl.UInt8,
    # Sample weight of the person among all the persons interviewed.
    "sample_weight_all": pl.Float64,
    # Sample weight of the person among all the persons whose trips were surveyed.
    "sample_weight_surveyed": pl.Float64,
}

PURPOSE_ENUM = pl.Enum(
    [
        "home:main",
        "home:secondary",
        "work:declared",
        "work:telework",
        "work:secondary",
        "work:business_meal",
        "work:other",
        "work:professional_tour",
        "education:childcare",
        "education:declared",
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

MODE_ENUM = pl.Enum(
    [
        # Walking
        "walking",
        # Bicycle
        "bicycle:driver",
        "bicycle:driver:shared",
        "bicycle:driver:traditional",
        "bicycle:driver:traditional:shared",
        "bicycle:driver:electric",
        "bicycle:driver:electric:shared",
        "bicycle:passenger",
        # Motorcycle
        "motorcycle:driver",
        "motorcycle:passenger",
        "motorcycle:driver:moped",
        "motorcycle:passenger:moped",
        "motorcycle:driver:moto",
        "motorcycle:passenger:moto",
        # Car
        "car:driver",
        "car:passenger",
        "taxi",
        "VTC",
        "taxi_or_VTC",
        # Public transit
        "public_transit:urban",
        "public_transit:urban:bus",
        "public_transit:urban:coach",
        "public_transit:urban:tram",
        "public_transit:urban:metro",
        "public_transit:urban:funicular",
        "public_transit:urban:rail",
        "public_transit:urban:TER",
        "public_transit:urban:demand_responsive",
        "public_transit:interurban:coach",
        "public_transit:interurban:TGV",
        "public_transit:interurban:intercités",
        "public_transit:interurban:other_train",
        "public_transit:school",
        # Other
        "reduced_mobility_transport",
        "employer_transport",
        "truck:driver",
        "truck:passenger",
        "water_transport",
        "airplane",
        "wheelchair",
        "personal_transporter:non_motorized",
        "personal_transporter:motorized",
        "personal_transporter:unspecified",
        "other",
    ]
)

MODE_GROUP_ENUM = pl.Enum(
    ["walking", "bicycle", "motorcycle", "car_driver", "car_passenger", "public_transit", "other"]
)

TRIP_SCHEMA = {
    # Identifier of the trip.
    "trip_id": pl.UInt32,
    # Identifier of the person who performed the trip.
    "person_id": pl.UInt32,
    # Identifier of the household in which the person who performed the trip belongs.
    "household_id": pl.UInt32,
    # Index of the trip among the person's trips.
    "trip_index": pl.UInt8,
    # Whether the trip is the first one of the person.
    "first_trip": pl.Boolean,
    # Whether the trip is the last one of the person.
    "last_trip": pl.Boolean,
    # Cumulative number of times that the person started a trip from their main home.
    "home_sequence_index": pl.UInt8,
    # Identifier of the trip in the original survey data.
    "original_trip_id": pl.Struct,
    # Purpose of the activity performed at the trip's origin.
    "origin_purpose": PURPOSE_ENUM,
    # Purpose group of the activity performed at the trip's origin.
    "origin_purpose_group": PURPOSE_GROUP_ENUM,
    # Duration at the activity performed at the trip's origin, in minutes.
    "origin_activity_duration": pl.UInt16,
    # Purpose of the activity performed at the trip's destination.
    "destination_purpose": PURPOSE_ENUM,
    # Purpose group of the activity performed at the trip's destination.
    "destination_purpose_group": PURPOSE_GROUP_ENUM,
    # Duration at the activity performed at the trip's destination, in minutes.
    "destination_activity_duration": pl.UInt16,
    # Purpose of the activity performed at the trip's origin by the person who is escorted.
    "origin_escort_purpose": PURPOSE_ENUM,
    # Purpose group of the activity performed at the trip's origin by the person who is escorted.
    "origin_escort_purpose_group": PURPOSE_GROUP_ENUM,
    # Purpose of the activity performed at the trip's destination by the person who is escorted.
    "destination_escort_purpose": PURPOSE_ENUM,
    # Purpose group of the activity performed at the trip's destination by the person who is
    # escorted.
    "destination_escort_purpose_group": PURPOSE_GROUP_ENUM,
    # Type of shop where the activity at origin was performed.
    "origin_shop_type": SHOP_TYPE_ENUM,
    # Type of shop where the activity at destination was performed.
    "destination_shop_type": SHOP_TYPE_ENUM,
    # Longitude of the trip's origin.
    "origin_lng": pl.Float64,
    # Latitude of the trip's origin.
    "origin_lat": pl.Float64,
    # Special location of the trip's origin.
    "origin_special_location": pl.String,
    # Detailed zone of the trip's origin.
    "origin_detailed_zone": pl.String,
    # Draw zone of the trip's origin.
    "origin_draw_zone": pl.String,
    # INSEE code of the municipality of trip's origin.
    "origin_insee": pl.String,
    # Name of the municipality of trip's origin.
    "origin_insee_name": pl.String,
    # Density category of the origin INSEE municipality.
    "origin_insee_density": pl.UInt8,
    # Category of the origin INSEE municipality within the AAV.
    "origin_insee_aav_type": pl.UInt8,
    # Code of the AAV of the trip's origin.
    "origin_aav": pl.String,
    # Name of the AAV of the trip's origin.
    "origin_aav_name": pl.String,
    # Category of the AAV of the trip's origin.
    "origin_aav_category": pl.String,
    # Département code of the trip's origin.
    "origin_dep": pl.String,
    # Département name of the trip's origin.
    "origin_dep_name": pl.String,
    # NUTS 2 code of the trip's origin.
    "origin_nuts2": pl.String,
    # NUTS 2 name of the trip's origin.
    "origin_nuts2_name": pl.String,
    # NUTS 1 code of the trip's origin.
    "origin_nuts1": pl.String,
    # NUTS 1 name of the trip's origin.
    "origin_nuts1_name": pl.String,
    # Longitude of the trip's destination.
    "destination_lng": pl.Float64,
    # Latitude of the trip's destination.
    "destination_lat": pl.Float64,
    # Special location of the trip's destination.
    "destination_special_location": pl.String,
    # Detailed zone of the trip's destination.
    "destination_detailed_zone": pl.String,
    # Draw zone of the trip's destination.
    "destination_draw_zone": pl.String,
    # INSEE code of the municipality of trip's destination.
    "destination_insee": pl.String,
    # Name of the municipality of trip's destination.
    "destination_insee_name": pl.String,
    # Density category of the destination INSEE municipality.
    "destination_insee_density": pl.UInt8,
    # Category of the destination INSEE municipality within the AAV.
    "destination_insee_aav_type": pl.UInt8,
    # Code of the AAV of the trip's destination.
    "destination_aav": pl.String,
    # Name of the AAV of the trip's destination.
    "destination_aav_name": pl.String,
    # Category of the AAV of the trip's destination.
    "destination_aav_category": pl.String,
    # Département code of the trip's destination.
    "destination_dep": pl.String,
    # Département name of the trip's destination.
    "destination_dep_name": pl.String,
    # NUTS 2 code of the trip's destination.
    "destination_nuts2": pl.String,
    # NUTS 2 name of the trip's destination.
    "destination_nuts2_name": pl.String,
    # NUTS 1 code of the trip's destination.
    "destination_nuts1": pl.String,
    # NUTS 1 name of the trip's destination.
    "destination_nuts1_name": pl.String,
    # Departure time from origin, in number of minutes after midnight.
    "departure_time": pl.UInt16,
    # Arrival time at destination, in number of minutes after midnight.
    "arrival_time": pl.UInt16,
    # Trip travel time, in minutes.
    "travel_time": pl.UInt16,
    # Date at which the trip took place.
    "trip_date": pl.Date,
    # Day of the week when the trip took place.
    "trip_weekday": pl.Enum(
        ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    ),
    # Main mode of transportation used for the trip.
    "main_mode": MODE_ENUM,
    # Mode group of the main mode of transportation used for the trip.
    "main_mode_group": MODE_GROUP_ENUM,
    # Whether the trip involved using two different transportation modes.
    "intermodality": pl.Boolean,
    # Mode of transportation used for the access part of the trips.
    "public_transit_access_mode": MODE_ENUM,
    # Mode group of the transportation mode used for the access part of the trips.
    "public_transit_access_mode_group": MODE_GROUP_ENUM,
    # Mode of transportation used for the egress part of the trips.
    "public_transit_egress_mode": MODE_ENUM,
    # Mode group of the transportation mode used for the egress part of the trips.
    "public_transit_egress_mode_group": MODE_GROUP_ENUM,
    # Euclidean distance between the trip's origin and destination, in kilometers.
    "trip_euclidean_distance_km": pl.Float64,
    # Travel distance of the trip, in kilometers.
    "trip_travel_distance_km": pl.Float64,
    # Whether the INSEE origin equals the INSEE destination.
    "intra_municipality": pl.Boolean,
    # Whether the origin AAV equals the destination AAV.
    "intra_aav": pl.Boolean,
    # Whether the origin département equals the destination département.
    "intra_dep": pl.Boolean,
    # Trip type with respect to the survey's perimiter.
    "trip_perimeter": pl.Enum(["internal", "crossing", "external", "unknown"]),
    # Number of stops for trips representing tours.
    "nb_tour_stops": pl.UInt8,
    # Number of legs in the trip.
    "nb_legs": pl.UInt8,
    # Number of walking legs in the trip.
    "nb_legs_walking": pl.UInt8,
    # Number of bicycle legs in the trip.
    "nb_legs_bicycle": pl.UInt8,
    # Number of motorcycle legs in the trip.
    "nb_legs_motorcycle": pl.UInt8,
    # Number of car_driver legs in the trip.
    "nb_legs_car_driver": pl.UInt8,
    # Number of car_passenger legs in the trip.
    "nb_legs_car_passenger": pl.UInt8,
    # Number of public_transit legs in the trip.
    "nb_legs_public_transit": pl.UInt8,
    # Number of other legs in the trip.
    "nb_legs_other": pl.UInt8,
}

LEG_PARKING_LOCATION_ENUM = pl.Enum(
    [
        "stop_only",
        "garage",
        "street",
        "parking_lot",
        "parking_lot:unsheltered",
        "parking_lot:sheltered",
        "P+R",
        "none",
        "other",
    ]
)

LEG_SCHEMA = {
    # Identifier of the leg.
    "leg_id": pl.UInt32,
    # Identifier of the trip that the leg belongs to.
    "trip_id": pl.UInt32,
    # Identifier of the person that performed the leg.
    "person_id": pl.UInt32,
    # Identifier of the household in which the person who performed the leg belongs.
    "household_id": pl.UInt32,
    # Index of the leg among the trip's legs.
    "leg_index": pl.UInt8,
    # Whether the leg is the first one of the trip.
    "first_leg": pl.Boolean,
    # Whether the leg is the last one of the trip.
    "last_leg": pl.Boolean,
    # Identifier of the leg in the original survey data.
    "original_leg_id": pl.Struct,
    # Mode of transportation used to perform the leg.
    "mode": MODE_ENUM,
    # Mode group of the mode of transportation used.
    "mode_group": MODE_GROUP_ENUM,
    # Name of the public-transit line taken.
    "public_transit_line": pl.String,
    # Longitude of the leg's start point.
    "start_lng": pl.Float64,
    # Latitude of the leg's start point.
    "start_lat": pl.Float64,
    # Special location from which the leg started (after walking).
    "start_special_location": pl.String,
    # Detailed zone from which the leg started (after walking).
    "start_detailed_zone": pl.String,
    # Draw zone from which the leg started (after walking).
    "start_draw_zone": pl.String,
    # INSEE code of the municipality from which the leg started (after walking).
    "start_insee": pl.String,
    # Name of the municipality from which the leg started (after walking).
    "start_insee_name": pl.String,
    # Département code of the leg's start point.
    "start_dep": pl.String,
    # Département name of the leg's start point.
    "start_dep_name": pl.String,
    # NUTS 2 code of the leg's start point.
    "start_nuts2": pl.String,
    # NUTS 2 name of the leg's start point.
    "start_nuts2_name": pl.String,
    # NUTS 1 code of the leg's start point.
    "start_nuts1": pl.String,
    # NUTS 1 name of the leg's start point.
    "start_nuts1_name": pl.String,
    # Longitude of the leg's end point.
    "end_lng": pl.Float64,
    # Latitude of the leg's end point.
    "end_lat": pl.Float64,
    # Special location at which the leg stopped (before walking).
    "end_special_location": pl.String,
    # Detailed zone at which the leg stopped (before walking).
    "end_detailed_zone": pl.String,
    # Draw zone at which the leg stopped (before walking).
    "end_draw_zone": pl.String,
    # INSEE code of the municipality at which the leg stopped (before walking).
    "end_insee": pl.String,
    # Name of the municipality at which the leg stopped (after walking).
    "end_insee_name": pl.String,
    # Département code of the leg's end point.
    "end_dep": pl.String,
    # Département name of the leg's end point.
    "end_dep_name": pl.String,
    # NUTS 2 code of the leg's end point.
    "end_nuts2": pl.String,
    # NUTS 2 name of the leg's end point.
    "end_nuts2_name": pl.String,
    # NUTS 1 code of the leg's end point.
    "end_nuts1": pl.String,
    # NUTS 1 name of the leg's end point.
    "end_nuts1_name": pl.String,
    # Travel time between start and stop points, in minutes.
    "leg_travel_time": pl.UInt16,
    # Euclidean distance between start and stop points, in kilometers.
    "leg_euclidean_distance_km": pl.Float64,
    # Travel distance between start and stop points, in kilometers.
    "leg_travel_distance_km": pl.Float64,
    # Type of car used for the leg.
    "car_type": pl.Enum(["household", "other_household", "rental", "company", "shared", "other"]),
    # Identifier of the car used to perform the leg.
    "car_id": pl.UInt32,
    # Whether the car used was a no-license car.
    "nolicense_car": pl.Boolean,
    # Number of persons that were present in the vehicle used.
    "nb_persons_in_vehicle": pl.UInt8,
    # Number of majors that were present in the vehicle used.
    "nb_majors_in_vehicle": pl.UInt8,
    # Number of minors that were present in the vehicle used.
    "nb_minors_in_vehicle": pl.UInt8,
    # Number of persons from the household that were present in the vehicle.
    "nb_household_members_in_vehicle": pl.UInt8,
    # Number of persons not from the household that were present in the vehicle.
    "nb_non_household_members_in_vehicle": pl.UInt8,
    # Ids of the person that were in the vehicle.
    "in_vehicle_person_ids": pl.List(pl.UInt32),
    # Type of motorcycle used for the leg.
    "motorcycle_type": pl.Enum(
        ["household", "other_household", "rental", "company", "shared", "other"]
    ),
    # Identifier of the motorcycle used to perform the leg.
    "motorcycle_id": pl.UInt32,
    # Location type where the car was parked at the end of the leg.
    "parking_location": LEG_PARKING_LOCATION_ENUM,
    # Type of parking (paid or free) used to park the car.
    "parking_type": PARKING_TYPE_ENUM,
    # Time spent searching for a parking spot.
    "parking_search_time": pl.UInt32,
}

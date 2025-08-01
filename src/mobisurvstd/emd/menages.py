import polars as pl

from mobisurvstd.common.cars import clean as clean_cars
from mobisurvstd.common.households import clean as clean_households
from mobisurvstd.common.motorcycles import clean as clean_motorcycles

SCHEMA = {
    "MP1": pl.UInt8,  # Code fichier = 1
    "IDM1": pl.UInt8,  # Type Enquête
    "IDM2": pl.UInt8,  # Méthode recueil données
    "IDM3": pl.UInt16,  # Année fin enquête
    "IDM4": pl.String,  # Code Insee ville centre
    "ZFM": pl.UInt32,  # zone fine
    "ECH": pl.UInt32,  # Numéro d’échantillon
    "GM1": pl.String,  # Insee Zone fine
    "STM": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine
    "M1": pl.UInt8,  # TYPE D'HABITAT
    "M2": pl.UInt8,  # TYPE D'OCCUPATION
    "M3": pl.UInt8,  # POSSESSION DU TELEPHONE
    "M4": pl.UInt8,  # Annuaire
    "M5": pl.UInt8,  # Disposition d’une connexion internet
    "M6": pl.UInt8,  # Nombre de VP du ménage
    "M7A": pl.UInt8,  # GENRE DU VEHICULE n°1
    "M8A": pl.UInt8,  # TYPE D'ENERGIE DU VEHICULE n°1
    "M9A": pl.UInt16,  # ANNEE DE PREMIERE MISE EN CIRCULATION DU VEHICULE n°1
    "M10A": pl.UInt8,  # PUISSANCE FISCALE DU VEHICULE n°1
    "M11A": pl.UInt8,  # POSSESSION VEHICULE n°1 PAR MENAGE
    "MAA": pl.UInt8,  # CAS DE NON-POSSESSION DU VEHICULE n°1
    "M12A": pl.UInt8,  # LIEU DE STATIONNEMENT LA NUIT DU VEHICULE n°1
    "M13A": pl.UInt8,  # TYPE DE STATIONNEMENT LA NUIT DU VEHICULE n°1
    "M7B": pl.UInt8,
    "M8B": pl.UInt8,
    "M9B": pl.UInt16,
    "M10B": pl.UInt8,
    "M11B": pl.UInt8,
    "MBB": pl.UInt8,
    "M12B": pl.UInt8,
    "M13B": pl.UInt8,
    "M7C": pl.UInt8,
    "M8C": pl.UInt8,
    "M9C": pl.UInt16,
    "M10C": pl.UInt8,
    "M11C": pl.UInt8,
    "MCC": pl.UInt8,
    "M12C": pl.UInt8,
    "M13C": pl.UInt8,
    "M7D": pl.UInt8,
    "M8D": pl.UInt8,
    "M9D": pl.UInt16,
    "M10D": pl.UInt8,
    "M11D": pl.UInt8,
    "MDD": pl.UInt8,
    "M12D": pl.UInt8,
    "M13D": pl.UInt8,
    "M14": pl.UInt8,  # Nombre de DRM du ménage
    "M15A": pl.UInt8,  # GENRE DU DEUX ROUES MOTORISES n°1
    "M16A": pl.UInt8,  # CYLINDREE DU DEUX ROUES MOTORISES n°1
    "M17A": pl.UInt8,  # TYPE DE MOTEUR THERMIQUE
    "M18A": pl.UInt16,  # ANNEE DE MISE EN CIRCULATION DU DRM n°1
    "M19A": pl.UInt8,  # LIEU DE STATIONNEMENT LA NUIT DU DRM n°1
    "M20A": pl.UInt8,  # TYPE DE STATIONNEMENT LA NUIT DU DRM n°1
    "M15B": pl.UInt8,
    "M16B": pl.UInt8,
    "M17B": pl.UInt8,
    "M18B": pl.UInt16,
    "M19B": pl.UInt8,
    "M20B": pl.UInt8,
    "M15C": pl.UInt8,
    "M16C": pl.UInt8,
    "M17C": pl.UInt8,
    "M18C": pl.UInt16,
    "M19C": pl.UInt8,
    "M20C": pl.UInt8,
    "M15D": pl.UInt8,
    "M16D": pl.UInt8,
    "M17D": pl.UInt8,
    "M18D": pl.UInt16,
    "M19D": pl.UInt8,
    "M20D": pl.UInt8,
    "M21": pl.UInt8,  # VELOS A DISPOSITION
    "M22": pl.UInt8,  # VELOS ELECTRIQUES
    "M23": pl.UInt8,  # DISPOSITION D'UN LIEU DE STATIONNEMENT VELO AU DOMICILE
    "COE0": pl.Float64,  # COEFFICIENT DE REDRESSEMENT MENAGE
}

SURVEY_METHOD_MAP = {
    1: "face_to_face",
    2: "phone",
}

HOUSING_TYPE_MAP = {
    1: "house",  # Individuel isolé
    2: "house",  # Individuel accolé
    3: "apartment",  # Petit collectif (R+1 à R+3)
    4: "apartment",  # Grand collectif (R+4 et plus)
    5: "other",  # Autres
}

HOUSING_STATUS_MAP = {
    1: "owner:unspecified",  # Propriétaire ou accédant à la propriété
    2: "tenant:public_housing",  # Locataire HLM
    3: "tenant:private",  # Autre locataire
    4: "rent_free",  # Logé gratuitement
    5: "university_resident",  # Locataire en résidence universitaire
    6: "other",  # Autre Exclusif
    7: "other",  # Autre Non précisé
    8: "tenant:unspecified",  # Locataire sans précision
    9: None,
}

CAR_TYPE_MAP = {
    1: "passenger_car",  # Véhicule de tourisme
    2: "recreational_vehicle",  # Camping-car
    3: "utility_vehicle",  # Véhicule utilitaire de 800kg à 1000kg
    4: "license_free_car",  # Voiture sans permis
}

CAR_FUEL_TYPE_MAP = {
    1: "thermic:petrol",  # Sans plomb
    2: "thermic:petrol",  # Super
    3: "thermic:diesel",  # Diesel
    4: "thermic:gas",  # Gaz
    5: "electric",  # Électrique
    6: "hybrid:unspecified",  # Hybride
    7: "other",  # Autre
    9: None,  # NR-Refus
}

CAR_FUEL_TYPE_GROUP_MAP = {
    1: "thermic",  # Sans plomb
    2: "thermic",  # Super
    3: "thermic",  # Diesel
    4: "thermic",  # Gaz
    5: "electric",  # Électrique
    6: "hybrid",  # Hybride
    7: "other",  # Autre
    9: None,  # NR-Refus
}

# Map for variable M11A + MAA.
CAR_OWNERSHIP_MAP = {
    1: "personal",  # Possession véhicule par ménage
    2: None,  # This should not be possible but it occurs for Strasbourg 2009.
    3: "employer:full_availability",  # Possédé par l'employeur mais à disposition totale d'une personne
    4: "employer:limited_availability",  # Possédé par l'employeur mais à disposition limitée d'une personne
    5: "other",  # Autre
    9: None,  # NR-Refus
}

PARKING_LOCATION_MAP = {
    1: "garage",  # Dans un garage, box, autre emplacement réservé
    2: "street",  # Dans la rue
    3: "parking_lot",  # Dans un parc à ciel ouvert (ou place publique)
    4: "parking_lot",  # Dans un parc couvert accessible au public
    5: "other",  # Autre (egt)
}

PARKING_TYPE_MAP = {
    1: "forbidden",  # Interdit
    2: "free",  # Gratuit
    3: "paid",  # Payant à votre charge
    4: "paid_by_other",  # Payant à la charge de quelqu'un d'autre
    5: "other",  # Autre (egt)
}

MOTORCYCLE_TYPE_MAP = {
    1: "moped",  # Cyclomoteur
    2: "scooter",  # Scooter
    3: "motorbike",  # Moto
    4: "motorized_tricycle",  # 3-roues motorisé
}

MOTORCYCLE_FUEL_TYPE_MAP = {
    1: "thermic",
    2: "thermic",
    3: "thermic",
    4: "thermic",
    5: "thermic",
    6: "electric",
    7: "electric",
    8: "electric",
    9: "thermic",
    90: "other",
}

MOTORCYCLE_SIZE_LOWERBOUND_MAP = {
    1: 0,
    2: 50,
    3: 125,
    4: 250,
    5: 750,
    9: 125,
}

MOTORCYCLE_SIZE_UPPERBOUND_MAP = {
    1: 50,
    2: 125,
    3: 250,
    4: 750,
}

MOTORCYCLE_KW_LOWERBOUND_MAP = {
    6: 0,
    7: 4,
    8: 11,
}

MOTORCYCLE_KW_UPPERBOUND_MAP = {
    6: 4,
    7: 11,
}

MOTORCYCLE_THERMIC_ENGINE_TYPE_MAP = {
    1: "two_stroke",
    2: "four_stroke",
}


def scan_households(source: str | bytes):
    lf = pl.scan_csv(source, separator=";", schema_overrides=SCHEMA, null_values=["a"])
    return lf


def standardize_households(
    source: str | bytes,
    special_locations_coords: pl.DataFrame | None,
    detailed_zones_coords: pl.DataFrame | None,
):
    lf = scan_households(source)
    lf = lf.rename(
        {
            "ZFM": "home_detailed_zone",
            "GM1": "home_insee",
            "M6": "nb_cars",
            "M14": "nb_motorcycles",
            "M21": "nb_bicycles",
            "M22": "nb_electric_bicycles",
            "COE0": "sample_weight",
        }
    )
    lf = lf.with_columns(
        original_household_id=pl.struct("ECH", "STM"),
        home_draw_zone="STM",
        survey_method=pl.col("IDM2").replace_strict(SURVEY_METHOD_MAP),
        housing_type=pl.col("M1").replace_strict(HOUSING_TYPE_MAP),
        housing_status=pl.col("M2").replace_strict(HOUSING_STATUS_MAP),
        has_internet=pl.col("M5") == 1,
        has_bicycle_parking=pl.col("M23") == 1,
    )
    lf = clean_households(
        lf, special_locations=special_locations_coords, detailed_zones=detailed_zones_coords
    )
    return lf


def standardize_cars(source: str | bytes, households: pl.LazyFrame):
    lf = scan_households(source)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("ECH", "STM")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = pl.concat(
        (
            lf.select(
                "household_id",
                original_car_id=pl.struct("ECH", "STM", index=pl.lit(a, dtype=pl.String)),
                car_index=pl.lit(i + 1, dtype=pl.UInt8),
                type=pl.col(f"M7{a}").replace_strict(CAR_TYPE_MAP),
                fuel_type=pl.col(f"M8{a}").replace_strict(CAR_FUEL_TYPE_MAP),
                fuel_type_group=pl.col(f"M8{a}").replace_strict(CAR_FUEL_TYPE_GROUP_MAP),
                # Value 9999 seems to be used when year is unknown.
                year=pl.col(f"M9{a}").replace(9999, None),
                tax_horsepower=f"M10{a}",
                v=pl.col(f"M11{a}") + pl.col(f"M{a}{a}"),
                ownership=(pl.col(f"M11{a}") + pl.col(f"M{a}{a}")).replace_strict(
                    CAR_OWNERSHIP_MAP
                ),
                parking_location=pl.col(f"M12{a}").replace_strict(PARKING_LOCATION_MAP),
                parking_type=pl.col(f"M13{a}").replace_strict(PARKING_TYPE_MAP),
            )
            for i, a in enumerate(("A", "B", "C", "D"))
        ),
        how="vertical",
    )
    # Drop the lines with empty car characteristics (there are always 4 cars per
    # households even when the household has less than 4 cars).
    lf = lf.filter(
        pl.any_horizontal(
            pl.all().exclude("household_id", "original_car_id", "car_index").is_not_null()
        )
    )
    lf = clean_cars(lf)
    return lf


def standardize_motorcycles(source: str | bytes, households: pl.LazyFrame):
    lf = scan_households(source)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("ECH", "STM")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = pl.concat(
        (
            lf.select(
                "household_id",
                original_motorcycle_id=pl.struct("ECH", "STM", index=pl.lit(a, dtype=pl.String)),
                motorcycle_index=pl.lit(i + 1, dtype=pl.UInt8),
                type=pl.col(f"M15{a}").replace_strict(MOTORCYCLE_TYPE_MAP),
                fuel_type=pl.col(f"M16{a}").replace_strict(MOTORCYCLE_FUEL_TYPE_MAP),
                # Value 9999 seems to be used when year is unknown.
                year=pl.col(f"M18{a}").replace(9999, None),
                cm3_lower_bound=pl.col(f"M16{a}").replace_strict(
                    MOTORCYCLE_SIZE_LOWERBOUND_MAP, default=None
                ),
                cm3_upper_bound=pl.col(f"M16{a}").replace_strict(
                    MOTORCYCLE_SIZE_UPPERBOUND_MAP, default=None
                ),
                kw_lower_bound=pl.col(f"M16{a}").replace_strict(
                    MOTORCYCLE_KW_LOWERBOUND_MAP, default=None
                ),
                kw_upper_bound=pl.col(f"M16{a}").replace_strict(
                    MOTORCYCLE_KW_UPPERBOUND_MAP, default=None
                ),
                thermic_engine_type=pl.col(f"M17{a}").replace_strict(
                    MOTORCYCLE_THERMIC_ENGINE_TYPE_MAP, default=None
                ),
                parking_location=pl.col(f"M19{a}").replace_strict(PARKING_LOCATION_MAP),
                # `default=None` is required because in some surveys (Rennes 2018), other values are
                # used without being documented
                parking_type=pl.col(f"M20{a}").replace_strict(PARKING_TYPE_MAP, default=None),
            )
            for i, a in enumerate(("A", "B", "C", "D"))
        ),
        how="vertical",
    )
    lf = lf.filter(
        pl.any_horizontal(
            pl.all()
            .exclude("household_id", "original_motorcycle_id", "motorcycle_index")
            .is_not_null()
        )
    )
    lf = clean_motorcycles(lf)
    return lf


def main_survey_insee(source: str | bytes):
    lf = scan_households(source)
    return lf.select("IDM4").first().collect().item()

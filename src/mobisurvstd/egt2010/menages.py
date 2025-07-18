from datetime import timedelta

import polars as pl

from mobisurvstd.common.cars import clean as clean_cars
from mobisurvstd.common.households import clean as clean_households
from mobisurvstd.common.motorcycles import clean as clean_motorcycles

SCHEMA = {
    "SEM": pl.UInt32,  # Semaine d'enquête
    "NQUEST": pl.UInt32,  # Identifiant du ménage
    "POIDSM": pl.Float64,  # Poids du ménage
    "RESCOUR": pl.UInt8,  # Couronne de résidence
    "RESDEP": pl.String,  # Département de résidence
    "RESSECT": pl.String,  # Secteur de résidence
    "RESCOMM": pl.String,  # Commune de résidence
    "RESC": pl.String,  # Carreau de résidence
    "JDEP": pl.UInt8,  # Jour (semaine) des déplacements
    "MNP": pl.UInt8,  # Nombre de personnes du ménage
    "MNP5": pl.UInt8,  # Nombre de personnes du ménage de 5 ans et plus
    "MNPMOB": pl.UInt8,  # Nombre de personnes du ménage qui se sont déplacées la veille
    "MNPACT": pl.UInt8,  # Nombre d'actifs dans le ménage
    "TYPELOG": pl.UInt8,  # Type de logement
    "OCCUPLOG": pl.UInt8,  # Occupation du logement
    "LOY_HC": pl.UInt16,  # Montant du loyer hors charge
    "LOY_NSP": pl.UInt8,  # Ne sait pas
    "ALLOC": pl.UInt8,  # Allocations
    "CHG": pl.UInt16,  # Montant des charges mensuelles
    "CHG_NSP": pl.UInt8,  # Ne sait pas
    "LOY_PARK": pl.UInt16,  # Montant des loyers de parking
    "PARK": pl.UInt8,  # Loyers de parking
    "NBPI": pl.UInt8,  # Nombre de pièces
    "SURF": pl.UInt16,  # Superficie totale du logement
    "TELFIX": pl.UInt8,  # Téléphone fixe
    "INTERNET": pl.UInt8,  # Internet
    "ANEM": pl.UInt8,  # Nombre d'années passées dans ce logement
    "MNEM": pl.UInt8,  # Nombre de mois passés dans ce logement
    "CHOIXLOG1": pl.UInt8,  # Raison 1 de choix du logement
    "CHOIXLOG2": pl.UInt8,  # Raison 2 de choix du logement
    "CHOIXLOG3": pl.UInt8,  # Raison 3 de choix du logement
    "ACOMM": pl.String,  # Commune de résidence précédente
    "NB_VELO": pl.UInt8,  # Nombre de vélos (en état de marche)
    "NB_VAE": pl.UInt8,  # Nombre de VAE
    "PARKVELO": pl.UInt8,  # Parking à vélo
    "NB_VD": pl.UInt8,  # Nombre de voitures à disposition
    "TYPEV1": pl.UInt8,  # Type de véhicule du véhicule 1
    "ENERGV1": pl.UInt8,  # Energie du véhicule
    "APMCV1": pl.UInt16,  # Année de première mise en circulation
    "PUISSV1": pl.UInt8,  # Puissance fiscale en chevaux
    "ANKMV1": pl.UInt32,  # Kilométrage moyen annuel
    "CPTKMV1": pl.UInt32,  # Kilométrage au compteur
    "POSSV1": pl.UInt8,  # Possession du véhicule 1
    "STATV1": pl.UInt8,  # Stationnement la nuit
    "TYPEV2": pl.UInt8,  # Idem voiture numéro 2
    "ENERGV2": pl.UInt8,
    "APMCV2": pl.UInt16,
    "PUISSV2": pl.UInt8,
    "ANKMV2": pl.UInt32,
    "CPTKMV2": pl.UInt32,
    "POSSV2": pl.UInt8,
    "STATV2": pl.UInt8,
    "TYPEV3": pl.UInt8,  # Idem voiture numéro 3
    "ENERGV3": pl.UInt8,
    "APMCV3": pl.UInt16,
    "PUISSV3": pl.UInt8,
    "ANKMV3": pl.UInt32,
    "CPTKMV3": pl.UInt32,
    "POSSV3": pl.UInt8,
    "STATV3": pl.UInt8,
    "TYPEV4": pl.UInt8,  # Idem voiture numéro 4
    "ENERGV4": pl.UInt8,
    "APMCV4": pl.UInt16,
    "PUISSV4": pl.UInt8,
    "ANKMV4": pl.UInt32,
    "CPTKMV4": pl.UInt32,
    "POSSV4": pl.UInt8,
    "STATV4": pl.UInt8,
    "NB_2RM": pl.UInt8,  # Nombre de 2RM, 3RM à disposition
    "NB_VEH": pl.UInt8,  # Nombre de véhicules motorisés à disposition
    "TYPERM1": pl.UInt8,  # Type du 2RM/3RM 1
    "MOTRM1": pl.UInt8,  # Type de moteur
    "ENERM1": pl.UInt8,  # Type d'énergie
    "APMCRM1": pl.UInt16,  # Année de première mise en circulation
    "CYLRM1": pl.UInt8,  # Cylindrée
    "ANKMRM1": pl.UInt32,  # Kilométrage moyen annuel
    "STATRM1": pl.UInt8,  # Stationnement la nuit
    "TYPERM2": pl.UInt8,
    "MOTRM2": pl.UInt8,
    "ENERM2": pl.UInt8,
    "APMCRM2": pl.UInt16,  # Idem 2RM / 3RM numéro 2
    "CYLRM2": pl.UInt8,
    "ANKMRM2": pl.UInt32,
    "STATRM2": pl.UInt8,
    "TYPERM3": pl.UInt8,
    "MOTRM3": pl.UInt8,
    "ENERM3": pl.UInt8,
    "APMCRM3": pl.UInt16,  # Idem 2RM / 3RM numéro 3
    "CYLRM3": pl.UInt8,
    "ANKMRM3": pl.UInt32,
    "STATRM3": pl.UInt8,
    "TYPERM4": pl.UInt8,
    "MOTRM4": pl.UInt8,
    "ENERM4": pl.UInt8,
    "APMCRM4": pl.UInt16,  # Idem 2RM / 3RM numéro 4
    "CYLRM4": pl.UInt8,
    "ANKMRM4": pl.UInt32,
    "STATRM4": pl.UInt8,
    "ANCOUT": pl.UInt8,  # Coût annuel estimé pour la flotte de véhicules (entretien, réparation)
    "ASSCOUT": pl.UInt8,  # Coût annuel de l'assurance
    "REVENU": pl.UInt8,  # Classe de revenut net mensuel
}

HOUSING_TYPE_MAP = {
    1: "house",  # Individuel sans jardin
    2: "house",  # Individuel avec jardin <=300m²
    3: "house",  # Individuel avec jardin >300m²
    4: "apartment",  # Collectif moins de 50 logements
    5: "apartment",  # Collectif 50 à 100 logements
    6: "apartment",  # collectif plus de 100 logements
    7: "other",  # Autre
}

HOUSING_STATUS_MAP = {
    1: "owner:fully_repaid",  # Propriétaire
    2: "owner:ongoing_loan",  # Accédant à la propriété
    3: "tenant:public_housing",  # Locataire d'un organisme HLM
    4: "tenant:private",  # Locataire du parc privé en meublé
    5: "tenant:private",  # Locataire du parc privé sous régime loi 48
    6: "tenant:private",  # Autre type de locataire du parc privé
    7: "rent_free",  # Logé gratuitement par l'employeur / logement de fonction
    8: "rent_free",  # Logé gratuitement (sans loyer, avec charges éventuelles)
    9: "other",  # Autres
}

REVENU_LB_MAP = {
    1: 0,  # Moins de 800€
    2: 800,  # De 800 à 1200€
    3: 1200,  # De 1200 à 1600€
    4: 1600,  # De 1600 à 2000€
    5: 2000,  # De 2000 à 2400€
    6: 2400,  # De 2400 à 3000€
    7: 3000,  # De 3000 à 3500€
    8: 3500,  # De 3500 à 4500€
    9: 4500,  # De 4500 à 5500€
    10: 5500,  # 5500€ et plus
    11: None,  # Refus
    12: None,  # Ne sait pas
}

REVENU_UB_MAP = {
    1: 800,  # Moins de 800€
    2: 1200,  # De 800 à 1200€
    3: 1600,  # De 1200 à 1600€
    4: 2000,  # De 1600 à 2000€
    5: 2400,  # De 2000 à 2400€
    6: 3000,  # De 2400 à 3000€
    7: 3500,  # De 3000 à 3500€
    8: 4500,  # De 3500 à 4500€
    9: 5500,  # De 4500 à 5500€
    10: None,  # 5500€ et plus
    11: None,  # Refus
    12: None,  # Ne sait pas
}

CAR_TYPE_MAP = {
    1: "passenger_car",  # Véhicule de tourisme ou utilitaire (<800 kg de charge utile)
    2: "utility_vehicle",  # Véhicule utilitaire (800-1000 kg de charge utile)
    3: "utility_vehicle",  # Véhicule utilitaire (+1000 kg de charge utile, >3500 kg PTAC)
    4: "recreational_vehicle",  # Camping car
    5: "license_free_car",  # Voiture sans permis
}

CAR_FUEL_TYPE_MAP = {
    1: "thermic:petrol",  # Sans plomb
    2: "thermic:petrol",  # Super
    3: "thermic:diesel",  # Diesel
    # NOTE. In 2010, plug-in hybrid cars were not really available and most hybrid cars were petrol.
    4: "hybrid:regular:petrol",  # Hybride
    5: "electric",  # Électrique
    6: "thermic:gas",  # Autre (GPL)
}

CAR_OWNERSHIP_MAP = {
    1: "personal",  # Possédé par le ménage
    2: "employer:full_availability",  # Possédé par le ménage (aide employeur)
    3: "employer:limited_availability",  # Possédé par l'employeur
    4: "other",  # Autres (location,prêt, leasing)
}

PARKING_LOCATION_MAP = {
    "1": "street",  # Voie publique, payant à durée limitée
    "2": "street",  # Voie publique, payant tarif résidentiel
    "3": "street",  # Voie publique, gratuit autorisé
    "4": "street",  # Voie publique, gratuit non autorisé
    "5": "garage",  # Emplacement privé, gratuit
    "6": "garage",  # Emplacement privé, propriétaire
    "7": "garage",  # Emplacement privé, locataire
    "8": "parking_lot",  # Stationnement ouvert au public, gratuit
    "9": "parking_lot",  # Stationnement ouvert au public, propriétaire
    "10": "parking_lot",  # Stationnement ouvert au public, locataire
    "11": "parking_lot",  # Stationnement ouvert au public, payant à l'horaire
    "12": "parking_lot",  # Stationnement ouvert au public, autres
}

PARKING_TYPE_MAP = {
    "1": "paid",  # Voie publique, payant à durée limitée
    "2": "paid",  # Voie publique, payant tarif résidentiel
    "3": "free",  # Voie publique, gratuit autorisé
    "4": "forbidden",  # Voie publique, gratuit non autorisé
    "5": "free",  # Emplacement privé, gratuit
    "6": "free",  # Emplacement privé, propriétaire
    "7": "paid",  # Emplacement privé, locataire
    "8": "free",  # Stationnement ouvert au public, gratuit
    "9": "free",  # Stationnement ouvert au public, propriétaire
    "10": "paid",  # Stationnement ouvert au public, locataire
    "11": "paid",  # Stationnement ouvert au public, payant à l'horaire
    "12": "other",  # Stationnement ouvert au public, autres
}

MOTORCYCLE_TYPE_MAP = {
    1: "motorbike",  # Moto
    2: "scooter",  # Scooter
    3: "other",  # Autre 2RM
    4: "motorized_tricycle",  # 3 roues motorisé
}

MOTORCYCLE_FUEL_TYPE_MAP = {
    1: "electric",  # Electrique
    2: "thermic",  # Essence
}

MOTORCYCLE_THERMIC_ENGINE_TYPE_MAP = {
    2: "two_stroke",  # Deux temps
    4: "four_stroke",  # Quatre temps
}

MOTORCYCLE_CM3_LB_MAP = {
    "1": 0,  # inférieur à 50 cm3
    "2": 50,  # 50-125 cm3
    "3": 125,  # Supérieur à 125 cm3
}

MOTORCYCLE_CM3_UB_MAP = {
    "1": 50,  # inférieur à 50 cm3
    "2": 125,  # 50-125 cm3
    "3": None,  # Supérieur à 125 cm3
}


def scan_households(filename: str):
    lf = pl.scan_csv(
        filename,
        separator=";",
        schema_overrides=SCHEMA,
    )
    return lf


def standardize_households(filename: str):
    lf = scan_households(filename)
    lf = lf.rename(
        {
            "POIDSM": "sample_weight",
            "RESC": "home_detailed_zone",
            "RESSECT": "home_draw_zone",
            "RESCOMM": "home_insee",
            "NB_VD": "nb_cars",
            "NB_2RM": "nb_motorcycles",
            "NB_VELO": "nb_bicycles",
            "NB_VAE": "nb_electric_bicycles",
            "MNP": "nb_persons",
            "MNP5": "nb_persons_5plus",
        }
    )
    lf = lf.with_columns(
        original_household_id=pl.struct("NQUEST"),
        survey_method=pl.lit("face_to_face"),
        income_lower_bound=pl.col("REVENU").replace_strict(REVENU_LB_MAP),
        income_upper_bound=pl.col("REVENU").replace_strict(REVENU_UB_MAP),
        housing_type=pl.col("TYPELOG").replace_strict(HOUSING_TYPE_MAP),
        housing_status=pl.col("OCCUPLOG").replace_strict(HOUSING_STATUS_MAP),
        has_internet=pl.col("INTERNET") == 1,
        has_bicycle_parking=pl.col("PARKVELO") == 1,
        year=pl.col("SEM") // 100,
        # `-1` is needed here because `.str.to_date` assumes that week 1 starts with the first
        # Monday of the year. In contrast, EGT2010 use 1 for the actual first week of the year.
        week_number=(pl.col("SEM") % 100).cast(pl.String).str.pad_start(2, "0"),
    )
    lf = lf.with_columns(
        # Read interview date from year, week number, and JDEP (weekday: 1 for monday, 2 for
        # tuesday, etc.).
        # The interview date is 1 day after that date.
        interview_date=pl.concat_str("year", "week_number", "JDEP").str.to_date("%G%V%w")
        + timedelta(days=1),
    )
    lf = clean_households(lf)
    return lf


def standardize_cars(filename: str, households: pl.LazyFrame):
    lf = scan_households(filename)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("NQUEST")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = pl.concat(
        (
            # We use `select` instead of `with_columns` to simplify the `filter` that is used below.
            lf.select(
                "household_id",
                year=f"APMCV{i}",
                tax_horsepower=f"PUISSV{i}",
                total_mileage=f"CPTKMV{i}",
                annual_mileage=f"ANKMV{i}",
                original_car_id=pl.struct("NQUEST", index=pl.lit(i, dtype=pl.UInt8)),
                car_index=pl.lit(i),
                type=pl.col(f"TYPEV{i}").replace_strict(CAR_TYPE_MAP),
                fuel_type=pl.col(f"ENERGV{i}").replace_strict(CAR_FUEL_TYPE_MAP),
                ownership=pl.col(f"POSSV{i}").replace_strict(CAR_OWNERSHIP_MAP),
                parking_location=pl.col(f"STATV{i}").replace_strict(PARKING_LOCATION_MAP),
                parking_type=pl.col(f"STATV{i}").replace_strict(PARKING_TYPE_MAP),
            )
            for i in range(1, 5)
        ),
        how="vertical",
    )
    # Drop the lines with empty car characteristics (there are always 4 cars per
    # households even when the household has less than 4 cars).
    lf = lf.filter(
        pl.any_horizontal(pl.exclude("household_id", "car_index", "original_car_id").is_not_null())
    )
    lf = clean_cars(lf)
    return lf


def standardize_motorcycles(filename: str, households: pl.LazyFrame):
    lf = scan_households(filename)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("NQUEST")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = pl.concat(
        (
            lf.select(
                "household_id",
                year=f"APMCRM{i}",
                annual_mileage=f"ANKMRM{i}",
                original_motorcycle_id=pl.struct("NQUEST", index=pl.lit(i, dtype=pl.UInt8)),
                motorcycle_index=pl.lit(i),
                type=pl.col(f"TYPERM{i}").replace_strict(MOTORCYCLE_TYPE_MAP),
                fuel_type=pl.col(f"ENERM{i}").replace_strict(MOTORCYCLE_FUEL_TYPE_MAP),
                thermic_engine_type=pl.col(f"MOTRM{i}").replace_strict(
                    MOTORCYCLE_THERMIC_ENGINE_TYPE_MAP
                ),
                cm3_lower_bound=pl.col(f"CYLRM{i}").replace_strict(MOTORCYCLE_CM3_LB_MAP),
                cm3_upper_bound=pl.col(f"CYLRM{i}").replace_strict(MOTORCYCLE_CM3_UB_MAP),
                parking_location=pl.col(f"STATRM{i}").replace_strict(PARKING_LOCATION_MAP),
                parking_type=pl.col(f"STATRM{i}").replace_strict(PARKING_TYPE_MAP),
            )
            for i in range(1, 5)
        ),
        how="vertical",
    )
    # Drop the lines with empty motorcycle characteristics (there are always 4 motorcycles per
    # households even when the household has less than 4 motorcycles).
    lf = lf.filter(
        pl.any_horizontal(
            pl.exclude("household_id", "motorcycle_index", "original_motorcycle_id").is_not_null()
        )
    )
    lf = clean_motorcycles(lf)
    return lf

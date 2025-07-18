import polars as pl

from mobisurvstd.common.cars import clean

SCHEMA = {
    "IDCEREMA": pl.String,  # Identifiant du ménage
    "TYPE_QUEST": pl.String,  # Type de questionnaire
    "NVP": pl.UInt8,  # Numéro de la voiture parmi ceux du ménage
    "MARQ": pl.String,  # Marque
    "MDL": pl.String,  # Modèle
    "ENERG": pl.UInt8,  # Motorisation du véhicule
    "ENERG_txt": pl.String,  # Motorisation du véhicule
    "PUISS": pl.UInt8,  # Puissance fiscale en chevaux
    "POSS": pl.UInt8,  # Possession du véhicule
    "POSS_txt": pl.String,  # Possession du véhicule
    "APMC": pl.UInt16,  # Année de première mise en circulation
    "ANKM": pl.UInt8,  # Kilomètres annuels
    "STAT": pl.UInt8,  # Stationnement au domicile
    "STAT_txt": pl.String,  # Stationnement au domicile
    "STAT_G": pl.UInt8,  # Le stationnement est-il payant (Garage ou stationnement sur la voie publique et payant en journée (STAT = 2 et STAT_VT = 31 ou 32) ou si parking public ou centre commercial (STAT = 3 ou 4) ou Autre) ?
    "STAT_GT": pl.Float64,  # Tarif garage
    "STAT_VT": pl.UInt8,  # Type de stationnement sur voirie
}

FUEL_TYPE_MAP = {
    1: "thermic:diesel",  # Diesel (Gazole)
    2: "thermic:petrol",  # Essence
    3: "hybrid:regular:petrol",  # Hybride non rechargeable essence
    4: "hybrid:regular:diesel",  # Hybride non rechargeable diesel
    5: "hybrid:plug-in",  # Hybride rechargeable
    6: "electric",  # 100% électrique
    7: "thermic:gas",  # Gaz (GPL, GNV,…)
    9: "other",  # Autre
}

MILEAGE_LB_MAP = {
    1: 0,  # 5 000 km ou moins
    2: 5001,  # 5 001 km à 10 000 km
    3: 10001,  # 10 0001 km à 15 000 km
    4: 15001,  # 15 001 km à 20 000 km
    5: 20000,  # Plus de 20 000 km
}

MILEAGE_UB_MAP = {
    1: 5000,  # 5 000 km ou moins
    2: 10000,  # 5 001 km à 10 000 km
    3: 15000,  # 10 0001 km à 15 000 km
    4: 20000,  # 15 001 km à 20 000 km
    5: None,  # Plus de 20 000 km
}

OWNERSHIP_MAP = {
    11: "personal",  # Acheté comptant ou à crédit (neuf ou occasion)
    12: "leasing",  # En location avec option d'achat (LOA)
    13: "leasing",  # En location longue durée (LLD)
    20: "shared",  # Véhicule partagé avec d'autres ménages
    31: "employer:full_availability",  # Voiture de fonction
    32: "employer:limited_availability",  # Voiture de service
    90: "other",  # Autre
}

PARKING_LOCATION_MAP = {
    1: "garage",  # Dans un garage, dans un box ou un autre emplacement réservé
    2: "street",  # Sur la voie publique
    3: "parking_lot",  # Dans un parking public
    4: "parking_lot",  # Dans le parking d'un centre commercial ou dans le parking de son entreprise
    9: "other",  # Autre
}

# Parking type is read from column STAT_G * 100 + STAT_VT (with nulls replaced by 0).
PARKING_TYPE_MAP = {
    0: None,  # Both nulls.
    10: "forbidden",  # Stationnement voirie non autorisé
    20: "free",  # Stationnement voirie gratuit toute la journée
    31: "paid",  # Stationnement voirie payant au tarif résidentiel
    32: "paid",  # Stationnement voirie payant à un autre tarif
    100: "paid",  # Stationnement payant (hors voirie)
    131: "paid",  # Stationnement voirie payant au tarif résidentiel
    132: "paid",  # Stationnement voirie payant à un autre tarif
    200: "free",  # Propriétaire de l'emplacement
}


def scan_cars(filename: str):
    lf = pl.scan_csv(
        filename, separator=";", encoding="utf8-lossy", schema_overrides=SCHEMA, null_values=["-1"]
    )
    return lf


def standardize_cars(filename: str, households: pl.LazyFrame):
    lf = scan_cars(filename)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("IDCEREMA")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename({"PUISS": "tax_horsepower"})
    lf = lf.with_columns(
        original_car_id=pl.struct("IDCEREMA", "NVP"),
        fuel_type=pl.col("ENERG").replace_strict(FUEL_TYPE_MAP),
        # 1900 is used as undetermined year.
        year=pl.col("APMC").replace([1900], None),
        annual_mileage_lower_bound=pl.col("ANKM").replace_strict(MILEAGE_LB_MAP),
        annual_mileage_upper_bound=pl.col("ANKM").replace_strict(MILEAGE_UB_MAP),
        ownership=pl.col("POSS").replace_strict(OWNERSHIP_MAP),
        parking_location=pl.col("STAT").replace_strict(PARKING_LOCATION_MAP),
        parking_type=(
            pl.col("STAT_G").fill_null(0) * 100 + pl.col("STAT_VT").fill_null(0)
        ).replace_strict(PARKING_TYPE_MAP),
    )
    lf = lf.with_columns(
        # Some cars ownership status were not set to "personal" because the proposed answer was
        # "acheté comptant ou à crédit". However, some households own their car even if they did not
        # buy it. We can track that using the `POSS_txt` variable.
        # The "ritage" answer is used to find "héritage" answers (with encoding issues).
        ownership=pl.when(
            pl.col("POSS_txt").str.contains(
                "(?i)don|offert|cadeau|ritage|change|troc|gratuit|sucession|session"
            )
        )
        .then(pl.lit("personal"))
        .otherwise(pl.col("ownership")),
    )
    lf = clean(lf)
    return lf

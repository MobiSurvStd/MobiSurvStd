import polars as pl

from mobisurvstd.common.motorcycles import clean

SCHEMA = {
    "IDCEREMA": pl.String,  # Identifiant du ménage
    "TYPE_QUEST": pl.String,  # Type de questionnaire
    "NRM": pl.UInt8,  # Numéro du deux-roues motorisé parmi ceux du ménage
    "MARQ": pl.String,  # Marque
    "MDL": pl.String,  # Modèle
    "ENERG": pl.UInt8,  # Motorisation du véhicule
    "ENERG_txt": pl.String,  # Motorisation du véhicule
    "APMC": pl.UInt16,  # Année de première mise en circulation
    "CYL": pl.UInt16,  # Cylindrée
    "ANKM": pl.UInt8,  # Kilomètres annuels
    "STAT": pl.UInt8,  # Stationnement au domicile
    "STAT_txt": pl.String,  # Stationnement au domicile
    "STAT_G": pl.UInt8,  # Le stationnement est-il payant (STAT=2 ou STAT =3 et STAT_VT<>3) ?
    "STAT_GT": pl.Float64,  # Tarif garage
    "STAT_VT": pl.UInt8,  # Type de stationnement sur voirie
}

FUEL_TYPE_MAP = {
    "11": "thermic",  # Essence (moteur 2 temps)
    "12": "thermic",  # Essence (moteur 4 temps)
    "2": "electric",  # Electrique
    "9": "other",  # Autre
}

THERMIC_ENGINE_TYPE_MAP = {
    "11": "two_stroke",  # Essence (moteur 2 temps)
    "12": "four_stroke",  # Essence (moteur 4 temps)
    "2": None,  # Electrique
    "9": None,  # Autre
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

PARKING_LOCATION_MAP = {
    1: "garage",  # Dans un garage, dans un box ou un autre emplacement réservé
    2: "street",  # Sur la voie publique
    3: "parking_lot",  # Dans un parking public
    4: "parking_lot",  # Dans le parking d'un centre commercial ou dans le parking de son entreprise
    9: "other",  # Autre
}

PARKING_TYPE_MAP = {
    0: "free",
    1: "paid",
    2: "free",
}


def scan_motorcycles(filename: str):
    lf = pl.scan_csv(
        filename,
        separator=";",
        encoding="utf8-lossy",
        schema_overrides=SCHEMA,
        null_values=["-1"],
    )
    return lf


def standardize_motorcycles(filename: str, households: pl.LazyFrame):
    lf = scan_motorcycles(filename)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("IDCEREMA")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = lf.with_columns(
        original_motorcycle_id=pl.struct("IDCEREMA", "NRM"),
        fuel_type=pl.col("ENERG").replace_strict(FUEL_TYPE_MAP),
        # 1900 is used as undetermined year.
        year=pl.col("APMC").replace([1900], None),
        thermic_engine_type=pl.col("ENERG").replace_strict(THERMIC_ENGINE_TYPE_MAP),
        # 0 is used for unknown cm3
        cm3_lower_bound=pl.col("CYL").replace([0], None),
        cm3_upper_bound=pl.col("CYL").replace([0], None),
        annual_mileage_lower_bound=pl.col("ANKM").replace_strict(MILEAGE_LB_MAP),
        annual_mileage_upper_bound=pl.col("ANKM").replace_strict(MILEAGE_UB_MAP),
        parking_location=pl.col("STAT").replace_strict(PARKING_LOCATION_MAP),
        parking_type=pl.col("STAT_G").replace_strict(PARKING_TYPE_MAP),
    )
    lf = clean(lf)
    return lf

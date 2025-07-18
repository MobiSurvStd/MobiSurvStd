import polars as pl

from mobisurvstd.common.motorcycles import clean

SCHEMA = {
    "IDENT_NUMVEH": pl.String,  # Identifiant véh. tous types
    "IDENT_MEN": pl.String,  # Identifiant ménage
    "NUM_VEH": pl.UInt8,  # Numéro du véhicule à disposition du ménage
    "pond_veh": pl.Float64,  # Poids du véhicule
    "ANNEE_1mec": pl.UInt16,  # Année de 1ère mise en circulation
    "ANNEE_acq": pl.UInt16,  # Année de mise à disposition
    "age_mois_veh": pl.UInt16,  # Age du véhicule (en mois)
    "KVAVCAT2R": pl.UInt8,  # Type du deux-roues motorisé
    "KVCYLIND2R": pl.Float64,  # Cylindrée (en m3)
    "KVQUICON2R01": pl.UInt8,  # 01ième utilisateur cité du véhicule
    "KVQUICON2R02": pl.UInt8,  # 02ième utilisateur cité du véhicule
    "KVQUICON2R03": pl.UInt8,  # 03ième utilisateur cité du véhicule
    "KVQUICON2R04": pl.UInt8,  # 04ième utilisateur cité du véhicule
    "KVQUICON2R05": pl.UInt8,  # 05ième utilisateur cité du véhicule
    "KVQUICON2R06": pl.UInt8,  # 06ième utilisateur cité du véhicule
    "KVQUICON2R07": pl.UInt8,  # 07ième utilisateur cité du véhicule
    "KVQUICON2R08": pl.UInt8,  # 08ième utilisateur cité du véhicule
    "KVQUICON2R09": pl.UInt8,  # 09ième utilisateur cité du véhicule
    "KVQUICON2R10": pl.UInt8,  # 10ième utilisateur cité du véhicule
    "KVQUICON2R11": pl.UInt8,  # 11ième utilisateur cité du véhicule
    "KVQUICON2R12": pl.UInt8,  # 12ième utilisateur cité du véhicule
    "KVQUICON2R13": pl.UInt8,  # 13ième utilisateur cité du véhicule
    "KVQUICON2R14": pl.UInt8,  # 14ième utilisateur cité du véhicule
    "KVQUICON2R15": pl.UInt8,  # 15ième utilisateur cité du véhicule
    "KVQUICON2R16": pl.UInt8,  # 16ième utilisateur cité du véhicule
    "KVQUICON2R17": pl.UInt8,  # 17ième utilisateur cité du véhicule
    "KVQUICON2R18": pl.UInt8,  # 18ième utilisateur cité du véhicule
    "KVQUICON2R19": pl.UInt8,  # 19ième utilisateur cité du véhicule
    "KVQUICON2R20": pl.UInt8,  # 20ième utilisateur cité du véhicule
    "KVQUICON2R21": pl.UInt8,  # 21ième utilisateur cité du véhicule
    "KVQUICONP2R": pl.UInt8,  # Conducteur principal du véhicule
    "KVPARK2R": pl.UInt8,  # Lieu de stationn. du véhicule la nuit (ou jour si travail de nuit)
    "KVKM1AN2R": pl.UInt32,  # Nb de km parcourus 12 derniers mois
    "KVKM1AN2RT": pl.UInt8,  # Nb de km parcourus 12 derniers mois (par tranche)
}

TYPE_MAP = {
    1: "motorbike",
    2: "scooter",
    3: "moped",
}

AN_MILEAGE_LB_MAP = {
    1: 0,
    2: 300,
    3: 1_000,
    4: 2_000,
    5: 3_000,
    6: 6_000,
}

AN_MILEAGE_UB_MAP = {
    1: 300,
    2: 1_000,
    3: 2_000,
    4: 3_000,
    5: 6_000,
    6: None,
}

PARKING_LOCATION_MAP = {
    1: "garage",  # Dans un parking couvert, un garage ou un box
    2: "garage",  # Sur un parking résidentiel, en plein air ou dans un jardin
    3: "parking_lot",  # Sur un parc de stationnement non résidentiel en plein air
    4: "street",  # Sur la voie publique gratuite
    5: "street",  # Sur la voie publique payante
    6: None,
    8: None,
    9: None,
}

PARKING_TYPE_MAP = {
    1: "free",  # Dans un parking couvert, un garage ou un box
    2: "free",  # Sur un parking résidentiel, en plein air ou dans un jardin
    3: "free",  # Sur un parc de stationnement non résidentiel en plein air
    4: "free",  # Sur la voie publique gratuite
    5: "paid",  # Sur la voie publique payante
    6: None,
    8: None,
    9: None,
}


def scan_motorcycles(filename: str):
    lf = pl.scan_csv(
        filename,
        separator=";",
        encoding="utf8-lossy",
        schema_overrides=SCHEMA,
        null_values=".",
    )
    return lf


def standardize_motorcycles(filename: str, households: pl.LazyFrame):
    lf = scan_motorcycles(filename)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("IDENT_MEN")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename({"NUM_VEH": "motorcycle_index", "ANNEE_1mec": "year"})
    lf = lf.with_columns(
        original_motorcycle_id=pl.struct("IDENT_NUMVEH"),
        type=pl.col("KVAVCAT2R").replace_strict(TYPE_MAP),
        cm3_lower_bound=pl.col("KVCYLIND2R").round(),
        cm3_upper_bound=pl.col("KVCYLIND2R").round(),
        annual_mileage=pl.col("KVKM1AN2R").round(),
        annual_mileage_lower_bound=pl.col("KVKM1AN2R").fill_null(
            pl.col("KVKM1AN2RT").replace_strict(AN_MILEAGE_LB_MAP, default=None)
        ),
        annual_mileage_upper_bound=pl.col("KVKM1AN2R").fill_null(
            pl.col("KVKM1AN2RT").replace_strict(AN_MILEAGE_LB_MAP, default=None)
        ),
        parking_location=pl.col("KVPARK2R").replace_strict(PARKING_LOCATION_MAP),
        parking_type=pl.col("KVPARK2R").replace_strict(PARKING_TYPE_MAP),
    )
    lf = clean(lf)
    return lf

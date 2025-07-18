import polars as pl

from mobisurvstd.common.cars import clean

SCHEMA = {
    "IDENT_NUMVEH": pl.String,  # Identifiant véh. tous types
    "IDENT_MEN": pl.String,  # Identifiant ménage
    "NUM_VEH": pl.UInt8,  # Numéro du véhicule à disposition du ménage
    "pond_veh": pl.Float64,  # Poids du véhicule
    "KVROUL": pl.UInt8,  # Ce véhicule a roulé depuis 1 ans
    "cylindree_fin": pl.String,  # Cylindrée (en litres)
    "energie_fin": pl.String,  # Energie du véhicule (mention carte grise)
    "energie_agrege": pl.UInt8,  # Energie du véhicule (agrege)
    "hybride": pl.String,  # Type d'hybride (complément énergie agrégée)
    "energie_statinfo": pl.UInt8,  # Energie du véhicule (Statinfo)
    "energie_CritAir": pl.UInt8,  # Energie du véhicule (Crit'air)
    "critair": pl.String,  # Vignette Crit'air (si connue)
    "puis_fisc_fin": pl.UInt8,  # Puissance fiscale
    "ANNEE_1mec": pl.UInt16,  # Année de 1ère mise en circulation
    "age": pl.UInt16,  # Age du véhicule (en mois)
    "ANNEE_acq": pl.UInt16,  # Année de mise à disposition
    "dur_acq": pl.UInt16,  # Durée de possession (en mois)
    "KVAQUIV": pl.UInt8,  # Propriétaire du véhicule
    "KVAQUINO01": pl.UInt8,  # 01ième propriétaire cité du véhicule
    "KVAQUINO02": pl.UInt8,  # 02ième propriétaire cité du véhicule
    "KVAQUINO03": pl.UInt8,  # 03ième propriétaire cité du véhicule
    "KVAQUINO04": pl.UInt8,  # 04ième propriétaire cité du véhicule
    "KVAQUINO05": pl.UInt8,  # 05ième propriétaire cité du véhicule
    "KVAQUINO06": pl.UInt8,  # 06ième propriétaire cité du véhicule
    "KVAQUINO07": pl.UInt8,  # 07ième propriétaire cité du véhicule
    "KVAQUINO08": pl.UInt8,  # 08ième propriétaire cité du véhicule
    "KVAQUINO09": pl.UInt8,  # 09ième propriétaire cité du véhicule
    "KVAQUINO10": pl.UInt8,  # 10ième propriétaire cité du véhicule
    "KVAQUINO11": pl.UInt8,  # 11ième propriétaire cité du véhicule
    "KVAQUINO12": pl.UInt8,  # 12ième propriétaire cité du véhicule
    "KVAQUINO13": pl.UInt8,  # 13ième propriétaire cité du véhicule
    "KVAQUINO14": pl.UInt8,  # 14ième propriétaire cité du véhicule
    "KVAQUINO15": pl.UInt8,  # 15ième propriétaire cité du véhicule
    "KVAQUINO16": pl.UInt8,  # 16ième propriétaire cité du véhicule
    "KVAQUINO17": pl.UInt8,  # 17ième propriétaire cité du véhicule
    "KVAQUINO18": pl.UInt8,  # 18ième propriétaire cité du véhicule
    "KVAQUINO19": pl.UInt8,  # 19ième propriétaire cité du véhicule
    "KVAQUINO20": pl.UInt8,  # 20ième propriétaire cité du véhicule
    "KVAQUINO21": pl.UInt8,  # 21ième propriétaire cité du véhicule
    "KVQUICONV01": pl.UInt8,  # 01ième utilisateur cité du véhicule
    "KVQUICONV02": pl.UInt8,  # 02ième utilisateur cité du véhicule
    "KVQUICONV03": pl.UInt8,  # 03ième utilisateur cité du véhicule
    "KVQUICONV04": pl.UInt8,  # 04ième utilisateur cité du véhicule
    "KVQUICONV05": pl.UInt8,  # 05ième utilisateur cité du véhicule
    "KVQUICONV06": pl.UInt8,  # 06ième utilisateur cité du véhicule
    "KVQUICONV07": pl.UInt8,  # 07ième utilisateur cité du véhicule
    "KVQUICONV08": pl.UInt8,  # 08ième utilisateur cité du véhicule
    "KVQUICONV09": pl.UInt8,  # 09ième utilisateur cité du véhicule
    "KVQUICONV10": pl.UInt8,  # 10ième utilisateur cité du véhicule
    "KVQUICONV11": pl.UInt8,  # 11ième utilisateur cité du véhicule
    "KVQUICONV12": pl.UInt8,  # 12ième utilisateur cité du véhicule
    "KVQUICONV13": pl.UInt8,  # 13ième utilisateur cité du véhicule
    "KVQUICONV14": pl.UInt8,  # 14ième utilisateur cité du véhicule
    "KVQUICONV15": pl.UInt8,  # 15ième utilisateur cité du véhicule
    "KVQUICONV16": pl.UInt8,  # 16ième utilisateur cité du véhicule
    "KVQUICONV17": pl.UInt8,  # 17ième utilisateur cité du véhicule
    "KVQUICONV18": pl.UInt8,  # 18ième utilisateur cité du véhicule
    "KVQUICONV19": pl.UInt8,  # 19ième utilisateur cité du véhicule
    "KVQUICONV20": pl.UInt8,  # 20ième utilisateur cité du véhicule
    "KVQUICONV21": pl.UInt8,  # 21ième utilisateur cité du véhicule
    "KVQUI9COV": pl.UInt8,  # Conduite du véhicule par des pers. ext. au mén.
    "KVQUICONPV": pl.UInt8,  # Conducteur principal du véhicule
    "KVKMV": pl.Float64,  # Nombre de kilomètres au compteur
    "indic_km_corr": pl.String,  # Méthode de définition du km au compteur
    "KVKMVT": pl.UInt8,  # Tranche kilomètres au compteur
    "KVKM1ANV": pl.Float64,  # Nombre de kilomètres parcourus au cours des 12 derniers mois
    "indic_km_annu_corr": pl.String,  # Méthode de définition du km annuel
    "KVKM1ANVT": pl.UInt8,  # Tranche kilomètres parcourus au cours des 12 derniers mois
    "KVCONS": pl.Float64,  # Consommation aux 100 km
    "KVGAREJOUR": pl.UInt8,  # Lieu de stationn. du véhicule la journée quand pas utilisé
    "KVGARENUIT": pl.UInt8,  # Lieu de stationn. du véhicule la nuit (ou jour si travail de nuit)
    "KVGARELEC_FLAG": pl.Int8,  # Variable drapeau du SetOf KVGARELEC
    "KVGARELEC_A": pl.UInt8,  # Le lieu de stationn. nuit est equipé d'une prise électrique ordinaire
    "KVGARELEC_B": pl.UInt8,  # Le lieu de stationn. nuit est equipé d'une prise spéciale de recharge électrique
}

FUEL_TYPE_MAP = {
    1: "thermic:petrol",
    2: "thermic:diesel",
    3: "thermic:gas",
    4: "hybrid:unspecified",
    5: "electric",
    6: "other",
    9: None,
}

HYBRID_MAP = {
    "EE": "hybrid:plug-in",
    "GH": "hybrid:regular:diesel",
    "EH": "hybrid:regular:petrol",
    None: "hybrid:unspecified",
}

FUEL_TYPE_GROUP_MAP = {
    1: "thermic:petrol",
    2: "thermic:diesel",
    3: "thermic:gas",
    4: "hybrid",
    5: "electric",
    6: "other",
    9: None,
}

TOT_MILEAGE_LB_MAP = {
    1: 0,
    2: 25_000,
    3: 50_000,
    4: 75_000,
    5: 100_000,
    6: 150_000,
    7: 200_000,
}

TOT_MILEAGE_UB_MAP = {
    1: 25_000,
    2: 50_000,
    3: 75_000,
    4: 100_000,
    5: 150_000,
    6: 200_000,
    7: None,
}

AN_MILEAGE_LB_MAP = {
    1: 0,
    2: 4_000,
    3: 8_000,
    4: 10_000,
    5: 15_000,
    6: 20_000,
}

AN_MILEAGE_UB_MAP = {
    1: 4_000,
    2: 8_000,
    3: 10_000,
    4: 15_000,
    5: 20_000,
    6: None,
}

PARKING_LOCATION_MAP = {
    1: "garage",  # Dans un parking couvert, un garage ou un box
    2: "garage",  # Sur un parking résidentiel, en plein air ou dans un jardin
    3: "parking_lot",  # Sur un parc de stationnement non résidentiel en plein air
    4: "street",  # Sur la voie publique gratuite
    5: "street",  # Sur la voie publique payante
    8: None,
    9: None,
}

PARKING_TYPE_MAP = {
    1: "free",  # Dans un parking couvert, un garage ou un box
    2: "free",  # Sur un parking résidentiel, en plein air ou dans un jardin
    3: "free",  # Sur un parc de stationnement non résidentiel en plein air
    4: "free",  # Sur la voie publique gratuite
    5: "paid",  # Sur la voie publique payante
    8: None,
    9: None,
}


def scan_cars(filename: str):
    lf = pl.scan_csv(
        filename,
        separator=";",
        encoding="utf8-lossy",
        schema_overrides=SCHEMA,
        null_values=".",
    )
    return lf


def standardize_cars(filename: str, households: pl.LazyFrame):
    lf = scan_cars(filename)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("IDENT_MEN")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename(
        {"NUM_VEH": "car_index", "ANNEE_1mec": "year", "puis_fisc_fin": "tax_horsepower"}
    )
    lf = lf.with_columns(
        original_car_id=pl.struct("IDENT_NUMVEH"),
        fuel_type=pl.col("energie_agrege").replace_strict(FUEL_TYPE_MAP),
        total_mileage=pl.col("KVKMV").round(),
        total_mileage_lower_bound=pl.col("KVKMV").fill_null(
            pl.col("KVKMVT").replace_strict(TOT_MILEAGE_LB_MAP, default=None)
        ),
        total_mileage_upper_bound=pl.col("KVKMV").fill_null(
            pl.col("KVKMVT").replace_strict(TOT_MILEAGE_UB_MAP, default=None)
        ),
        annual_mileage=pl.col("KVKM1ANV").round(),
        annual_mileage_lower_bound=pl.col("KVKM1ANV").fill_null(
            pl.col("KVKM1ANVT").replace_strict(AN_MILEAGE_LB_MAP, default=None)
        ),
        annual_mileage_upper_bound=pl.col("KVKM1ANV").fill_null(
            pl.col("KVKM1ANVT").replace_strict(AN_MILEAGE_UB_MAP, default=None)
        ),
        parking_location=pl.col("KVGARENUIT").replace_strict(PARKING_LOCATION_MAP),
        parking_type=pl.col("KVGARENUIT").replace_strict(PARKING_TYPE_MAP),
    )
    lf = lf.with_columns(
        # The precise hybrid type is read from the `energie_fin` variable.
        fuel_type=pl.when(pl.col("fuel_type").eq("hybrid:unspecified"))
        .then(pl.col("energie_fin").replace_strict(HYBRID_MAP, default=None))
        .otherwise("fuel_type")
    )
    lf = clean(lf)
    return lf

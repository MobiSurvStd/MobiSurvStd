from datetime import timedelta

import polars as pl

from mobisurvstd.common.households import clean

SCHEMA = {
    "IDCEREMA": pl.String,  # Identifiant du ménage
    "TYPE_QUEST": pl.String,  # Type de questionnaire
    "NBP_CATI": pl.UInt8,  # Nombre d’occupants du logement recueilli par téléphone
    "RESCOMM": pl.String,  # Commune de résidence
    "RESDEP": pl.String,  # Département de résidence
    "RESCOUR": pl.UInt8,  # Couronne de résidence
    "RESLNG": pl.Float64,  # Longitude du lieu de résidence
    "RESLAT": pl.Float64,  # Latitude du lieu de résidence
    "JOUR": pl.UInt8,  # Jour de l’enquête (JJ)
    "MOIS": pl.UInt8,  # Mois de l’enquête (MM)
    "ANNEE": pl.UInt16,  # Année de l’enquête (AAAA)
    "JOURSEM": pl.String,  # Jour de la semaine de la date schéma des déplacements
    "MNP": pl.UInt8,  # Nombre de personnes du ménage
    "MNP5": pl.UInt8,  # Nombre de personnes du ménage de 5 ans et plus
    "MNPMOB": pl.UInt8,  # Nombre de personnes du ménage qui se sont déplacées la veille
    "MNPACT": pl.UInt8,  # Nombre d'actifs occupés dans le ménage
    "TYPE_MEN": pl.String,  # Type de ménage
    "TYPELOG": pl.UInt8,  # Type de logement
    "OCCUPLOG": pl.UInt8,  # Occupation du logement
    "OCCUPLOG_txt": pl.String,  # Occupation du logement
    "ANARR_LOG": pl.UInt16,  # Année d'arrivée dans le logement
    "ACOMM_T": pl.UInt8,  # Type commune précédente
    "ACOMM_N": pl.String,  # Nom commune précédente
    "INTERNET": pl.UInt8,  # Présence d'un accès Internet au sein du domicile
    "NB_VD": pl.UInt8,  # Nombre de voitures à disposition
    "NB_2RM": pl.UInt8,  # Nombre de deux-roues motorisés à disposition
    "NB_VEH": pl.UInt8,  # Nombre de véhicules motorisés à disposition
    "NB_VELO": pl.UInt8,  # Nombre de vélos (en état de marche pour les personnes âgées d'au moins 10 ans))
    "NB_VAE": pl.UInt8,  # Nombre de vélo à assistance électrique
    "VP_ENT": pl.UInt8,  # Dépense Voiture entretien
    "VP_ASS": pl.UInt8,  # Dépense Voiture assurance
    "DEUXRM_ENT": pl.UInt8,  # Dépense Deux-roues motorisé entretien
    "DEUXRM_ASS": pl.UInt8,  # Dépense Deux-roues motorisé assurance
    "ABRI_VL": pl.UInt8,  # Abri Vélo
    "REVENU": pl.UInt8,  # Classe de revenu net mensuel
    "POIDSM": pl.Float64,  # Poids du ménage
}

SURVEY_METHOD_MAP = {
    "CAPI": "face_to_face",
    "CATI": "phone",
}

HOUSEHOLD_TYPE_MAP = {
    "Homme seul": "single:man",
    "Femme seule": "single:woman",
    "Couple sans enfant": "couple:no_child",
    "Couple avec enfant": "couple:children",
    "Famille monoparentale père": "singleparent:father",
    "Famille monoparentale mère": "singleparent:mother",
    "Autre": "other",
}

HOUSING_TYPE_MAP = {
    1: "house",  # Une maison
    2: "apartment",  # Un appartement
    3: "other",  # Autre
    9: "other",  # Note. Une the variable dictionary Autre is 3 but it seems that 9 is used instead.
}

HOUSING_STATUS_MAP = {
    1: "owner:ongoing_loan",  # Propriétaire en cours de prêt immobilier
    2: "owner:fully_repaid",  # Propriétaire hors prêt immobilier
    10: "owner:unspecified",  # Propriétaire sans précision
    3: "tenant:public_housing",  # Locataire d'un organisme HLM, RIVP
    4: "tenant:private",  # Locateur du secteur privé
    5: "university_resident",  # Locataire d'une résidence universitaire
    9: "other",  # Autre
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
}


def scan_households(filename: str):
    # We use the inefficient `read_csv().lazy()` because we need to use `encoding="latin1"`, which
    # does not exist with `scan_csv()`.
    lf = pl.read_csv(
        filename,
        separator=";",
        encoding="latin1",
        schema_overrides=SCHEMA,
        null_values=["-1", "-2"],
    ).lazy()
    return lf


def standardize_households(filename: str):
    lf = scan_households(filename)
    lf = lf.rename(
        {
            "POIDSM": "sample_weight",
            "RESLNG": "home_lng",
            "RESLAT": "home_lat",
            "RESCOMM": "home_insee",
            "RESDEP": "home_dep",
            "NB_VD": "nb_cars",
            "NB_2RM": "nb_motorcycles",
            "NB_VELO": "nb_bicycles",
            "NB_VAE": "nb_electric_bicycles",
        }
    )
    lf = lf.with_columns(
        original_household_id=pl.struct("IDCEREMA"),
        survey_method=pl.col("TYPE_QUEST").replace_strict(SURVEY_METHOD_MAP),
        interview_date=pl.date(year="ANNEE", month="MOIS", day="JOUR") + timedelta(days=1),
        household_type=pl.col("TYPE_MEN").replace_strict(HOUSEHOLD_TYPE_MAP),
        income_lower_bound=pl.col("REVENU").replace_strict(REVENU_LB_MAP),
        income_upper_bound=pl.col("REVENU").replace_strict(REVENU_UB_MAP),
        housing_type=pl.col("TYPELOG").replace_strict(HOUSING_TYPE_MAP),
        housing_status=pl.col("OCCUPLOG").replace_strict(HOUSING_STATUS_MAP),
        has_internet=pl.col("INTERNET") == 1,
        nb_standard_bicycles=pl.col("nb_bicycles") - pl.col("nb_electric_bicycles"),
        has_bicycle_parking=pl.col("ABRI_VL") == 1,
        # Set `nb_electric_bicycles` to NULL when `nb_bicycles` is NULL (column NB_VAE is 0 instead
        # of NULL when NB_VELO is NULL).
        nb_electric_bicycles=pl.when(pl.col("nb_bicycles").is_not_null()).then(
            "nb_electric_bicycles"
        ),
    )
    lf = lf.with_columns(
        # More details on the housing status can be read in the `OCCUPLOG_txt` variable.
        housing_status=pl.when(pl.col("OCCUPLOG_txt").str.contains("(?i)usufruit"))
        .then(pl.lit("owner:usufructuary"))
        .otherwise(
            pl.when(pl.col("OCCUPLOG_txt").str.contains("(?i)gratuit|gracieux|fonction"))
            .then(pl.lit("rent_free"))
            .otherwise(pl.col("housing_status"))
        ),
    )
    lf = clean(lf)
    return lf

from datetime import timedelta

import polars as pl

from mobisurvstd.common.households import clean as clean_households

from .personnes import scan_persons

HOUSEHOLD_TYPE_MAP = {
    "Je n'ai aucun lien de parenté avec les autres membres": None,
    "Je suis en colocation": "other",
    "Je suis en couple avec enfant(s)": "couple:children",
    "Je suis en couple sans enfant": "couple:no_child",
    "Je suis un autre membre de la famille": None,
    "Je suis un parent seul (divorcé / séparé / veuf)": "singleparent",
    "Je vis avec un ou mes parents": "singleparent",
    "Je vis seul.e": "single"
}

def standardize_households(filename: str):
    lf = scan_persons(filename)

    lf = lf.with_columns(
        original_household_id=pl.col("ID"),
        home_insee=pl.col("CODGEO"),
        household_type_simple=pl.col("TYPE_MEN").replace_strict(HOUSEHOLD_TYPE_MAP),
        nb_cars=pl.col("NB_VP"),
        nb_motorcycles=pl.col("2RM"),
        nb_bicycles=pl.col("VELO"),
        nb_persons=pl.col("NBPERS_MEN"),
        nb_majors=pl.col("NB_18_24") + pl.col("NB_25_64") + pl.col("NB_65"),
        nb_minors=pl.col("NB_10") + pl.col("NB_11_17"),
    )

    lf = lf.with_columns(
        household_type=pl
            .when(pl.col("household_type_simple").eq("single"), pl.col("SEXE").eq("Femme"))
            .then(pl.lit("single:woman"))
            .when(pl.col("household_type_simple").eq("single"), pl.col("SEXE").eq("Homme"))
            .then(pl.lit("single:man"))
            .when(pl.col("household_type_simple").eq("singleparent"), pl.col("SEXE").eq("Femme"))
            .then(pl.lit("singleparent:mother"))
            .when(pl.col("household_type_simple").eq("singleparent"), pl.col("SEXE").eq("Homme"))
            .then(pl.lit("singleparent:father"))
            .otherwise("household_type_simple")
    )

    lf = lf.sort("original_household_id")
    lf = clean_households(lf, year=2023)

    return lf

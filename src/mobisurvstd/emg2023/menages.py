from datetime import timedelta

import polars as pl

from mobisurvstd.common.households import clean as clean_households

from .personnes import scan_persons

def standardize_households(filename: str):
    lf = scan_persons(filename)

    lf = lf.with_columns(
        original_household_id=pl.col("ID"),
        complete_household=False,
        home_insee=pl.col("CODGEO"),
        nb_cars=pl.col("NB_VP"),
        nb_motorcycles=pl.col("2RM"),
        nb_bicycles=pl.col("VELO"),
        nb_persons=pl.col("NBPERS_MEN"),
    )

    lf = lf.sort("original_household_id")
    lf = clean_households(lf, year=2023)

    return lf

import os
import zipfile

import geopandas as gpd
import polars as pl
from loguru import logger

from mobisurvstd.utils import tmp_download

from . import CACHE_DIR

OUTPUT_FILE = os.path.join(CACHE_DIR, "insee_data.parquet")

CODE_GEO_URL = "https://www.insee.fr/fr/statistiques/fichier/8377162/v_commune_2025.csv"

INSEE_CHANGE_URL = (
    "https://www.insee.fr/fr/statistiques/fichier/7671867/table_passage_geo2003_geo2025.zip"
)

DENSITY_URL_DICT = {
    "2015_to_2020": "https://www.insee.fr/fr/statistiques/fichier/6439600/grille_densite_7_niveaux_2015-2020.zip",
    "2021": "https://www.insee.fr/fr/statistiques/fichier/6439600/grille_densite_7_niveaux_2021.xlsx",
    "2022": "https://www.insee.fr/fr/statistiques/fichier/6439600/grille_densite_7_niveaux_2022.xlsx",
    "2023": "https://www.insee.fr/fr/statistiques/fichier/6439600/grille_densite_7_niveaux_2023.xlsx",
    "2024": "https://www.insee.fr/fr/statistiques/fichier/6439600/grille_densite_7_niveaux_2024.xlsx",
}

AAV_URL_DICT = {
    "2020": "https://www.insee.fr/fr/statistiques/fichier/4803954/fonds_AAV2020_geo20.zip",
    "2021": "https://www.insee.fr/fr/statistiques/fichier/4803954/fonds_AAV2020_geo21.zip",
    "2022": "https://www.insee.fr/fr/statistiques/fichier/4803954/fonds_aav2020_2022.zip",
    "2023": "https://www.insee.fr/fr/statistiques/fichier/4803954/fonds_aav2020_2023.zip",
    "2024": "https://www.insee.fr/fr/statistiques/fichier/4803954/fonds_aav2020_2024.zip",
}


def get_insee_code_geo():
    with tmp_download(CODE_GEO_URL) as fn:
        df = pl.read_csv(
            fn,
            columns=["COM", "DEP", "LIBELLE", "COMPARENT"],
            schema_overrides={"COM": pl.String, "DEP": pl.String, "COMPARENT": pl.String},
            null_values=[""],
        )
    df = df.rename(
        {"COM": "insee", "DEP": "dep", "LIBELLE": "insee_name", "COMPARENT": "parent_insee"}
    )
    # If the same INSEE code appears multiple times, then keep only the most recent row.
    df = df.sort("parent_insee", nulls_last=False).unique(subset=["insee"], keep="first")
    # Add missing dep values from parent.
    df = df.with_columns(
        dep=pl.col("dep").fill_null(
            pl.col("parent_insee").replace_strict(pl.col("insee"), pl.col("dep"), default=None)
        )
    )
    return df


def get_insee_changes():
    with tmp_download(INSEE_CHANGE_URL) as fn:
        with zipfile.ZipFile(fn) as z:
            df = pl.read_excel(
                z.read(z.filelist[0]),
                read_options={"header_row": 5},
                columns=["CODGEO_INI", "CODGEO_2025"],
                schema_overrides={"CODGEO_INI": pl.String, "CODGEO_2025": pl.String},
            )
    df = df.rename({"CODGEO_INI": "insee", "CODGEO_2025": "parent_insee"})
    return df


def read_density_excel(source: bytes | str, year: str):
    return pl.read_excel(
        source,
        read_options={"header_row": 4},
        columns=["CODGEO", "DENS"],
        schema_overrides={"CODGEO": pl.String, "DENS": pl.UInt8},
    ).rename({"CODGEO": "insee", "DENS": f"insee_density_{year}"})


def get_insee_density():
    df = pl.DataFrame({"insee": pl.Series(dtype=pl.String)})
    with tmp_download(DENSITY_URL_DICT["2015_to_2020"]) as fn:
        with zipfile.ZipFile(fn) as z:
            for year in range(2015, 2021):
                tmp_df = read_density_excel(
                    z.read(f"grille_densite_7_niveaux_{year}.xlsx"), str(year)
                )
                df = df.join(tmp_df, on="insee", how="full", coalesce=True)
    for year in range(2021, 2025):
        with tmp_download(DENSITY_URL_DICT[str(year)]) as fn:
            tmp_df = read_density_excel(fn, str(year))
            df = df.join(tmp_df, on="insee", how="full", coalesce=True)
    df = df.sort("insee")
    return df


AAV_TYPE_MAP = {
    "Commune-Centre": 11,
    "Autre commune du pôle principal": 12,
    "Commune d'un pôle secondaire": 13,
    "Commune de la couronne": 20,
    "Commune hors attraction des villes": 30,
}

AAV_CAT_MAP = {
    "Aire de Paris": 1,
    "Aire de 700 000 habitants ou plus (hors Paris)": 2,
    "Aire de 200 000 à moins de 700 000 habitants": 3,
    "Aire de 200 000 à 700 000 hab.": 3,
    "Aire de 50 000 à moins de 200 000 habitants": 4,
    "Aire de 50 000 à moins de 200 000 hab.": 4,
    "Aire de moins de 50 000 habitants": 5,
    "Aire de moins de 50 000 hab.": 5,
}


def read_aav(source: zipfile.ZipExtFile | str, year: str):
    with zipfile.ZipFile(source) as z:
        if year == "2020":
            # Format is different for year 2020.
            df = pl.concat(
                (
                    pl.from_pandas(
                        gpd.read_file(z.open("fond_AAV2020_geo20_metro.zip")).drop(
                            columns="geometry"
                        )
                    ),
                    pl.from_pandas(
                        gpd.read_file(z.open("fond_AAV2020_geo20_DOM.zip")).drop(columns="geometry")
                    ),
                ),
                how="diagonal_relaxed",
            )
            df = df.select(
                insee=pl.col("CODGEO").cast(pl.String),
                aav_2020=pl.col("AAV20").cast(pl.String),
                insee_aav_type_2020=pl.col("CATEAAV").cast(pl.UInt8),
                aav_name_2020=pl.col("LIBAAV2").cast(pl.String),
                aav_category_2020=pl.col("LIBTAAV").replace_strict(
                    AAV_CAT_MAP, default=None, return_dtype=pl.UInt8
                ),
            )
        else:
            if year == "2021":
                fn_insee = f"AAV20_compcom_geo{year}.zip"
                fn_aav = f"AAV20_contours_geo{year}.zip"
            else:
                fn_insee = f"com_aav2020_{year}.zip"
                fn_aav = f"aav2020_{year}.zip"
            df_insee = pl.from_pandas(gpd.read_file(z.open(fn_insee)).drop(columns="geometry"))
            insee_col = next(col for col in df_insee.columns if col.lower().startswith("codgeo"))
            aav_col = next(col for col in df_insee.columns if col.lower().startswith("aav"))
            insee_aav_type_col = next(
                col for col in df_insee.columns if col.lower().startswith("cateaav")
            )
            # Depending on the year, "insee_aav_type" are either numeric values (11, 12, 13, 20, 30)
            # or the type name as String.
            try:
                df_insee = df_insee.with_columns(pl.col(insee_aav_type_col).cast(pl.UInt8))
            except pl.exceptions.InvalidOperationError:
                df_insee = df_insee.with_columns(
                    pl.col(insee_aav_type_col).replace_strict(AAV_TYPE_MAP, return_dtype=pl.UInt8)
                )
            df_insee = df_insee.select(
                pl.col(insee_col).cast(pl.String).alias("insee"),
                pl.col(aav_col).cast(pl.String).alias(f"aav_{year}"),
                pl.col(insee_aav_type_col).alias(f"insee_aav_type_{year}"),
            )

            df_aav = pl.from_pandas(gpd.read_file(z.open(fn_aav)).drop(columns="geometry"))
            aav_col = next(col for col in df_aav.columns if col.lower().startswith("aav"))
            aav_name_col = next(col for col in df_aav.columns if col.lower().startswith("libaav"))
            aav_category_col = next(col for col in df_aav.columns if col.lower().startswith("taav"))
            # Depending on the year, "aav_category" are either numeric values (1, 2, 3, 4, 5) or
            # the category name as String.
            try:
                # Set AAV category 0 (no AAV) to NULL.
                df_aav = df_aav.with_columns(
                    pl.col(aav_category_col).cast(pl.UInt8).replace({0: None})
                )
            except pl.exceptions.InvalidOperationError:
                df_aav = df_aav.with_columns(
                    pl.col(aav_category_col).replace_strict(AAV_CAT_MAP, return_dtype=pl.UInt8)
                )
            df_aav = df_aav.select(
                pl.col(aav_col).cast(pl.String).alias(f"aav_{year}"),
                pl.col(aav_name_col).cast(pl.String).alias(f"aav_name_{year}"),
                pl.col(aav_category_col).alias(f"aav_category_{year}"),
            )
            df = df_insee.join(df_aav, on=f"aav_{year}", how="left")
        # Set AAV name to NULL for municipalities outside any AAV.
        df = df.with_columns(
            pl.when(pl.col(f"aav_{year}").eq("000"))
            .then(pl.lit(None))
            .otherwise(f"aav_name_{year}")
            .alias(f"aav_name_{year}")
        )
        assert df[f"insee_aav_type_{year}"].is_in((11, 12, 13, 20, 30)).all()
        assert df[f"aav_category_{year}"].is_in((1, 2, 3, 4, 5)).all()
        return df


def get_insee_aav():
    df = pl.DataFrame({"insee": pl.Series(dtype=pl.String)})
    for year in range(2020, 2025):
        with tmp_download(AAV_URL_DICT[str(year)]) as fn:
            tmp_df = read_aav(fn, str(year))
            df = df.join(tmp_df, on="insee", how="full", coalesce=True)
    df = df.sort("insee")
    return df


def download_insee_data():
    logger.warning("INSEE municipality-level data not found")
    logger.warning("Data will be downloaded from the INSEE website")
    logger.warning("This operation only needs to be performed once")
    logger.debug("Retrieving INSEE codes")
    df_codes = get_insee_code_geo()
    logger.debug("Retrieving INSEE code changes")
    df_changes = get_insee_changes()
    logger.debug("Retrieving INSEE densities")
    df_density = get_insee_density()
    logger.debug("Retrieving INSEE AAV")
    df_aav = get_insee_aav()
    # Add INSEE codes missing from code géo.
    missing = df_changes.join(df_codes, on="insee", how="anti").join(
        df_codes.drop("parent_insee"), left_on="parent_insee", right_on="insee", how="left"
    )
    df = pl.concat((df_codes, missing), how="diagonal")
    # Add density data.
    df = df.with_columns(
        pl.col("insee")
        .replace_strict(df_density["insee"], df_density[col], default=None)
        .fill_null(
            pl.col("parent_insee").replace_strict(
                df_density["insee"], df_density[col], default=None
            )
        )
        .alias(col)
        for col in df_density.columns
        if col != "insee"
    )
    # Add AAV data.
    df = df.with_columns(
        pl.col("insee")
        .replace_strict(df_aav["insee"], df_aav[col], default=None)
        .fill_null(
            pl.col("parent_insee").replace_strict(df_aav["insee"], df_aav[col], default=None)
        )
        .alias(col)
        for col in df_aav.columns
        if col != "insee"
    )
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    logger.debug(f"Writing INSEE data to `{OUTPUT_FILE}`")
    df.write_parquet(OUTPUT_FILE)
    return df


def load_insee_data(columns: list[str] | None = None):
    if not os.path.isfile(OUTPUT_FILE):
        return download_insee_data()
    else:
        return pl.read_parquet(OUTPUT_FILE, columns=columns)


def add_insee_data(lf: pl.LazyFrame, prefix: str, year: int | None = None, skip_dep=False):
    """Add the municipality name and département code from the INSEE code column.

    If `year` is not None, then also add density and AAV data for that year.

    If `skip_dep` is True, then the corresponding département code is not added (useful to use the
    département codes reported by the travel survey when some observations have a département code
    but no INSEE code).
    """
    columns = ["insee", "insee_name"]
    if not skip_dep:
        columns.append("dep")
    if year is not None:
        density_year = max(2015, min(2024, year))
        aav_year = max(2020, min(2024, year))
        columns.extend(
            [
                f"insee_density_{density_year}",
                f"aav_{aav_year}",
                f"insee_aav_type_{aav_year}",
                f"aav_name_{aav_year}",
                f"aav_category_{aav_year}",
            ]
        )
    data = load_insee_data(columns)
    insee_col = f"{prefix}_insee"
    lf = lf.join(data.lazy(), left_on=insee_col, right_on="insee", how="left", coalesce=True)
    lf = lf.rename({"insee_name": f"{prefix}_insee_name"})
    if not skip_dep:
        lf = lf.rename({"dep": f"{prefix}_dep"})
    if year is not None:
        lf = lf.rename(
            {
                f"insee_density_{density_year}": f"{prefix}_insee_density",
                f"aav_{aav_year}": f"{prefix}_aav",
                f"insee_aav_type_{aav_year}": f"{prefix}_insee_aav_type",
                f"aav_name_{aav_year}": f"{prefix}_aav_name",
                f"aav_category_{aav_year}": f"{prefix}_aav_category",
            }
        )
    return lf

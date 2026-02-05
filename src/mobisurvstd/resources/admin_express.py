import os
import re
import tempfile

import geopandas as gpd
import pandas as pd
import polars as pl
import py7zr
from loguru import logger

from mobisurvstd.utils import tmp_download

from . import CACHE_DIR

URL = "https://data.geopf.fr/telechargement/download/ADMIN-EXPRESS-COG/ADMIN-EXPRESS-COG_4-0__GPKG_WGS84G_FRA_2025-01-01/ADMIN-EXPRESS-COG_4-0__GPKG_WGS84G_FRA_2025-01-01.7z"
OUTPUT_FILE = os.path.join(CACHE_DIR, "insee_geometries.geo.parquet")


def read_admin_express():
    logger.warning("Data will be downloaded from the IGN website")
    logger.warning("This operation only needs to be performed once")
    # Download ADMIN-EXPRESS data.
    with tmp_download(URL) as fn:
        # Read the downloaded file as a 7zip archive.
        with py7zr.SevenZipFile(fn, "r") as archive:
            # Find the Geopackage file within the archive.
            allfiles = archive.getnames()
            filter_pattern = re.compile(r".*[.]gpkg")
            selected_files = [f for f in allfiles if filter_pattern.match(os.path.basename(f))]
            assert len(selected_files) == 1
            gpkg_file = selected_files[0]
            # Create a temporary directory and extract the selected file within it.
            with tempfile.TemporaryDirectory() as tmpdir:
                logger.debug(f"Extracting ADMIN EXPRESS data to `{tmpdir}`")
                archive.extract(path=tmpdir, targets=[gpkg_file])
                communes = gpd.read_file(
                    os.path.join(tmpdir, gpkg_file),
                    layer="commune",
                    columns=["geometry", "code_insee"],
                )
                arrondissements = gpd.read_file(
                    os.path.join(tmpdir, gpkg_file),
                    layer="arrondissement_municipal",
                    columns=["geometry", "code_insee", "code_insee_de_la_commune_de_rattach"],
                )
    # Remove communes with arrondissements (Paris, Lyon, and Marseille).
    communes = communes.loc[
        ~communes["code_insee"].isin(arrondissements["code_insee_de_la_commune_de_rattach"])
    ]
    # Concatenate the communes and arrondissements.
    gdf = pd.concat(
        (
            communes.rename(columns={"code_insee": "insee"}),
            arrondissements.rename(columns={"code_insee": "insee"}).drop(
                columns=["code_insee_de_la_commune_de_rattach"]
            ),
        ),
        ignore_index=True,
    )
    gdf = gdf.sort_values("insee")
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    logger.debug(f"Writing ADMIN EXPRESS data to `{OUTPUT_FILE}`")
    gdf.to_parquet(OUTPUT_FILE)
    return gdf


def load_insee_geometries():
    if not os.path.isfile(OUTPUT_FILE):
        logger.warning("ADMIN EXPRESS data not found")
        return read_admin_express()
    else:
        return gpd.read_parquet(OUTPUT_FILE)


def find_insee(lf: pl.LazyFrame, prefix: str, id_col: str):
    """Add the `*_insee` columns from the `*_lng` and `*_lat` columns."""
    insee_col = f"{prefix}_insee"
    lng_col = f"{prefix}_lng"
    lat_col = f"{prefix}_lat"
    gdf = load_insee_geometries()
    logger.debug(f'Assigning INSEE municipality from coordinates for "{prefix}"')
    xy = lf.select(id_col, lng_col, lat_col).collect()
    points = gpd.GeoDataFrame(
        data=xy[id_col].to_pandas(),
        geometry=gpd.GeoSeries.from_xy(xy[lng_col], xy[lat_col], crs="EPSG:4326"),
    )
    join = gpd.sjoin(points, gdf, predicate="within")
    # A point can belong to 2 INSEE if it is on the geometry borders. In this case, we only keep one
    # INSEE.
    join = join.drop_duplicates(subset=[id_col], ignore_index=True)
    df = pl.from_pandas(join.loc[:, [id_col, "insee"]]).rename({"insee": insee_col})
    lf = lf.join(df.lazy(), on=id_col, how="left")
    return lf

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

URL = "https://data.geopf.fr/telechargement/download/ADMIN-EXPRESS-COG-CARTO/ADMIN-EXPRESS-COG-CARTO_3-2__SHP_WGS84G_FRA_2025-04-02/ADMIN-EXPRESS-COG-CARTO_3-2__SHP_WGS84G_FRA_2025-04-02.7z"
PATH = "ADMIN-EXPRESS-COG-CARTO_3-2__SHP_WGS84G_FRA_2025-04-02/ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2025-04-00194/ADECOGC_3-2_SHP_WGS84G_FRA-ED2025-04-02/"
OUTPUT_FILE = os.path.join(CACHE_DIR, "insee_geometries.geo.parquet")


def read_admin_express():
    logger.warning("ADMIN EXPRESS data not found")
    logger.warning("Data will be downloaded from the IGN website")
    logger.warning("This operation only needs to be performed once")
    # Download ADMIN-EXPRESS data.
    with tmp_download(URL) as fn:
        # Read the downloaded file as a 7zip archive.
        with py7zr.SevenZipFile(fn, "r") as archive:
            # Find the COMMUNE.* and ARRONDISSEMENT.* files within the archive.
            allfiles = archive.getnames()
            filter_pattern = re.compile(r"(COMMUNE|ARRONDISSEMENT_MUNICIPAL)\.\w*")
            selected_files = [f for f in allfiles if filter_pattern.match(os.path.basename(f))]
            # Create a temporary directory and extract the selected files within it.
            with tempfile.TemporaryDirectory() as tmpdir:
                logger.debug(f"Extracting ADMIN EXPRESS data to `{tmpdir}`")
                archive.extract(path=tmpdir, targets=selected_files)
                # Find the directory of the 7zip file within which the extracted files are located
                # (COMMUNE and ARRONDISSEMENT are supposed to be located in the same directory).
                path = os.path.dirname(selected_files[0])
                communes = gpd.read_file(
                    os.path.join(tmpdir, path, "COMMUNE.shp"),
                    columns=["geometry", "INSEE_COM"],
                )
                arrondissements = gpd.read_file(
                    os.path.join(tmpdir, path, "ARRONDISSEMENT_MUNICIPAL.shp"),
                    columns=["geometry", "INSEE_ARM", "INSEE_COM"],
                )
    # Remove communes with arrondissements (Paris, Lyon, and Marseille).
    communes = communes.loc[~communes["INSEE_COM"].isin(arrondissements["INSEE_COM"])]
    # Concatenate the communes and arrondissements.
    gdf = pd.concat(
        (
            communes.rename(columns={"INSEE_COM": "insee"}),
            arrondissements.rename(columns={"INSEE_ARM": "insee"}).drop(columns=["INSEE_COM"]),
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

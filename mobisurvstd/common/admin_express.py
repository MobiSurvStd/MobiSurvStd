import os

import geopandas as gpd
import pandas as pd
import polars as pl
import polars_st as st

PATH = "./data/ADMIN-EXPRESS-COG-CARTO_3-2__SHP_WGS84G_FRA_2025-04-02/ADMIN-EXPRESS-COG-CARTO/1_DONNEES_LIVRAISON_2025-04-00194/ADECOGC_3-2_SHP_WGS84G_FRA-ED2025-04-02/"
OUTPUT_FILE = "./output/insee_geometries.geo.parquet"


def read_admin_express():
    print("Reading ADMIN EXPRESS")
    communes = gpd.read_file(os.path.join(PATH, "COMMUNE.shp"), columns=["geometry", "INSEE_COM"])
    arrondissements = gpd.read_file(
        os.path.join(PATH, "ARRONDISSEMENT_MUNICIPAL.shp"),
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
    gdf.to_parquet(OUTPUT_FILE)
    return gdf


# TODO. Update when saving with geoparquet is possible.
def read_admin_express2():
    print("Reading ADMIN EXPRESS")
    communes = st.read_file(os.path.join(PATH, "COMMUNE.shp"), columns=["geometry", "INSEE_COM"])
    arrondissements = st.read_file(
        os.path.join(PATH, "ARRONDISSEMENT_MUNICIPAL.shp"),
        columns=["geometry", "INSEE_ARM", "INSEE_COM"],
    )
    # Remove communes with arrondissements (Paris, Lyon, and Marseille).
    communes = communes.filter(pl.col("INSEE_COM").is_in(arrondissements["INSEE_COM"]).not_())
    # Concatenate the communes and arrondissements.
    gdf = pl.concat(
        (
            communes.rename({"INSEE_COM": "insee"}),
            arrondissements.rename({"INSEE_ARM": "insee"}).drop(["INSEE_COM"]),
        ),
        how="vertical",
    )
    gdf = gdf.sort("insee")
    gdf.write_parquet(OUTPUT_FILE)
    return gdf


def load_insee_geometries():
    return gpd.read_parquet(OUTPUT_FILE)


def load_insee_geometries2():
    return st.from_geopandas(gpd.read_parquet(OUTPUT_FILE))


def find_insee(lf: pl.LazyFrame, prefix: str, id_col: str):
    """Add the `*_insee` columns from the `*_lng` and `*_lat` columns."""
    insee_col = f"{prefix}_insee"
    lng_col = f"{prefix}_lng"
    lat_col = f"{prefix}_lat"
    gdf = load_insee_geometries()
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


# TODO. Update when saving with geoparquet is possible.
def find_insee2(lf: pl.LazyFrame, prefix: str, id_col: str):
    """Add the `*_insee` columns from the `*_lng` and `*_lat` columns."""
    insee_col = f"{prefix}_insee"
    lng_col = f"{prefix}_lng"
    lat_col = f"{prefix}_lat"
    point_col = f"{prefix}_point"
    gdf = load_insee_geometries()
    lf = lf.with_columns(
        st.from_coords(pl.concat_arr(lng_col, lat_col)).st.set_srid(4326).alias(point_col)
    )
    lf = lf.st.sjoin(
        gdf.lazy(), left_on=point_col, right_on="geometry", how="left", predicate="within"
    )
    lf = lf.rename({"insee": insee_col})
    # A point can belong to 2 INSEE if it is on the geometry borders. In this case, we only keep one
    # INSEE.
    lf = lf.unique(subset=[id_col])
    return lf

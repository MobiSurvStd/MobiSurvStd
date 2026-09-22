import geopandas as gpd
import polars as pl

from mobisurvstd import SurveyDataReader, read_many
from mobisurvstd.resources.admin_express import load_insee_geometries


def get_survey_area(data: SurveyDataReader, gdf: gpd.GeoDataFrame):
    if data.metadata["type"] == "EMP2019":
        # Ignore EMP2019 (national).
        return
    name = data.metadata["name"]
    print(name)
    insees = data.households.select(pl.col("home_insee").unique()).to_series().to_list()
    geom = (
        gpd.GeoSeries([gdf.loc[gdf["insee"].isin(insees)].union_all()], crs=gdf.crs)
        .concave_hull(ratio=0.25)
        .to_crs("EPSG:4326")
        .iloc[0]
    )
    return [
        {
            "name": name,
            "survey_type": data.metadata["type"],
            "nb_households": data.metadata["nb_households"],
            "start_date": data.metadata["start_date"],
            "end_date": data.metadata["end_date"],
            "geometry": geom,
        }
    ]


# Load INSEE geometries.
print("Reading INSEE geometries")
insee = load_insee_geometries()

data = read_many("./output/all", lambda d: get_survey_area(d, insee), lambda x, y: x + y)

gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
gdf.to_parquet("output/survey_areas.geo.parquet")

import geopandas as gpd
import polars as pl

from mobisurvstd.resources.admin_express import read_admin_express
from mobisurvstd.resources.insee_data import download_insee_data


def test_admin_express():
    gdf = read_admin_express()
    assert isinstance(gdf, gpd.GeoDataFrame)


def test_insee_data():
    df = download_insee_data()
    assert isinstance(df, pl.DataFrame)

import geopandas as gpd
from loguru import logger


def read_detailed_zones(filename: str):
    logger.debug("Reading detailed zones from `{filename}`")
    gdf = gpd.read_file(filename, columns=["IDENT"])
    # Shapefile is in Lambert Nord CRS, although it is not specified in the file.
    gdf.set_crs("EPSG:27561", inplace=True)
    gdf.rename(columns={"IDENT": "detailed_zone_id"}, inplace=True)
    return gdf

import geopandas as gpd
import polars as pl


def get_coords(gdf: gpd.GeoDataFrame, name: str):
    centroids = gdf.geometry.centroid.to_crs("EPSG:4326")
    df = pl.DataFrame(
        {
            f"{name}_id": gdf[f"{name}_id"],
            "lng": centroids.x,
            "lat": centroids.y,
        }
    )
    return df


def add_lng_lat_columns(
    lf: pl.LazyFrame, existing_columns: list[str], coords: pl.DataFrame, prefix: str, name: str
):
    """Add longitude, latitude columns from zone coordinates."""
    zone_col = f"{prefix}_{name}"
    lng_col = f"{prefix}_lng"
    lat_col = f"{prefix}_lat"
    if zone_col in existing_columns:
        lf = lf.with_columns(
            tmp_lng=pl.col(zone_col).replace_strict(
                coords[f"{name}_id"], coords["lng"], default=None
            ),
            tmp_lat=pl.col(zone_col).replace_strict(
                coords[f"{name}_id"], coords["lat"], default=None
            ),
        )
        if lng_col in existing_columns:
            lf = lf.with_columns(pl.col(lng_col).fill_null(pl.col("tmp_lng"))).drop("tmp_lng")
        else:
            lf = lf.rename({"tmp_lng": lng_col})
            existing_columns.append(lng_col)
        if lat_col in existing_columns:
            lf = lf.with_columns(pl.col(lat_col).fill_null(pl.col("tmp_lat"))).drop("tmp_lat")
        else:
            lf = lf.rename({"tmp_lat": lat_col})
            existing_columns.append(lat_col)
    return lf

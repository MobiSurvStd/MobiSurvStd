import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from mobisurvstd import SurveyDataReader, read_many
from mobisurvstd.resources.admin_express import load_insee_geometries


def get_trip_origins(data: SurveyDataReader):
    if data.metadata["type"] in ("EGT2010", "EMP2019"):
        # Ignore EGT2010 (too old) and EMP2019 (national).
        return
    name = data.metadata["name"]
    print(name)
    return data.trips.select("origin_insee", "main_mode_group", name=pl.lit(name))


# Retrive all trips' origin INSEE and main mode group.
origins = read_many("./output", get_trip_origins, lambda x, y: pl.concat((x, y)))

# Compute bicycle share by INSEE.
df = (
    origins.filter(pl.col("origin_insee").is_not_null())
    .group_by("origin_insee")
    .agg(bicycle_share=pl.col("main_mode_group").eq("bicycle").mean(), count=pl.len())
    .filter(pl.col("count") > 30)
)

# Create categories.
bins = list(np.arange(0.0, 0.06, 0.01))
labels = ["0%", "1%", "2%", "3%", "4%", "5%", "6%+"]
df = df.with_columns(bicycle_share_bin=pl.col("bicycle_share").cut(bins, labels=labels))

# Load INSEE geometries and add them to the DataFrame.
gdf = load_insee_geometries().to_crs("epsg:2154")
gdf = gdf.merge(df.to_pandas(), left_on="insee", right_on="origin_insee", how="inner")

cmap = plt.get_cmap("GnBu", len(labels))

# Create a map.
fig, ax = plt.subplots(figsize=(15, 8), subplot_kw={"projection": ccrs.epsg(2154)})
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.set_facecolor("lightgrey")
gdf.plot(
    ax=ax,
    column="bicycle_share_bin",
    cmap=cmap,
    # edgecolor="black",
    # linewidth=0.1,
    legend=True,
    legend_kwds={"title": "Bicycle Share"},
)
ax.set_global()
plt.savefig("docs/src/images/bicycle_shares_by_insee.png", bbox_inches="tight", dpi=200)

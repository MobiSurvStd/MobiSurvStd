import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import polars as pl

from mobisurvstd import SurveyDataReader, read_many
from mobisurvstd.resources.admin_express import load_insee_geometries


def get_home_insee(data: SurveyDataReader):
    if data.metadata["type"] == "EMP2019":
        # Ignore EMP2019 (national).
        return
    name = data.metadata["name"]
    print(name)
    survey_type = data.metadata["type"]
    return data.households.select("home_insee", name=pl.lit(name), survey_type=pl.lit(survey_type))


# Retrive all home' INSEE.
homes = read_many("./output", get_home_insee, lambda x, y: pl.concat((x, y)))

# Compute nb homes by INSEE.
df = homes.drop_nulls()["home_insee"].value_counts()
df = df.filter(pl.col("home_insee").str.slice(0, 2).is_in(("97", "98", "99")).not_())

# Create categories.
bins = [10, 100, 1000]
labels = [
    "[1, 10)",
    "[10, 100)",
    "[100, 1000)",
    "[1000, +∞)",
]
df = df.with_columns(count_bin=pl.col("count").cut(bins, labels=labels))

# Load INSEE geometries and add them to the DataFrame.
gdf = load_insee_geometries().to_crs("epsg:2154")
gdf = gdf.merge(df.to_pandas(), left_on="insee", right_on="home_insee", how="inner")

cmap = plt.get_cmap("Blues", len(labels))
centroids = gdf.geometry.centroid
margin = 1e5
xlim = (centroids.x.min() - margin, centroids.x.max() + margin)
ylim = (centroids.y.min() - margin, centroids.y.max() + margin)

# Create a map.
fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={"projection": ccrs.epsg(2154)})
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.set_facecolor("lightgrey")
gdf.plot(
    ax=ax,
    column="count_bin",
    cmap=cmap,
    legend=True,
    legend_kwds={"title": "# households", "loc": "upper right"},
)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
# ax.set_global()
plt.savefig("docs/src/images/households_by_insee_map.png", bbox_inches="tight", dpi=200)

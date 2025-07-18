from datetime import date

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import polars as pl

from mobisurvstd import SurveyDataReader, read_many


def get_bicycle_share(data: SurveyDataReader):
    if data.metadata["type"] in ("EGT2010", "EMP2019"):
        # Ignore EGT2010 (too old) and EMP2019 (national).
        return
    print(data.metadata["name"])
    df = data.trips.join(data.persons, on="person_id", how="left").select(
        bicycle_weight=pl.col("sample_weight_surveyed").filter(main_mode_group="bicycle").sum(),
        total_weight=pl.col("sample_weight_surveyed").sum(),
    )
    total_weight = df["total_weight"].item()
    bicycle_weight = df["bicycle_weight"].item()
    bicycles_per_household = data.households["nb_bicycles"].mean()
    return [
        {
            "insee": data.metadata["insee"],
            "name": data.metadata["name"],
            "date": data.mean_date(),
            "total_weight": total_weight,
            "bicycle_weight": bicycle_weight,
            "bicycle_share": bicycle_weight / total_weight,
            "bicycles_per_household": bicycles_per_household,
        }
    ]


shares = read_many("./output", get_bicycle_share, lambda x, y: x + y)
df = pl.DataFrame(shares)

markersizes = 200.0 * df["total_weight"].sqrt() / df["total_weight"].sqrt().mean()
fig, ax = plt.subplots(figsize=(9, 7), dpi=200)
scatter = ax.scatter(
    df["date"],
    df["bicycle_share"] * 100,
    s=markersizes,
    c=df["bicycles_per_household"],
    cmap=mpl.colormaps["YlGn"],
    alpha=0.7,
)
cbar = fig.colorbar(scatter, ax=ax)
cbar.set_label("Bicycles per household")
for row in df.sort("total_weight", descending=True)[:5].iter_rows(named=True):
    ax.annotate(
        row["name"],
        (row["date"], 100 * row["bicycle_share"]),
        xytext=(row["date"], 100 * row["bicycle_share"] - 0.2),
        textcoords="data",
        horizontalalignment="center",
        # arrowprops={"width": 1, "headwidth": 5, "headlength": 3},
    )
ax.set_xlabel("Survey date")
ax.set_ylabel("Share of trips by bicycle (%)")
ax.set_xticks([date(y, 6, 1) for y in range(df["date"].min().year, df["date"].max().year + 1)])
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_ylim(bottom=0)
fig.tight_layout()
fig.savefig("./docs/src/images/bicycle_shares.png")

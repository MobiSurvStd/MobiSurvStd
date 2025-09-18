from datetime import date

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import polars as pl

from mobisurvstd import SurveyDataReader, read_many


def get_commuting_time(data: SurveyDataReader):
    if data.metadata["type"] == "EMP2019":
        # Ignore EMP2019 (national).
        return
    name = data.metadata["name"]
    print(name)
    df = (
        data.trips.join(data.persons, on="person_id", how="left")
        .filter(origin_purpose_group="home", destination_purpose_group="work")
        .filter(main_mode_group="car_driver")
        .group_by("pcs_group", "pcs_group_code")
        .agg(
            name=pl.lit(name),
            date=pl.lit(data.mean_date()),
            count=pl.len(),
            weight=pl.col("sample_weight_surveyed").sum(),
            commuting_time=(pl.col("travel_time") * pl.col("sample_weight_surveyed")).sum()
            / pl.col("sample_weight_surveyed").sum(),
        )
    )
    return df


df = read_many("./output/all", get_commuting_time, lambda x, y: pl.concat((x, y)))

# Remove the least used PCS codes (agriculteurs, artisans, retraités).
df = df.filter(pl.col("pcs_group_code").is_between(3, 6))

for (code,), df_code in df.partition_by("pcs_group_code", as_dict=True).items():
    pcs = df_code["pcs_group"][0]
    markersizes = 200.0 * df_code["weight"].sqrt() / df_code["weight"].sqrt().mean()
    fig, ax = plt.subplots(figsize=(9, 7), dpi=200)
    scatter = ax.scatter(df_code["date"], df_code["commuting_time"], s=markersizes, alpha=0.7)
    for row in df_code.sort("weight", descending=True)[:10].iter_rows(named=True):
        ax.annotate(
            row["name"],
            (row["date"], row["commuting_time"]),
            xytext=(row["date"], row["commuting_time"] - 1),
            textcoords="data",
            horizontalalignment="center",
            # arrowprops={"width": 1, "headwidth": 5, "headlength": 3},
        )
    ax.set_title(pcs)
    ax.set_xlabel("Survey date")
    ax.set_ylabel("Average commuting time (min.)")
    ax.set_xticks(
        [date(y, 6, 1) for y in range(df_code["date"].min().year, df_code["date"].max().year + 1)]
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.tight_layout()
    fig.savefig(f"./docs/src/images/commuting_time_{code}.png")

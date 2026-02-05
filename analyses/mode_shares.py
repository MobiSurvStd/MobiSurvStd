import matplotlib.pyplot as plt
import matplotlib.style
import matplotlib.ticker
import numpy as np
import polars as pl

from mobisurvstd import SurveyDataReader, read_many

matplotlib.style.use("seaborn-v0_8-colorblind")


def get_mode_share(data: SurveyDataReader):
    print(data.metadata["name"])
    df = (
        data.trips.join(data.persons, on="person_id", how="left")
        .filter(pl.col("main_mode_group").is_not_null())
        .group_by(mode="main_mode_group")
        .agg(len=pl.len(), weight=pl.col("sample_weight_surveyed").sum())
        .with_columns(share=pl.col("weight") / pl.col("weight").sum())
    )
    shares = dict(zip(df["mode"], df["share"]))
    return [
        {
            "survey_type": data.metadata["type"],
            "insee": data.metadata["insee"],
            "survey_name": data.metadata["name"],
            "date": data.mean_date(),
            "total_trips": df["len"].sum(),
            "total_weight": df["weight"].sum(),
        }
        | shares
    ]


shares = read_many("./output/all/", get_mode_share, lambda x, y: x + y)
df = pl.DataFrame(shares)

modes = [
    "car_driver",
    "walking",
    "car_passenger",
    "public_transit",
    "motorcycle",
    "bicycle",
    "other",
]
df = df.with_columns(pl.col(modes).fill_null(0.0))
df = df.sort(modes[0], descending=True)

fig, ax = plt.subplots(figsize=(8, 18))
total = np.zeros(len(df))
for mode in modes:
    values = df[mode].to_numpy()
    ax.barh(df["survey_name"], values, height=0.95, label=mode, left=total)
    total += values
ax.set(xlim=(0, 1), xlabel="Share", ylim=(-0.5, len(df) - 0.5))
ax.legend(title="Modes", bbox_to_anchor=(1.01, 0.5))
ax.grid(which="major", axis="x")
ax.xaxis.set_label_position("top")
ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1))
ax.tick_params(top=True, labeltop=True, bottom=True, labelbottom=True)
fig.tight_layout()
fig.savefig("./docs/src/images/mode_shares.png", dpi=300)

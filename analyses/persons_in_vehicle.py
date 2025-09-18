import matplotlib.pyplot as plt
import numpy as np
import polars as pl

from mobisurvstd import SurveyDataReader, read_many


def get_legs(data: SurveyDataReader):
    name = data.metadata["name"]
    print(name)
    df = (
        data.legs.join(data.trips, on="trip_id", how="left")
        .join(
            data.persons.select("person_id", "sample_weight_surveyed"), on="person_id", how="left"
        )
        .drop("original_leg_id", "original_trip_id")
        .with_columns(survey_name=pl.lit(name))
    )
    return df


df = read_many("./output/all/", get_legs, lambda x, y: pl.concat((x, y)))

df = df.with_columns(
    valid_sequence=pl.col("destination_purpose_group")
    .eq("work")
    .any()
    .over("survey_name", "person_id", "home_sequence_index"),
    work_trip_id=pl.col("trip_id")
    .filter(pl.col("destination_purpose_group").eq("work"))
    .first()
    .over("survey_name", "person_id", "home_sequence_index"),
)

df = df.filter("valid_sequence", pl.col("trip_id") <= pl.col("work_trip_id"))
df = df.filter(
    pl.col("nb_persons_in_vehicle").is_not_null(),
    pl.col("mode_group").eq("car_driver"),
)

df = df.filter(pl.col("leg_euclidean_distance_km").is_null().mean().over("survey_name") < 0.1)

df = df.filter(
    pl.col("leg_euclidean_distance_km")
    .sum()
    .over("survey_name", "person_id", "home_sequence_index")
    < 100.0
)

df = df.filter(pl.col("person_id").n_unique().over("survey_name") > 3000)

df = df.with_columns(nb_persons_in_vehicle=pl.min_horizontal("nb_persons_in_vehicle", 5))

shares = (
    df.group_by("survey_name", "nb_persons_in_vehicle")
    .agg(value=(pl.col("leg_euclidean_distance_km") * pl.col("sample_weight_surveyed")).sum())
    .with_columns(share=pl.col("value") / pl.col("value").sum().over("survey_name"))
    .sort(
        pl.col("share").filter(pl.col("nb_persons_in_vehicle") == 1).sum().over("survey_name"),
        "nb_persons_in_vehicle",
    )
)

surveys = shares["survey_name"].unique(maintain_order=True)

idx = pl.DataFrame(
    {"survey_name": surveys, "nb_persons_in_vehicle": [list(range(1, 6))] * len(surveys)}
).explode("nb_persons_in_vehicle")
shares = idx.join(shares, on=["survey_name", "nb_persons_in_vehicle"], how="left").with_columns(
    share=pl.col("share").fill_null(0.0)
)

fig, ax = plt.subplots(figsize=(5.5, 4))
bottom = np.zeros(len(surveys))
colors = plt.cm.Set3.colors[:5]
for i in range(1, 6):
    values = shares.filter(nb_persons_in_vehicle=i)["share"].to_numpy()
    alpha = 1.0 if i == 1 else 0.5
    ax.bar(surveys, values, width=0.95, label=i, bottom=bottom, color=colors[i - 1], alpha=alpha)
    if i == 1:
        for j, (survey, value) in enumerate(zip(surveys, values)):
            ax.text(
                j, bottom[j] + value / 2, f"{value:.1%}", ha="center", va="center", color="black"
            )
    bottom += values
ax.set_xticks(surveys)
ax.set_xticklabels(surveys, rotation=60)
ax.margins(x=0.01)
ax.set_ylabel("Share of trips' euclidean distance")
ax.set_ylim(0, 1)
ax.set_title("Share of home-to-work trips by vehicle occupancy")
ax.legend(title="# persons\nin car", bbox_to_anchor=(1.01, 0.75))
fig.tight_layout()
fig.savefig("nb_persons_in_vehicle_shares.png", dpi=200)

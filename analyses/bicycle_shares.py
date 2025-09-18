import polars as pl
import seaborn as sns
from matplotlib.ticker import PercentFormatter

from mobisurvstd import SurveyDataReader, read_many


def get_bicycle_share(data: SurveyDataReader):
    if data.metadata["type"] == "EMP2019":
        # Ignore EMP2019 (national).
        return
    print(data.metadata["name"])
    df = data.trips.join(data.persons, on="person_id", how="left").select(
        bicycle_weight=pl.col("sample_weight_surveyed").filter(main_mode_group="bicycle").sum(),
        total_weight=pl.col("sample_weight_surveyed").sum(),
        total_trips=pl.len(),
    )
    total_weight = df["total_weight"].item()
    total_trips = df["total_trips"].item()
    bicycle_weight = df["bicycle_weight"].item()
    bicycles_per_household = data.households["nb_bicycles"].mean()
    return [
        {
            "insee": data.metadata["insee"],
            "survey_type": data.metadata["type"],
            "survey_name": data.metadata["name"],
            "date": data.mean_date(),
            "total_weight": total_weight,
            "total_trips": total_trips,
            "bicycle_weight": bicycle_weight,
            "bicycle_share": bicycle_weight / total_weight,
            "bicycles_per_household": bicycles_per_household,
        }
    ]


shares = read_many("./output/all", get_bicycle_share, lambda x, y: x + y)
df = pl.DataFrame(shares)
df = df.with_columns(pl.col("bicycles_per_household").fill_null(-1.0))
df = df.sort("total_trips")

g = sns.relplot(
    height=4,
    aspect=1.5,
    data=df,
    x="date",
    y="bicycle_share",
    size="total_trips",
    sizes=(100, 1000),
    hue="survey_type",
)
g.ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
g.savefig("./docs/src/images/bicycle_shares.png")

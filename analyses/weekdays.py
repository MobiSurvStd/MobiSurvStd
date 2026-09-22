import polars as pl

from mobisurvstd import SurveyDataReader, read_many


def get_weekdays(data: SurveyDataReader):
    if data.metadata["type"] == "EMP2019":
        # Ignore EMP2019 (national).
        return
    name = data.metadata["name"]
    print(name)
    nb_persons = data.persons["is_surveyed"].sum()
    df = (
        data.trips.group_by("destination_purpose_group", "trip_weekday")
        .agg(pl.col("travel_time").sum() / 60 / nb_persons)
        .with_columns(name=pl.lit(name))
    )
    return df


df = read_many("./output/all", get_weekdays, lambda x, y: pl.concat((x, y)))

df = (
    df.group_by("trip_weekday", "destination_purpose_group")
    .agg(pl.col("travel_time").mean())
    .sort("trip_weekday", "destination_purpose_group")
    .drop_nulls()
)

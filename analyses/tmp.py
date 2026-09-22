import polars as pl

from mobisurvstd import SurveyDataReader, read_many


def get_weekdays(data: SurveyDataReader):
    if data.metadata["type"] == "EMP2019":
        # Ignore EMP2019 (national).
        return
    name = data.metadata["name"]
    print(name)
    df = data.persons.filter(pl.col("age") > 5).select(
        "person_id", "is_surveyed", name=pl.lit(name)
    )
    return df


df = read_many("./output/all", get_weekdays, lambda x, y: pl.concat((x, y)))

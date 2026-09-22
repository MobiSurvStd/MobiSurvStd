import polars as pl

from mobisurvstd import SurveyDataReader, read_many


def get_legs(data: SurveyDataReader):
    name = data.metadata["name"]
    print(name)
    if name != "EGT2020":
        return 0
    person_ids = data.persons.filter(
        pl.col("reference_person_link").eq("spouse").any().over("household_id"),
        pl.col("reference_person_link").is_in(("reference_person", "spouse")),
    )["person_id"].to_list()
    trips = data.trips.filter(pl.col("person_id").is_in(person_ids))
    trips = trips.filter(
        pl.col("destination_purpose_group").eq("work"),
        pl.col("destination_purpose_group").eq("escort").any().over("household_id"),
        pl.col("main_mode_group").eq("car_driver").any().over("household_id"),
        pl.col("main_mode_group").eq("car_passenger").any().over("household_id"),
    )
    return len(trips)


n = read_many("./output/all/", get_legs, lambda x, y: x + y)

import polars as pl

from mobisurvstd import SurveyDataReader, read_many


def get_pt_sub(data: SurveyDataReader):
    name = data.metadata["name"]
    print(name)
    df = (
        data.trips.join(data.persons, on="person_id")
        .filter(main_mode_group="public_transit")
        .group_by(pt_sub="has_public_transit_subscription")
        .agg(w=pl.col("sample_weight_surveyed").sum())
        .with_columns(share=pl.col("w") / pl.col("w").sum())
        .select("pt_sub", "share", name=pl.lit(name))
    )
    return df


df = read_many("./output/all", get_pt_sub, lambda x, y: pl.concat((x, y)))

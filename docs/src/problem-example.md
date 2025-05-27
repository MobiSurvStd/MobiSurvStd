# Why MobiSurvStd?

```python
import polars as pl
pers = pl.read_csv("Csv/Fichiers_Standard/brest_2018_std_pers.csv", separator=";")
depl = pl.read_csv("Csv/Fichiers_Standard/brest_2018_std_depl.csv", separator=";")
print(
    depl
    .join(
        pers,
        left_on=["DMET", "ZFD", "ECH", "PER"],
        right_on=["PMET", "ZFP", "ECH", "PER"]
    )
    .group_by("P2")
    .agg(
        (pl.col("D9") * pl.col("COEP")).sum()
        / pl.col("COEP").sum()
    )
    .sort("P2")
)
```

```
shape: (2, 2)
┌─────┬───────────┐
│ P2  ┆ D9        │
│ --- ┆ ---       │
│ i64 ┆ f64       │
╞═════╪═══════════╡
│ 1   ┆ 18.145294 │
│ 2   ┆ 15.915749 │
└─────┴───────────┘
```

```python
import polars
pers = pl.read_parquet("persons.parquet")
trips = pl.read_parquet("trips.parquet")
print(
    trips
    .join(pers, on="person_id")
    .group_by("woman")
    .agg(
        (pl.col("travel_time") * pl.col("sample_weight_surveyed")).sum()
        / pl.col("sample_weight_surveyed").sum()
    )
    .sort("woman")
)
```

```
┌───────┬─────────────┐
│ woman ┆ travel_time │
│ ---   ┆ ---         │
│ bool  ┆ f64         │
╞═══════╪═════════════╡
│ false ┆ 18.145294   │
│ true  ┆ 15.915749   │
└───────┴─────────────┘
```

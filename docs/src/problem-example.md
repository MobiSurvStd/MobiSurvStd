# Why MobiSurvStd?

Consider the following example: you want to compare the average travel time over a day, between men
and women, for various territories / years.

## EMC² Survey

With the EMC² standard, you can write a single code that can be run on any EMC² survey (with only
minor changes to filenames).
For example, for the survey of Brest 2018 and using the [polars](https://pola.rs/) Python library,
the code would look like:

```python
# === Read average travel time by gender for EMC2 surveys. ===
import polars as pl
# Read the person (personne) file with `;` as value separator.
pers = pl.read_csv(
    "Csv/Fichiers_Standard/brest_2018_std_pers.csv",
    separator=";",
)
# Read the trip (déplacements) file with `;` as value separator.
depl = pl.read_csv(
    "Csv/Fichiers_Standard/brest_2018_std_depl.csv",
    separator=";",
)
print(
    depl
    # Join the two DataFrames using the 4 index columns.
    # (Notice the different column name between the two DataFrames.)
    .join(
        pers,
        left_on=["DMET", "ZFD", "ECH", "PER"],
        right_on=["PMET", "ZFP", "ECH", "PER"],
    )
    # Group trips by gender of the person (column "P2").
    .group_by("P2")
    .agg(
        # Compute the average travel time (column "D9"), weighted by sample
        # weight (column "COEP").
        (pl.col("D9") * pl.col("COEP")).sum()
        / pl.col("COEP").sum()
    )
    .sort("P2")
)
```

The code would print (1 is for men, 2 is for women):

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

## EGT2020 Survey

Now, assume that you want to compare with the values for Île-de-France.
You would need to use the EGT2020 (or EGT2010) format and write a different but similar code:

```python
# === Read average travel time by gender for EGT2020 survey. ===
import polars as pl
# Read the person (individu) file with `;` as value separator, proper encoding
# and infer_schema_length=10000 so that variable dtypes are correctly read.
pers = pl.read_csv(
    "Csv/b_individu_egt1820.csv",
    separator=";",
    encoding="latin1",
    infer_schema_length=10000,
)
# Read the trip (déplacements) file with `;` as value separator and proper
# encoding.
depl = pl.read_csv(
    "Csv/c_deplacement_egt1820.csv",
    separator=";",
    encoding="latin1",
)
print(
    depl
    # Join the two DataFrames using the 2 index columns.
    .join(pers, on=["IDCEREMA", "NP"])
    # Group trips by gender of the person (column "SEXE").
    .group_by("SEXE")
    .agg(
        # Compute the average travel time (column "DUREE"), weighted by sample
        # weight (column "POIDSI").
        (pl.col("DUREE") * pl.col("POIDSI")).sum()
        / pl.col("POIDSI").sum()
    )
    .sort("SEXE")
)
```

The code would print (1 is for men, 2 is for women):

```
shape: (2, 2)
┌──────┬───────────┐
│ SEXE ┆ DUREE     │
│ ---  ┆ ---       │
│ i64  ┆ f64       │
╞══════╪═══════════╡
│ 1    ┆ 26.753822 │
│ 2    ┆ 23.716359 │
└──────┴───────────┘
```

## MobiSurvStd

Instead of having to write 2 (or more) different codes, MobiSurvStd allows you to write a single
cleaner code that can run on many travel surveys.
With MobiSurvStd, the code to compute average travel time by gender would be:

```python
# === Read average travel time by gender with MobiSurvStd. ===
import polars as pl
# Read the persons parquet file.
pers = pl.read_parquet("persons.parquet")
# Read the trips parquet file.
trips = pl.read_parquet("trips.parquet")
print(
    trips
    # Join the two DataFrames using the "person_id" column.
    .join(pers, on="person_id")
    # Group trips by gender of the person (column "woman").
    .group_by("woman")
    .agg(
        # Compute the average travel time (column "travel_time"), weighted by
        # sample weight (column "sample_weight_surveyed").
        (pl.col("travel_time") * pl.col("sample_weight_surveyed")).sum()
        / pl.col("sample_weight_surveyed").sum()
    )
    .sort("woman")
)
```

The code would print (for the Brest 2018 EMC²):

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

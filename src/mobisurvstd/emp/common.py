import polars as pl


def insee_density_col(col: str):
    # The encoding of the file is incorrect so we need to resort to the following function to
    # convert INSEE density names to codes.
    return (
        pl.when(pl.col(col).eq("Grands centres urbains"))
        .then(1)
        .when(pl.col(col).str.starts_with("Centres urbanis interm"))
        .then(2)
        .when(pl.col(col).eq("Ceintures urbaines"))
        .then(3)
        .when(pl.col(col).eq("Petites villes"))
        .then(4)
        .when(pl.col(col).eq("Bourgs ruraux"))
        .then(5)
        .when(pl.col(col).str.contains("habitat dispers"))
        .then(6)
        .when(pl.col(col).str.contains("habitat tr"))
        .then(7)
    )

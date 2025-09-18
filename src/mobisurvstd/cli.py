from typing import Optional

import typer
from typing_extensions import Annotated

from .main import bulk_standardize, standardize
from .resources import clear_cache


def clear_cache_callback(value: bool):
    if value:
        clear_cache()
        raise typer.Exit()


def standardizer(
    source: Annotated[
        str,
        typer.Argument(
            help="Path to the directory or the zipfile where the survey data is located."
        ),
    ],
    output_directory: Annotated[
        str,
        typer.Argument(
            help="Path to the directory where the standardized survey should be stored."
        ),
    ],
    survey_type: Annotated[
        str | None,
        typer.Option(
            help="Format of the original survey. Possible values: `emc2`, `emp2019`, `egt2010`, `egt2020`, `edgt`, `edvm`, `emd`."
        ),
    ] = None,
    bulk: bool = typer.Option(
        False, "--bulk", help="Import surveys in bulk from the given directory"
    ),
    skip_spatial: bool = typer.Option(False, "--skip-spatial", help="Do not read spatial data"),
    no_validation: bool = typer.Option(
        False,
        "--no-validation",
        help="Do not validate the standardized data (some guarantees might not be satisfied)",
    ),
    clear_cache: Annotated[
        Optional[bool],
        typer.Option(
            "--clear-cache", callback=clear_cache_callback, help="Clear the cache data and exit"
        ),
    ] = None,
):
    """Mobility Survey Standardizer: a Python command line tool to convert mobility surveys to a
    clean standardized format.
    """
    if bulk:
        bulk_standardize(
            source,
            output_directory,
            survey_type,
            skip_spatial=skip_spatial,
            no_validation=no_validation,
        )
    else:
        standardize(
            source,
            output_directory,
            survey_type,
            skip_spatial=skip_spatial,
            no_validation=no_validation,
        )


app = typer.Typer()
app.command()(standardizer)


if __name__ == "__main__":
    app()

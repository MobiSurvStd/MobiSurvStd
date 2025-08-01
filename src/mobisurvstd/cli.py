import typer
from typing_extensions import Annotated

from .main import bulk_standardize, standardize


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
    bulk: Annotated[
        bool, typer.Option(help="Import surveys in bulk from the given directory")
    ] = False,
):
    """Mobility Survey Standardizer: a Python command line tool to convert mobility surveys to a
    clean standardized format.
    """
    if bulk:
        bulk_standardize(source, output_directory, survey_type)
    else:
        standardize(source, output_directory, survey_type)


app = typer.Typer()
app.command()(standardizer)


if __name__ == "__main__":
    app()

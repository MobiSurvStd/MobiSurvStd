import os
from zipfile import ZipFile

from loguru import logger

from . import edgt, edvm, egt2010, egt2020, emc2, emd, emp
from .classes import SurveyData
from .utils import guess_survey_type, read_source


def standardize(
    source: str,
    output_directory: str | None = None,
    survey_type: str | None = None,
    add_name_subdir: bool = False,
    skip_spatial: bool = False,
) -> SurveyData | None:
    """Converts a mobility survey to a clean standardized format.

    Parameters
    ----------
    source
        Path to a directory or zipfile.
        When a directory is given, it must be the top-level directory of the survey to be converted.
        When a zipfile is given, the directories within the zipfile are read recursively so that the
        survey's files can be found no matter how deeply nested the zipfile is.
    output_directory
        Path to the directory where the standardized survey should be stored.
        If the directory does not exist, MobiSurvStd will create it (recursively).
        If None, the standardized survey will not be saved.
    survey_type
        String indicating the type of the survey to be converted.
        If the value is omitted, MobiSurvStd will do its best to guess the survey type.
        Possible values: "emc2", "emp2019", "egt2020", "egt2010", "edgt", "edvm", "emd".
    add_name_subdir
        Whether the standardized survey is stored directly in `output_directory` or within a
        subdirectory of `output_directory`.
        If True, the standardized survey is stored in a subdirectory within `output_directory`. The
        subdirectory name is the survey name.
        If False (default), the standardized survey is stored directly in `output_directory`.
    skip_spatial
        If True, MobiSurvStd will not try to read spatial data from the survey.
        This means that special locations, detailed zones, and draw zones will not be read and
        proposed as an output.
        Some variables (e.g., home_lng, home_lat) might also be missing as a result.

    Returns
    -------
    SurveyData

    Examples
    --------

    Read the EGT2020 survey from the `original_egt2020.zip` file and store the standardized version
    in the `standardized_egt2020` directory.

    >>> import mobisurvstd
    >>> mobisurvstd.standardize(
    >>>     "original_egt2020.zip",
    >>>     "standardized_egt2020",
    >>>     survey_type="egt2020",
    >>> )
    """
    dir_or_zip = read_source(source)
    if dir_or_zip is None:
        return None
    if survey_type is None:
        survey_type = guess_survey_type(dir_or_zip)
    if survey_type is None:
        # Survey type could not be guessed correctly.
        logger.error(f"Cannot guess survey type from source `{source}`")
        return None
    # Note that I actually define here some aliases for the `survey_type` argument that are not
    # documented (because why not?).
    if survey_type == "emc2":
        survey_data = emc2.standardize(dir_or_zip, skip_spatial=skip_spatial)
    elif survey_type == "edgt":
        survey_data = edgt.standardize(dir_or_zip, skip_spatial=skip_spatial)
    elif survey_type == "edvm":
        survey_data = edvm.standardize(dir_or_zip, skip_spatial=skip_spatial)
    elif survey_type == "emd":
        survey_data = emd.standardize(dir_or_zip, skip_spatial=skip_spatial)
    elif survey_type in ("emp", "emp2019"):
        survey_data = emp.standardize(dir_or_zip, skip_spatial=skip_spatial)
    elif survey_type in ("egt2020", "egt20", "egt1820"):
        survey_data = egt2020.standardize(dir_or_zip, skip_spatial=skip_spatial)
    elif survey_type in ("egt2010", "egt10"):
        survey_data = egt2010.standardize(dir_or_zip, skip_spatial=skip_spatial)
    else:
        logger.error(f"Unsupported survey type: {survey_type}")
        return None
    if survey_data is None:
        source_name = source.filename if isinstance(source, ZipFile) else source
        logger.error(f"Failed to read survey from `{source_name}`")
        return None
    if output_directory is not None:
        if add_name_subdir:
            output_directory = os.path.join(output_directory, survey_data.metadata["name"])
        survey_data.save(output_directory)
    # survey_data = survey_data.clean()
    return survey_data


def bulk_standardize(
    directory: str,
    output_directory: str,
    survey_type: str | None = None,
    skip_spatial: bool = False,
):
    """Standardizes mobility surveys in bulk from a given directory.

    MobiSurvStd will explore all directories and zipfiles within `directory`, try to standardize
    them and store the standardized data in `output_directory`.

    Parameters
    ----------
    directory
        Path to a directory.
        The directory must contain survey data, stored within directories or zipfiles.
    output_directory
        Path to the directory where the standardized surveys should be stored.
        If the directory does not exist, MobiSurvStd will create it (recursively).
        Each survey read is stored in a subdirectory whose name is the survey's name.
    survey_type
        String indicating the type of the surveys to be converted.
        If the directory contains surveys of different types, leave this value to None and
        MobiSurvStd will try to guess the type of each survey.
        Possible values: "emc2", "emp2019", "egt2020", "egt2010", "edgt", "edvm", "emd".
    skip_spatial
        If True, MobiSurvStd will not try to read spatial data from the surveys.
        This means that special locations, detailed zones, and draw zones will not be read and
        proposed as an output.
        Some variables (e.g., home_lng, home_lat) might also be missing as a result.

    Examples
    --------

    Read all surveys in the `my_surveys` directory and store their standardized version in the
    `standardized_surveys` directory.

    >>> import mobisurvstd
    >>> mobisurvstd.bulk_standardize("my_surveys", "standardized_surveys")
    """
    n = bulk_standardize_impl(directory, output_directory, survey_type, skip_spatial, n=0)
    if n > 0:
        logger.success(f"Successfully read {n} surveys from `{directory}`")
    if n == 0:
        logger.error(f"No survey could be read from `{directory}`")


def bulk_standardize_impl(
    directory: str,
    output_directory: str,
    survey_type: str | None = None,
    skip_spatial: bool = False,
    n: int = 0,
):
    if not os.path.isdir(directory):
        logger.error(f"Not a valid directory: {directory}")
        return n
    for inner in os.listdir(directory):
        source = os.path.join(directory, inner)
        if os.path.isdir(source):
            maybe_type = guess_survey_type(directory)
            if maybe_type is None:
                # The directory does not seem to be a valid survey.
                # We try to iteratively read that directory.
                n = bulk_standardize_impl(source, output_directory, survey_type, skip_spatial, n)
            else:
                data = standardize(
                    source,
                    output_directory,
                    survey_type,
                    add_name_subdir=True,
                    skip_spatial=skip_spatial,
                )
                if data is not None:
                    n += 1
        if source.endswith(".zip"):
            data = standardize(
                source,
                output_directory,
                survey_type,
                add_name_subdir=True,
                skip_spatial=skip_spatial,
            )
            if data is not None:
                n += 1
    return n

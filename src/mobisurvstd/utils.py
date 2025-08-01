import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from zipfile import BadZipFile, ZipFile

import polars as pl
import requests
from loguru import logger


def read_source(source: str) -> str | ZipFile | None:
    """Converts the input string given by the user as either a directory path or a ZipFile.

    Returns None if the source is not a directory or zipfile.
    """
    if os.path.isdir(source):
        return source
    elif os.path.isfile(source):
        try:
            z = ZipFile(source)
        except BadZipFile as e:
            logger.error(f"Not a valid zipfile: `{source}`:\n{e}")
            return None
        return z
    else:
        logger.error(f"Not a directory nor a valid zipfile: `{source}`")
        return None


def find_file(
    source: str | ZipFile, regex: str, subdir: str = "", as_url=False
) -> str | bytes | None:
    """Reads the files in a source directory or zipfile and returns the first file that matches the
    given regex.

    Optionally, the `subdir` parameter can be used to constrain the search to a sub directory.

    Returns `None` if there is no file that matches the regex.
    """
    if isinstance(source, str):
        directory = os.path.join(source, subdir)
        if os.path.isdir(directory):
            return find_file_in_directory(directory, regex)
        else:
            return None
    elif isinstance(source, ZipFile):
        return find_file_in_zipfile(source, subdir, regex, as_url)
    else:
        logger.error(f"Invalid source: `{source}`")
        return None


def find_file_in_directory(directory: str, regex: str) -> str | None:
    """Returns the path to the first file that matches the given regex in the input directory.

    Returns `None` if there is no file that matches the regex.
    """
    pattern = re.compile(regex, flags=re.IGNORECASE)
    for filename in os.listdir(directory):
        if pattern.match(filename):
            return os.path.join(directory, filename)


def find_file_in_zipfile(z: ZipFile, subdir: str, regex: str, as_url=False) -> str | bytes | None:
    """Returns the first file that matches the given regex in the input ZipFile.

    If `as_url` is `True`, the file is returned as a url "zip://[ZIPFILE_PATH]!/FILE_PATH", suitable
    to be open by geopandas.

    If `as_url` is `False`, the file is returned as a bytes, suitable to be open by polars.

    Optionally, the search can be constrained to the given `subdir`.

    Returns `None` if there is no file that matches the regex.
    """
    if subdir:
        pattern = re.compile(f".*{subdir}/{regex}", flags=re.IGNORECASE)
    else:
        pattern = re.compile(regex, flags=re.IGNORECASE)
    for fileinfo in z.infolist():
        if pattern.match(fileinfo.filename):
            if as_url:
                return f"zip://{z.filename}!/{fileinfo.filename}"
            else:
                return z.read(fileinfo)


@contextmanager
def tmp_download(url):
    """Downloads a file from the given url to a temporary location, then deletes it."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        logger.debug(f"Requesting url: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        logger.debug(f"Saving returned data to file `{tmp_file.name}`")
        with open(tmp_file.name, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        try:
            yield tmp_file.name
        finally:
            try:
                logger.debug(f"Removing temporary file `{tmp_file.name}`")
                os.remove(tmp_file.name)
            except OSError as e:
                logger.debug(f"Removing temporary file `{tmp_file.name}` failed:\n{e}")
                pass


def guess_survey_type(source: str | ZipFile) -> str | None:
    """Returns the type of the survey data stored in `source` as a string.

    If the survey type cannot be guessed, returns None.
    """
    if find_file(source, "k_individu_public_V3.csv", as_url=True):
        return "emp2019"
    if find_file(source, "a_menage_egt1820.csv", subdir="Csv", as_url=True):
        return "egt2020"
    if find_file(source, "menages_semaine.csv", subdir="Csv", as_url=True):
        return "egt2010"
    if find_file(source, ".*_std_faf_men.csv", subdir="Csv", as_url=True):
        return "edgt"
    if find_file(source, ".*evreux_2018_std_men.csv", subdir="Csv", as_url=True):
        # Special case for Evreux 2018 which is an EMC2 survey but is defined as an EDVM survey in
        # the IDM1 variable.
        return "emc2"
    if find_file(source, ".*gap_2018_std_men.csv", subdir="Csv", as_url=True):
        # Special case for Gap 2018 which is an EMC2 survey but is defined as an EDVM survey in
        # the IDM1 variable.
        return "emc2"
    if find_file(source, ".*poitiers_2018_std_men.csv", subdir="Csv", as_url=True):
        # Special case for Poitiers 2018 which is an EMC2 survey but is defined as an EDVM survey in
        # the IDM1 variable.
        return "emc2"
    if bytes := find_file(source, ".*_std_men.csv", subdir=os.path.join("Csv"), as_url=False):
        survey_type = (
            pl.scan_csv(bytes, separator=";", schema_overrides={"IDM1": pl.UInt8})
            .select(pl.col("IDM1").first())
            .collect()
            .item()
        )
        if survey_type == 1:
            # EMD.
            return "emd"
        elif survey_type == 2:
            # EDGT.
            logger.warning(
                "Survey is of type EDGT (IDM1 = 2) but the files are not organized as expected"
            )
            return None
        elif survey_type == 3:
            # EDVM.
            return "edvm"
        elif survey_type == 4:
            # Autre.
            # The only survey I observed with that value is Puisaye-Forterre 2012 which is actually
            # an EDVM.
            return "edvm"
        elif survey_type == 5:
            # EMC2.
            return "emc2"
        elif survey_type == 6:
            # MC3 (EMC2 surveys disturbed by Covid-19).
            return "emc2"
    return None

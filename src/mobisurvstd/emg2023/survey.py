from zipfile import ZipFile

import polars as pl
from loguru import logger

from mobisurvstd.common.clean import clean
from mobisurvstd.utils import find_file

from .deplacements import standardize_distances, standardize_legs, standardize_trips
from .menages import standardize_households
from .personnes import standardize_persons


def standardize(source: str | ZipFile, skip_spatial: bool = False, skip_insee: bool = False):
    source_name = source.filename if isinstance(source, ZipFile) else source
    logger.info(f"Standardizing EMG2023 survey from `{source_name}`")

    filename = persons_filename(source)
    if not filename:
        logger.error(f"Missing persons file: {filename}")
        return None

    # Households.
    households = standardize_households(filename, skip_insee)

    # Persons.
    persons = standardize_persons(filename, households)

    # Distances.
    filename = distances_filename(source)
    distances = standardize_distances(filename) if filename else None

    # Trips.
    filename = trips_filename(source)
    if not filename:
        logger.error(f"Missing trips file: {filename}")
        return None

    trips = standardize_trips(filename, persons, skip_insee, distances=distances)

    legs = standardize_legs(filename, trips)

    return clean(
        households=households,
        persons=persons,
        trips=trips,
        legs=legs,
        cars=pl.LazyFrame({"car_id": []}),
        motorcycles=pl.LazyFrame({"motorcycle_id": []}),
        survey_type="EMG2023",
        survey_name="EMG2023",
        main_insee="75056",
    )


def persons_filename(source: str | ZipFile):
    return find_file(source, r"EMG_BD_Individus_.+\.xlsx")


def trips_filename(source: str | ZipFile):
    return find_file(source, r"EMG_BD_Deplacements_.+\.xlsx")


def distances_filename(source: str | ZipFile):
    return find_file(source, r"EMG_Distance.xlsx")

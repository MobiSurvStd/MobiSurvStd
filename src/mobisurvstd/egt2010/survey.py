import os
from zipfile import ZipFile

from loguru import logger

from mobisurvstd.common.clean import clean
from mobisurvstd.utils import find_file

from .deplacements import standardize_trips
from .menages import standardize_cars, standardize_households, standardize_motorcycles
from .personnes import standardize_persons
from .trajets import standardize_legs
from .zones import read_detailed_zones


def standardize(source: str | ZipFile, skip_spatial: bool = False):
    source_name = source.filename if isinstance(source, ZipFile) else source
    logger.info(f"Standardizing EGT2010 survey from `{source_name}`")
    if skip_spatial:
        detailed_zones = None
    else:
        # Detailed zones.
        filename = detailed_zones_filename(source)
        if filename is None:
            logger.error("Missing detailed zones file")
            return None
        detailed_zones = read_detailed_zones(filename)
    # Households.
    filename = households_filename(source)
    if filename is None:
        logger.error("Missing households file")
        return None
    households = standardize_households(filename)
    # Cars.
    cars = standardize_cars(filename, households)
    # motorcycles.
    motorcycles = standardize_motorcycles(filename, households)
    # Persons.
    filename = persons_filename(source)
    if filename is None:
        logger.error("Missing persons file")
        return None
    persons = standardize_persons(filename, households)
    # Trips.
    filename = trips_filename(source)
    if filename is None:
        logger.error("Missing trips file")
        return None
    trips = standardize_trips(filename, persons, households)
    # Legs.
    filename = legs_filename(source)
    if filename is None:
        logger.error("Missing legs file")
        return None
    legs = standardize_legs(filename, trips, cars, motorcycles, detailed_zones)
    return clean(
        households=households,
        persons=persons,
        trips=trips,
        legs=legs,
        cars=cars,
        motorcycles=motorcycles,
        detailed_zones=detailed_zones,
        survey_type="EGT2010",
        survey_name="EGT2010",
        main_insee="75056",
    )


def households_filename(source: str | ZipFile):
    return find_file(source, "menages_semaine.csv", subdir="Csv")


def persons_filename(source: str | ZipFile):
    return find_file(source, "personnes_semaine.csv", subdir="Csv")


def trips_filename(source: str | ZipFile):
    return find_file(source, "deplacements_semaine.csv", subdir="Csv")


def legs_filename(source: str | ZipFile):
    return find_file(source, "trajets_semaine.csv", subdir="Csv")


def detailed_zones_filename(source: str | ZipFile):
    return find_file(
        source, "carr100m.shp", subdir=os.path.join("Doc", "Carreaux_shape_mifmid"), as_url=True
    )

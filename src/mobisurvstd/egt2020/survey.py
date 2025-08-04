from zipfile import ZipFile

from loguru import logger

from mobisurvstd.common.clean import clean
from mobisurvstd.utils import find_file

from .deplacements import standardize_trips
from .menages import standardize_households
from .motos import standardize_motorcycles
from .personnes import standardize_persons
from .trajets import standardize_legs
from .voitures import standardize_cars


def standardize(source: str | ZipFile, skip_spatial: bool = False):
    source_name = source.filename if isinstance(source, ZipFile) else source
    logger.info(f"Standardizing EGT2020 survey from `{source_name}`")
    # Households.
    filename = households_filename(source)
    if filename is None:
        logger.error("Missing households file")
        return None
    households = standardize_households(filename)
    # Cars.
    filename = cars_filename(source)
    if filename is None:
        logger.error("Missing cars file")
        return None
    cars = standardize_cars(filename, households)
    # motorcycles.
    filename = motorcycles_filename(source)
    if filename is None:
        logger.error("Missing motorcycles file")
        return None
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
    trips = standardize_trips(filename, households, persons)
    # Legs.
    filename = legs_filename(source)
    if filename is None:
        logger.error("Missing legs file")
        return None
    legs = standardize_legs(filename, trips, cars, motorcycles, persons)
    return clean(
        households=households,
        persons=persons,
        trips=trips,
        legs=legs,
        cars=cars,
        motorcycles=motorcycles,
        survey_type="EGT2020",
        survey_name="EGT2020",
        main_insee="75056",
    )


def households_filename(source: str | ZipFile):
    return find_file(source, "a_menage_egt1820.csv", subdir="Csv")


def persons_filename(source: str | ZipFile):
    return find_file(source, "b_individu_egt1820.csv", subdir="Csv")


def trips_filename(source: str | ZipFile):
    return find_file(source, "c_deplacement_egt1820.csv", subdir="Csv")


def legs_filename(source: str | ZipFile):
    return find_file(source, "d_trajet_egt1820.csv", subdir="Csv")


def cars_filename(source: str | ZipFile):
    return find_file(source, "e_voiture_egt1820.csv", subdir="Csv")


def motorcycles_filename(source: str | ZipFile):
    return find_file(source, "f_drm_egt1820.csv", subdir="Csv")

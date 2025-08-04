from datetime import date
from zipfile import ZipFile

from loguru import logger

from mobisurvstd.common.clean import clean
from mobisurvstd.utils import find_file

from .deplacements import standardize_legs, standardize_trips
from .menages import standardize_households
from .motos import standardize_motorcycles
from .personnes import standardize_persons
from .voitures import standardize_cars


def standardize(source: str | ZipFile, skip_spatial: bool = False):
    source_name = source.filename if isinstance(source, ZipFile) else source
    logger.info(f"Standardizing EMP survey from `{source_name}`")
    # Households.
    filenames = households_filename(source)
    if filenames is None:
        return None
    households = standardize_households(*filenames)
    # Cars.
    filename = cars_filename(source)
    if filename is None:
        return None
    cars = standardize_cars(filename, households)
    # motorcycles.
    filename = motorcycles_filename(source)
    if filename is None:
        return None
    motorcycles = standardize_motorcycles(filename, households)
    # Persons.
    filenames = persons_filename(source)
    if filenames is None:
        return None
    persons = standardize_persons(*filenames, households)
    # Trips.
    filename = trips_filename(source)
    if filename is None:
        return None
    trips = standardize_trips(filename, persons)
    # Legs.
    legs = standardize_legs(filename, trips)
    return clean(
        households=households,
        persons=persons,
        trips=trips,
        legs=legs,
        cars=cars,
        motorcycles=motorcycles,
        survey_type="EMP2019",
        survey_name="EMP2019",
        start_date=date(2018, 5, 1),
        end_date=date(2019, 4, 30),
    )


def read_files(source: str | ZipFile, names: tuple[str, ...]):
    files = list()
    for name in names:
        f = find_file(source, name)
        if f is None:
            logger.error(f"Missing file: `{name}`")
            return None
        files.append(f)
    return files


def households_filename(source: str | ZipFile):
    return read_files(source, ("tcm_men_public_V3.csv", "q_menage_public_V3.csv"))


def persons_filename(source: str | ZipFile):
    return read_files(
        source,
        ("tcm_ind_public_V3.csv", "tcm_ind_kish_public_V3.csv", "k_individu_public_V3.csv"),
    )


def trips_filename(source: str | ZipFile):
    # In version November 2024, the filename a "5. " prefix for some reason, hence the ".*" in the
    # regex.
    return read_files(source, (".*k_deploc_public_V4.csv",))


def cars_filename(source: str | ZipFile):
    return read_files(source, ("q_voitvul_public_V3.csv",))


def motorcycles_filename(source: str | ZipFile):
    return read_files(source, ("q_2rmot_public_V3.csv",))

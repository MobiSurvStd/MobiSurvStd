import os

from mobisurvstd.common.clean import clean

from .deplacements import standardize_trips
from .menages import standardize_households
from .motos import standardize_motorcycles
from .personnes import standardize_persons
from .trajets import standardize_legs
from .voitures import standardize_cars


def standardize(directory: str):
    # Households.
    filename = households_filename(directory)
    households = standardize_households(filename)
    # Cars.
    filename = cars_filename(directory)
    cars = standardize_cars(filename, households)
    # motorcycles.
    filename = motorcycles_filename(directory)
    motorcycles = standardize_motorcycles(filename, households)
    # Persons.
    filename = persons_filename(directory)
    persons = standardize_persons(filename, households)
    # Trips.
    filename = trips_filename(directory)
    trips = standardize_trips(filename, households, persons)
    # Legs.
    filename = legs_filename(directory)
    legs = standardize_legs(filename, trips, cars, motorcycles, persons)
    return clean(
        households=households,
        persons=persons,
        trips=trips,
        legs=legs,
        cars=cars,
        motorcycles=motorcycles,
        survey_type="EGT2020",
        main_insee="75056",
    )


def households_filename(directory: str):
    return os.path.join(directory, "Csv", "a_menage_egt1820.csv")


def persons_filename(directory: str):
    return os.path.join(directory, "Csv", "b_individu_egt1820.csv")


def trips_filename(directory: str):
    return os.path.join(directory, "Csv", "c_deplacement_egt1820.csv")


def legs_filename(directory: str):
    return os.path.join(directory, "Csv", "d_trajet_egt1820.csv")


def cars_filename(directory: str):
    return os.path.join(directory, "Csv", "e_voiture_egt1820.csv")


def motorcycles_filename(directory: str):
    return os.path.join(directory, "Csv", "f_drm_egt1820.csv")

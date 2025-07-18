import functools
import json
import os
from collections.abc import Callable
from datetime import date

import geopandas as gpd
import polars as pl
from loguru import logger

from .clean import clean


class SurveyData:
    """Data structure to hold the standardized survey data."""

    def __init__(
        self,
        households: pl.DataFrame,
        cars: pl.DataFrame,
        motorcycles: pl.DataFrame,
        persons: pl.DataFrame,
        trips: pl.DataFrame,
        legs: pl.DataFrame,
        special_locations: gpd.GeoDataFrame | None,
        detailed_zones: gpd.GeoDataFrame | None,
        draw_zones: gpd.GeoDataFrame | None,
        metadata: dict,
    ):
        self.households = households
        self.cars = cars
        self.motorcycles = motorcycles
        self.persons = persons
        self.trips = trips
        self.legs = legs
        self.special_locations = special_locations
        self.detailed_zones = detailed_zones
        self.draw_zones = draw_zones
        self.metadata = metadata

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["households"],
            data["cars"],
            data["motorcycles"],
            data["persons"],
            data["trips"],
            data["legs"],
            data.get("special_locations"),
            data.get("detailed_zones"),
            data.get("draw_zones"),
            data["metadata"],
        )

    def clean(self):
        data = clean(
            households=self.households,
            cars=self.cars,
            motorcycles=self.motorcycles,
            persons=self.persons,
            trips=self.trips,
            legs=self.legs,
            special_locations=self.special_locations,
            detailed_zones=self.detailed_zones,
            draw_zones=self.draw_zones,
        )
        data["metadata"] = self.metadata
        return self.__class__.from_dict(data)

    def save(self, output_directory: str):
        """Saves the MobiSurvStd survey to the given directory."""
        logger.info(f"Saving standardized survey data to `{output_directory}`")
        if not os.path.isdir(output_directory):
            logger.debug(f"Creating missing directory: `{output_directory}`")
            os.makedirs(output_directory)
        elif os.listdir(output_directory):
            # Directory is not empty.
            logger.warning("Output directory is not empty, some data might be erased")
        logger.debug("Saving households")
        self.households.write_parquet(os.path.join(output_directory, "households.parquet"))
        logger.debug("Saving cars")
        self.cars.write_parquet(os.path.join(output_directory, "cars.parquet"))
        logger.debug("Saving motorcycles")
        self.motorcycles.write_parquet(os.path.join(output_directory, "motorcycles.parquet"))
        logger.debug("Saving persons")
        self.persons.write_parquet(os.path.join(output_directory, "persons.parquet"))
        logger.debug("Saving trips")
        self.trips.write_parquet(os.path.join(output_directory, "trips.parquet"))
        logger.debug("Saving legs")
        self.legs.write_parquet(os.path.join(output_directory, "legs.parquet"))
        if self.special_locations is not None:
            logger.debug("Saving special locations")
            self.special_locations.to_parquet(
                os.path.join(output_directory, "special_locations.geo.parquet")
            )
        if self.detailed_zones is not None:
            logger.debug("Saving detailed zones")
            self.detailed_zones.to_parquet(
                os.path.join(output_directory, "detailed_zones.geo.parquet")
            )
        if self.draw_zones is not None:
            logger.debug("Saving draw zones")
            self.draw_zones.to_parquet(os.path.join(output_directory, "draw_zones.geo.parquet"))
        with open(os.path.join(output_directory, "metadata.json"), "w") as f:
            logger.debug("Saving metadata")
            json.dump(self.metadata, f, indent=2)


class SurveyDataReader:
    """Data structure representing a MobiSurvStd survey.

    Parameters
    ----------
    directory: str
        Path to the directory where the MobiSurvStd survey to read is stored.

    Examples
    --------
    Create a SurveyDataReader from a directory.

    >>> data = SurveyDataReader("output/emp2019/")

    Access the survey's metadata as a dictionary:

    >>> data.metadata
    {'type': 'EMP2019',
     'survey_method': 'face_to_face',
     'nb_households': 13825,
     'nb_cars': 18817,
     'nb_motorcycles': 1264,
     'nb_persons': 31694,
     'nb_trips': 45169,
     'nb_legs': 46507,
     'nb_special_locations': 0,
     'nb_detailed_zones': 0,
     'nb_draw_zones': 0,
     'start_date': '2018-05-01',
     'end_date': '2019-04-30',
     'insee': None}

    Access the survey's households as a polars.DataFrame:

    >>> data.households
    ┌─────────────┬─────────────┬────────────┬────────────┬───┬────────────┬────────────┬───────────┬───────────┐
    │ household_i ┆ original_ho ┆ survey_met ┆ interview_ ┆ … ┆ nb_persons ┆ nb_persons ┆ nb_majors ┆ nb_minors │
    │ d           ┆ usehold_id  ┆ hod        ┆ date       ┆   ┆ ---        ┆ _5plus     ┆ ---       ┆ ---       │
    │ ---         ┆ ---         ┆ ---        ┆ ---        ┆   ┆ u8         ┆ ---        ┆ u8        ┆ u8        │
    │ u32         ┆ struct[1]   ┆ enum       ┆ date       ┆   ┆            ┆ u8         ┆           ┆           │
    ╞═════════════╪═════════════╪════════════╪════════════╪═══╪════════════╪════════════╪═══════════╪═══════════╡
    │ 1           ┆ {"110000011 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
    │             ┆ 4000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ 2           ┆ {"110000011 ┆ face_to_fa ┆ null       ┆ … ┆ 4          ┆ null       ┆ 3         ┆ 1         │
    │             ┆ 5000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ 3           ┆ {"110000011 ┆ face_to_fa ┆ null       ┆ … ┆ 2          ┆ null       ┆ 2         ┆ 0         │
    │             ┆ 6000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ 4           ┆ {"110000012 ┆ face_to_fa ┆ null       ┆ … ┆ 2          ┆ null       ┆ 2         ┆ 0         │
    │             ┆ 4000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ 5           ┆ {"110000012 ┆ face_to_fa ┆ null       ┆ … ┆ 2          ┆ null       ┆ 2         ┆ 0         │
    │             ┆ 5000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ …           ┆ …           ┆ …          ┆ …          ┆ … ┆ …          ┆ …          ┆ …         ┆ …         │
    │ 13821       ┆ {"940000036 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
    │             ┆ 1000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ 13822       ┆ {"940000036 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
    │             ┆ 4000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ 13823       ┆ {"940000041 ┆ face_to_fa ┆ null       ┆ … ┆ 2          ┆ null       ┆ 2         ┆ 0         │
    │             ┆ 5000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ 13824       ┆ {"940000044 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
    │             ┆ 1000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    │ 13825       ┆ {"940000052 ┆ face_to_fa ┆ null       ┆ … ┆ 1          ┆ 1          ┆ 1         ┆ 0         │
    │             ┆ 1000"}      ┆ ce         ┆            ┆   ┆            ┆            ┆           ┆           │
    └─────────────┴─────────────┴────────────┴────────────┴───┴────────────┴────────────┴───────────┴───────────┘
    """

    def __init__(self, directory: str):
        self.directory = directory
        self._households = None
        self._cars = None
        self._motorcycles = None
        self._persons = None
        self._trips = None
        self._legs = None
        self._special_locations = None
        self._detailed_zones = None
        self._draw_zones = None
        self._metadata = None

    @property
    def metadata(self) -> dict:
        if self._metadata is None:
            filename = os.path.join(self.directory, "metadata.json")
            logger.debug(f"Reading metadata from `{filename}`")
            self._metadata = json.load(open(filename))
        return self._metadata

    @property
    def households(self) -> pl.DataFrame:
        if self._households is None:
            filename = os.path.join(self.directory, "households.parquet")
            logger.debug(f"Reading households from `{filename}`")
            self._households = pl.read_parquet(filename)
        return self._households

    @property
    def cars(self) -> pl.DataFrame:
        if self._cars is None:
            filename = os.path.join(self.directory, "cars.parquet")
            logger.debug(f"Reading cars from `{filename}`")
            self._cars = pl.read_parquet(filename)
        return self._cars

    @property
    def motorcycles(self) -> pl.DataFrame:
        if self._motorcycles is None:
            filename = os.path.join(self.directory, "motorcycles.parquet")
            logger.debug(f"Reading motorcycles from `{filename}`")
            self._motorcycles = pl.read_parquet(filename)
        return self._motorcycles

    @property
    def persons(self) -> pl.DataFrame:
        if self._persons is None:
            filename = os.path.join(self.directory, "persons.parquet")
            logger.debug(f"Reading persons from `{filename}`")
            self._persons = pl.read_parquet(filename)
        return self._persons

    @property
    def trips(self) -> pl.DataFrame:
        if self._trips is None:
            filename = os.path.join(self.directory, "trips.parquet")
            logger.debug(f"Reading trips from `{filename}`")
            self._trips = pl.read_parquet(filename)
        return self._trips

    @property
    def legs(self) -> pl.DataFrame:
        if self._legs is None:
            filename = os.path.join(self.directory, "legs.parquet")
            logger.debug(f"Reading legs from `{filename}`")
            self._legs = pl.read_parquet(filename)
        return self._legs

    @property
    def special_locations(self) -> gpd.GeoDataFrame:
        if self._special_locations is None:
            filename = os.path.join(self.directory, "special_locations.geo.parquet")
            if os.path.isfile(filename):
                logger.debug(f"Reading special locations from `{filename}`")
                self._special_locations = pl.read_parquet(filename)
        return self._special_locations

    @property
    def detailed_zones(self) -> gpd.GeoDataFrame:
        if self._detailed_zones is None:
            filename = os.path.join(self.directory, "detailed_zones.geo.parquet")
            if os.path.isfile(filename):
                logger.debug(f"Reading detailed zones from `{filename}`")
                self._detailed_zones = pl.read_parquet(filename)
        return self._detailed_zones

    @property
    def draw_zones(self) -> gpd.GeoDataFrame:
        if self._draw_zones is None:
            filename = os.path.join(self.directory, "draw_zones.geo.parquet")
            if os.path.isfile(filename):
                logger.debug(f"Reading draw zones from `{filename}`")
                self._draw_zones = pl.read_parquet(filename)
        return self._draw_zones

    def mean_date(self) -> date:
        """Returns the mean date at which the survey was conducted (the middle date between the
        survey's start and end date).
        """
        start_date = date.fromisoformat(self.metadata["start_date"])
        end_date = date.fromisoformat(self.metadata["end_date"])
        return start_date + (end_date - start_date) / 2


def iter_many(directory: str):
    """Iterates over the MobiSurvStd data located within a directory (potentially recursively)."""
    if not os.path.isdir(directory):
        raise Exception(f"Not a valid directory: `{directory}`")
    for name in os.listdir(directory):
        item = os.path.join(directory, name)
        if not os.path.isdir(item):
            logger.debug(f"Skipping non-directory: `{item}`")
            continue
        if not is_valid_mobisurvstd_dir(item):
            # The current item is a directory but does not contain valid MobiSurvStd data.
            # We go recursively to read MobiSurvStd directories within that directory (if any).
            logger.debug(f"Recursively reading data from `{item}`")
            yield from iter_many(item)
            continue
        logger.debug(f"Found a valid MobiSurvStd directory at `{item}`")
        data = SurveyDataReader(item)
        yield data


def read_many(directory: str, read_fn: Callable, acc_fn: Callable):
    """Runs a function on all MobiSurvStd surveys found in a directory and aggregates the results.

    Parameters
    ----------
    directory
        Path to the directory where the MobiSurvStd surveys to read are stored.
        The directory will be read recursively so the surveys can be stored in subdirectories.
    read_fn
        Function to be run on each survey.
        It takes a single argument whose type is `SurveyDataReader`.
    acc_fn
        Function to aggregate the results from two surveys.
        This must be a function of two arguments, whose type is the same as the return type of
        `read_fn`.

    Examples
    --------
    Read the total number of households from all surveys in the "output" directory:

    >>> read_many("output/", lambda d: len(d.households), lambda x, y: x + y)

    Concatenate all trips in a single DataFrame:

    >>> read_many("output/", lambda d: d.trips, lambda x, y: pl.concat((x, y)))
    """
    return functools.reduce(
        acc_fn, filter(lambda r: r is not None, map(read_fn, iter_many(directory)))
    )


def is_valid_mobisurvstd_dir(directory: str) -> bool:
    """Checks if a directory contains all the mandatory MobiSurvStd files."""
    for name in (
        "metadata.json",
        "households.parquet",
        "persons.parquet",
        "trips.parquet",
        "legs.parquet",
        "cars.parquet",
        "motorcycles.parquet",
    ):
        if not os.path.isfile(os.path.join(directory, name)):
            return False
    return True

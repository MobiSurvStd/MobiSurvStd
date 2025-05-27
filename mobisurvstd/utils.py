import json
import os
import re

import geopandas as gpd
import polars as pl

from .clean import clean


class SurveyData:
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
        insee_zones: gpd.GeoDataFrame | None,
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
        self.insee_zones = insee_zones
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
            data.get("insee_zones"),
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
            insee_zones=self.insee_zones,
        )
        data["metadata"] = self.metadata
        return self.__class__.from_dict(data)

    def save(self, output_directory: str):
        if not os.path.isdir(output_directory):
            os.makedirs(output_directory)
        self.households.write_parquet(os.path.join(output_directory, "households.parquet"))
        self.cars.write_parquet(os.path.join(output_directory, "cars.parquet"))
        self.motorcycles.write_parquet(os.path.join(output_directory, "motorcycles.parquet"))
        self.persons.write_parquet(os.path.join(output_directory, "persons.parquet"))
        self.trips.write_parquet(os.path.join(output_directory, "trips.parquet"))
        self.legs.write_parquet(os.path.join(output_directory, "legs.parquet"))
        if self.detailed_zones is not None:
            self.detailed_zones.to_parquet(os.path.join(output_directory, "detailed_zones.parquet"))
        if self.draw_zones is not None:
            self.draw_zones.to_parquet(os.path.join(output_directory, "draw_zones.parquet"))
        if self.insee_zones is not None:
            self.insee_zones.to_parquet(os.path.join(output_directory, "insee_zones.parquet"))
        with open(os.path.join(output_directory, "metadata.json"), "w") as f:
            json.dump(self.metadata, f)


def find_file(directory: str, regex: str):
    pattern = re.compile(regex)
    for filename in os.listdir(directory):
        if pattern.match(filename):
            return os.path.join(directory, filename)

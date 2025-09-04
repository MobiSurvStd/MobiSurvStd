from datetime import date

import polars as pl
from loguru import logger
from polars.datatypes.classes import DataTypeClass

from .guarantees import (
    AutoFixed,
    Guarantee,
    Invalid,
    Valid,
)


class Variable:
    def __init__(self, name: str, dtype: DataTypeClass, guarantees: list[Guarantee] = []):
        self.name = name
        self.dtype = dtype
        self.guarantees = guarantees

    def check_guarantees(self, df: pl.DataFrame):
        res = Valid()
        for guarantee in self.guarantees:
            if not guarantee.check(df, self.name):
                error = guarantee.fail_msg(df, self.name)
                df_or_none = guarantee.auto_fix(df, self.name)
                if df_or_none is None:
                    # Guarantee is not satisfied and auto-fix is not possible.
                    logger.error(f"Guarantee unsatisfied for column `{self.name}`: {error}")
                    res = Invalid()
                else:
                    # The DataFrame has been modified to fix the issue.
                    logger.warning(f"Guarantee auto-fixed for column `{self.name}`: {error}")
                    res = AutoFixed(df_or_none)
                    df = df_or_none
        return res


PARKING_LOCATION_ENUM = pl.Enum(["garage", "street", "parking_lot", "other"])

PARKING_TYPE_ENUM = pl.Enum(["forbidden", "free", "paid", "paid_by_other", "other"])

MODE_ENUM = pl.Enum(
    [
        # Walking
        "walking",
        # Bicycle
        "bicycle:driver",
        "bicycle:driver:shared",
        "bicycle:driver:traditional",
        "bicycle:driver:traditional:shared",
        "bicycle:driver:electric",
        "bicycle:driver:electric:shared",
        "bicycle:passenger",
        # Motorcycle
        "motorcycle:driver",
        "motorcycle:passenger",
        "motorcycle:driver:moped",
        "motorcycle:passenger:moped",
        "motorcycle:driver:moto",
        "motorcycle:passenger:moto",
        # Car
        "car:driver",
        "car:passenger",
        "taxi",
        "VTC",
        "taxi_or_VTC",
        # Public transit
        "public_transit:urban",
        "public_transit:urban:bus",
        "public_transit:urban:coach",
        "public_transit:urban:tram",
        "public_transit:urban:metro",
        "public_transit:urban:funicular",
        "public_transit:urban:rail",
        "public_transit:urban:TER",
        "public_transit:urban:demand_responsive",
        "public_transit:interurban:coach",
        "public_transit:interurban:TGV",
        "public_transit:interurban:intercités",
        "public_transit:interurban:other_train",
        "public_transit:school",
        # Other
        "reduced_mobility_transport",
        "employer_transport",
        "truck:driver",
        "truck:passenger",
        "water_transport",
        "airplane",
        "wheelchair",
        "personal_transporter:non_motorized",
        "personal_transporter:motorized",
        "personal_transporter:unspecified",
        "other",
    ]
)

MODE_GROUPS = [
    "walking",
    "bicycle",
    "motorcycle",
    "car_driver",
    "car_passenger",
    "public_transit",
    "other",
]
MODE_GROUP_ENUM = pl.Enum(MODE_GROUPS)

MODE_TO_GROUP = {
    # Walking
    "walking": "walking",
    # Bicycle
    "bicycle:driver": "bicycle",
    "bicycle:driver:shared": "bicycle",
    "bicycle:driver:traditional": "bicycle",
    "bicycle:driver:traditional:shared": "bicycle",
    "bicycle:driver:electric": "bicycle",
    "bicycle:driver:electric:shared": "bicycle",
    "bicycle:passenger": "bicycle",
    # Motorcycle
    "motorcycle:driver": "motorcycle",
    "motorcycle:passenger": "motorcycle",
    "motorcycle:driver:moped": "motorcycle",
    "motorcycle:passenger:moped": "motorcycle",
    "motorcycle:driver:moto": "motorcycle",
    "motorcycle:passenger:moto": "motorcycle",
    # Car
    "car:driver": "car_driver",
    "car:passenger": "car_passenger",
    "taxi": "car_passenger",
    "VTC": "car_passenger",
    "taxi_or_VTC": "car_passenger",
    # Public transit
    "public_transit:urban": "public_transit",
    "public_transit:urban:bus": "public_transit",
    "public_transit:urban:coach": "public_transit",
    "public_transit:urban:tram": "public_transit",
    "public_transit:urban:metro": "public_transit",
    "public_transit:urban:funicular": "public_transit",
    "public_transit:urban:rail": "public_transit",
    "public_transit:urban:TER": "public_transit",
    "public_transit:urban:demand_responsive": "public_transit",
    "public_transit:interurban:coach": "public_transit",
    "public_transit:interurban:TGV": "public_transit",
    "public_transit:interurban:intercités": "public_transit",
    "public_transit:interurban:other_train": "public_transit",
    "public_transit:school": "public_transit",
    # Other
    "reduced_mobility_transport": "other",
    "employer_transport": "other",
    "truck:driver": "other",
    "truck:passenger": "other",
    "water_transport": "other",
    "airplane": "other",
    "wheelchair": "other",
    "personal_transporter:non_motorized": "other",
    "personal_transporter:motorized": "other",
    "personal_transporter:unspecified": "other",
    "other": "other",
}

CURRENT_YEAR = date.today().year

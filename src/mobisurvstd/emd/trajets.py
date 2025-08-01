import polars as pl

from mobisurvstd.common.legs import clean

from .common import MODE_MAP

SCHEMA = {
    "TP1": pl.UInt8,  # Code fichier = 4 (trajet)
    "IDT3": pl.UInt16,  # Année de fin d'enquête
    "IDT4": pl.String,  # Code Insee ville centre
    "ZFT": pl.UInt32,  # Zone fine de résidence
    "ECH": pl.UInt32,  # Numéro d’échantillon
    "PER": pl.UInt8,  # Numéro de personne
    "NDEP": pl.UInt8,  # Numéro de déplacement
    "T1": pl.UInt8,  # Numéro de trajet
    "GT1": pl.String,  # Insee Zone fine du lieu de résidence de la personne concernée par le trajet
    "STT": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine (résidence)
    "T2": pl.UInt16,  # Temps de marche à pied au départ
    "T3": pl.UInt8,  # Mode utilisé
    "T4": pl.UInt32,  # Zone fine de départ du mode mécanisé
    "GTO1": pl.String,  # Insee Zone fine Origine du trajet
    "STTO": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine (origine du trajet)
    "T5": pl.UInt32,  # Zone fine d'arrivée du mode mécanisé
    "GTD1": pl.String,  # Insee Zone fine Destination du trajet
    "STTD": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine (destination du trajet)
    "T6": pl.UInt16,  # Temps de marche à pied à l’arrivée
    "T7": pl.UInt8,  # Numéro du véhicule
    "T8": pl.UInt8,  # Nombre de personnes total
    "T8A": pl.UInt8,  # Nombre de passagers majeurs
    "T8B": pl.UInt8,  # Nombres de passagers mineurs
    "T9": pl.UInt8,  # Lieu de stationnement
    "T10": pl.UInt8,  # Nature du stationnement
    "T11": pl.UInt16,  # Durée de recherche du stationnement
    "T12": pl.Float64,  # Longueur à vol d’oiseau
    "T13": pl.Float64,  # Distance parcourue
}

PARKING_LOCATION_MAP = {
    0: "stop_only",  # Arrêt pour prendre ou déposer une personne
    1: "garage",  # Dans un garage, box, autre emplacement réservé
    2: "street",  # Dans la rue
    3: "parking_lot:unsheltered",  # Dans un parc de stationnement à ciel ouvert (ou place publique)
    4: "parking_lot:sheltered",  # Dans un parc de stationnement couvert accessible au public
    5: "P+R",  # Dans un parking relais
    6: "none",  # Aucun : emporté dans le mode suivant
    9: "other",  # Autre
}

PARKING_TYPE_MAP = {
    1: "forbidden",  # Interdit
    2: "free",  # Gratuit
    3: "paid",  # Payant à votre charge
    4: "paid_by_other",  # Payant à la charge de quelqu'un d'autre
    5: "other",  # Autre (egt)
}

CAR_MAP = {
    1: "household",
    2: "household",
    3: "household",
    4: "household",
    5: "other_household",  # autre véhicule du ménage
    6: "rental",  # véhicule de location
    7: "company",  # véhicule de l'entreprise
    8: "other",  # autre véhicule
    9: "shared",  # véhicule en autopartage
}

# For motorcycles, either the 1, 2, 3, 4 values or the 11, 12, 13, 14 values can be used to refer
# to the household surveyed motorcycles.
MOTORCYCLE_MAP = {
    1: "household",
    2: "household",
    3: "household",
    4: "household",
    5: "other_household",
    6: "rental",
    7: "company",
    8: "other",
    9: "shared",
    11: "household",
    12: "household",
    13: "household",
    14: "household",
    15: "shared",
    16: "other",
}


def scan_legs(source: str | bytes):
    lf = pl.scan_csv(source, separator=";", schema_overrides=SCHEMA, null_values=["a"])
    return lf


def standardize_legs(
    source: str | bytes,
    trips: pl.LazyFrame,
    cars: pl.LazyFrame,
    motorcycles: pl.LazyFrame,
    special_locations_coords: pl.DataFrame | None,
    detailed_zones_coords: pl.DataFrame | None,
):
    lf = scan_legs(source)
    # Join with trips to get household_id, person_id, and trip_id, but also origins and destination
    # to construct the walking legs.
    lf = lf.with_columns(
        original_trip_id=pl.struct(ECH="ECH", STD="STT", PER="PER", NDEP="NDEP")
    ).join(
        trips.select(
            "original_trip_id",
            "trip_id",
            "person_id",
            "household_id",
            "origin_detailed_zone",
            "origin_insee",
            "origin_draw_zone",
            "destination_detailed_zone",
            "destination_insee",
            "destination_draw_zone",
        ),
        on="original_trip_id",
        how="left",
        coalesce=True,
    )
    idx = ["ECH", "STT", "PER", "NDEP"]

    # For EMD, the walking legs are not recorded explicitly, instead, the walking time before and
    # after the legs are defined.
    # We create actual walking legs from these walking times.

    # Part 1: walking leg from origin
    # The walking leg from origin is read from the start walking time of the first leg of each trip.
    # The origin is set to the origin of the trip. The destination is set to the start point of the
    # first leg.
    # The trip index is set to 1.
    lf1 = (
        lf.filter(pl.col("T1") == 1, pl.col("T2") > 0)
        .rename(
            {
                "origin_detailed_zone": "start_detailed_zone",
                "origin_insee": "start_insee",
                "origin_draw_zone": "start_draw_zone",
                "T4": "end_detailed_zone",
                "GTO1": "end_insee",
                "STTO": "end_draw_zone",
                "T2": "leg_travel_time",
            }
        )
        .with_columns(
            original_leg_id=pl.struct(idx + [pl.lit(None, dtype=pl.UInt8).alias("T1")]),
            leg_index=pl.lit(1, dtype=pl.UInt8),
            mode=pl.lit("walking"),
        )
    )
    # Part 2: non-walking legs
    # The trip index is set to twice the original trip index, i.e., 2, 4, 6, etc.
    lf2 = lf.rename(
        {
            "T4": "start_detailed_zone",
            "GTO1": "start_insee",
            "STTO": "start_draw_zone",
            "T5": "end_detailed_zone",
            "GTD1": "end_insee",
            "STTD": "end_draw_zone",
            "T8": "nb_persons_in_vehicle",
            "T8A": "nb_majors_in_vehicle",
            "T8B": "nb_minors_in_vehicle",
            "T11": "parking_search_time",
        }
    ).with_columns(
        original_leg_id=pl.struct(idx + ["T1"]),
        leg_index=2 * pl.col("T1"),
        mode=pl.col("T3").replace_strict(MODE_MAP),
        parking_location=pl.col("T9").replace_strict(PARKING_LOCATION_MAP),
        parking_type=pl.col("T10").replace_strict(PARKING_TYPE_MAP),
        leg_euclidean_distance_km=pl.col("T12") / 1e3,
        leg_travel_distance_km=pl.col("T13") / 1e3,
    )
    # Part 3: walking legs after actual legs
    # The remaining walking leg are read from the end walking time of each leg.
    # The origin is set to the end point of the leg. The destination is set to the start point of
    # the next leg (or to the trip's destination if there is no leg after).
    # The trip index is set to twice the original trip index + 1, i.e., 3, 5, 7, etc.
    # NOTE. The end walking time of the leg is supposed to be equal to the start walking time of the
    # next leg. In practise, this rule is not respected in some rare cases. Here, we do not check
    # that rule and we use directly the end walking time.
    lf3 = (
        lf.filter(pl.col("T6") > 0)
        .rename(
            {
                "T5": "start_detailed_zone",
                "GTD1": "start_insee",
                "STTD": "start_draw_zone",
                "T6": "leg_travel_time",
            }
        )
        .with_columns(
            original_leg_id=pl.struct(idx + [pl.lit(None, dtype=pl.UInt8).alias("T1")]),
            leg_index=2 * pl.col("T1") + 1,
            mode=pl.lit("walking"),
            end_detailed_zone=pl.col("T4")
            .shift(-1)
            .over("trip_id")
            .fill_null(pl.col("destination_detailed_zone")),
            end_insee=pl.col("GTO1")
            .shift(-1)
            .over("trip_id")
            .fill_null(pl.col("destination_insee")),
            end_draw_zone=pl.col("STTO")
            .shift(-1)
            .over("trip_id")
            .fill_null(pl.col("destination_draw_zone")),
        )
    )
    # Part 4: walking legs for walk-only trips.
    # For walk-only trips, there is no leg so we create a single walking legs with same origin,
    # destination and travel time as the corresponding trip.
    lf4 = trips.filter(pl.col("main_mode") == "walking").select(
        "household_id",
        "person_id",
        "trip_id",
        leg_index=pl.lit(1, dtype=pl.UInt8),
        mode=pl.lit("walking"),
        start_detailed_zone="origin_detailed_zone",
        start_insee="origin_insee",
        start_draw_zone="origin_draw_zone",
        end_detailed_zone="destination_detailed_zone",
        end_insee="destination_insee",
        end_draw_zone="destination_draw_zone",
        leg_travel_time="travel_time",
        leg_euclidean_distance_km="trip_euclidean_distance_km",
        leg_travel_distance_km="trip_travel_distance_km",
    )
    # Concatenate the 4 leg types and fix the leg index to be running from 1 to n.
    lf = pl.concat((lf1, lf2, lf3, lf4), how="diagonal")
    # Add car and motorcycle types.
    lf = lf.with_columns(
        car_type=pl.when(pl.col("mode").str.starts_with("car:")).then(
            pl.col("T7").replace_strict(CAR_MAP, default=None)
        ),
        motorcycle_type=pl.when(pl.col("mode").str.starts_with("motorcycle:")).then(
            pl.col("T7").replace_strict(MOTORCYCLE_MAP, default=None)
        ),
        car_index=pl.when(pl.col("mode").str.starts_with("car:") & pl.col("T7").is_between(1, 4))
        .then("T7")
        .cast(pl.UInt8),
        # The `motorcycle_index` is either 1, 2, 3, 4 or 11, 12, 13, 14 depending on the surveys.
        # We "force" it to be 1, 2, 3, 4.
        motorcycle_index=pl.when(
            pl.col("mode").str.starts_with("motorcycle:")
            & pl.col("T7").is_in((1, 2, 3, 4, 11, 12, 13, 14))
        )
        .then(pl.col("T7") - 10 * (pl.col("T7") >= 11))
        .cast(pl.UInt8),
    )
    # Add car id.
    lf = lf.join(
        cars.select("household_id", "car_index", "car_id"),
        on=["household_id", "car_index"],
        how="left",
        coalesce=True,
    )
    # Add motorcycle id.
    lf = lf.join(
        motorcycles.select("household_id", "motorcycle_index", "motorcycle_id"),
        on=["household_id", "motorcycle_index"],
        how="left",
        coalesce=True,
    )
    lf = clean(lf, special_locations=special_locations_coords, detailed_zones=detailed_zones_coords)
    return lf

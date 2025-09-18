import polars as pl
from loguru import logger

from mobisurvstd.common.legs import clean

SCHEMA = {
    "TP1": pl.UInt8,  # Code fichier = 4 (trajet)
    "TMET": pl.UInt8,  # Méthode d'enquête du ménage (EMC2 only)
    "IDT3": pl.UInt16,  # Année de fin d'enquête
    "IDT4": pl.String,  # Code Insee ville centre
    "ZFT": pl.String,  # Zone fine de résidence
    "ECH": pl.UInt32,  # Numéro d’échantillon
    "PER": pl.UInt8,  # Numéro de personne
    "NDEP": pl.UInt8,  # Numéro de déplacement
    "T1": pl.UInt8,  # Numéro de trajet
    "GT1": pl.String,  # Insee Zone fine du lieu de résidence de la personne concernée par le trajet
    "STT": pl.String,  # Secteur de tirage dans l’enquête d’origine (résidence)
    "T2": pl.Int32,  # Temps de marche à pied au départ
    "T3": pl.UInt8,  # Mode utilisé
    "T4": pl.String,  # Zone fine de départ du mode mécanisé
    "GTO1": pl.String,  # Insee Zone fine Origine du trajet
    "STTO": pl.String,  # Secteur de tirage dans l’enquête d’origine (origine du trajet)
    "T5": pl.String,  # Zone fine d'arrivée du mode mécanisé
    "GTD1": pl.String,  # Insee Zone fine Destination du trajet
    "STTD": pl.String,  # Secteur de tirage dans l’enquête d’origine (destination du trajet)
    "T6": pl.Int32,  # Temps de marche à pied à l’arrivée
    "T7": pl.UInt8,  # Numéro du véhicule
    "T3A": pl.UInt8,  # Voiture sans permis (EMC2 only)
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
    6: "stop_only",  # Aucun : emporté dans le mode suivant
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


def scan_legs_impl(source: str | bytes):
    return pl.scan_csv(
        source, separator=";", schema_overrides=SCHEMA, null_values=["a", "aa", "aaaaa"]
    )


class LegsReader:
    def scan_legs(self):
        lfs_iter = map(scan_legs_impl, self.legs_filenames())
        lf = pl.concat(lfs_iter, how="vertical")
        if "T3A" not in lf.collect_schema().names():
            # In the old Cerema surveys (EMD, EDGT, EDVM), the T3A column does not exist.
            lf = lf.with_columns(T3A=None)
        return lf

    def standardize_legs(self):
        lf = self.scan_legs()
        # Join with trips to get household_id, person_id, and trip_id, but also origins and
        # destination to construct the walking legs.
        lf = lf.with_columns(
            original_trip_id=pl.struct(**self.get_trip_index_cols_from_legs())
        ).join(
            self.trips.select(
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

        lf = lf.with_columns(
            # Values 99000, 99999, 99095, 99300 do not represent any known INSEE / country.
            GTO1=pl.col("GTO1").replace(["99000", "99999", "99095", "99300"], None),
            GTD1=pl.col("GTD1").replace(["99000", "99999", "99095", "99300"], None),
        )

        # For Cerema surveys, the walking legs are not recorded explicitly, instead, the walking
        # time before and after the legs are defined.
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
                original_leg_id=pl.struct(
                    self.get_leg_index_cols() + [pl.lit(None, dtype=pl.UInt8).alias("T1")]
                ),
                tmp_leg_index=pl.lit(1, dtype=pl.UInt8),
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
            original_leg_id=pl.struct(self.get_leg_index_cols() + ["T1"]),
            tmp_leg_index=2 * pl.col("T1"),
            mode=pl.col("T3").replace_strict(self.get_mode_map()),
            nolicense_car=pl.col("T3A") == 1,
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
                original_leg_id=pl.struct(
                    self.get_leg_index_cols() + [pl.lit(None, dtype=pl.UInt8).alias("T1")]
                ),
                tmp_leg_index=2 * pl.col("T1") + 1,
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
        lf4 = self.trips.filter(pl.col("main_mode") == "walking").select(
            "household_id",
            "person_id",
            "trip_id",
            tmp_leg_index=pl.lit(1, dtype=pl.UInt8),
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
        # Part 5: non-walking legs with no leg.
        # Special case for Créil 2017, some trips whose mode is not walking have no leg.
        # We create a single leg for them, with the data we have.
        lf5 = (
            self.trips.filter(pl.col("main_mode") != "walking")
            .join(lf, on="original_trip_id", how="anti")
            .select(
                "household_id",
                "person_id",
                "trip_id",
                tmp_leg_index=pl.lit(1, dtype=pl.UInt8),
                mode=pl.col("main_mode"),
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
        )
        # Concatenate the 5 leg types.
        lf = pl.concat((lf1, lf2, lf3, lf4, lf5), how="diagonal")
        lf = lf.sort("trip_id", "tmp_leg_index")
        # Add car and motorcycle types.
        lf = lf.with_columns(
            car_type=pl.when(pl.col("mode").str.starts_with("car:")).then(
                pl.col("T7").replace_strict(CAR_MAP, default=None)
            ),
            motorcycle_type=pl.when(pl.col("mode").str.starts_with("motorcycle:")).then(
                pl.col("T7").replace_strict(MOTORCYCLE_MAP, default=None)
            ),
            original_car_index=pl.when(
                pl.col("mode").str.starts_with("car:") & pl.col("T7").is_between(1, 4)
            )
            .then("T7")
            .cast(pl.UInt8),
            # The `original_motorcycle_index` is either 1, 2, 3, 4 or 11, 12, 13, 14 depending on
            # the surveys.
            # We "force" it to be 1, 2, 3, 4.
            original_motorcycle_index=pl.when(
                pl.col("mode").str.starts_with("motorcycle:")
                & pl.col("T7").is_in((1, 2, 3, 4, 11, 12, 13, 14))
            )
            .then(pl.col("T7") - 10 * (pl.col("T7") >= 11))
            .cast(pl.UInt8),
        )
        # Add car id.
        lf = lf.join(
            self.cars.select("household_id", "original_car_index", "car_id"),
            on=["household_id", "original_car_index"],
            how="left",
            coalesce=True,
        )
        # For Angers 2012 (and maybe others), column T7 is sometimes set to 2 (for example) while
        # the household has no car with index 2.
        # In this case, `car_type` is changed from "household" to "other_household".
        lf = lf.with_columns(
            car_type=pl.when(pl.col("original_car_index").is_not_null(), pl.col("car_id").is_null())
            .then(pl.lit("other_household"))
            .otherwise("car_type")
        )
        # Add motorcycle id.
        lf = lf.join(
            self.motorcycles.select("household_id", "original_motorcycle_index", "motorcycle_id"),
            on=["household_id", "original_motorcycle_index"],
            how="left",
            coalesce=True,
        )
        # Same fix as for cars.
        lf = lf.with_columns(
            motorcycle_type=pl.when(
                pl.col("original_motorcycle_index").is_not_null(), pl.col("motorcycle_id").is_null()
            )
            .then(pl.lit("other_household"))
            .otherwise("motorcycle_type")
        )
        # Columns T8A and T8B actually represent the number of major and minor *passengers* not the
        # number of majors and minors *persons* in vehicle.
        # If the mode is driver-related, we include the driver (their age is known).
        # If the mode is passenger-related, we assume that the driver is major.
        lf = lf.join(
            self.persons.select("person_id", is_major=pl.col("age") >= 18),
            on="person_id",
            how="left",
        )
        lf = lf.with_columns(
            nb_majors_in_vehicle=pl.when("is_major" | pl.col("mode").str.contains("passenger"))
            .then(pl.col("nb_majors_in_vehicle") + 1)
            .otherwise("nb_majors_in_vehicle"),
            nb_minors_in_vehicle=pl.when(
                pl.col("is_major").not_() & pl.col("mode").str.contains("driver"),
            )
            .then(pl.col("nb_minors_in_vehicle") + 1)
            .otherwise("nb_minors_in_vehicle"),
        )
        # For Nantes 2015 and Saint-Denis-de-la-Réunion 2016, the `nb_minors_in_vehicle` column has
        # many nulls. The value can be deduced from `nb_persons_in_vehicle` and
        # `nb_majors_in_vehicle`.
        lf = lf.with_columns(
            nb_minors_in_vehicle=pl.when(
                pl.col("nb_minors_in_vehicle").is_null(),
                pl.col("nb_persons_in_vehicle").is_not_null(),
                pl.col("nb_majors_in_vehicle").is_not_null(),
            )
            .then(
                pl.when(pl.col("nb_persons_in_vehicle") > pl.col("nb_majors_in_vehicle"))
                .then(pl.col("nb_persons_in_vehicle") - pl.col("nb_majors_in_vehicle"))
                .otherwise(0)
            )
            .otherwise("nb_minors_in_vehicle")
        )
        lf = fix_start_end_detailed_zones(lf)
        df = lf.collect()
        # For Bourg-en-Bresse 2017 et Besançon 2018, some persons are missing.
        n = df["trip_id"].null_count()
        if n > 0:
            logger.warning(f"{n} legs are assigned to an unknown trip. They are dropped.")
            df = df.filter(pl.col("trip_id").is_not_null())
        self.legs = clean(
            df.lazy(),
            special_locations=self.special_locations_coords,
            detailed_zones=self.detailed_zones_coords,
        )
        # When the INSEE code ends with "000" or "999" it means "rest of the département".
        # We drop these values because they do not add any additional information compared to `_dep`
        # columns.
        # This is done after the automatic cleaning so that the département is correctly read.
        self.legs = self.legs.with_columns(
            start_insee=pl.when(
                pl.col("start_insee").str.ends_with("000")
                | pl.col("start_insee").str.ends_with("999")
            )
            .then(None)
            .otherwise("start_insee"),
            end_insee=pl.when(
                pl.col("end_insee").str.ends_with("000") | pl.col("end_insee").str.ends_with("999")
            )
            .then(None)
            .otherwise("end_insee"),
        )


def fix_start_end_detailed_zones(lf: pl.LazyFrame):
    # For external start / end location, the detailed zone id is sometimes set to
    # "8" + INSEE or "9" + INSEE. In this case, keeping the detailed zone id does not add any
    # information so we set it to NULL.
    lf = lf.with_columns(
        start_detailed_zone=pl.when("8" + pl.col("start_insee") == pl.col("start_detailed_zone"))
        .then(None)
        .when("9" + pl.col("start_insee") == pl.col("start_detailed_zone"))
        .then(None)
        .otherwise("start_detailed_zone"),
        end_detailed_zone=pl.when("8" + pl.col("end_insee") == pl.col("end_detailed_zone"))
        .then(None)
        .when("9" + pl.col("end_insee") == pl.col("end_detailed_zone"))
        .then(None)
        .otherwise("end_detailed_zone"),
    )
    return lf

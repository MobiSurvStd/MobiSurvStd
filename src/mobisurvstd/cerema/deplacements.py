import polars as pl
from loguru import logger

from mobisurvstd.common.trips import clean

SCHEMA = {
    "DP1": pl.UInt8,  # Code fichier = 3 (déplacement)
    "DMET": pl.UInt8,  # Méthode d'enquête du ménage (EMC2 only)
    "IDD3": pl.UInt16,  # Année de fin d'enquête
    "IDD4": pl.String,  # Code Insee ville centre
    "ZFD": pl.String,  # Zone fine de résidence
    "ECH": pl.UInt32,  # Numéro d’échantillon
    "PER": pl.UInt8,  # Numéro de personne
    "NDEP": pl.UInt8,  # Numéro de déplacement
    "GD1": pl.String,  # Insee Zone fine du lieu de résidence de la personne concernée par le déplacement
    "STD": pl.String,  # Secteur de tirage dans l’enquête d’origine  (résidence)
    "D2A": pl.UInt8,  # Motif Origine du déplacement
    "D2B": pl.UInt8,  # Motif Origine de la personne accompagnée
    "D3": pl.String,  # Zone fine Origine du déplacement
    "GDO1": pl.String,  # Insee Zone fine Origine du déplacement
    "STDO": pl.String,  # Secteur de tirage dans l’enquête d’origine (origine du déplacement)
    "D4": pl.Int32,  # Heure de départ du déplacement
    "D5A": pl.UInt8,  # Motif Destination du déplacement
    "D5B": pl.UInt8,  # Motif Destination de la personne accompagnée
    "D6": pl.UInt8,  # Nombre d’arrêts sur la tournée
    "D7": pl.String,  # Zone fine Destination du déplacement
    "GDD1": pl.String,  # Insee Zone fine Destination du déplacement
    "STDD": pl.String,  # Secteur de tirage dans l’enquête d’origine (destination du déplacement)
    "D8": pl.Int32,  # Heure d'arrivée du déplacement
    "D9": pl.Int32,  # Durée du déplacement
    "D10": pl.UInt8,  # Nombre de trajets (en modes mécanisés)
    "D11": pl.Float64,  # Longueur à vol d'oiseau
    "D12": pl.Float64,  # Distance parcourue
    "MODP": pl.UInt8,  # Mode principal
    "TYPD": pl.UInt8,  # Type de déplacement
}

PURPOSE_MAP = {
    1: "home:main",  # Domicile (partir de, se rendre à).
    2: "home:secondary",  # Résidence secondaire, logement occasionnel, hôtel, autre domicile (partir de, se rendre à).
    11: "work:usual",  # Travailler sur le lieu d’emploi déclaré.
    12: "work:telework",  # Travailler sur un autre lieu – télétravail.
    13: "work:secondary",  # Travailler sur un autre lieu hors télétravail
    14: "work:other",  # Travailler sur un autre lieu sans distinction
    # NOTE. We discard the information on the exact study location type (middle-school, high-school,
    # etc.) because the information can read from the person characteristics (`student_group`).
    21: "education:childcare",  # Être gardé (Nourrice, crèche...).
    22: "education:usual",  # Étudier sur le lieu d'études déclaré (école maternelle et primaire).
    23: "education:usual",  # Étudier sur le lieu d'études déclaré (collège).
    24: "education:usual",  # Étudier sur le lieu d'études déclaré (lycée).
    25: "education:usual",  # Étudier sur le lieu d'études déclaré (universités et grandes écoles).
    26: "education:other",  # Étudier sur un autre lieu (école maternelle et primaire).
    27: "education:other",  # Étudier sur un autre lieu (collège).
    28: "education:other",  # Étudier sur un autre lieu (lycée).
    29: "education:other",  # Étudier sur un autre lieu (universités et grandes écoles).
    30: "shopping:no_purchase",  # Visite d’un magasin, d’un centre commercial ou d’un marché de plein vent sans effectuer d’achat
    31: "shopping:unspecified",  # Réaliser plusieurs motifs en centre commercial.
    32: "shopping:unspecified",  # Faire des achats en grand magasin, supermarché, hypermarché et leurs galeries marchandes.
    33: "shopping:unspecified",  # Faire des achats en petit et moyen commerce et drive in
    34: "shopping:unspecified",  # Faire des achats en marché couvert et de plein vent.
    35: "shopping:pickup",  # Récupérer des achats faits à distance (Drive, points relais)
    41: "task:healthcare",  # Recevoir des soins (santé).
    42: "task:procedure",  # Faire une démarche autre que rechercher un emploi.
    43: "task:job_search",  # Rechercher un emploi.
    51: "leisure:sport_or_culture",  # Participer à des loisirs, des activités sportives, culturelles ou associatives.
    52: "leisure:walk_or_driving_lesson",  # Faire une promenade, du « lèche-vitrines », prendre une leçon de conduite.
    53: "leisure:restaurant",  # Se restaurer hors du domicile.
    54: "leisure:visiting",  # Visiter des parents ou des amis.
    # NOTE. We discard the information on whether the escorted person is present during pick_up /
    # drop_off activity as it can be deduced (when I go pick-up someone, he's not there; when I come
    # back from picking-up someone, he's there). Also, there are some errors in the data (like
    # having the escorted person both before and after picking him up).
    61: "escort:activity:drop_off",  # Accompagner quelqu’un (personne présente).
    62: "escort:activity:pick_up",  # Aller chercher quelqu’un (personne présente).
    63: "escort:activity:drop_off",  # Accompagner quelqu’un (personne absente).
    64: "escort:activity:pick_up",  # Aller chercher quelqu’un (personne absente).
    68: "escort:unspecified:drop_off",  # Accompagner quelqu’un ou déposer quelqu’un à un mode de transport (sans info présence personne)
    69: "escort:unspecified:pick_up",  # Aller chercher quelqu’un ou reprendre quelqu’un à un mode de transport (sans info présence personne)
    71: "escort:transport:drop_off",  # Déposer une personne à un mode de transport (personne présente).
    72: "escort:transport:pick_up",  # Reprendre une personne à un mode de transport (personne présente).
    73: "escort:transport:drop_off",  # Déposer d’une personne à un mode de transport (personne absente).
    74: "escort:transport:pick_up",  # Reprendre une personne à un mode de transport( personne absente).
    81: "work:professional_tour",  # Réaliser une tournée professionnelle.
    82: "shopping:tour_no_purchase",  # Tournée de magasin sans achat
    91: "other",  # Autres motifs
    # 96: "escort:middle_high_school",  # Étudier sur le lieu d'études déclaré (collège ou lycée). Cas egt personne accompagnée
    # 97: "escort:middle_high_school:other",  # Étudier sur un autre lieu (collège ou lycée). Cas egt personne accompagnée
    # 98: "escort:shopping",  # Faire des achats sans précision (egt, motif personne accompagnée)
    # Note: Values 96, 97, and 98 are documented but never appear in a survey.
}

SHOP_TYPE_MAP = {
    31: "mall",  # Réaliser plusieurs motifs en centre commercial.
    32: "supermarket_or_hypermarket",  # Faire des achats en grand magasin, supermarché, hypermarché et leurs galeries marchandes.
    33: "small_shop",  # Faire des achats en petit et moyen commerce et drive in
    34: "market",  # Faire des achats en marché couvert et de plein vent.
    35: "drive_in",  # Récupérer des achats faits à distance (Drive, points relais)
}

TRIP_PERIMETER_MAP = {
    1: "internal",  # interne au périmètre d'enquête
    2: "crossing",  # en échange
    3: "external",  # externe au périmètre d'enquête
    9: None,  # inconnu (cas où origine ou destination inconnue)
}


def scan_trips_impl(source: str | bytes):
    return pl.scan_csv(source, separator=";", schema_overrides=SCHEMA, null_values=["aa", "aaaaa"])


class TripsReader:
    def scan_trips(self):
        lfs_iter = map(scan_trips_impl, self.trips_filenames())
        lf = pl.concat(lfs_iter, how="vertical")
        return lf

    def standardize_trips(self):
        lf = self.scan_trips()
        # Add household_id, person_id, and trip date.
        lf = lf.with_columns(
            original_person_id=pl.struct(**self.get_person_index_cols_from_trips())
        ).join(
            self.persons.select("original_person_id", "person_id", "household_id", "trip_date"),
            on="original_person_id",
            how="left",
            coalesce=True,
        )
        lf = lf.rename(
            {
                "GDO1": "origin_insee",
                "D3": "origin_detailed_zone",
                "STDO": "origin_draw_zone",
                "GDD1": "destination_insee",
                "D7": "destination_detailed_zone",
                "STDD": "destination_draw_zone",
                "D6": "nb_tour_stops",
            }
        )
        lf = lf.with_columns(
            original_trip_id=pl.struct(self.get_trip_index_cols()),
            origin_purpose=pl.col("D2A").replace_strict(PURPOSE_MAP),
            origin_escort_purpose=pl.col("D2B").replace_strict(PURPOSE_MAP),
            origin_shop_type=pl.col("D2A").replace(SHOP_TYPE_MAP, default=None),
            departure_time=60 * (pl.col("D4") // 100) + pl.col("D4") % 100,
            destination_purpose=pl.col("D5A").replace_strict(PURPOSE_MAP),
            destination_escort_purpose=pl.col("D5B").replace_strict(PURPOSE_MAP),
            destination_shop_type=pl.col("D5A").replace(SHOP_TYPE_MAP, default=None),
            arrival_time=60 * (pl.col("D8") // 100) + pl.col("D8") % 100,
            trip_euclidean_distance_km=pl.col("D11") / 1e3,
            trip_travel_distance_km=pl.col("D12") / 1e3,
            main_mode=pl.col("MODP").replace_strict(self.get_mode_map()),
            trip_perimeter=pl.col("TYPD").replace_strict(TRIP_PERIMETER_MAP),
        )
        lf = lf.with_columns(
            # In some cases, the departure and arrival times are switched.
            departure_time=pl.when(
                pl.col("D9") == pl.col("departure_time") - pl.col("arrival_time")
            )
            .then("arrival_time")
            .otherwise("departure_time"),
            arrival_time=pl.when(pl.col("D9") == pl.col("departure_time") - pl.col("arrival_time"))
            .then("departure_time")
            .otherwise("arrival_time"),
            # When destination purpose is 52 (« Faire une promenade, du « lèche-vitrines », prendre
            # une leçon de conduite. ») and `nb_tour_stops` is defined, then we know that purpose is
            # « lèche-vitrines » so we can set purpose to "shopping:tour_no_purchase".
            destination_purpose=pl.when(pl.col("D5A").eq(52), pl.col("nb_tour_stops").is_not_null())
            .then(pl.lit("shopping:tour_no_purchase"))
            .otherwise("destination_purpose"),
            # Special case for Saint-Brieuc 2012: there is no NULL value in the D6 column
            # (nb_tour_stops). It seems that the column represents either the trip travel time or
            # the actual number of tour stops. To be safe, we just throw away all the values.
            nb_tour_stops=pl.when(pl.col("nb_tour_stops").is_not_null().all())
            .then(pl.lit(None))
            .otherwise("nb_tour_stops"),
            # Values 99000, 99999, 99095, 99300 do not represent any known INSEE / country.
            origin_insee=pl.col("origin_insee").replace(["99000", "99999", "99095", "99300"], None),
            destination_insee=pl.col("destination_insee").replace(
                ["99000", "99999", "99095", "99300"], None
            ),
        )
        lf = lf.sort("original_trip_id")
        lf = fix_origin_destination_detailed_zones(lf)
        df = lf.collect()
        year = round(df["trip_date"].dt.year().mean())
        # For Besançon 2018, there is one missing person.
        n = df["person_id"].null_count()
        if n > 0:
            logger.warning(f"{n} trips are assigned to an unknown person. They are dropped.")
            df = df.filter(pl.col("person_id").is_not_null())
        self.trips = clean(
            df.lazy(),
            year=year,
            special_locations=self.special_locations_coords,
            detailed_zones=self.detailed_zones_coords,
        )
        # When the INSEE code ends with "000" or "999" it means "rest of the département".
        # We drop these values because they do not add any additional information compared to `_dep`
        # columns.
        # This is done after the automatic cleaning so that the département is correctly read.
        self.trips = self.trips.with_columns(
            origin_insee=pl.when(
                pl.col("origin_insee").str.ends_with("000")
                | pl.col("origin_insee").str.ends_with("999")
            )
            .then(None)
            .otherwise("origin_insee"),
            destination_insee=pl.when(
                pl.col("destination_insee").str.ends_with("000")
                | pl.col("destination_insee").str.ends_with("999")
            )
            .then(None)
            .otherwise("destination_insee"),
        )


def fix_origin_destination_detailed_zones(lf: pl.LazyFrame):
    # For external origin / destination location, the detailed zone id is sometimes set to
    # "8" + INSEE or "9" + INSEE. In this case, keeping the detailed zone id does not add any
    # information so we set it to NULL.
    lf = lf.with_columns(
        origin_detailed_zone=pl.when("8" + pl.col("origin_insee") == pl.col("origin_detailed_zone"))
        .then(None)
        .when("9" + pl.col("origin_insee") == pl.col("origin_detailed_zone"))
        .then(None)
        .otherwise("origin_detailed_zone"),
        destination_detailed_zone=pl.when(
            "8" + pl.col("destination_insee") == pl.col("destination_detailed_zone")
        )
        .then(None)
        .when("9" + pl.col("destination_insee") == pl.col("destination_detailed_zone"))
        .then(None)
        .otherwise("destination_detailed_zone"),
    )
    return lf

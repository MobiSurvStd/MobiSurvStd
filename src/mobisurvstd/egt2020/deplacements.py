from datetime import timedelta

import polars as pl

from mobisurvstd.common.trips import clean

SCHEMA = {
    "IDCEREMA": pl.String,  # Identifiant du ménage
    "TYPE_QUEST": pl.String,  # Type de questionnaire
    "NP": pl.UInt8,  # Numéro de personne dans le ménage
    "ND": pl.UInt8,  # Numéro de déplacement de la personne
    "RESCOUR": pl.UInt8,  # Couronne de résidence de la personne effectuant le déplacement
    "RESDEP": pl.String,  # Département de résidence
    "JOURSEM": pl.String,  # Jour de la semaine de la date schéma des déplacements
    "ORLNG": pl.Float64,  # Longitude du lieu d'origine
    "ORLAT": pl.Float64,  # Latitude du lieu d'origine
    "ORCOMM": pl.String,  # Commune d'origine du déplacement
    "ORDEP": pl.String,  # Département d'origine du déplacement
    "ORINSEE": pl.String,  # Code INSEE de la commune d'origine du déplacement
    "ORCOUR": pl.UInt8,  # Couronne d'origine du déplacement
    "ORHOR": pl.UInt16,  # Horaire de départ
    "ORMOT": pl.UInt16,  # Motif au départ
    "ORMOT_H9": pl.UInt8,  # Motif au départ (regroupé en 9 catégories)
    "DESTLNG": pl.Float64,  # Longitude du lieu de destination
    "DESTLAT": pl.Float64,  # Latitude du lieu de destination
    "DESTCOMM": pl.String,  # Commune de destination du déplacement
    "DESTDEP": pl.String,  # Département de destination du déplacement
    "DESTINSEE": pl.String,  # Code INSEE de la commune de destination du déplacement
    "DESTCOUR": pl.UInt8,  # Couronne de destination du déplacement
    "DESTHOR": pl.UInt16,  # Horaire d'arrivée
    "DESTMOT": pl.UInt16,  # Motif à l'arrivée
    "DESTMOT_H9": pl.UInt8,  # Motif à l'arrivée (regroupé en 9 catégories)
    "MOTIF_COMBINE": pl.UInt8,  # Motif combiné origine / destination
    "DUREE": pl.UInt16,  # Durée du déplacement en minutes
    "DPORTEE": pl.Float64,  # Distance à vol d'oiseau du déplacement en kilomètres
    "N_MAP": pl.UInt8,  # Nombre d'utilisation de la marche à pied dans le déplacement
    "N_UFR": pl.UInt8,  # Nombre d'utilisation d'un fauteuil roulant dans le déplacement
    "N_VEL": pl.UInt8,  # Nombre d'utilisation d'un vélo dans le déplacement
    "N_2RM": pl.UInt8,  # Nombre d'utilisation d'un deux-roues motorisé dans le déplacement
    "N_VOI": pl.UInt8,  # Nombre d'utilisation d'une voiture dans le déplacement
    "N_TCO": pl.UInt8,  # Nombre d'utilisation des transports collectifs dans le déplacement
    "N_TAX": pl.UInt8,  # Nombre d'utilisation d'un taxi dans le déplacement
    "N_AUT": pl.UInt8,  # Nombre d'utilisation d'autres modes dans le déplacement
    "TLA": pl.UInt8,  # Type de lieu d'achat (si destination = lieu d'achat)
    "MODP_H6": pl.String,  # Mode principal en 6 modalités
    "MODP_H7": pl.String,  # Mode principal en 7 modalités
    "MODP_H12": pl.String,  # Mode principal en 12 modalités
    "MRAB": pl.String,  # Mode principal de rabattement vers les transports collectifs (avant d'emprunter la première ligne de transports collectifs du déplacement)
    "MDIFF": pl.String,  # Mode principal de diffusion depuis les transports collectifs (après avoir emprunté la dernière ligne de transports collectifs du déplacement)
    "NBCO_1": pl.UInt8,  # Nombre de correspondances si déplacement effectué en transports collectifs
    "DUR_TC1": pl.UInt32,  # Si l’itinéraire a inclus une utilisation des transports en commun ET que cet itinéraire a été renseigné à l’aide de ViaNavigo, cette variable indique la durée totale de l’itinéraire choisi. En secondes.
    "DUR_TC2": pl.UInt32,  # Si l’itinéraire a inclus une utilisation des transports en commun ET que cet itinéraire a été renseigné à l’aide de ViaNavigo, cette variable indique la durée totale de l’itinéraire le plus rapide (qui n’est pas forcément celui choisi par la personne). En secondes.
    "NBCO_2": pl.UInt8,  # Si l’itinéraire a inclus une utilisation des transports en commun ET que cet itinéraire a été renseigné à l’aide de ViaNavigo, cette variable indique le nombre minimal théorique de correspondances, basé sur les divers itinéraires possibles. Il est en effet possible que la personne ait un itinéraire préférentiel qui ne soit pas forcément celui considéré comme optimal par l’application.
    "POIDSI": pl.Float64,  # Poids de l'individu ayant réalisé le déplacement
}

PURPOSE_MAP = {
    # Domicile
    11: "home:main",  # Mon domicile
    12: "home:secondary",  # Autre domicile de la garde alternée
    13: "home:secondary",  # Résidence secondaire, logement occasionnel, hôtel, autre domicile
    # Travail
    21: "work:declared",  # Travail / Lieu travail précis
    31: "work:other",  # Affaires professionnelles (RV pro, réunion, etc.) hors lieu de travail habituel
    32: "work:other",  # Travail chez des particuliers
    33: "work:other",  # Travail dans un espace de co-working
    34: "work:telework",  # Travail au domicile personnel
    35: "work:other",  # Travail sur un autre lieu
    36: "work:professional_tour",  # Tournée professionnelle
    # Restauration
    611: "leisure:restaurant",  # Restaurant, cantine, cafétéria, bar, café…
    37: "work:business_meal",  # Repas d’affaires, déjeuner professionnel
    # Etudes ou crèche
    41: "education:childcare",  # Garde d'enfants
    42: "education:declared",  # Etudes
    43: "education:other",  # Etudes sur un autre lieu
    # Achats
    51: "shopping:daily",  # Achats quotidiens
    52: "shopping:weekly",  # Achats hebdomadaires
    53: "shopping:specialized",  # Achats occasionnels
    54: "shopping:pickup",  # Récupérer un colis
    621: "shopping:no_purchase",  # Lèche vitrines
    # Loisirs
    631: "leisure:sport_or_culture",  # Sortie
    622: "leisure:walk_or_driving_lesson",  # Promenade dans / vers un lieu précis (monument, parc, bois…)
    623: "leisure:walk_or_driving_lesson",  # Promenade sans but précis (dans le quartier…)
    641: "leisure:visiting",  # Rendre visite
    651: "leisure:sport_or_culture",  # Faire du sport
    652: "leisure:sport_or_culture",  # Participation à une activité artistique ou associative
    690: "leisure:other",  # Autres loisirs
    # Démarches
    71: "task:procedure",  # Démarches administratives
    72: "task:job_search",  # Recherche d’emploi
    73: "task:healthcare",  # Aide ou soins à des proches
    74: "task:healthcare",  # Santé
    75: "task:other",  # Affaires personnelles autres
    624: "leisure:walk_or_driving_lesson",  # Leçons de conduite
    # Accompagner quelqu'un
    811: "escort:transport:drop_off",  # Accompagner quelqu’un à un mode de transport
    821: "escort:transport:pick_up",  # Aller chercher quelqu’un à un mode de transport
    812: "escort:activity:drop_off",  # Accompagner quelqu’un
    822: "escort:activity:pick_up",  # Aller chercher quelqu’un
    # Autre
    90: "other",  # Autre lieu
}

SHOP_TYPE_MAP = {
    1: "small_shop",  # Dans un petit commerce
    2: "supermarket",  # Dans un supermarché
    3: "hypermarket",  # Dans un hypermarché ou une grande surface
    4: "mall",  # Dans un centre commercial ou un grand magasin
    5: "market",  # Dans un marché ou un marché aux puces
    6: "drive_in",  # Dans un drive-in ou un point relais
    7: "private",  # Chez un particulier
    9: "other",  # Autre
}


def scan_trips(filename: str):
    # We use the inefficient `read_csv().lazy()` because we need to use `encoding="latin1"`, which
    # does not exist with `scan_csv()`.
    lf = pl.read_csv(
        filename,
        separator=";",
        encoding="latin1",
        schema_overrides=SCHEMA,
        null_values=["-1"],
    ).lazy()
    return lf


def standardize_trips(filename: str, households: pl.LazyFrame, persons: pl.LazyFrame):
    lf = scan_trips(filename)
    # Add household_id and person_id.
    lf = lf.with_columns(original_person_id=pl.struct("IDCEREMA", "NP")).join(
        persons.select("original_person_id", "person_id", "household_id"),
        on="original_person_id",
        how="left",
        coalesce=True,
    )
    # Add interview_date.
    lf = lf.join(
        households.select("household_id", "interview_date"),
        on="household_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename(
        {
            "ORLNG": "origin_lng",
            "ORLAT": "origin_lat",
            "ORINSEE": "origin_insee",
            "DESTLNG": "destination_lng",
            "DESTLAT": "destination_lat",
            "DESTINSEE": "destination_insee",
            "DPORTEE": "trip_euclidean_distance_km",
        }
    )
    lf = lf.with_columns(
        original_trip_id=pl.struct("IDCEREMA", "NP", "ND"),
        # TODO: In the current version, home purpose is not specified but almost all nulls purposes
        # seem to be home.
        origin_purpose=pl.col("ORMOT").replace_strict(PURPOSE_MAP).fill_null("home:main"),
        destination_purpose=pl.col("DESTMOT").replace_strict(PURPOSE_MAP).fill_null("home:main"),
        destination_shop_type=pl.col("TLA").replace_strict(SHOP_TYPE_MAP),
        departure_time=(pl.col("ORHOR") // 100) * 60 + pl.col("ORHOR") % 100,
        arrival_time=(pl.col("DESTHOR") // 100) * 60 + pl.col("DESTHOR") % 100,
        # For INSEE in départements < 10, the starting 0 is omitted (e.g., "02307" is "2307") so we
        # need to add it.
        origin_insee=pl.when(pl.col("origin_insee").str.len_chars() < 4)
        .then(pl.lit(None))
        .when(pl.col("origin_insee").str.len_chars() == 4)
        .then(pl.col("origin_insee").str.pad_start(5, "0"))
        .otherwise("origin_insee"),
        destination_insee=pl.when(pl.col("destination_insee").str.len_chars() < 4)
        .then(pl.lit(None))
        .when(pl.col("destination_insee").str.len_chars() == 4)
        .then(pl.col("destination_insee").str.pad_start(5, "0"))
        .otherwise("destination_insee"),
        # The trip took place the day before the interview.
        trip_date=pl.col("interview_date") - timedelta(days=1),
    ).with_columns(
        # Read the `origin_shop_type` from the `destination_shop_type` of the previous trip.
        origin_shop_type=pl.when(pl.col("origin_purpose").str.starts_with("shopping:")).then(
            pl.col("destination_shop_type").shift(1).over("person_id")
        ),
    )
    # For EGT2020, we use the AAV and density data from 2020 (even if some interviews are from 2018
    # and 2019).
    # The survey perimiters cover excatly the 8 départements of the IDF region.
    lf = clean(lf, 2020, perimeter_deps=["75", "77", "78", "91", "92", "93", "94", "95"])
    return lf

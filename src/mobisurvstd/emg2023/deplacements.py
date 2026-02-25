from datetime import timedelta

import polars as pl

from mobisurvstd.common.trips import clean as clean_trips
from mobisurvstd.common.legs import clean as clean_legs


SCHEMA = {
    "KEY": pl.String, # Identifiant unique des déplacements (ID* jour * date au format numérique * numéro de déplacement)
    "ID": pl.String, # Identifiant de l'individu
    "Jour_EMG": pl.String, # Jour enquêté (Lundi à Dimanche)
    "Date_EMG": pl.Date, # Date du jour enquêté (une journée commence à 4h le jour enquêté et se termine à 4h le jour suivant)
    "Type_Jour": pl.String, # Indique si c'est un jour férié, un jour durant une période de vacances scolaires ou un jour de grève nationale des transports
    "Num_depl": pl.String, # numéro du déplacement de la journée
    "Type_OD": pl.String, # Indique la nature géographique du déplacement
    "Com_O": pl.String, # Commune d'origine du déplacement
    "Com_D": pl.String, # Commune de destination du déplacement
    "Code_INSEE_O": pl.String, # Code INSEE de la commune d'origine du déplacement
    "Code_INSEE_D": pl.String, # Code INSEE de la commune de destination du déplacement
    "Couronne_O": pl.String, # Couronne d'origine du déplacement
    "Couronne_D": pl.String, # Couronne de destination du déplacement
    "Couronne_OD": pl.String, # Indique la liaison géographique du déplacement pour les déplacements internes à l'Île-de-France
    "Dept_O": pl.String, # Département d'origine du déplacement
    "Dept_D": pl.String, # Département de destination du déplacement
    "Date_O": pl.Date, # Date d'origine du déplacement
    "Heure_O": pl.Time, # Heure d'origine du déplacement
    "Date_D": pl.Date, # Date de destination du déplacement
    "Heure_D": pl.Time, # Heure de destination du déplacement
    "Duree": pl.Float64, # Durée du déplacement (en minutes)
    "Motif_O": pl.String, # Motif ou activité à l'origine du déplacement
    "Motif_D": pl.String, # Motif ou activité à destination du déplacement
    "Mode_Principal": pl.String, # Mode principal utilisé au cours du déplacement (selon la hiérarchie conventionnelle des modes)
    "Mode_1": pl.String, # Modes utilisés au cours du déplacement
    "Mode_2": pl.String, # Modes utilisés au cours du déplacement
    "Mode_3": pl.String, # Modes utilisés au cours du déplacement
    "Mode_4": pl.String, # Modes utilisés au cours du déplacement
    "Mode_5": pl.String, # Modes utilisés au cours du déplacement
    "Poids_Jour": pl.Float64
}

PURPOSE_GROUP_MAP = {
    "ACCOM": "escort", # Accompagner, déposer ou aller chercher quelqu’un (à l’école, à la garderie, à la gare, au sport, au travail …)
    "ACHAT": "shopping", # Achats ou courses : boulangerie, commerce, hypermarché ...
    "AFF PRO": "work", # Affaires professionnelles, autre lieu de travail (réunion, tournée, colloque ...)
    "AUTRE": "other", # Visite à la famille ou à des amis, démarche administrative ou personnelle (recherche d’emploi, agence bancaire, avocat, garagiste …), aller déjeuner à midi à l’extérieur
    "DOMICILE": "home", # Retour au domicile
    "ETUDES": "education", # Se rendre à son lieu d'enseignement habituel
    "LOISIRS": "leisure", # Activité de loisirs (cinéma, restaurant, sports, promenade …), voyage de tourisme
    "SANTE": "other", # Se rendre à l'hôpital, au cabinet médical ou infirmier, au laboratoire d’analyse, dentiste, kiné, pharmacie
    "TRAVAIL": "work", # Se rendre à son lieu de travail habituel
}

MODE_MAP = {
    "2RM": "motorcycle:driver", # Deux-roues motorisé
    "AUTRE": "other", #	Autre mode (skateboard, roller, ...)
    "AVION": "airplane", # Avion
    "BUS": "public_transit:urban:bus", # Bus
    "MAP": "walking", #	Marche à pied
    "METRO": "public_transit:urban:metro", # Métro
    "RER/TRAIN": "public_transit:urban:rail", #	RER ou Train du réseau régional francilien
    "RER/METRO": "public_transit:urban:rail", #	There is one entry "RER/METRO" that should be RER.
    "TAD": "public_transit:urban:demand_responsive", # Transport à la demande
    "TAXI/VTC": "taxi_or_VTC", # Taxi ou Vtc
    "TGV/INTERCITES/TER": "public_transit:interurban:other_train", # TGV ou Intercités ou Train express régional
    "TRAM": "public_transit:urban:tram", # Tramway
    "TROTTINETTE": "personal_transporter:motorized", # Trottinette électrique
    "VAE": "bicycle:driver:electric", # Vélo à assistance électrique
    "VELO": "bicycle:driver:traditional", # Vélo
    "VPC": "car:driver", # Voiture particulière en tant que conducteur
    "VPP": "car:passenger", # Voiture particulière en tant que passager
    "VUL": "truck:driver", # Véhicule utilitaire léger
}

WEEKDAY_MAP = {
    "lundi": "monday",
    "mardi": "tuesday",
    "mercredi": "wednesday",
    "jeudi": "thursday",
    "vendredi": "friday",
    "samedi": "saturday",
    "dimanche": "sunday"
}

def scan_trips(filename: str):
    lf = pl.read_excel(filename, schema_overrides=SCHEMA).lazy()
    return lf

def standardize_trips(
    filename: str,
    persons: pl.LazyFrame,
    distances: pl.LazyFrame | None = None
):
    lf = scan_trips(filename)

    lf = lf.with_columns(original_person_id=pl.col("ID")).join(
        persons.select("original_person_id", "person_id", "household_id"),
        on="original_person_id",
        how="left",
        coalesce=True,
    )

    lf = lf.with_columns(
        original_trip_id=pl.col("KEY"),
        index=pl.col("KEY").str.extract("-([0-9]+)$").cast(pl.UInt8),
        origin_purpose_group=pl.col("Motif_O").str.to_uppercase().replace_strict(PURPOSE_GROUP_MAP),
        destination_purpose_group=pl.col("Motif_D").str.to_uppercase().replace_strict(PURPOSE_GROUP_MAP),
        origin_insee=pl.when(pl.col("Code_INSEE_O").is_in(("ETRANGER", "HORS IDF"))).then(None).otherwise("Code_INSEE_O"),
        destination_insee=pl.when(pl.col("Code_INSEE_D").is_in(("ETRANGER", "HORS IDF"))).then(None).otherwise("Code_INSEE_D"),
        departure_time=pl.col("Heure_O").dt.hour().cast(pl.UInt16) * 60 + pl.col("Heure_O").dt.minute(),
        arrival_time=pl.col("Heure_D").dt.hour().cast(pl.UInt16) * 60 + pl.col("Heure_D").dt.minute(),
        trip_date=pl.col("Date_EMG"),
        trip_weekday=pl.col("Jour_EMG").replace_strict(WEEKDAY_MAP),
        main_mode=pl.col("Mode_Principal").str.to_uppercase().replace_strict(MODE_MAP),
        # Mode_1 is needed for the fix below.
        Mode_1=pl.col("Mode_1").str.to_uppercase().str.strip_chars().replace_strict(MODE_MAP),
    )

    # In 3 cases, `main_mode` is "walking" but `Mode_1` is something else and the other `Mode_*`
    # variables are not defined.
    # In this case, set `Mode_1` as the main mode.
    lf = lf.with_columns(
        main_mode=pl.when(
            pl.col("main_mode").eq("walking"),
            pl.col("Mode_1").ne("walking"),
            pl.col("Mode_2").is_null(),
            pl.col("Mode_3").is_null(),
            pl.col("Mode_4").is_null(),
            pl.col("Mode_5").is_null(),
        )
        .then("Mode_1")
        .otherwise("main_mode")
    )

    if distances is not None:
        lf = lf.join(
            distances.select("original_trip_id", "trip_travel_distance_km"),
            on="original_trip_id",
            how="left",
            coalesce=True,
        )

    lf = lf.with_columns(
        origin_insee=pl.when(pl.col("origin_insee").str.ends_with("000"))
        .then(None)
        .otherwise("origin_insee"),
        destination_insee=pl.when(pl.col("destination_insee").str.ends_with("000"))
        .then(None)
        .otherwise("destination_insee"),
    )

    lf = lf.sort(["person_id", "trip_date", "index"])

    # fix the case where we are departing at 23:40 on day 1 and arrive at 00:20 on day 2
    lf = lf.with_columns(
        arrival_time=pl.when(
            pl.col("arrival_time") + 24 * 60 == pl.col("departure_time") + pl.col("Duree")
        ).then(pl.col("arrival_time") + 24 * 60).otherwise("arrival_time")
    )

    # filter out days without trace (PDT), without trip (PDD), or outside IDF (HORS IDF)
    lf = lf.filter(pl.col("Num_depl").is_in(["PDT", "PDD", "HORS IDF"]).not_())

    lf = clean_trips(
        lf,
        2023,
        perimeter_deps=["75", "77", "78", "91", "92", "93", "94", "95"]
    )
    
    return lf

DISTANCES_SCHEMA = {
    "KEY": pl.String, # unique trip identifier
    "Distance": pl.Float64, # trip distance (not clear if Euclidean or routed)
}

def scan_distances(filename: str):
    lf = pl.read_excel(filename, schema_overrides=DISTANCES_SCHEMA).lazy()
    return lf

def standardize_distances(filename: str):
    lf = scan_distances(filename)

    lf = lf.with_columns(
        original_trip_id=pl.col("KEY"),
        trip_travel_distance_km=pl.col("Distance") * 1e-3,
    )
    
    lf = lf.sort("original_trip_id")
    return lf

def standardize_legs(filename: str, trips: pl.LazyFrame):
    lf = scan_trips(filename)
    # filter out days without trace (PDT), without trip (PDD), or outside IDF (HORS IDF)
    lf = lf.filter(pl.col("Num_depl").is_in(["PDT", "PDD", "HORS IDF"]).not_())
    # The `fill_null` is required for 8 trips with a main mode but no leg mode defined.
    lf = lf.select(
        "KEY",
        pl.col("Mode_1").fill_null(pl.col("Mode_Principal")).alias("1"),
        pl.col("Mode_2").alias("2"),
        pl.col("Mode_3").alias("3"),
        pl.col("Mode_4").alias("4"),
        pl.col("Mode_5").alias("5"),
    )
    lf = lf.unpivot(index="KEY", variable_name="leg_index", value_name="mode")
    lf = lf.with_columns(pl.col("leg_index").cast(pl.UInt8))
    # Add household_id, person_id, and trip_id + main_mode (needed below).
    lf = lf.with_columns(original_trip_id=pl.col("KEY")).join(
        trips.select("original_trip_id", "household_id", "person_id", "trip_id", "main_mode"),
        on="original_trip_id",
        how="left",
        coalesce=True,
    )
    # Drop legs with NULL mode (there is by default 5 legs by trip).
    lf = lf.filter(pl.col("mode").is_not_null(), pl.col("mode").ne(""))
    lf = lf.with_columns(
        original_leg_id=pl.struct("KEY", "leg_index"),
        # `strip_chars` is needed to remove an extra whitespace
        mode=pl.col("mode").str.to_uppercase().str.strip_chars().replace_strict(MODE_MAP),
    )
    # For 3 trips, only one leg-mode is defined and it does not match the main trip-mode.
    # In this case, my best guess is to replace the leg-mode by the trip-mode.
    lf = lf.with_columns(
        mode=pl.when(
            pl.len().over("trip_id").eq(1),
            pl.col("main_mode") != pl.col("mode"),
            pl.col("main_mode") != "walking",
        )
        .then("main_mode")
        .otherwise("mode")
    )
    lf = lf.sort("trip_id", "leg_index")
    # Rebuild `leg_index` since some modes can be skip (e.g., "Modes_1" and "Modes_3" are defined
    # but not "Modes_2").
    lf = lf.with_columns(leg_index=pl.int_range(1, pl.len() + 1).over("trip_id"))
    lf = clean_legs(lf)
    return lf


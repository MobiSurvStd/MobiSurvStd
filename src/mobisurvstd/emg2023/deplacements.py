from datetime import timedelta

import polars as pl

from mobisurvstd.common.trips import clean


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

MODE_GROUP_MAP = {
    "2RM": "motorcycle", # Deux-roues motorisé
    "AUTRE": "other", #	Autre mode (skateboard, roller, ...)
    "AVION": "public_transit", # Avion
    "BUS": "public_transit", # Bus
    "MAP": "walking", #	Marche à pied
    "METRO": "public_transit", # Métro
    "RER/TRAIN": "public_transit", #	RER ou Train du réseau régional francilien
    "TAD": "public_transit", # Transport à la demande
    "TAXI/VTC": "public_transit", # Taxi ou Vtc
    "TGV/INTERCITES/TER": "public_transit", # TGV ou Intercités ou Train express régional
    "TRAM": "public_transit", # Tramway
    "TROTTINETTE": "other", # Trottinette électrique
    "VAE": "bicycle", # Vélo à assistance électrique
    "VELO": "bicycle", # Vélo
    "VPC": "car_driver", # Voiture particulière en tant que conducteur
    "VPP": "car_passenger", # Voiture particulière en tant que passager
    "VUL": "other", # Véhicule utilitaire léger
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
    distances: pl.LazyFrame = None
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
        origin_purpose=None, # added because requested downstream
        origin_purpose_group=pl.col("Motif_O").str.to_uppercase().replace_strict(PURPOSE_GROUP_MAP),
        destination_purpose=None, # added because requested downstream
        destination_purpose_group=pl.col("Motif_D").str.to_uppercase().replace_strict(PURPOSE_GROUP_MAP),
        origin_insee=pl.when(pl.col("Code_INSEE_O").is_in(("ETRANGER", "HORS IDF"))).then(None).otherwise("Code_INSEE_O"),
        destination_insee=pl.when(pl.col("Code_INSEE_D").is_in(("ETRANGER", "HORS IDF"))).then(None).otherwise("Code_INSEE_D"),
        departure_time=pl.col("Heure_O").dt.hour().cast(pl.UInt16) * 60 + pl.col("Heure_O").dt.minute(),
        arrival_time=pl.col("Heure_D").dt.hour().cast(pl.UInt16) * 60 + pl.col("Heure_D").dt.minute(),
        trip_date=pl.col("Date_EMG"),
        trip_weekday=pl.col("Jour_EMG").replace_strict(WEEKDAY_MAP),
        main_mode_group=pl.col("Mode_Principal").str.to_uppercase().replace_strict(MODE_GROUP_MAP),
    )

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

    # we order by departure time since some trips seem to have been added to the end of the day
    # (from data correction?)
    lf = lf.sort(["person_id", "trip_date", "departure_time"])

    # generate an offset for the times
    lf = lf.with_columns(
        offset=pl.col("trip_date").ne(pl.col("trip_date").shift(1)).cum_sum().over("person_id").fill_null(0).cast(pl.UInt8)
    )

    lf = lf.with_columns(
        departure_time=pl.col("departure_time").add(pl.col("offset").mul(24 * 60)),
        arrival_time=pl.col("arrival_time").add(pl.col("offset").mul(24 * 60)),
        sequence=pl.int_range(1, pl.len() + 1),
    )

    # fix the case where we are departing at 23:40 on day 1 and arrive at 00:20 on day 2
    lf = lf.with_columns(
        arrival_time=pl.when(
            (pl.col("arrival_time") < pl.col("departure_time")) &
            (
                (pl.col("trip_date").shift(-1) == pl.col("trip_date") + timedelta(days = 1)) |
                pl.col("sequence").eq(pl.col("sequence").last().over("person_id"))
            )
        ).then(pl.col("arrival_time") + 24 * 60).otherwise("arrival_time").over("person_id")
    )

    # filter out days without trace (PDT), without trip (PDD), or outside IDF (HORS IDF)
    lf = lf.filter(pl.col("Num_depl").is_in(["PDT", "PDD", "HORS IDF"]).not_())

    lf = lf.drop("sequence")

    lf = clean(
        lf,
        2023,
        perimeter_deps=["75", "77", "78", "91", "92", "93", "94", "95"]
    )
    
    lf = lf.sort(["trip_id"])
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

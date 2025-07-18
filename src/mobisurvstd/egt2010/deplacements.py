from datetime import timedelta

import polars as pl

from mobisurvstd.common.trips import clean

SCHEMA = {
    "NQUEST": pl.UInt32,  # Identifiant du ménage
    "NP": pl.UInt8,  # Numéro de personne dans le ménage
    "ND": pl.UInt8,  # Numéro de déplacement de la personne
    "POIDSP": pl.Float64,  # Poids de la personne réalisant le déplacement
    "JDEP": pl.UInt8,  # Jour de la semaine où le déplacement est effectué
    "RESCOUR": pl.UInt8,  # Couronne de résidence de la personne effectuant le déplacement
    "RESDEP": pl.String,  # Département de résidence de la personne effectuant le déplacement
    "RESSECT": pl.String,  # Secteur de résidence de la personne effectuant le déplacement
    "RESCOMM": pl.String,  # Commune de résidence de la personne effectuant le déplacement
    "RESC": pl.String,  # Carreau de résidence de la personne effectuant le déplacement
    "ORCOUR": pl.UInt8,  # Couronne d'origine du déplacement
    "ORDEP": pl.String,  # Département d'origine du déplacement
    "ORSECT": pl.String,  # Secteur d'origine du déplacement
    "ORCOMM": pl.String,  # Commune d'origine du déplacement
    "ORC": pl.String,  # Carreau d'origine du déplacement
    "ORH": pl.UInt16,  # Heure de départ
    "ORM": pl.UInt16,  # Minute de départ
    "ORMOT": pl.UInt8,  # Motif au départ
    "ORMOT_H9": pl.UInt8,  # Motif au départ (regroupé en 9 catégories)
    "DESTCOUR": pl.UInt8,  # Couronne de destination du déplacement
    "DESTDEP": pl.String,  # Département de destination du déplacement
    "DESTSECT": pl.String,  # Secteur de destination du déplacement
    "DESTCOMM": pl.String,  # Commune de destination du déplacement
    "DESTC": pl.String,  # Carreau de destination du déplacement
    "DESTH": pl.UInt16,  # Heure d'arrivée
    "DESTM": pl.UInt16,  # Minute d'arrivée
    "DESTMOT": pl.UInt8,  # Motif à l'arrivée
    "DESTMOT_H9": pl.UInt8,  # Motif à l'arrivée (regroupé en 9 catégories)
    "DESTMOT_IAURIF02": pl.UInt8,  # Motif à l'arrivée (définition IAURIF)
    "MOTIF_COMBINE": pl.UInt8,  # Motif combiné origine / destination
    "DPORTEE": pl.Float64,  # Portée du déplacement en kilomètres (pour interne IdF)
    "DUREE": pl.UInt16,  # Durée du déplacement en minutes (pour interne IdF)
    "ACCMOT": pl.UInt8,  # Motif de la personne accompagnée
    "ACCMOT_H9": pl.UInt8,  # Motif de la personne accompagnée (regroupé en 9 catégories)
    "ACCNP": pl.UInt8,  # Numéro de la personne accompagnée si personne du ménage
    "TLT": pl.UInt8,  # Type de lieu de travail (si destination = lieu de travail)
    "TLA": pl.UInt8,  # Type de lieu d'achat (si destination = lieu d'achat)
    "NBAT": pl.UInt8,  # Nombre d'arrêts dans la tournée
    "TRP": pl.UInt8,  # Avez-vous traversé Paris intra muros pendant le déplacement
    "MODP_STRICT": pl.UInt8,  # Mode principal strict détaillé
    "MODP_H6": pl.UInt8,  # Mode principal en 6 modalités
    "MODP_H7": pl.UInt8,  # Mode principal en 7 modalités
    "MODP_H12": pl.UInt8,  # Mode principal en 12 modalités
    "MODP_H19": pl.UInt8,  # Mode principal en 19 modalités
    "NBTRAJ": pl.UInt8,  # Nombre de trajets réalisés dans le déplacement
    "NBTRAJVP": pl.UInt8,  # Nombre de trajets réalisés en voiture (passager ou conducteur) dans le déplacement
    "NBTRAJVPC": pl.UInt8,  # Nombre de trajets réalisés en voiture (conducteur) dans le déplacement
    "NBTRAJTC": pl.UInt8,  # Nombre de trajets réalisés en transports collectifs dans le déplacement
    "NBTRAJVELO": pl.UInt8,  # Nombre de trajets réalisés à vélo dans le déplacement
    "NBTRAJ2RM": pl.UInt8,  # Nombre de trajets réalisés en deux roues-motorisé dans le déplacement
    "IDM": pl.UInt8,  # Indicateur de déplacement motorisé
    "NBCO": pl.UInt8,  # Nombre de correspondances si déplacement effectué en transports collectifs
    "RAB_TC": pl.UInt8,  # Mode principal de rabattement vers les transports collectifs (avant d'emprunter la première ligne de transports collectifs du déplacement)
    "DIFF_TC": pl.UInt8,  # Mode principal de diffusion depuis les transports collectifs (après avoir emprunté la dernière ligne de transports collectifs du déplacement)
}

PURPOSE_MAP = {
    "1": "home:main",  # Domicile habituel (celui où la personne est enquêtée)
    "2": "home:secondary",  # Un des domiciles correspondant à une garde alternée
    "3": "home:secondary",  # Résidence secondaire, logement occasionnel, hôtel, autre domicile
    # Motifs professionnels
    "11": "work:declared",  # Travail sur le lieu de travail déclaré dans la fiche personne
    "12": "work:secondary",  #  Travail sur un autre lieu (hors affaires professionnelles)
    "13": "work:other",  #  Affaires professionnelles hors lieu de travail habituel (RV professionnel, réunion, etc.)
    "14": "work:professional_tour",  # Tournée professionnelle
    # Restauration hors domicile
    "15": "work:business_meal",  # Repas d’affaires, déjeuner professionnel
    "16": "leisure:lunch_break",  # Pause déjeuner durant la journée de travail (cantine, cafétéria, restaurant situés hors du lieu de travail…)
    "17": "leisure:restaurant",  # Autre restauration hors domicile (restaurant, bar, café, cybercafé…)
    # Etudes -Garde d’enfants
    "21": "education:childcare",  # Nourrice, crèche, garde d’enfants
    "22": "education:declared",  # Études sur le lieu d'études déclaré (école maternelle et primaire)
    "23": "education:declared",  # Études sur le lieu d'études déclaré (enseignement secondaire : collège et lycée)
    "24": "education:declared",  # Études sur le lieu d'études déclaré (enseignement supérieur, universités et grandes écoles)
    "25": "education:other",  # Études sur un autre lieu (école maternelle et primaire)
    "26": "education:other",  # Études sur un autre lieu (enseignement secondaire : collège et lycée)
    "27": "education:other",  # Études sur un autre lieu (enseignement supérieur, universités et grandes écoles)
    # Achats
    "31": "shopping:daily",  # Achats quotidiens (pain, journal, …)
    "32": "shopping:weekly",  # Achats hebdomadaires ou bi hebdomadaires
    "33": "shopping:specialized",  # Achats occasionnels (livres, vêtements, électroménager, musique, meubles etc.)
    # Loisirs
    "41": "leisure:sport_or_culture",  # Participation à une activité sportive, culturelle, associative ou religieuse
    "42": "leisure:walk_or_driving_lesson",  # Promenade, lèche-vitrines (sans achat), leçons de conduite
    "43": "leisure:visiting:parents",  # Visite à des parents
    "44": "leisure:visiting:friends",  # Visite à des amis
    "45": "leisure:sport_or_culture",  # Spectacle, exposition, cinéma, musée, théâtre, concert, match de foot…
    "46": "leisure:sport_or_culture",  # Voyage, sortie touristique
    "47": "leisure:other",  # Autres loisirs
    # Démarches administratives/ Affaires personnelles
    "50": "task:procedure",  # Démarches administratives
    "51": "task:job_search",  # Recherche d’emploi (y. entretiens)
    "52": "task:healthcare",  # Aide ou soins à des proches
    "53": "task:healthcare:hospital",  # Santé (hôpital, clinique)
    "54": "task:healthcare:doctor",  # Santé autres (consultation professionnel de la santé hors hôpital : médecin, dentiste, kiné, etc.)
    "55": "task:other",  # Affaires personnelles autres (avocat, notaire, garage, réunion parents d’élèves, réunion de copropriétaires etc.)
    # Accompagnement
    "61": "escort:transport:drop_off",  # Dépose d’une personne à un mode de transport (station, gare, arrêt de bus, aéroport…)
    "62": "escort:transport:pick_up",  # Reprise d’une personne à un mode de transport (station, gare, arrêt de bus, aéroport…)
    "63": "escort:activity:drop_off",  # Accompagner quelqu’un dans un lieu autre qu’un mode de transport (école, garderie, amis, cinéma, sport, travail etc.)
    "64": "escort:activity:pick_up",  # Aller chercher quelqu’un (dans un lieu autre qu’un mode de transport (école, garderie, amis, cinéma, sport, travail etc.)
    "98": "other",  # Autre motif
}

SHOP_TYPE_MAP = {
    1: "small_shop",  # Petit commerce
    2: "small_shop",  # Supérette
    3: "supermarket",  # Supermarché
    4: "hypermarket",  # Grande surface
    5: "hypermarket",  # Hypermarché
    6: "mall",  # Centre commercial
    7: "mall",  # Grands magasin
    8: "market",  # Marché
    9: "drive_in",  # Marché aux puces
}


def scan_trips(filename: str):
    lf = pl.scan_csv(filename, separator=";", schema_overrides=SCHEMA)
    return lf


def standardize_trips(filename: str, persons: pl.LazyFrame, households: pl.LazyFrame):
    lf = scan_trips(filename)
    # Add household_id and person_id.
    lf = lf.with_columns(original_person_id=pl.struct("NQUEST", "NP")).join(
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
            "ORC": "origin_detailed_zone",
            "ORSECT": "origin_draw_zone",
            "ORCOMM": "origin_insee",
            "DESTC": "destination_detailed_zone",
            "DESTSECT": "destination_draw_zone",
            "DESTCOMM": "destination_insee",
            "NBAT": "nb_tour_stops",
            "DPORTEE": "trip_euclidean_distance_km",
        }
    )
    lf = lf.with_columns(
        trip_index="ND",
        original_trip_id=pl.struct("NQUEST", "NP", "ND"),
        origin_purpose=pl.col("ORMOT").replace_strict(PURPOSE_MAP),
        destination_purpose=pl.col("DESTMOT").replace_strict(PURPOSE_MAP),
        origin_escort_purpose=pl.col("ACCMOT").replace_strict(PURPOSE_MAP),
        destination_escort_purpose=pl.col("ACCMOT").replace_strict(PURPOSE_MAP),
        destination_shop_type=pl.col("TLA").replace_strict(SHOP_TYPE_MAP),
        departure_time=pl.col("ORH") * 60 + pl.col("ORM"),
        arrival_time=pl.col("DESTH") * 60 + pl.col("DESTM"),
        # The trip took place the day before the interview.
        trip_date=pl.col("interview_date") - timedelta(days=1),
    ).with_columns(
        # Read the `origin_shop_type` from the `destination_shop_type` of the previous trip.
        origin_shop_type=pl.when(pl.col("origin_purpose").str.starts_with("shopping:")).then(
            pl.col("destination_shop_type").shift(1).over("person_id")
        ),
        # Set escort purpose to null when the purpose is not escort.
        # (EGT 2010 uses a single column for escort purpose at origin and at destination)
        origin_escort_purpose=pl.when(pl.col("origin_purpose").str.starts_with("escort:")).then(
            "origin_escort_purpose"
        ),
        destination_escort_purpose=pl.when(
            pl.col("destination_purpose").str.starts_with("escort:")
        ).then("destination_escort_purpose"),
    )
    # For EGT2010, we use the AAV and density data from 2010.
    # The survey perimiters cover excatly the 8 départements of the IDF region.
    lf = clean(lf, 2010, perimeter_deps=["75", "77", "78", "91", "92", "93", "94", "95"])
    return lf

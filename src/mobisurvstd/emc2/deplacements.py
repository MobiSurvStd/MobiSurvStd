import polars as pl

from mobisurvstd.common.trips import clean

from .common import MODE_MAP

SCHEMA = {
    "DP1": pl.UInt8,  # Code fichier = 3 (déplacement)
    "DMET": pl.UInt8,  # Méthode d'enquête du ménage
    "IDD3": pl.UInt16,  # Année de fin d'enquête
    "IDD4": pl.String,  # Code Insee ville centre
    "ZFD": pl.UInt32,  # Zone fine de résidence
    "ECH": pl.UInt32,  # Numéro d’échantillon
    "PER": pl.UInt8,  # Numéro de personne
    "NDEP": pl.UInt8,  # Numéro de déplacement
    "GD1": pl.String,  # Insee Zone fine du lieu de résidence de la personne concernée par le déplacement
    "STD": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine  (résidence)
    "D2A": pl.UInt8,  # Motif Origine du déplacement
    "D2B": pl.UInt8,  # Motif Origine de la personne accompagnée
    "D3": pl.UInt32,  # Zone fine Origine du déplacement
    "GDO1": pl.String,  # Insee Zone fine Origine du déplacement
    "STDO": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine (origine du déplacement)
    "D4": pl.UInt16,  # Heure de départ du déplacement
    "D5A": pl.UInt8,  # Motif Destination du déplacement
    "D5B": pl.UInt8,  # Motif Destination de la personne accompagnée
    "D6": pl.UInt8,  # Nombre d’arrêts sur la tournée
    "D7": pl.UInt32,  # Zone fine Destination du déplacement
    "GDD1": pl.String,  # Insee Zone fine Destination du déplacement
    "STDD": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine (destination du déplacement)
    "D8": pl.UInt16,  # Heure d'arrivée du déplacement
    "D9": pl.UInt16,  # Durée du déplacement
    "D10": pl.UInt8,  # Nombre de trajets (en modes mécanisés)
    "D11": pl.Float64,  # Longueur à vol d'oiseau
    "D12": pl.Float64,  # Distance parcourue
    "MODP": pl.UInt8,  # Mode principal
    "TYPD": pl.UInt8,  # Type de déplacement
}

PURPOSE_MAP = {
    1: "home:main",  # Domicile (partir de, se rendre à).
    2: "home:secondary",  # Résidence secondaire, logement occasionnel, hôtel, autre domicile (partir de, se rendre à).
    11: "work:declared",  # Travailler sur le lieu d’emploi déclaré.
    12: "work:telework",  # Travailler sur un autre lieu – télétravail.
    13: "work:secondary",  # Travailler sur un autre lieu hors télétravail
    14: "work:other",  # Travailler sur un autre lieu sans distinction
    # NOTE. We discard the information on the exact study location type (middle-school, high-school,
    # etc.) because the information can read from the person characteristics (`student_group`).
    21: "education:childcare",  # Être gardé (Nourrice, crèche...).
    22: "education:declared",  # Étudier sur le lieu d'études déclaré (école maternelle et primaire).
    23: "education:declared",  # Étudier sur le lieu d'études déclaré (collège).
    24: "education:declared",  # Étudier sur le lieu d'études déclaré (lycée).
    25: "education:declared",  # Étudier sur le lieu d'études déclaré (universités et grandes écoles).
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
    # TODO: Fix 96, 97, and 98 if I find these values in a dataset.
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


def scan_trips(source: str | bytes):
    lf = pl.scan_csv(source, separator=";", schema_overrides=SCHEMA, null_values=["aa"])
    return lf


def standardize_trips(
    source: str | bytes,
    persons: pl.LazyFrame,
    special_locations_coords: pl.DataFrame | None,
    detailed_zones_coords: pl.DataFrame | None,
):
    lf = scan_trips(source)
    # Add household_id, person_id, and trip date.
    lf = lf.with_columns(
        original_person_id=pl.struct(PMET="DMET", ECH="ECH", STP="STD", PER="PER")
    ).join(
        persons.select("original_person_id", "person_id", "household_id", "trip_date"),
        on="original_person_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename(
        {
            "D3": "origin_detailed_zone",
            "GDO1": "origin_insee",
            "STDO": "origin_draw_zone",
            "D6": "nb_tour_stops",
            "D7": "destination_detailed_zone",
            "GDD1": "destination_insee",
            "STDD": "destination_draw_zone",
        }
    )
    lf = lf.with_columns(
        original_trip_id=pl.struct("DMET", "ECH", "STD", "PER", "NDEP"),
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
        main_mode=pl.col("MODP").replace_strict(MODE_MAP),
        trip_perimeter=pl.col("TYPD").replace_strict(TRIP_PERIMETER_MAP),
    )
    year = int(lf.select(pl.col("trip_date").dt.year().mean().round()).collect().item())
    lf = clean(
        lf,
        year=year,
        special_locations=special_locations_coords,
        detailed_zones=detailed_zones_coords,
    )
    return lf

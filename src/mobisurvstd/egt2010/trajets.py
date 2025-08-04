import geopandas as gpd
import polars as pl

from mobisurvstd.common.legs import clean

SCHEMA = {
    "NQUEST": pl.UInt32,  # Identifiant du ménage
    "NP": pl.UInt8,  # Numéro de personne dans le ménage
    "ND": pl.UInt8,  # Numéro de déplacement de la personne
    "NT": pl.UInt8,  # Numéro de trajet dans le déplacement
    "POIDSP": pl.Float64,  # Poids de la personne réalisant le trajet
    "JDEP": pl.UInt8,  # Jour de la semaine où le trajet est effectué
    "MOYEN": pl.UInt8,  # Mode utilisé pour le trajet
    "TT": pl.UInt8,  # Titre de transport utilisé
    "LIGNE": pl.String,  # Ligne utilisée (métro, RER)
    "ENTC": pl.String,  # Carreau d'entrée dans le mode
    "SORTC": pl.String,  # Carreau de sortie du mode
    "TPORTEE": pl.Float64,  # Portée du trajet en kilomètres (pour les trajets des déplacements internes IdF)
    "TYPV": pl.UInt8,  # Numéro du véhicule du ménage utilisé
    "TSTAT": pl.UInt8,  # Type de stationnement
    "NBPV": pl.UInt8,  # Nombre de personnes dans le véhicule (passagers + conducteurs)
    "LSC": pl.UInt8,  # Stationnement connu à la destination
    "UTP": pl.UInt8,  # Emprunté le périphérique
    "UTA86": pl.UInt8,  # Emprunté l'A86
    "UTFRL": pl.UInt8,  # Emprunté la francilienne
    "SRES": pl.UInt8,  # Stationnement réservé à destination liée au travail
    "REMBF": pl.UInt8,  # Remboursement des frais du véhicule par employeur
    "PCT": pl.UInt8,  # Coût du trajet à charge
    "entsect": pl.String,  # Secteur d'entrée dans le mode
    "sortsect": pl.String,  # Secteur de sortie du mode
}


MODE_MAP = {
    1: "walking",  # Marche à pied
    # Transport collectif
    10: "public_transit:urban:rail",  # Train de banlieue SNCF(Transilien)
    11: "public_transit:urban:rail",  # RER (Lignes A, B, C, D, E ou Eole)
    12: "public_transit:urban:metro",  # Orly-Val
    13: "public_transit:urban:metro",  # Métro
    14: "public_transit:urban:tram",  # Tramway (y compris le T4)
    15: "public_transit:urban:bus",  # TVM
    16: "public_transit:urban:bus",  # Autobus Paris RATP  (Numéro de ligne inférieur à 100)
    17: "public_transit:urban:bus",  # Autobus de banlieue RATP  (Numéro de ligne supérieur à 100)
    18: "public_transit:urban:bus",  # Autre autobus de banlieue OPTILE (ex APTR,ADATRIF)
    19: "public_transit:urban:bus",  # Noctilien (bus de nuit ex Noctambus)
    20: "water_transport",  # Bateau bus – Voguéo
    30: "public_transit:urban:demand_responsive",  # Transport à la demande
    31: "employer_transport",  # Transports employeurs
    32: "public_transit:school",  # Ramassage scolaire
    33: "reduced_mobility_transport",  # Société de service spécialisée dans le transport des handicapés
    34: "other",  # Autres transports privés collectifs (navettes, …)
    35: "taxi",  # Taxi
    40: "airplane",  # Avion
    41: "public_transit:interurban:TGV",  # TGV
    42: "public_transit:interurban:other_train",  # Grande ligne SNCF autre que TGV
    43: "public_transit:urban:TER",  # TER
    # Conducteur de véhicule ou 2/3 roues motorisé
    50: "car:driver",  # Conducteur voiture particulière
    51: "car:driver",  # Conducteur dans un système de covoiturage organisé
    52: "car:driver",  # Conducteur véhicule utilitaire 800 à 1 000 kg
    53: "car:driver",  # Conducteur véhicule utilitaire de 1 000 kg ou plus
    54: "motorcycle:driver:moped",  # Conducteur véhicule à 2 (ou 3) roues à moteur non immatriculé
    55: "motorcycle:driver",  # Conducteur véhicule à 2 (ou 3) roues à moteur immatriculé
    # Vélo
    60: "bicycle:driver:shared",  # Véli’b
    61: "bicycle:driver:shared",  # Autre vélo en libre service
    62: "bicycle:driver:traditional",  # Vélo personnel
    63: "bicycle:driver:electric",  # Vélo personnel à assistance électrique
    # Passager de véhicule ou 2/3 roues
    70: "car:passenger",  # Passager d’une voiture particulière
    71: "car:passenger",  # Passager dans un système de covoiturage organisé
    72: "car:passenger",  # Passager d’un véhicule utilitaire 800 à 1 000 kg
    73: "car:passenger",  # Passager  véhicule utilitaire de 1 000 kg ou plus
    74: "motorcycle:passenger:moped",  # Passager d’un véhicule à 2 (ou 3) roues à moteur non immatriculé
    75: "motorcycle:passenger",  # Passager d’un véhicule à 2 (ou 3) roues à moteur immatriculé
    # Autre moyen de transport
    80: "wheelchair",  # Fauteuil roulant avec ou sans moteur, voiturette  (handicapés)
    81: "personal_transporter:unspecified",  # Rollers, skate, trottinette
    82: "other",  # Autre moyen de transport
}

VEHICLE_TYPE_MAP = {
    1: "household",
    2: "household",
    3: "household",
    4: "household",
    5: "other_household",  # Autre véhicule du ménage
    6: "rental",  # Véhicule de location
    7: "shared",  # Véhicule en Autolib ou Autopartage
    8: "company",  # Véhicule de l’entreprise
    9: "other",  # Autre véhicule
}

# Index of household car based on "TYPV" column.
VEHICLE_INDEX_MAP = {
    "1": 1,  # Modèle voiture 1
    "2": 2,  # Modèle voiture 2
    "3": 3,  # Modèle voiture 3
    "4": 4,  # Modèle voiture 4
}

PARKING_LOCATION_MAP = {
    1: "stop_only",  # Dépose minute
    # Sur la voie publique :
    2: "street",  # Stationnement Payant à durée limitée
    3: "street",  # Stationnement Payant à tarif préférentiel résidents
    4: "street",  # Stationnement Gratuit durée illimitée
    5: "street",  # Stationnement Gratuit durée limitée (zone bleue)
    6: "street",  # Stationnement Non autorisé
    # Sur un emplacement privé :
    7: "garage",  # Propriétaire
    8: "garage",  # Locataire
    9: "garage",  # A titre gratuit
    # Dans un parc de stationnement ou garage commercial ouvert au public :
    10: "parking_lot",  # Parc relais (parc de rabattement à une gare) à titre gratuit
    11: "parking_lot",  # Parc relais (parc de rabattement à une gare) à titre payant
    12: "other",  # Autre gratuit
    13: "garage",  # Autre propriétaire
    14: "other",  # Autre abonné, locataire avec ou sans réservation
    15: "other",  # Autre payant horaire
    16: "other",  # Autre stationnement
}

PARKING_TYPE_MAP = {
    1: None,  # Dépose minute
    # Sur la voie publique :
    2: "paid",  # Stationnement Payant à durée limitée
    3: "paid",  # Stationnement Payant à tarif préférentiel résidents
    4: "free",  # Stationnement Gratuit durée illimitée
    5: "free",  # Stationnement Gratuit durée limitée (zone bleue)
    6: "forbidden",  # Stationnement Non autorisé
    # Sur un emplacement privé :
    7: "free",  # Propriétaire
    8: "free",  # Locataire
    9: "free",  # A titre gratuit
    # Dans un parc de stationnement ou garage commercial ouvert au public :
    10: "free",  # Parc relais (parc de rabattement à une gare) à titre gratuit
    11: "paid",  # Parc relais (parc de rabattement à une gare) à titre payant
    12: "free",  # Autre gratuit
    13: "free",  # Autre propriétaire
    14: None,  # Autre abonné, locataire avec ou sans réservation
    15: "paid",  # Autre payant horaire
    16: None,  # Autre stationnement
}


def scan_legs(filename: str):
    lf = pl.scan_csv(filename, separator=";", schema_overrides=SCHEMA)
    return lf


def standardize_legs(
    filename: str,
    trips: pl.LazyFrame,
    cars: pl.LazyFrame,
    motorcycles: pl.LazyFrame,
    detailed_zones: gpd.GeoDataFrame | None,
):
    lf = scan_legs(filename)
    # Add household_id, person_id, and trip_id.
    lf = lf.with_columns(original_trip_id=pl.struct("NQUEST", "NP", "ND")).join(
        trips.select("original_trip_id", "household_id", "person_id", "trip_id"),
        on="original_trip_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename(
        {
            "ENTC": "start_detailed_zone",
            "SORTC": "end_detailed_zone",
            "entsect": "start_draw_zone",
            "sortsect": "end_draw_zone",
            "LIGNE": "public_transit_line",
            "TPORTEE": "leg_euclidean_distance_km",
            "NBPV": "nb_persons_in_vehicle",
        }
    )
    lf = lf.with_columns(
        leg_index="NT",
        original_leg_id=pl.struct("NQUEST", "NP", "ND", "NT"),
        mode=pl.col("MOYEN").replace_strict(MODE_MAP),
        vehicle_type=pl.col("TYPV").replace_strict(VEHICLE_TYPE_MAP),
        vehicle_index=pl.col("TYPV").replace_strict(VEHICLE_INDEX_MAP, default=None),
        parking_location=pl.col("TSTAT").replace_strict(PARKING_LOCATION_MAP),
        parking_type=pl.col("TSTAT").replace_strict(PARKING_TYPE_MAP),
    )
    lf = lf.with_columns(
        car_type=pl.when(pl.col("mode").str.starts_with("car:")).then("vehicle_type"),
        car_index=pl.when(pl.col("mode").str.starts_with("car:")).then("vehicle_index"),
        motorcycle_type=pl.when(pl.col("mode").str.starts_with("motorcycle:")).then("vehicle_type"),
        motorcycle_index=pl.when(pl.col("mode").str.starts_with("motorcycle:")).then(
            "vehicle_index"
        ),
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
    lf = clean(lf, detailed_zones)
    return lf

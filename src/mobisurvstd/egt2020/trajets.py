import polars as pl

from mobisurvstd.common.legs import clean

SCHEMA = {
    "IDCEREMA": pl.String,  # Identifiant du ménage
    "TYPE_QUEST": pl.String,  # Type de questionnaire
    "NP": pl.UInt8,  # Numéro de personne dans le ménage
    "ND": pl.UInt8,  # Numéro de déplacement de la personne
    "NT": pl.UInt8,  # Numéro de trajet dans le déplacement
    "JOURSEM": pl.String,  # Jour de la semaine de la date schéma des déplacements
    "MOYEN": pl.String,  # Mode utilisé pour le trajet
    "LIGNE": pl.String,  # Ligne utilisée (Nom commercial)
    "ENTLNG": pl.Float64,  # Longitude de début du trajet
    "ENTLAT": pl.Float64,  # Latitude de début du trajet
    "ENTGARE": pl.String,  # Station/gare de début du trajet
    "SORLNG": pl.Float64,  # Longitude de fin du trajet
    "SORLAT": pl.Float64,  # Latitude de fin du trajet
    "SORGARE": pl.String,  # Station/gare de fin du trajet
    "TPORTEE": pl.Float64,  # Distance à vol d'oiseau du trajet
    "TT": pl.String,  # Titre de transport utilisé
    "UTBP": pl.UInt8,  # Utilisation du boulevard périphérique
    "UTA86": pl.UInt8,  # Utilisation de l'A86
    "UTFRL": pl.UInt8,  # Utilisation de la francilienne
    "NBPV": pl.UInt8,  # Nombre de personnes dans le véhicule (passagers + conducteurs)
    "LISTE_PV": pl.String,  # Liste des personnes du ménage dans la voiture
    "NBPV_M": pl.UInt8,  # Nombre de personnes dans le véhicule (passagers + conducteurs) du ménage
    "NBPV_A": pl.UInt8,  # Nombre de personnes dans le véhicule (passagers + conducteurs) hors ménage
    "UVP": pl.String,  # Voiture utilisée
    "UVP_txt": pl.String,  # Voiture utilisée
    "VP_COVOIT": pl.UInt8,  # Mise en relation du conducteur et/ou des passagers avec une application dans le cas d'un covoiturage
    "VP_COVOIT_APP": pl.UInt8,  # Type d'application de voiture en autopartage ou libre-service utilisée au cours du dernier mois
    "VP_COVOIT_APP_txt": pl.String,  # Type d'application de covoiturage utilisée
    "TSTAT_VP": pl.String,  # Stationnement du véhicule au terme du trajet
    "TSTAT_VP_txt": pl.String,  # Stationnement du véhicule au terme du trajet
    "PSTAT_CVP": pl.Float64,  # Prix du stationnement si payant
    "U2RM": pl.UInt8,  # Deux-roues motorisé utilisé
    "U2RM_txt": pl.String,  # Deux-roues motorisé utilisé
    "TSTAT_2RM": pl.String,  # Stationnement du deux-roues motorisé au terme du trajet
    "TSTAT_2RM_txt": pl.String,  # Stationnement du deux-roues motorisé au terme du trajet
    "PSTAT_2RM": pl.Float64,  # Prix du stationnement deux-roues motorisé si payant
    "PTAXI": pl.Float64,  # Prix du taxi
    "UVELO": pl.UInt8,  # Vélo utilisé
    "UTROT": pl.UInt8,  # Trottinette utilisée
    "UTROT_txt": pl.String,  # Trottinette utilisée
    # "UVP_LS_APP": pl.UInt8,  # Type de voiture en autopartage ou libre-service utilisée
    # "UVP_LS_APP_txt": pl.String,  # Type de voitures en autopartage ou libre-service utilisée
    "UVP_LS_txt": pl.String,  # Type de voitures en autopartage ou libre-service utilisée
    "UTROT_LS": pl.UInt8,  # Type de trottinette en libre-service utilisée
    "UTROT_LS_txt": pl.String,  # Type d'application de trottinette électrique utilisée
    "UVELO_LS": pl.UInt8,  # Type de vélo en libre-service utilisé
    "UVELO_LS_txt": pl.String,  # Type d'application de vélo en libre-service utilisée
    "U2RM_LS": pl.UInt8,  # Type de deux-roues motorisé en libre-service utilisée
    "U2RM_LS_txt": pl.String,  # Type de deux-roues motorisé en libre-service utilisée
    "VPASS_COVOIT": pl.UInt8,  # Si le trajet s’est fait en covoiturage en tant que passager et en dehors du ménage, avez-vous été mis en relation avec le conducteur à l’aide d’une application ?
}


MODE_MAP = {
    "B11": "public_transit:urban:rail",  # Transports collectifs : Train ou RER
    "B12": "public_transit:urban:metro",  # Transports collectifs : Métro
    "B13": "public_transit:urban:tram",  # Transports collectifs : Tramway
    "B14": "public_transit:urban:bus",  # Transports collectifs : Bus
    "B15": "public_transit:urban",  # Transports collectifs : Autres
    "B511": "taxi",  # Taxi, Uber ou autres VTC + Taxi (artisan taxi, G7, taxis-bleus…)
    "B512": "VTC",  # Taxi, Uber ou autres VTC + Über
    "B513": "VTC",  # Taxi, Uber ou autres VTC + Autres VTC
    "B51": "taxi_or_VTC",  # Taxi, Uber ou autres VTC + non réponse
    "B521": "airplane",  # Avion
    "B522": "public_transit:interurban:other_train",  # TER ou TGV
    "B529": "public_transit:interurban:coach",  # Cars interurbains dits "cars Macron"
    "B524": "public_transit:urban",  # Transports collectifs hors Ile-de-France (bus, car, tramway, métro, TER…)
    "B525": "public_transit:school",  # Autres modes + Ramassage scolaire
    "B526": "employer_transport",  # Autres modes + Transport employeur, navette d'entreprise
    "B527": "public_transit:urban:demand_responsive",  # Autres modes + Transport à la demande (TAD)
    "B528": "reduced_mobility_transport",  # Autres modes + Transport spécialisé pour les personnes à mobilité réduite (dont PAM)
    "B21": "car:driver",  # Voiture + Conducteur
    "B31": "motorcycle:driver",  # Moto, scooter + Conducteur
    "B22": "car:passenger",  # Voiture + Passager
    "B32": "motorcycle:passenger",  # Moto, scooter + Passager
    "B40": "bicycle:driver",  # Vélo
    "B52": "other",  # Autres modes + non réponse
    "B523": "other",  # Autres modes + Autre
    "B622": "wheelchair",  # Fauteuil roulant + Fauteuil roulant motorisé ou scooter PMR
    "B621": "wheelchair",  # Fauteuil roulant + Fauteuil roulant manuel
    "B62": "wheelchair",  # Fauteuil roulant + non réponse
    "B615": "personal_transporter:motorized",  # Marche + Trottinette électrique
    "B614": "personal_transporter:non_motorized",  # Marche + Trottinette
    "B616": "personal_transporter:non_motorized",  # Marche + Autres
    "B611": "walking",  # Marche + A pied
    # There is no B61.
    "B61": "walking",  # Marche + non réponse
    # B612 and B613 are used 15 times but are not defined in the documentation. We assume it is
    # "walking" because it starts by "B61".
    "B612": "walking",
    "B613": "walking",
}

UVP_MAP = {
    "1": "household",  # Modèle voiture 1
    "2": "household",  # Modèle voiture 2
    "3": "household",  # Modèle voiture 3
    "4": "household",  # Modèle voiture 4
    "50": "other_household",  # Une autre voiture du ménage + non réponse
    "51": "other_household",  # Une autre voiture du ménage + Une voiture
    "52": "other_household",  # Une autre voiture du ménage + Un utilitaire, une camionnette ou un camion
    "60": "shared",  # Une voiture en autopartage ou libre-service + non réponse
    "61": "shared",  # Une voiture en autopartage ou libre-service + Une voiture
    "62": "shared",  # Une voiture en autopartage ou libre-service + Un utilitaire, une camionnette ou un camion
    "70": "rental",  # Une voiture de location+ non réponse
    "71": "rental",  # Une voiture de location+ Une voiture
    "72": "rental",  # Une voiture de location+ Un utilitaire, une camionnette ou un camion
    "80": "company",  # Une voiture mise à disposition par mon employeur+ non réponse
    "81": "company",  # Une voiture mise à disposition par mon employeur+ Une voiture
    "82": "company",  # Une voiture mise à disposition par mon employeur+ Un utilitaire, une camionnette ou un camion
    "100": "other",  # Une voiture qui m’a été prêtée + non réponse
    "101": "other",  # Une voiture qui m’a été prêtée + Une voiture
    "102": "other",  # Une voiture qui m’a été prêtée + Un utilitaire, une camionnette ou un camion
    "90": "other",  # Autre - Veuillez préciser. (Champ textuel saisissable) + non réponse
    "91": "other",  # Autre - Veuillez préciser. (Champ textuel saisissable) + Une voiture
    "92": "other",  # Autre - Veuillez préciser. (Champ textuel saisissable) + Un utilitaire, une camionnette ou un camion
}

# Index of household car based on "UVP" column.
VEHICLE_INDEX_MAP = {
    "1": 1,  # Modèle voiture 1
    "2": 1,  # Modèle voiture 2
    "3": 1,  # Modèle voiture 3
    "4": 1,  # Modèle voiture 4
}

U2RM_MAP = {
    "1": "household",  # Modèle 2RM 1
    "2": "household",  # Modèle 2RM 2
    "3": "household",  # Modèle 2RM 3
    "4": "household",  # Modèle 2RM 4
    "5": "other_household",  # Une autre moto / un autre scooter du ménage
    "6": "shared",  # Une moto / scooter en libre-service
    "7": "rental",  # Une moto / scooter de location
    "9": "other",  # Autre - Veuillez préciser. (Champ textuel saisissable)
    "10": "company",  # Un scooter mis à disposition par mon employeur
}

PARKING_LOCATION_MAP = {
    # Au domicile
    "1": "garage",  # Dans un garage, dans un box ou un autre emplacement réservé
    "2": "street",  # Sur la voie publique
    "3": "parking_lot",  # Dans un parking public
    "4": "parking_lot",  # Dans le parking d'un centre commercial ou dans le parking de mon entreprise
    "9": "other",  # Autre - Veuillez préciser. (Champ textuel saisissable)
    # Ailleurs
    "11": "garage",  # Chez quelqu’un (garage, box, un autre emplacement réservé )
    "20": "street",  # Sur la voie publique + non réponse
    "21": "street",  # Sur la voie publique + gratuit + non réponse
    "211": "street",  # Sur la voie publique + gratuit + autorisé
    "212": "street",  # Sur la voie publique + gratuit + non autorisé
    "22": "street",  # Sur la voie publique + payant + non réponse
    "221": "street",  # Sur la voie publique + payant + résidentiel
    "222": "street",  # Sur la voie publique + payant + autre tarif
    "30": "parking_lot",  # Dans un parking public + non réponse
    "31": "parking_lot",  # Dans un parking public + payant
    "32": "parking_lot",  # Dans un parking public + gratuit
    "40": "parking_lot",  # Dans un parking de centre commercial ou réservé au personnel d’une entreprise + non réponse
    "41": "parking_lot",  # Dans un parking de centre commercial ou réservé au personnel d’une entreprise + payant
    "42": "parking_lot",  # Dans un parking de centre commercial ou réservé au personnel d’une entreprise + gratuit
    "90": "other",  # Autre - Veuillez préciser. (Champ textuel saisissable)
}

PARKING_TYPE_MAP = {
    # Au domicile
    "1": "free",  # Dans un garage, dans un box ou un autre emplacement réservé
    "2": None,  # Sur la voie publique
    "3": None,  # Dans un parking public
    "4": None,  # Dans le parking d'un centre commercial ou dans le parking de mon entreprise
    "9": None,  # Autre - Veuillez préciser. (Champ textuel saisissable)
    "-1": None,  # pas de réponse
    # Ailleurs
    "11": "free",  # Chez quelqu’un (garage, box, un autre emplacement réservé )
    "20": None,  # Sur la voie publique + non réponse
    "21": "free",  # Sur la voie publique + gratuit + non réponse
    "211": "free",  # Sur la voie publique + gratuit + autorisé
    "212": "forbidden",  # Sur la voie publique + gratuit + non autorisé
    "22": "paid",  # Sur la voie publique + payant + non réponse
    "221": "paid",  # Sur la voie publique + payant + résidentiel
    "222": "paid",  # Sur la voie publique + payant + autre tarif
    "30": None,  # Dans un parking public + non réponse
    "31": "paid",  # Dans un parking public + payant
    "32": "free",  # Dans un parking public + gratuit
    "40": None,  # Dans un parking de centre commercial ou réservé au personnel d’une entreprise + non réponse
    "41": "paid",  # Dans un parking de centre commercial ou réservé au personnel d’une entreprise + payant
    "42": "free",  # Dans un parking de centre commercial ou réservé au personnel d’une entreprise + gratuit
    "90": None,  # Autre - Veuillez préciser. (Champ textuel saisissable)
}


def scan_legs(filename: str):
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


def standardize_legs(
    filename: str,
    trips: pl.LazyFrame,
    cars: pl.LazyFrame,
    motorcycles: pl.LazyFrame,
    persons: pl.LazyFrame,
):
    lf = scan_legs(filename)
    # Add household_id, person_id, and trip_id.
    lf = lf.with_columns(original_trip_id=pl.struct("IDCEREMA", "NP", "ND")).join(
        trips.select("original_trip_id", "household_id", "person_id", "trip_id"),
        on="original_trip_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename(
        {
            "LIGNE": "public_transit_line",
            "ENTLNG": "start_lng",
            "ENTLAT": "start_lat",
            "SORLNG": "end_lng",
            "SORLAT": "end_lat",
            "TPORTEE": "leg_euclidean_distance_km",
            "NBPV_M": "nb_household_members_in_vehicle",
            "NBPV_A": "nb_non_household_members_in_vehicle",
        }
    )
    lf = lf.with_columns(
        original_leg_id=pl.struct("IDCEREMA", "NP", "ND", "NT"),
        # The extract call is required because some modes are reported as "B616,skate", for example.
        mode=pl.col("MOYEN").str.extract(r"(\w+),?").replace_strict(MODE_MAP),
        car_type=pl.col("UVP").str.extract(r"(\w+),?").replace_strict(UVP_MAP),
        car_index=pl.col("UVP")
        .str.extract(r"(\w+),?")
        .replace_strict(VEHICLE_INDEX_MAP, default=None),
        motorcycle_type=pl.col("U2RM").replace_strict(U2RM_MAP),
        motorcycle_index=pl.col("U2RM").replace_strict(
            VEHICLE_INDEX_MAP, return_dtype=pl.UInt8, default=None
        ),
        # The value of NBPV_A can be null when NBPV = NBPV_M. We set it to 0 in this case.
        nb_non_household_members_in_vehicle=pl.when(
            pl.col("nb_household_members_in_vehicle").is_not_null()
        )
        .then(pl.col("nb_non_household_members_in_vehicle").fill_null(0))
        .otherwise(None),
        in_vehicle_person_index=pl.col("LISTE_PV")
        .str.replace_all(".", ",", literal=True)
        .str.split(",")
        .cast(pl.List(pl.UInt8))
        .list.set_difference(pl.lit([99])),
        parking_location=pl.col("TSTAT_VP")
        .str.extract(r"(\w+),?")
        .replace_strict(PARKING_LOCATION_MAP),
        parking_type=pl.col("TSTAT_VP").str.extract(r"(\w+),?").replace_strict(PARKING_TYPE_MAP),
    )
    lf = lf.with_columns(
        # In some cases, the parking location is a paid location but the person reported a
        # parking price of zero (maybe because the person parked during weekend or night when
        # the parking is free, or the person parked for a short duration). In this case, we set
        # the parking type to "free".
        parking_type=pl.when(pl.col("PSTAT_CVP").eq(0.0), pl.col("parking_type").eq("free"))
        .then(pl.lit("free"))
        .otherwise("parking_type"),
        # In some cases, there are more person listed to be in the vehicle (variable LISTE_PV) than
        # the reported number of persons in the car (NBPV, NBPV_M, NBPV_A).
        nb_household_members_in_vehicle=pl.max_horizontal(
            "nb_household_members_in_vehicle", pl.col("in_vehicle_person_index").list.len()
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
    # Add `in_vehicle_person_ids`.
    lf = (
        # Add the person_index and person_id of all persons that belongs to the same household as
        # the current person (this duplicates each row by the number of persons in the household).
        lf.join(
            persons.select("household_id", "person_index", in_vehicle_person_id="person_id"),
            on="household_id",
            how="left",
            coalesce=True,
        )
        # Group by leg_id to end up again with one row per leg.
        .group_by("original_leg_id")
        .agg(
            # Take the first value for all columns except `in_vehicle_person_id` (all values are
            # equal so taking the first one is good).
            pl.exclude("in_vehicle_person_id").first(),
            # Column "in_vehicle_person_id" takes the value of each person_id for the household.
            # We collect in the list the values of "in_vehicle_person_id", only for the rows where
            # the person_index appears in "in_vehicle_person_index".
            in_vehicle_person_ids=pl.col("in_vehicle_person_id").filter(
                pl.col("in_vehicle_person_index").list.contains(pl.col("person_index"))
            ),
        )
    )
    lf = clean(lf)
    return lf

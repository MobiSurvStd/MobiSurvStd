import polars as pl

from mobisurvstd.common.persons import clean

SCHEMA = {
    "PP1": pl.UInt8,  # Code fichier = 2 (personne)
    "IDP3": pl.UInt16,  # Année de fin d'enquête
    "IDP4": pl.String,  # Code Insee ville centre
    "ZFP": pl.UInt32,  # Zone fine de résidence
    "ECH": pl.UInt32,  # Numéro d’échantillon
    "PER": pl.UInt8,  # Numéro de personne
    "GP1": pl.String,  # Insee Zone fine du lieu de résidence de la personne
    "STP": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine (résidence)
    "ANNEE": pl.UInt16,  # Année du jour d’enquête
    "MOIS": pl.UInt8,  # Mois du jour d’enquête
    "DATE": pl.UInt8,  # Jour d’enquête
    "JOUR": pl.UInt8,  # Jour des déplacements
    "PENQ": pl.UInt8,  # Personne enquêtée ?
    "P2": pl.UInt8,  # Sexe de la personne
    "P3": pl.UInt8,  # Lien avec la personne de référence
    "P4": pl.UInt8,  # Âge de la personne
    "P5": pl.UInt8,  # Possession d'un téléphone portable
    "P6": pl.UInt8,  # Possession d'une adresse de messagerie électronique
    "P7": pl.UInt8,  # Possession du permis de conduire voiture
    "P8": pl.String,  # Niveau d’études
    "P9": pl.UInt8,  # Occupation principale de la personne
    "P10": pl.UInt8,  # Occupation secondaire
    "PCSC": pl.String,  # PCS courte
    "PCSD": pl.UInt8,  # PCS détaillée
    "P12": pl.UInt8,  # Possession d'un abonnement TC valide hier
    "P14": pl.UInt8,  # Travail, études à domicile
    "P15": pl.UInt32,  # Zone fine du lieu de travail ou d’études
    "DP15": pl.Float64,  # Distance domicile - travail / études à vol d'oiseau
    "GP5": pl.String,  # Insee Zone fine du lieu de travail / études
    "STW": pl.UInt32,  # Secteur de tirage dans l’enquête d’origine (lieu de travail / études)
    "P16": pl.UInt8,  # Disposition d'une VP pour se rendre sur le lieu de travail ou d'études
    "P17": pl.UInt8,  # Problèmes de stationnement sur le lieu de travail ou d'études
    "P18": pl.UInt8,  # Difficultés de stationnement sur le lieu de travail ou d'études
    "P18A": pl.UInt8,  # Stationnement du vélo sur le lieu de travail / études
    "P19": pl.UInt8,  # Fréquence de déplacement à pied
    "P20": pl.UInt8,  # Fréquence d’utilisation d'un vélo
    "P21": pl.UInt8,  # Fréquence d’utilisation d'un deux-roues motorisé
    "P22": pl.UInt8,  # Fréquence d’utilisation de la VP en tant que conducteur
    "P23": pl.UInt8,  # Fréquence d’utilisation de la VP en tant que passager
    "P24": pl.UInt8,  # Fréquence d’utilisation du réseau urbain
    "P25": pl.UInt8,  # Situation la veille du jour d’enquête
    "P26": pl.UInt8,  # Travail la veille
    "COE1": pl.Float64,  # Coefficient de redressement -Toutes Personnes
    "COEP": pl.Float64,  # Coefficient de redressement - Personnes Enquêtées
}

REFERENCE_PERSON_LINK_MAP = {
    1: "reference_person",  # Personne de référence
    2: "spouse",  # Conjoint
    3: "child",  # Enfant
    4: "roommate_or_tenant",  # Colocataire, locataire ou sous-locataire
    5: "other:relative",  # Autre (avec lien de parenté)
    6: "other:non_relative",  # Autre (sans lien de parenté)
    7: "other:non_relative",  # Autre Non précisé
}

DRIVING_LICENSE_MAP = {
    1: "yes",
    2: "no",
    3: "in_progress",  # Conduite accompagnée et leçons de conduite
}

EDUCATION_LEVEL_MAP = {
    "00": None,  # En cours de scolarité
    "01": "primary",  # Primaire
    "02": "secondary:no_bac",  # Secondaire (de la 6e à la 3e, CAP)
    "03": "secondary:no_bac",  # Secondaire (de la seconde à la terminale, BEP), non titulaire du bac
    "04": "secondary:bac",  # Secondaire, titulaire du bac
    "05": "higher:at_most_bac+2",  # Supérieur jusqu’à bac + 2
    "06": "higher:at_least_bac+3",  # Supérieur, bac + 3 et plus
    # Apprentissage is usually something like CAP so we put secondary:no_bac
    "07": "secondary:no_bac",  # Apprentissage (école primaire ou secondaire uniquement)
    # Apprentissage (études supérieurs) should rarely be higher than BAC+2
    "08": "higher:at_most_bac+2",  # Apprentissage (études supérieures)
    "09": "no_studies_or_no_diploma",  # Pas d’études
    # For the two modalities below we have to make an assumption.
    "93": "secondary:no_bac",  # Secondaire (sans distinction titulaire du bac ou non)
    "97": "secondary:no_bac",  #  Apprentissage (sans distinction)
    "90": None,  # autre (egt)
}

DETAILED_EDUCATION_LEVEL_MAP = {
    "00": None,  # En cours de scolarité
    "01": "primary:unspecified",  # Primaire
    # CAP should actually be in the other category but given that EMC2 are the only one to do that
    # there is no appropriate category.
    "02": "secondary:no_bac:college",  # Secondaire (de la 6e à la 3e, CAP)
    "03": "secondary:no_bac:CAP/BEP",  # Secondaire (de la seconde à la terminale, BEP), non titulaire du bac
    "04": "secondary:bac:unspecified",  # Secondaire, titulaire du bac
    "05": "higher:at_most_bac+2:unspecified",  # Supérieur jusqu’à bac + 2
    "06": "higher:at_least_bac+3:unspecified",  # Supérieur, bac + 3 et plus
    "07": "secondary:no_bac:CAP/BEP",  # Apprentissage (école primaire ou secondaire uniquement)
    "08": "higher:at_most_bac+2:unspecified",  # Apprentissage (études supérieures)
    "09": "no_studies",  # Pas d’études
    "93": None,  # Secondaire (sans distinction titulaire du bac ou non)
    "97": None,  #  Apprentissage (sans distinction)
    "90": None,  # autre (egt)
}

DETAILED_PROFESSIONAL_OCCUPATION_MAP = {
    1: "worker:full_time",  # Travail à plein temps.
    2: "worker:part_time",  # Travail à temps partiel.
    3: "student:apprenticeship",  # Formation en alternance (apprentissage, professionnalisation), stage.
    4: "student:higher",  # Étudiant.
    5: "student:primary_or_secondary",  # Scolaire jusqu'au bac.
    6: "other:unemployed",  # Chômeur, recherche un emploi.
    7: "other:retired",  # Retraité.
    8: "other:homemaker",  # Reste au foyer.
    9: "other:unspecified",  # Autre.
}

SECONDARY_PROFESSIONAL_OCCUPATION_MAP = {
    0: None,  # Non concerné
    1: "work",  # Travail
    2: "education",  # Etudes
}

PCS_GROUP_CODE_MAP = {
    "00": None,  # Non réponse
    "01": 1,  # Agriculteurs exploitants
    "02": 2,  # Artisans, commerçants et chefs d'entreprise
    "03": 3,  # Cadres et professions intellectuelles supérieures
    "04": 4,  # Professions Intermédiaires
    "05": 5,  # Employés
    "06": 6,  # Ouvriers
    "07": None,  # Élèves, étudiants
    "08": 8,  # Chômeurs n'ayant jamais travaillé
    "09": 8,  # Autres inactifs n'ayant jamais travaillé
}

# NOTE. Some details are lost here because I do not really understand what
# "Secondaires, titulaires du Bac" means. I think it's fine because we still keep
# the main information.
STUDENT_GROUP_MAP = {
    "83": "primaire",  # Écoliers (primaire)
    "84": "collège",  # Secondaires jusqu'en 3ème
    "85": "lycée",  # Secondaires, de la seconde à la terminale
    "86": "lycée",  # Secondaires, titulaires du Bac
    "90": "lycée",  # Secondaires, de la seconde à la terminale (Sans précision des titulaires du Bac ou non) egt
    "87": "supérieur",  # Supérieurs (Bac+2)
    "80": "supérieur",  # Sans précision secondaires titulaires du Bac + supérieurs (Bac+2)
    "88": "supérieur",  # Supérieurs (Bac+3 et plus)
    "89": "lycée",  # Apprentis  # NOTE. I assume here that this is not used for "alternant"
}

PUBLIC_TRANSIT_SUBSCRIPTION_MAP = {
    1: "yes:free",  # Oui, gratuit
    2: "yes:paid:with_employer_contribution",  # Oui, payant avec prise en charge partielle par l'employeur
    3: "yes:paid:without_employer_contribution",  # Oui, payant sans prise en charge partielle par l'employeur
    4: "no",  # Non
    5: "yes:paid",  # Oui, payant (sans information sur la prise en charge)
    6: "yes:unspecified",  # Oui, mais sans précision
}

HAS_CAR_TO_COMMUTE_MAP = {
    1: "yes:full_commute",  # Oui et je l’utilise jusqu'à mon lieu de travail ou d'études
    2: "yes:partial_commute",  # Oui mais je ne l’utilise que sur une partie du déplacement
    3: "yes:not_used",  # Oui, mais je ne l’utilise pas
    4: "no",  # Non
    5: "yes:partial_or_not_used",  # Oui, mais je ne l'utilise qu'en partie ou pas du tout (2+3 sans distinction)
    6: "yes:full_or_partial",  # Oui et je l’utilise pour tout ou partie du déplacement (1+2 sans distinction)
}

WORK_STUDY_CAR_PARKING_MAP = {
    1: "no",  # Non
    2: "yes:reserved",  # Oui , car j’ai (ou pourrai avoir) une place réservée
    3: "yes:many_spots",  # Oui, offre importante à proximité
    4: "yes:compatible_schedule",  # Oui, compte tenu de mes horaires
}

WORK_STUDY_BICYCLE_PARKING_MAP = {
    1: "yes:on_site:sheltered",  # Oui, dans l'enceinte du lieu et abrité
    2: "yes:on_site:unsheltered",  # Oui, dans l'enceinte du lieu mais non abrité
    3: "yes:nearby:sheltered",  # Oui, à proximité du lieu et abrité
    4: "yes:nearby:unsheltered",  # Oui, à proximité du lieu mais non abrité
    5: "no",  # Non
    6: "yes:on_site",  # Oui, dans l'enceinte du lieu sans précision
    7: "yes:nearby",  # Oui, à proximité du lieu sans précision
    9: None,  # NR-Refus
}

TRAVELED_DAY_BEFORE_MAP = {
    1: "yes",  # Oui
    2: "no",  # Non
    3: "away",  # Absent (vieille enquête)
    4: None,  # déplacements non relevés
    5: "away",  # absent - longue durée-
    9: None,
}

WORKED_DAY_BEFORE_MAP = {
    0: None,  # Note. Used in some surveys but undefined.
    1: "yes:outside",  # Oui, hors du domicile.
    2: "yes:home:usual",  # Oui mais à domicile (travail toujours au domicile).
    3: "yes:home:telework",  # Oui mais à domicile – télétravail.
    4: "yes:home:other",  # Oui mais à domicile - autre
    5: "no:weekday",  # Non, ne travaille jamais ce jour-là.
    6: "no:reason",  # Non en raison de congés, grève ou maladie.
    7: "yes:unspecified",  # oui (sans précision)
    8: "no:unspecified",  # non (sans précision)
    9: "no:unspecified",  # Used in some surveys
}


def scan_persons(source: str | bytes):
    lf = pl.scan_csv(source, separator=";", schema_overrides=SCHEMA, null_values=["a", "aa"])
    return lf


def standardize_persons(
    source: str | bytes,
    households: pl.LazyFrame,
    special_locations_coords: pl.DataFrame | None,
    detailed_zones_coords: pl.DataFrame | None,
):
    lf = scan_persons(source)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct(ECH="ECH", STM="STP")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename({"P4": "age", "COE1": "sample_weight_all", "COEP": "sample_weight_surveyed"})
    # For Valenciennes 2011, the "MOIS" column is greater than 12 for 3 observations.
    # The MOIS and DATE columns seem to be inverted in this case.
    # There are also some dates equal to 31st April (which does not exist). My guess is that
    # they meant 31st March.
    lf = lf.with_columns(
        month=pl.when(pl.col("MOIS") > 12)
        .then("DATE")
        .when(MOIS=4, DATE=31)
        .then(3)
        .otherwise("MOIS"),
        day=pl.when(pl.col("MOIS") > 12).then("MOIS").otherwise("DATE"),
    )
    lf = lf.with_columns(
        original_person_id=pl.struct("ECH", "STP", "PER"),
        trip_date=pl.date(year="ANNEE", month="month", day="day"),
        # The `fill_null` is required here because in some cases, a null value is used instead
        # 0.
        is_surveyed=(pl.col("PENQ") == 1).fill_null(False),
        woman=pl.col("P2") == 2,
        reference_person_link=pl.col("P3").replace_strict(REFERENCE_PERSON_LINK_MAP),
        has_driving_license=pl.col("P7").replace_strict(DRIVING_LICENSE_MAP),
        education_level=pl.col("P8").replace_strict(EDUCATION_LEVEL_MAP),
        detailed_education_level=pl.col("P8").replace_strict(DETAILED_EDUCATION_LEVEL_MAP),
        detailed_professional_occupation=pl.col("P9").replace_strict(
            DETAILED_PROFESSIONAL_OCCUPATION_MAP
        ),
        secondary_professional_occupation=pl.col("P10").replace_strict(
            SECONDARY_PROFESSIONAL_OCCUPATION_MAP
        ),
        pcs_group_code=pl.col("PCSC").replace_strict(PCS_GROUP_CODE_MAP),
        pcs_category_code2003=pl.when(pl.col("PCSD").is_between(1, 69)).then("PCSD"),
        student_group=pl.col("PCSD").replace_strict(STUDENT_GROUP_MAP, default=None),
        has_public_transit_subscription=pl.col("P12") != 4,
        public_transit_subscription=pl.col("P12").replace_strict(PUBLIC_TRANSIT_SUBSCRIPTION_MAP),
        traveled_during_surveyed_day=pl.col("P25").replace_strict(TRAVELED_DAY_BEFORE_MAP),
        worked_during_surveyed_day=pl.col("P26").replace_strict(WORKED_DAY_BEFORE_MAP),
        is_student=pl.col("P8") == "00",
        insee=pl.col("GP5").replace(["aaaaa", "999999", "888888"], None),
        # Column P17 is just an improved version of column P18.
        work_study_parking=pl.col("P17").fill_null(pl.col("P18")),
    )
    lf = lf.with_columns(
        work_only_at_home=pl.when(pl.col("is_student").not_()).then(pl.col("P14") == 1),
        study_only_at_home=pl.when("is_student").then(pl.col("P14") == 1),
        work_detailed_zone=pl.when(pl.col("is_student").not_()).then("P15"),
        study_detailed_zone=pl.when("is_student").then("P15"),
        work_draw_zone=pl.when(pl.col("is_student").not_()).then("STW"),
        study_draw_zone=pl.when("is_student").then("STW"),
        work_insee=pl.when(pl.col("is_student").not_()).then("insee"),
        study_insee=pl.when("is_student").then("insee"),
        work_commute_euclidean_distance_km=pl.when(pl.col("is_student").not_()).then(
            pl.col("DP15") / 1e3
        ),
        study_commute_euclidean_distance_km=pl.when("is_student").then(pl.col("DP15") / 1e3),
        has_car_for_work_commute=pl.when(pl.col("is_student").not_()).then(
            pl.col("P16").replace_strict(HAS_CAR_TO_COMMUTE_MAP)
        ),
        has_car_for_study_commute=pl.when("is_student").then(
            pl.col("P16").replace_strict(HAS_CAR_TO_COMMUTE_MAP)
        ),
        work_car_parking=pl.when(pl.col("is_student").not_()).then(
            pl.col("work_study_parking").replace_strict(WORK_STUDY_CAR_PARKING_MAP)
        ),
        study_car_parking=pl.when("is_student").then(
            pl.col("work_study_parking").replace_strict(WORK_STUDY_CAR_PARKING_MAP)
        ),
        work_bicycle_parking=pl.when(pl.col("is_student").not_()).then(
            pl.col("P18A").replace_strict(WORK_STUDY_BICYCLE_PARKING_MAP)
        ),
        study_bicycle_parking=pl.when("is_student").then(
            pl.col("P18A").replace_strict(WORK_STUDY_BICYCLE_PARKING_MAP)
        ),
    )
    lf = lf.with_columns(
        # The `traveled_during_surveyed_day` variable must be set to null for non-surveyed
        # persons.
        traveled_during_surveyed_day=pl.when("is_surveyed").then("traveled_during_surveyed_day"),
        # The `sample_weight_surveyed` variable must be set to null for non-surveyed
        # persons.
        sample_weight_surveyed=pl.when("is_surveyed").then("sample_weight_surveyed"),
    )
    lf = clean(lf, special_locations=special_locations_coords, detailed_zones=detailed_zones_coords)
    return lf

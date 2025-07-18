import polars as pl

from mobisurvstd.common.persons import clean

SCHEMA = {
    "NQUEST": pl.UInt32,  # Identifiant du ménage
    "NP": pl.UInt8,  # Numéro de personne dans le ménage
    "POIDSP": pl.Float64,  # Poids de la personne
    "RESCOUR": pl.UInt8,  # Couronne de résidence
    "RESDEP": pl.String,  # Département de résidence
    "RESSECT": pl.String,  # Secteur de résidence
    "RESCOMM": pl.String,  # Commune de résidence
    "RESC": pl.String,  # Carreau de résidence
    "JDEP": pl.UInt8,  # Jour de la semaine où la personne a effectué les déplacements
    "TYPEP": pl.UInt8,  # Type de personne
    "SEXE": pl.UInt8,  # Sexe
    "LIENPREF": pl.UInt8,  # Lien avec la personne de référence
    "AGE": pl.UInt8,  # âge
    "TRAGE": pl.UInt8,  # Classes d'âge
    "PERMVP": pl.UInt8,  # Permis de conduire voiture
    "ABONVP": pl.UInt8,  # Abonnement autopartage
    "PERM2RM": pl.UInt8,  # Permis de conduire 2RM
    "ABONTC": pl.UInt8,  # Abonnement TC
    "ZONITC": pl.UInt8,  # Zonage de l'abonnement TC (première zone)
    "ZONFTC": pl.UInt8,  # Zonage de l'abonnement TC (dernière zone)
    "SUPPTC": pl.UInt8,  # Support de l'abonnement
    "REMBTC": pl.UInt8,  # % de l'abonnement à charge
    "ABONVLS": pl.UInt8,  # Abonnement de Vélib ou VLS
    "DIPL": pl.UInt8,  # Niveau d'étude atteint
    "OCCP": pl.UInt8,  # Occupation principale
    "TYPLT": pl.UInt8,  # Type du lieu de travail
    "CS24L": pl.UInt8,  # Catégorie socioprofessionnelle / classe fréquentée
    "CS8": pl.UInt8,  # Catégorie socioprofessionnelle en 8 postes
    "CAT": pl.UInt8,  # Catégorie de personne (Classes retenues pour le redressement)
    "ULTRAV": pl.UInt8,  # Unicité du lieu de travail ou d'étude
    "LTRAVCOUR": pl.UInt8,  # Couronne du lieu de travail / études principal
    "LTRAVDEP": pl.String,  # Département du lieu de travail / études principal
    "LTRAVSECT": pl.String,  # Secteur du lieu de travail / études principal
    "LTRAVCOMM": pl.String,  # Commune du lieu de travail / études principal
    "LTRAVC": pl.String,  # Carreau du lieu de travail / étude principal
    "PKVPTRAV": pl.UInt8,  # Disponibilité d'un  parking au lieu de travail / étude
    "PKVLTRAV": pl.UInt8,  # Disponibilité d'un  parking vélo au lieu de travail / étude
    "CHGTRAV": pl.UInt8,  # Changement de lieu de travail depuis 2000
    "ANCHGTRAV": pl.UInt16,  # Année de changement de lieu de travail depuis 2000
    "COMATRAV": pl.String,  # Commune du précédent lieu de travail
    "HANDI": pl.UInt8,  # Gêne dans les déplacements en général
    "HANDI1": pl.UInt8,  # Type de gêne 1
    "HANDI2": pl.UInt8,  # Type de gêne 2
    "HANDI3": pl.UInt8,  # Type de gêne 3
    "HANDI4": pl.UInt8,  # Type de gêne 4
    "ACHINT": pl.UInt8,  # Achats sur Internet
    "DEMINT": pl.UInt8,  # Démarches administratives sur Internet
    "CONGE": pl.UInt8,  # Congé, arrêt maladie
    "NONDEPL": pl.UInt8,  # Déplacements hier
    "PERTURB": pl.UInt8,  # Perturbations pour les déplacements
    "TPERTURB": pl.UInt8,  # Type de perturbation
    "GENE": pl.UInt8,  # Gêne temporaire ou permanente pour la journée enquêtée
    "PUVP": pl.UInt8,  # Possibilité d'utiliser un véhicule motorisés conducteur (même si pas utilisé)
    "NBDEPL": pl.UInt8,  # Nombre de déplacements réalisés
    "NBDEPLVP": pl.UInt8,  # Nombre de déplacements réalisés en voiture (passager ou conducteur)
    "NBDEPLVPC": pl.UInt8,  # Nombre de déplacements réalisés en voiture (conducteur)
    "NBDEPLTC": pl.UInt8,  # Nombre de déplacements réalisés en transports collectifs
    "NBDEPLVELO": pl.UInt8,  # Nombre de déplacements réalisés à vélo
    "NBDEPL2RM": pl.UInt8,  # Nombre de déplacements réalisés en deux roues-motorisé
    "NBDEPLMAP": pl.UInt8,  # Nombre de déplacements réalisés à pied
    "DDOMTRAV": pl.Float64,  # Portée du déplacement domicile - travail / études en kilomètres
}

REFERENCE_PERSON_LINK_MAP = {
    1: "reference_person",  # Personne de référence
    2: "spouse",  # Conjoint
    3: "child",  # Enfant, gendre, belle-fille
    4: "other:relative",  # Ascendants, beaux-parents
    5: "other:relative",  # Petits-enfants
    6: "other:relative",  # Autre parents
    7: "other:non_relative",  # Employés de maison salariés et logés
    8: "other:non_relative",  # Autre non parent
}

RESIDENT_TYPE_MAP = {
    1: "permanent_resident",  # Réside dans le logement une grande partie de l'année
    2: "mostly_weekends",  # Logé ailleurs pour motif travail ou études
    3: "mostly_weekdays",  # Logé ici pour motif travail ou études
}

EDUCATION_LEVEL_MAP = {
    1: None,  # Personne en cours de scolarité
    2: "primary",  # Primaire
    3: "secondary:no_bac",  # Secondaire (de la 6ème à la 3ème)
    4: "secondary:no_bac",  # Secondaire (de la seconde à la terminale, BEP, CAP) et non titulaire du bac
    5: "secondary:bac",  # Secondaire et titulaire du bac
    6: "higher:at_most_bac+2",  # Supérieur jusqu’à BAC + 2 (y compris BTS – DUT)
    7: "higher:at_least_bac+3",  # Supérieur BAC + 3 et plus
    # 8 represents only 54 observations
    8: None,  # Apprentissage
    9: "higher:at_most_bac+2",  # Autre formation postsecondaire (sanitaire et social ou artistique, …)
    0: "no_studies_or_no_diploma",  # La personne n’est jamais allée à l’école même en primaire
}

DETAILED_EDUCATION_LEVEL_MAP = {
    1: None,  # Personne en cours de scolarité
    2: "primary:unspecified",  # Primaire
    3: "secondary:no_bac:college",  # Secondaire (de la 6ème à la 3ème)
    4: "secondary:no_bac:CAP/BEP",  # Secondaire (de la seconde à la terminale, BEP, CAP) et non titulaire du bac
    5: "secondary:bac:unspecified",  # Secondaire et titulaire du bac
    6: "higher:at_most_bac+2:unspecified",  # Supérieur jusqu’à BAC + 2 (y compris BTS – DUT)
    7: "higher:at_least_bac+3:unspecified",  # Supérieur BAC + 3 et plus
    8: None,  # Apprentissage
    9: "higher:at_most_bac+2:paramedical_social",  # Autre formation postsecondaire (sanitaire et social ou artistique, …)
    0: "no_studies",  # La personne n’est jamais allée à l’école même en primaire
}

DETAILED_PROFESSIONAL_OCCUPATION_MAP = {
    1: "worker:full_time",  # Exerce un métier, a un emploi, aide un membre de sa famille (emploi rémunéré) à plein temps (actif à  plein temps)
    2: "worker:part_time",  # Exerce un métier, a un emploi, aide un membre de sa famille (emploi rémunéré) à temps partiel (actif à temps partiel)
    3: "student:higher",  # Etudiant
    4: "student:apprenticeship",  # Elève d’un centre d’apprentissage avec contrat de qualification
    5: "student:primary_or_secondary",  # Elève du primaire ou du secondaire
    6: "other:unemployed",  # Chômeur ayant déjà travaillé
    7: "other:retired",  # Retraité, ancien salarié, retiré des affaires
    8: "other:unemployed",  # Chômeur n’ayant jamais travaillé
    9: "other:homemaker",  # Reste au foyer, personne sans profession
    0: "other:unspecified",  # Inactif, pensionné
}

PCS_GROUP_MAP = {
    1: "agriculteurs_exploitants",  # Agriculteurs exploitants
    2: "artisans_commerçants_chefs_d'entreprise",  # Artisans, commerçants et chefs d'entreprise
    3: "cadres_et_professions_intellectuelles_supérieures",  # Cadres et professions intellectuelles supérieures
    4: "professions_intermédiaires",  # Professions Intermédiaires
    5: "employés",  # Employés
    6: "ouvriers",  # Ouvriers
    7: "retraités",  # Retraités
    8: "autres_personnes_sans_activité_professionnelle",  # Autres personnes sans activité professionelle
}

WORKPLACE_SINGULARITY_MAP = {
    1: "unique:outside",  # Oui, j'ai un seul lieu de travail / d'études habituel en dehors du domicile
    2: "unique:home",  # Oui, j'ai un seul lieu de travail / d'études habituel à domicile
    3: "variable",  # Non, je n'ai pas de lieu fixe de travail / d'études
}

CAR_PARKING_MAP = {1: "yes:unspecified", 2: "no"}

BICYCLE_PARKING_MAP = {1: "yes:on_site", 2: "no"}

STUDENT_CATEGORY_MAP = {
    # For person below 5 year old, the CS24L column is null, so we can reasonably assume that no one
    # is in maternelle.
    80: "primaire",  # Maternelle ou Primaire (CP à CM2)
    81: "collège:6e",  # Collège, 6ème
    82: "collège:5e",  # Collège, 5ème
    83: "collège:4e",  # Collège, 4ème
    84: "collège:3e",  # Collège, 3ème
    85: "collège:SEGPA",  # Collège, SEGPA
    86: "lycée:CAP",  # Technique court (CAP, BEP)
    87: "lycée:seconde",  # Lycée, Seconde
    88: "lycée:première",  # Lycée, 1ère
    89: "lycée:terminale",  # Lycée, Terminale, niveau Bac ou Brevet professionnel
    90: "supérieur:technique",  # Technique supérieur (IUT, BTS)
    91: "supérieur:prépa1",  # 1ère année de classe préparatoire (à des concours ou intégrée)
    92: "supérieur:prépa2",  # 2éme année de classe préparatoire (à des concours ou intégrée)
    93: "supérieur:BAC+1",  # Bac+1
    94: "supérieur:BAC+2",  # Bac+2
    95: "supérieur:BAC+3",  # Bac+3
    96: "supérieur:BAC+4",  # Bac+4
    97: "supérieur:BAC+5",  # Bac+5
    98: "supérieur:BAC+6&+",  # Bac+6 ou plus
}

DRIVING_LICENSE_MAP = {
    1: "yes",
    2: "no",
    3: "in_progress",
}

TRAVELED_MAP = {
    1: "yes",  # Oui
    2: "no",  # Non, à cause de la grippe A
    3: "no",  # Non, car incapacité permanente liée à des problèmes de santé
    4: "no",  # Non, car incapacité temporaire liée à des problèmes de santé (membre cassé …)
    5: "no",  # Non, car pas de moyen de locomotion motorisé à disposition ce jour là
    6: "no",  # Non, car intempéries
    7: "no",  # Non, n’est pas sorti de son domicile pour une autre raison
    8: "away",  # Non, car se trouvait hier hors région Ile de France
}

# NOTE. This is not actually used.
WORKED_MAP = {
    1: "no:reason",  # Congés hebdomadaires
    2: "no:reason",  # Congés / RTT toute la journée
    3: "yes:unspecified",  # Congés ou RTT le matin
    4: "yes:unspecified",  # Congés ou RTT l'après-midi
    5: "no:weekday",  # Temps partiel toute la journée
    6: "yes:unspecified",  # Temps partiel le matin
    7: "yes:unspecified",  # Temps partiel l'après-midi
    8: "yes:unspecified",  # Travail en horaires décalés
    9: "yes:unspecified",  # Travail en horaires aménagés (femmes enceintes …)
    10: "no:reason",  # Arrêt maladie ou enfant malade toute la journée
    11: "yes:unspecified",  # Arrêt maladie ou enfant malade le matin
    12: "yes:unspecified",  # Arrêt maladie ou enfant malade l'après-midi
    13: "no:reason",  # Autre arrêt (grève, chômage technique …)
    14: "no:reason",  # Congé de maternité
    15: "yes:unspecified",  # Aucune de ces situations
}


def scan_persons(filename: str):
    lf = pl.scan_csv(filename, separator=";", schema_overrides=SCHEMA)
    return lf


def standardize_persons(filename: str, households: pl.LazyFrame):
    lf = scan_persons(filename)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("NQUEST")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    is_student = pl.col("OCCP").is_in((3, 4, 5))
    lf = lf.rename(
        {
            "AGE": "age",
            "CS8": "pcs_group_code",
            "NBDEPL": "nb_trips",
            "POIDSP": "sample_weight_all",
        }
    )
    lf = lf.with_columns(
        person_index="NP",
        original_person_id=pl.struct("NQUEST", "NP"),
        reference_person_link=pl.col("LIENPREF").replace_strict(REFERENCE_PERSON_LINK_MAP),
        resident_type=pl.col("TYPEP").replace_strict(RESIDENT_TYPE_MAP),
        woman=pl.col("SEXE") == 2,
        education_level=pl.col("DIPL").replace_strict(EDUCATION_LEVEL_MAP),
        detailed_education_level=pl.col("DIPL").replace_strict(DETAILED_EDUCATION_LEVEL_MAP),
        detailed_professional_occupation=pl.col("OCCP").replace_strict(
            DETAILED_PROFESSIONAL_OCCUPATION_MAP
        ),
        pcs_category_code2003=pl.when(pl.col("CS24L").is_between(1, 69))
        .then("CS24L")
        .otherwise(None),
        workplace_singularity=pl.when(is_student.not_()).then(
            pl.col("ULTRAV").replace_strict(WORKPLACE_SINGULARITY_MAP)
        ),
        work_detailed_zone=pl.when(is_student.not_()).then("LTRAVC"),
        work_draw_zone=pl.when(is_student.not_()).then("LTRAVSECT"),
        work_insee=pl.when(is_student.not_()).then("LTRAVCOMM"),
        work_commute_euclidean_distance_km=pl.when(is_student.not_()).then("DDOMTRAV"),
        work_car_parking=pl.when(is_student.not_()).then(
            pl.col("PKVPTRAV").replace_strict(CAR_PARKING_MAP)
        ),
        work_bicycle_parking=pl.when(is_student.not_()).then(
            pl.col("PKVLTRAV").replace_strict(BICYCLE_PARKING_MAP)
        ),
        student_category=pl.col("CS24L").replace_strict(STUDENT_CATEGORY_MAP, default=None),
        study_only_at_home=pl.when(is_student).then(pl.col("ULTRAV").eq(2)),
        study_detailed_zone=pl.when(is_student).then("LTRAVC"),
        study_draw_zone=pl.when(is_student).then("LTRAVSECT"),
        study_insee=pl.when(is_student).then("LTRAVCOMM"),
        study_commute_euclidean_distance_km=pl.when(is_student).then("DDOMTRAV"),
        study_car_parking=pl.when(is_student).then(
            pl.col("PKVPTRAV").replace_strict(CAR_PARKING_MAP)
        ),
        study_bicycle_parking=pl.when(is_student).then(
            pl.col("PKVLTRAV").replace_strict(BICYCLE_PARKING_MAP)
        ),
        has_driving_license=pl.col("PERMVP").replace_strict(DRIVING_LICENSE_MAP),
        has_motorcycle_driving_license=pl.col("PERM2RM").replace_strict(DRIVING_LICENSE_MAP),
        public_transit_subscription=pl.when(pl.col("ABONTC").ne(1))
        .then(
            pl.when(pl.col("REMBTC").eq(1))
            .then(pl.lit("yes:free"))
            .when(pl.col("REMBTC").eq(9))
            .then(pl.lit("yes:paid:without_employer_contribution"))
            .when(pl.col("REMBTC").is_between(2, 8))
            .then(pl.lit("yes:paid:with_employer_contribution"))
            .otherwise(pl.lit("yes:unspecified"))
        )
        .when(pl.col("ABONTC").eq(1))
        .then(pl.lit("no")),
        has_car_sharing_subscription=pl.col("ABONVP").eq(1),
        has_bike_sharing_subscription=pl.col("ABONVLS").is_in((1, 2, 3)),
        has_travel_inconvenience=pl.col("HANDI").eq(1),
        # All persons are supposed to be surveyed, except children below 5.
        # Variable `NONDEPL` is null for all children below 5 + 2 persons (which we assume to have
        # not been surveyed).
        is_surveyed=pl.col("NONDEPL").is_not_null(),
        #
        traveled_during_surveyed_day=pl.col("NONDEPL").replace_strict(TRAVELED_MAP),
        # NOTE. Column CONGE cannot really be used to built the `worked_during_surveyed_day`
        # variable because it is not clear what it means and the values are inconsistent with
        # observations (e.g., 8% of people reporting "Congés hebdomadaires" did work the survey
        # day).
        # worked_during_surveyed_day=pl.col("CONGE").replace_strict(
        #     WORKED_MAP, return_dtype=PERSON_SCHEMA["worked_during_surveyed_day"]
        # ),
    )
    lf = lf.with_columns(
        # `sample_weight_surveyed` can be read from `sample_weight_all` because the only
        # non-surveyed persons are people below 5 (except for 2 other persons mentionned above).
        sample_weight_surveyed=pl.when("is_surveyed").then("sample_weight_all")
    )
    lf = clean(lf)
    return lf

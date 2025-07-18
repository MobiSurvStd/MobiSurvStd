import polars as pl

from mobisurvstd.common.persons import clean

SCHEMA = {
    "IDCEREMA": pl.String,  # Identifiant du ménage
    "TYPE_QUEST": pl.String,  # Type de questionnaire
    "NP": pl.UInt8,  # Numéro de personne dans le ménage
    "RESDEP": pl.String,  # Département de résidence
    "RESCOUR": pl.UInt8,  # Couronne de résidence
    "RESCOMM": pl.String,  # Commune de résidence
    "JOURSEM": pl.String,  # Jour de la semaine de la date schéma des déplacements
    "LIENP1": pl.UInt8,  # Lien de parenté avec la personne 1
    "SEXE": pl.UInt8,  # Sexe
    "AGE": pl.UInt8,  # Age
    "TRAGE": pl.UInt8,  # Classes d'âge
    "PERMVP": pl.UInt8,  # Permis de conduire voiture
    "ABONVP": pl.UInt8,  # Abonnement autopartage
    "T_ABONVP": pl.UInt8,  # Type d'abonnement autopartage
    "PERM2RM": pl.UInt8,  # Permis de conduire 2RM
    "ABONTC": pl.UInt8,  # Abonnement TC
    "ABONTC_10": pl.UInt8,  # Forfait Navigo
    "ABONC_11": pl.UInt8,  # Forfait Navigo + Annuel
    "ABONTC_12": pl.UInt8,  # Forfait Navigo + Mois
    "ABONTC_13": pl.UInt8,  # Forfait Navigo + Semaine
    "ABONTC_20": pl.UInt8,  # Forfait Navigo gratuité
    "ABONTC_30": pl.UInt8,  # Forfait Améthyste
    "ABONTC_40": pl.UInt8,  # Forfait Navigo Solidarité
    "ABONTC_41": pl.UInt8,  # Forfait Navigo Solidarité + Mois
    "ABONTC_42": pl.UInt8,  # Forfait Navigo Solidarité + Semaine
    "ABONTC_50": pl.UInt8,  # Forfait Imagine R
    "ABONTC_51": pl.UInt8,  # Forfait Imagine R + Scolaire
    "ABONTC_52": pl.UInt8,  # Forfait Imagine R + Etudiant
    "ABONTC_60": pl.UInt8,  # Forfait Gratuité Jeunes en insertion
    "ABONTC_70": pl.UInt8,  # Carte scolaire bus ligne régulière ou carte Scol'R
    "ABONTC_90": pl.UInt8,  # Autre abonnement (exemple : police, RATP…)
    "ZONTC": pl.UInt8,  # Zonage de l'abonnement TC
    "SUPPTC": pl.UInt8,  # Support de l'abonnement TC
    "SUPPTC_txt": pl.String,  # Support de l'abonnement TC
    "NV_MOIS": pl.UInt8,  # Nombre de forfaits Mois
    "NV_SEM": pl.UInt8,  # Nombre de forfaits Semaine
    "REMBTC": pl.UInt8,  # Prise en charge de l’abonnement TC par l’employeur
    "ABONVLS": pl.UInt8,  # Abonnement de Vélib ou VLS
    "OCCP": pl.UInt8,  # Occupation principale
    "OCCP_txt": pl.String,  # Occupation principale
    "DIPL": pl.UInt8,  # Plus haut niveau de diplôme obtenu
    "PROF": pl.String,  # Profession
    "CS8": pl.UInt8,  # Catégorie socioprofessionnelle Niveau 1
    "CS24L": pl.UInt8,  # Catégorie socioprofessionnelle Niveau 2
    "LIEU_TRAV": pl.UInt8,  # Habitude de travail
    "LIEU_TRAV_txt": pl.String,
    "TRAVCOMM": pl.String,  # Commune du lieu de travail
    "TRAVLNG": pl.Float64,  # Longitude du lieu de travail
    "TRAVLAT": pl.Float64,  # Latitude du lieu de travail
    "HIER_TRAV": pl.UInt8,  # Avez-vous travaillé hier ?
    "HIER_TRAV_txt": pl.String,  # 	Avez-vous travaillé hier ?
    "HIER_NON_TRAV": pl.String,  # Raison pour laquelle la personne n'a pas travaillé
    "HIER_NON_TRAV_txt": pl.String,  # 	Raison pour laquelle la personne n'a pas travaillé
    "PKVPTRAV": pl.UInt8,  # Disponibilité d'un  parking au lieu de travail
    "PKVLTRAV": pl.UInt8,  # Disponibilité d'un  parking vélo au lieu de travail
    "LIEU_ETUD": pl.UInt8,  # Habitude d'études
    "LIEU_ETUD_txt": pl.String,  # 	Habitude d'études
    "ETUDCOMM": pl.String,  # Commune du lieu d'études principal
    "ETUDLNG": pl.Float64,  # Longitude du lieu d'études
    "ETUDLAT": pl.Float64,  # Latitude du lieu d'études
    "PKVPETUD": pl.UInt8,  # Disponibilité d'un  parking au lieu d'études
    "PKVLETUD": pl.UInt8,  # Disponibilité d'un  parking vélo au lieu d'études
    "GENE": pl.UInt8,  # Gêne ressentie lors des déplacements
    "DEPL": pl.UInt8,  # La personne s'est-elle déplacée la veille ?
    "NBDEPL": pl.UInt8,  # Nombre de déplacements réalisés
    "NBDEPLVP": pl.UInt8,  # Nombre de déplacements réalisés en voiture (passager ou conducteur)
    "NBDEPLVPC": pl.UInt8,  # Nombre de déplacements réalisés en voiture (conducteur)
    "NBDEPLTC": pl.UInt8,  # Nombre de déplacements réalisés en transports collectifs
    "NBDEPLVELO": pl.UInt8,  # Nombre de déplacements réalisés à vélo
    "NBDEPL2RM": pl.UInt8,  # Nombre de déplacements réalisés en deux roues-motorisé
    "NBDEPLMAP": pl.UInt8,  # Nombre de déplacements réalisés à pied
    "DDOMTRAV": pl.Float64,  # Distance à vol d’oiseau entre le domicile et le lieu de travail ou d’étude (en km avec une décimale)
    "NONDEPL_T": pl.UInt8,  # Si la personne ne s’est pas déplacée pour aller au travail, quelle en était la raison ?
    "NONDEPL_T_txt": pl.String,  # 	Si la personne ne s’est pas déplacée pour aller au travail, quelle en était la raison ?
    "NONDEPL": pl.UInt8,  # Si la personne ne s’est pas déplacée du tout, quelle en était la raison ?
    "NONDEPL_txt": pl.String,  # 	Si la personne ne s’est pas déplacée du tout, quelle en était la raison
    "DERDEPL": pl.UInt32,  # Date du dernier déplacement
    "DERJOUR": pl.UInt16,  # Nombre de jours depuis le dernier déplacement
    "DER_CL": pl.UInt8,  # Classe du dernier déplacement
    "NB_7JOURS": pl.UInt8,  # Nombre de jours où la personne s'est déplacée la semaine passée
    "NB_7JOURS_T": pl.UInt8,  # Nombre de jours où la personne s'est déplacée la semaine passée pour le travail
    "TPS_PART": pl.UInt8,  # Quantité de temps partiel
    "ORG_TP": pl.UInt8,  # Organisation du temps partiel
    "HOR_TRAV": pl.UInt8,  # Horaires de travail
    "HOR_TRAV_txt": pl.String,  # 	Horaires de travail
    "FREQ_T": pl.UInt8,  # Fréquence des déplacements pour le travail ou les études
    "FREQ_A": pl.UInt8,  # Fréquence des déplacements pour les achats
    "FREQ_L": pl.UInt8,  # Fréquence des déplacements pour les loisirs
    "FREQ_D": pl.UInt8,  # Fréquence des déplacements pour les démarches
    "ACH_INT": pl.UInt8,  # Avez-vous effectué des achats sur internet au cours des 7 derniers jours ?
    "ACH_INT11": pl.UInt8,  # Avez-vous effectué des achats sur internet au cours des 7 derniers jours  pour des biens de consommation courante ?
    "ACH_INT12": pl.UInt8,  # Avez-vous effectué des achats sur internet au cours des 7 derniers jours  pour des vêtements ou accessoires ?
    "ACH_INT13": pl.UInt8,  # Avez-vous effectué des achats sur internet au cours des 7 derniers jours  pour bien d'équipement ou technologiques ?
    "ACH_INT14": pl.UInt8,  # Avez-vous effectué des achats sur internet au cours des 7 derniers jours  pour des biens ou services culturels ?
    "ACH_INT15": pl.UInt8,  # Avez-vous effectué des achats sur internet au cours des 7 derniers jours  pour des billets de transport ?
    "ACH_INT19": pl.String,  # Détails des achats sur internet au cours des 7 derniers jours
    "PORTAB": pl.UInt8,  # Possession d'un téléphone portable
    "APPS": pl.UInt8,  # Utilisation d'applications sur son smartphone pour se déplacer en Île-de-France
    "APPS_LIST": pl.String,  # Type d'application utilisée
    "APPS_LIST_txt": pl.String,  # 	Type d'application utilisée
    "TROT_LS": pl.UInt8,  # Utilisation d'une trottinette en libre-service au cours du dernier mois
    "TROT_LS_APP": pl.String,  # Type d'application de trottinette électrique utilisée au cours du dernier mois
    "TROT_LS_APP_txt": pl.String,  # 	Type d'application de trottinette électrique utilisée au cours du dernier mois
    "VELO_LS": pl.UInt8,  # Utilisation d'un vélo en libre-service au cours du dernier mois
    "VELO_LS_APP": pl.String,  # Type d'application de vélo en libre-service utilisée au cours du dernier mois
    "VELO_LS_APP_txt": pl.String,  # 	Type d'application de vélo en libre-service utilisée au cours du dernier mois
    "VOIT_LS": pl.UInt8,  # Utilisation d'un voiture en autopartage ou libre-service au cours du dernier mois
    "VOIT_LS_APP": pl.String,  # Type d'application de voiture en autopartage ou libre-service utilisée au cours du dernier mois
    "VOIT_LS_APP_txt": pl.String,  # 	Type d'application de voitures en autopartage ou libre-service utilisée au cours du dernier mois
    "COVOIT": pl.UInt8,  # Utilisation d'un application de covoiturage au cours du dernier mois
    "COVOIT_ROLE": pl.UInt8,  # Rôle pendant le covoiturage
    "COVOIT_APP": pl.String,  # Type d'application de covoiturage utilisée au cours du dernier mois
    "COVOIT_APP_txt": pl.String,  # 	Type d'application de covoiturage utilisée au cours du dernier mois
    "KISH": pl.UInt8,  # Dans le cas des enquêtes CATI, vaut 1 si l'individu  a été tiré au sort, sinon 0
    "POIDSI": pl.Float64,  # Poids de l'individu (uniquement les 5 ans et plus et ayant été enquêtés)
    "POIDSTI": pl.Float64,  # Poids de l'individu (tous les individus du ménage)
}

REFERENCE_PERSON_LINK_MAP = {
    None: "reference_person",
    1: "spouse",  # Conjoint
    2: "child",  # Enfant, gendre, belle-fille
    3: "other:relative",  # Petit-enfant
    4: "other:relative",  # Parent, beau-parent, ascendant
    5: "other:relative",  # Autre lien de parenté
    6: "other:non_relative",  # Employé de maison salarié et logé
    7: "other:relative",  # Frère, sœur
    8: "other:non_relative",  # Autre sans lien de parenté
    9: "other:non_relative",  # NOTE. It seems that 9 is used instead of 8...
}

EDUCATION_LEVEL_MAP = {
    0: "no_studies_or_no_diploma",  # Aucun diplôme
    1: "secondary:no_bac",  # CEP (certificat d'études primaires), BEPC, brevet élémentaire, brevet des collèges
    2: "secondary:no_bac",  # CAP, BEP ou diplôme de niveau équivalent
    3: "secondary:bac",  # Baccalauréat général ou technologique ou diplôme de niveau équivalent
    4: "higher:at_most_bac+2",  # BAC+2 : BTS, DUT, DEUG…
    5: "higher:at_least_bac+3",  # BAC+3 ou BAC+4 : licence, licence pro, maîtrise…
    6: "higher:at_least_bac+3",  # Bac+5 et plus : Master, DEA, DESS, diplôme de grandes écoles, doctorat…
}

DETAILED_EDUCATION_LEVEL_MAP = {
    0: "no_diploma",  # Aucun diplôme
    # CEP should actually be primary:CEP but let's assume that brevet is the most common choice here
    1: "secondary:no_bac:college",  # CEP (certificat d'études primaires), BEPC, brevet élémentaire, brevet des collèges
    2: "secondary:no_bac:CAP/BEP",  # CAP, BEP ou diplôme de niveau équivalent
    3: "secondary:bac:unspecified",  # Baccalauréat général ou technologique ou diplôme de niveau équivalent
    4: "higher:at_most_bac+2:unspecified",  # BAC+2 : BTS, DUT, DEUG…
    5: "higher:bac+3_or_+4",  # BAC+3 ou BAC+4 : licence, licence pro, maîtrise…
    6: "higher:at_least_bac+5",  # Bac+5 et plus : Master, DEA, DESS, diplôme de grandes écoles, doctorat…
}

PROFESSIONAL_OCCUPATION_MAP = {
    10: "worker",  # Emploi + non-réponse
    11: "worker",  # Emploi + à temps complet
    12: "worker",  # Emploi + à temps partiel
    20: "student",  # Apprentissage sous contrat ou stage rémunéré
    31: "student",  # Scolaire (école, collège, lycée) ou stage non rémunéré
    32: "student",  # Etudiant ou stage non rémunéré
    40: "other",  # Chômage (inscrit ou non à Pôle Emploi)
    50: "other",  # Retraite ou pré-retraite (ancien salarié ou ancien indépendant)
    60: "other",  # Femme ou homme au foyer
    90: "other",  # Autre
}

DETAILED_PROFESSIONAL_OCCUPATION_MAP = {
    10: "worker:unspecified",  # Emploi + non-réponse
    11: "worker:full_time",  # Emploi + à temps complet
    12: "worker:part_time",  # Emploi + à temps partiel
    20: "student:apprenticeship",  # Apprentissage sous contrat ou stage rémunéré
    31: "student:primary_or_secondary",  # Scolaire (école, collège, lycée) ou stage non rémunéré
    32: "student:higher",  # Etudiant ou stage non rémunéré
    40: "other:unemployed",  # Chômage (inscrit ou non à Pôle Emploi)
    50: "other:retired",  # Retraite ou pré-retraite (ancien salarié ou ancien indépendant)
    60: "other:homemaker",  # Femme ou homme au foyer
    90: "other:unspecified",  # Autre
}

WORKPLACE_SINGULARITY_MAP = {
    1: "unique:outside",  # Vous avez un lieu de travail principal hors de votre domicile (bureau, entreprise, usine…)
    2: "variable",  # Vous vous déplacez chez des clients
    3: "unique:home",  # Vous travaillez à votre domicile
    # NOTE. When looking at variable LIEU_TRAV_txt, it seems that almost all the "Autre" answers
    # would fit in the case "variable".
    9: "variable",  # Autre
}

CAR_PARKING_MAP = {0: "no", 1: "yes:unspecified"}

BICYCLE_PARKING_MAP = {
    0: "no",
    10: "yes:on_site",
    11: "yes:on_site:sheltered",
    12: "yes:on_site:unsheltered",
}

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
    0: "no",
    1: "yes",
    2: "in_progress",
}

CAR_SHARING_MAP = {
    # 0 is used instead of -1?
    0: None,
    1: "yes:organized",  # Est en libre-service : possibilité de rendre le véhicule ailleurs, réservation facultative (Autolib…)
    2: "yes:organized",  # Fonctionne en boucle - on doit rendre le véhicule où on l'a pris (ZipCar…)
    3: "yes:peer_to_peer",  # Se fait entre particuliers (Drivy…)
}


def scan_persons(filename: str):
    # We use the inefficient `read_csv().lazy()` because we need to use `encoding="latin1"`, which
    # does not exist with `scan_csv()`.
    lf = pl.read_csv(
        filename,
        separator=";",
        encoding="latin1",
        schema_overrides=SCHEMA,
        null_values=["-1", "-10"],
    ).lazy()
    return lf


def standardize_persons(filename: str, households: pl.LazyFrame):
    lf = scan_persons(filename)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct("IDCEREMA")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename(
        {
            "AGE": "age",
            "CS8": "pcs_group_code",
            "TRAVLNG": "work_lng",
            "TRAVLAT": "work_lat",
            "ETUDLNG": "study_lng",
            "ETUDLAT": "study_lat",
            "POIDSTI": "sample_weight_all",
            "POIDSI": "sample_weight_surveyed",
        }
    )
    lf = lf.with_columns(
        original_person_id=pl.struct("IDCEREMA", "NP"),
        reference_person_link=pl.col("LIENP1").replace_strict(REFERENCE_PERSON_LINK_MAP),
        woman=pl.col("SEXE") == 2,
        education_level=pl.col("DIPL").replace_strict(EDUCATION_LEVEL_MAP),
        detailed_education_level=pl.col("DIPL").replace_strict(DETAILED_EDUCATION_LEVEL_MAP),
        professional_occupation=pl.col("OCCP").replace_strict(PROFESSIONAL_OCCUPATION_MAP),
        detailed_professional_occupation=pl.col("OCCP").replace_strict(
            DETAILED_PROFESSIONAL_OCCUPATION_MAP
        ),
        pcs_category_code2003=pl.when(pl.col("CS24L").is_between(1, 69)).then("CS24L"),
        workplace_singularity=pl.col("LIEU_TRAV").replace_strict(WORKPLACE_SINGULARITY_MAP),
        # Column DDOMTRAV can represent either work commute distance or study commute distance.
        work_commute_euclidean_distance_km=pl.when(pl.col("work_lng").is_not_null())
        .then("DDOMTRAV")
        .otherwise(None),
        study_commute_euclidean_distance_km=pl.when(pl.col("study_lng").is_not_null())
        .then("DDOMTRAV")
        .otherwise(None),
        work_car_parking=pl.col("PKVPTRAV").replace_strict(CAR_PARKING_MAP),
        work_bicycle_parking=pl.col("PKVLTRAV").replace_strict(BICYCLE_PARKING_MAP),
        # The student category is not reported in CS24L, contrarily to what the survey documentation
        # says.
        # student_category=pl.col("CS24L").replace_strict(
        #     STUDENT_CATEGORY_MAP, default=None
        # ),
        study_only_at_home=pl.col("LIEU_ETUD").eq(2),
        study_car_parking=pl.col("PKVPETUD").replace_strict(CAR_PARKING_MAP),
        study_bicycle_parking=pl.col("PKVLETUD").replace_strict(BICYCLE_PARKING_MAP),
        has_driving_license=pl.col("PERMVP").replace_strict(DRIVING_LICENSE_MAP),
        has_motorcycle_driving_license=pl.col("PERM2RM").replace_strict(DRIVING_LICENSE_MAP),
        has_public_transit_subscription=pl.col("ABONTC").eq(1),
        public_transit_subscription=pl.when(
            # Forfait Navigo Gratuité, Améthyste et Gratuité Jeunes en insertion
            pl.col("ABONTC_20").eq(1) | pl.col("ABONTC_30").eq(1) | pl.col("ABONTC_60").eq(1)
        )
        .then(pl.lit("yes:free"))
        .when(
            pl.col("ABONTC_40").eq(1)
            | pl.col("ABONTC_41").eq(1)
            | pl.col("ABONTC_42").eq(1)
            | pl.col("ABONTC_90").eq(1)
        )
        .then(pl.lit("yes:unspecified"))
        .when(pl.col("ABONTC").eq(1) & pl.col("REMBTC").eq(1))
        .then(pl.lit("yes:paid:with_employer_contribution"))
        .when(pl.col("ABONTC").eq(1) & pl.col("REMBTC").eq(0))
        .then(pl.lit("yes:paid:without_employer_contribution"))
        .when(pl.col("ABONTC").eq(1))
        .then(pl.lit("yes:paid"))
        .when(pl.col("ABONTC").eq(0))
        .then(pl.lit("no"))
        .otherwise(None),
        has_car_sharing_subscription=pl.col("ABONVP").eq(1),
        car_sharing_subscription=pl.when(pl.col("ABONVP").eq(0))
        .then(pl.lit("no"))
        .otherwise(pl.col("T_ABONVP").replace_strict(CAR_SHARING_MAP)),
        has_bike_sharing_subscription=pl.col("ABONVLS").eq(1),
        has_travel_inconvenience=pl.col("GENE").is_in((1, 2, 3)),
        is_surveyed=pl.col("DEPL").is_not_null(),
        traveled_during_surveyed_day=pl.when(pl.col("DEPL").eq(1))
        .then(pl.lit("yes"))
        .when(pl.col("DEPL").eq(0))
        .then(pl.lit("no"))
        .otherwise(None),
        # Case 9 (Autre) is set to "yes:outside" as most reasons specified in "HIER_TRAV_txt"
        # imply that the person did work outside.
        worked_during_surveyed_day=pl.when(pl.col("HIER_TRAV").is_in((1, 2, 4, 5, 9)))
        .then(pl.lit("yes:outside"))
        .when(pl.col("HIER_TRAV").eq(3) & pl.col("LIEU_TRAV").eq(3))
        .then(pl.lit("yes:home:usual"))
        .when(pl.col("HIER_TRAV").eq(3) & pl.col("LIEU_TRAV").ne(3))
        .then(pl.lit("yes:home:telework"))
        .when(pl.col("HIER_NON_TRAV").eq("B22"))
        .then(pl.lit("no:weekday"))
        .when(pl.col("HIER_TRAV").eq(0))
        .then(pl.lit("no:reason"))
        .otherwise(None),
    )
    lf = lf.with_columns(
        is_retired=pl.col("pcs_group_code").eq(7),
        # is_student=pl.col("professional_occupation").eq("student"),
        is_non_apprentice_student=pl.col("professional_occupation").eq("student")
        & pl.col("detailed_professional_occupation").ne("student:apprenticeship"),
        # Set work secondary occupation for non-workers with a usual workplace.
        secondary_professional_occupation=pl.when(
            pl.col("professional_occupation").ne("worker")
            & pl.col("workplace_singularity").is_not_null()
        ).then(pl.lit("work")),
    )
    lf = lf.with_columns(
        # Force retired to actually be retired...
        professional_occupation=pl.when("is_retired")
        .then(pl.lit("other"))
        .otherwise("professional_occupation"),
        detailed_professional_occupation=pl.when("is_retired")
        .then(pl.lit("other:retired"))
        .otherwise("detailed_professional_occupation"),
        pcs_category_code2003=pl.when("is_retired")
        .then(pl.lit(None))
        .otherwise("pcs_category_code2003"),
        # Force non-students to have no `student_category`.
        # student_category=pl.when(pl.col("is_student").not_())
        # .then(pl.lit(None))
        # .otherwise("student_category"),
    )
    lf = lf.with_columns(
        # Set `pcs_group_code` to null for non-apprenticeship students.
        pcs_group_code=pl.when("is_non_apprentice_student")
        .then(pl.lit(None))
        .otherwise("pcs_group_code"),
        pcs_category_code2003=pl.when("is_non_apprentice_student")
        .then(pl.lit(None))
        .otherwise("pcs_category_code2003"),
    )
    lf = clean(lf)
    return lf

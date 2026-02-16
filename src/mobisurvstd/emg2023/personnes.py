import polars as pl

from mobisurvstd.common.persons import clean

SCHEMA = {
    "ID": pl.String, # Identifiant de l'individu
    "DEPT": pl.String, # Département de résidence de l'individu
    "CODGEO": pl.String, # Code géographique INSEE de la commune de résidence de l'individu
    "Zone_densité_Rés": pl.UInt8, #	
    "NOMCOM": pl.String, # Commune de résidence de l'individu
    "SEXE": pl.String, # Sexe de l'individu	
    "Age": pl.UInt8, # Âge de l'individu	
    "DIPLOME": pl.String, # Indique le plus haut niveau de diplôme obtenu par l'individu
    "PCS_NOM": pl.String, # Indique la catégorie socio-professionnelle de l'individu	
    "PCS_8": pl.UInt8, # Numéro de la catégorie socio-professionnelle de l'individu	
    "TYPE_MEN": pl.String, #	Type de ménage, situation familiale ou mode de cohabitation de l'individu
    "NBPERS_MEN": pl.UInt8, # Nombre de personnes du ménage de l'individu
    "NB_10": pl.UInt8, # Nombre de personnes du ménage de moins de 11 ans
    "NB_11_17": pl.UInt8, #	Nombre de personnes du ménage entre 11 ans et 17 ans
    "NB_18_24": pl.UInt8, #	Nombre de personnes du ménage entre 18 ans et 24 ans
    "NB_25_64": pl.UInt8, #	Nombre de personnes du ménage entre 25 ans et 64 ans
    "NB_65": pl.UInt8, # Nombre de personnes du ménage de 65 ans et plus
    "PMR": pl.String, # Indique si l'individu a des difficultés pour se déplacer
    "PERMIS_B": pl.String, #	Indique si l'individu possède le permis de conduire B
    "NB_VP": pl.UInt8, # Nombre de voitures du ménage
    "VP_THERM": pl.UInt8, #	Nombre de voitures du ménage à motorisation thermique (y compris hybride)
    "VP_ELEC": pl.UInt8, # Nombre de voitures du ménage à motorisation électrique (EV)
    "2RM": pl.UInt8, # Nombre de deux-roues motorisés du ménage (motos ou scooters y compris électriques)
    "VELO": pl.UInt8, #	Nombre de vélos et vélos à assitance électrique du ménage
    "TROTT_ELEC": pl.UInt8, # Nombre de trottinettes électriques du ménage
    "NAVIGO": pl.String, # Indique si l'individu possède un abonnement Navigo (annuel ou mensuel)
    "IMAGINER": pl.String, # Indique si l'individu possède un abonnement Imagine'R
    "AUTRE_ABO_TC": pl.String, #	Indique si l'individu possède un autre abonnement aux transports en commun
    "VELO_ABO": pl.String, # Indique si l'individu possède un abonnement pour l'utilisation d'un vélo en libre-service (type Vélib')
    "NSM_ABO": pl.String, # Indique si l'individu possède un abonnement pour l'utilisation d'un autre service de mobilité
    "POIDS_INDIV": pl.Float64, # Pondération de l'individu
}

EDUCATION_LEVEL_MAP = {
    "NR": None,
    "Aucun diplôme": "no_studies_or_no_diploma",
    "Brevet des collèges ou de niveau équivalent": "secondary:no_bac",
    "CAP, BEP ou de niveau équivalent": "secondary:no_bac",
    "Baccalauréat général, technologique ou de niveau équivalent": "secondary:bac",
    "Bac +2 : BTS, DUT, DEUG… ": "higher:at_most_bac+2",
    "Bac +3 ou +4 : Licence, Licence professionnelle, Maîtrise, Master 1…": "higher:at_least_bac+3",
    "Bac + 5 et plus : Master 2, DEA, DESS, Diplôme de grande école, Doctorat…": "higher:at_least_bac+3"
}

DETAILED_EDUCATION_LEVEL_MAP = {
    "NR": None,
    "Aucun diplôme": "no_diploma",
    "Brevet des collèges ou de niveau équivalent": "secondary:no_bac:college",
    "CAP, BEP ou de niveau équivalent": "secondary:no_bac:CAP/BEP",
    "Baccalauréat général, technologique ou de niveau équivalent": "secondary:bac:unspecified",
    "Bac +2 : BTS, DUT, DEUG… ": "higher:at_most_bac+2:unspecified",
    "Bac +3 ou +4 : Licence, Licence professionnelle, Maîtrise, Master 1…": "higher:bac+3_or_+4",
    "Bac + 5 et plus : Master 2, DEA, DESS, Diplôme de grande école, Doctorat…": "higher:at_least_bac+5"
}

# emg23 follows definition including students
PCS_CODES = {
    1: "agriculteurs_exploitants",
    2: "artisans_commerçants_chefs_d'entreprise",
    3: "cadres_et_professions_intellectuelles_supérieures",
    4: "professions_intermédiaires",
    5: "employés",
    6: "ouvriers",
    7: "retraités",
    8: "autres_personnes_sans_activité_professionnelle",
}

PCS_GROUP_CODE_MAP = {
    1: 2,  # EMG: Artisan, commerçant et chef d’entreprise
    2: 3,  # EMG: Cadre et profession intellectuelle supérieure
    3: 4,  # EMG: Professions Intermédiaires
    4: 5,  # EMG: Employés
    5: 6,  # EMG: Ouvriers
    6: 7,  # EMG: Retraité ou pré-retraité
    7: None,  # EMG: Étudiant ou lycée
    8: 8,  # Au chômage ou en inactivité)
}

DRIVING_LICENSE_MAP = {
    "Oui": "yes", "Non": "no", "NR": None
}

def scan_persons(filename: str):
    lf = pl.read_excel(filename, schema_overrides=SCHEMA).lazy()
    return lf


def standardize_persons(filename: str, households: pl.LazyFrame):
    lf = scan_persons(filename)

    lf = lf.with_columns(original_household_id=pl.col("ID")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )

    lf = lf.with_columns(
        original_person_id=pl.col("ID"),
        woman=pl.col("SEXE") == "Femme",
        age=pl.col("Age"),
        education_level=pl.col("DIPLOME").replace_strict(EDUCATION_LEVEL_MAP),
        detailed_education_level=pl.col("DIPLOME").replace_strict(DETAILED_EDUCATION_LEVEL_MAP),
        pcs_group_code=pl.col("PCS_8").replace_strict(PCS_GROUP_CODE_MAP),
        has_driving_license=pl.col("PERMIS_B").replace_strict(DRIVING_LICENSE_MAP),
        has_public_transit_subscription=
            pl.col("NAVIGO").eq("Oui") |
            pl.col("IMAGINER").eq("Oui") |
            pl.col("AUTRE_ABO_TC").eq("Oui"),
        has_bike_sharing_subscription=pl.col("VELO_ABO").eq("Oui"),
        has_travel_inconvenience=pl.col("PMR").eq("Oui"),
        sample_weight_all=pl.col("POIDS_INDIV"),
        sample_weight_surveyed=pl.col("POIDS_INDIV"),
        is_surveyed=pl.lit(True),
        professional_occupation=None # added because expected downstream
    )

    lf = lf.sort("original_person_id")
    lf = clean(lf)

    return lf

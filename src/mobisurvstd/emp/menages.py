import polars as pl

from mobisurvstd.common.households import clean

SCHEMA1 = {
    "ident_men": pl.String,  # IDENTIFIANT DU MENAGE
    "ident_log": pl.String,  # Identifiant du logement
    "vague_enq": pl.UInt8,  # Numéro de vague
    "BS": pl.UInt8,  # Numéro de ménage dans le logement
    "pond_menC": pl.Float64,  # Poids ménage
    "NPERS": pl.UInt8,  # Nombre de personnes du ménage
    "NCOUPLES": pl.UInt8,  # Nombre de couples dans le ménage
    "NENFANTS": pl.UInt8,  # Nombre d'enfants dans le ménage
    "NACTIFS": pl.UInt8,  # Nombre d'actifs dans le ménage
    "NENFACT": pl.UInt8,  # Nombre d'enfants actifs dans le ménage
    "TYPMEN5": pl.UInt8,  # Type de ménage au sens du TCM
    "TYPMEN15": pl.UInt8,  # Type de ménage détaillé au sens du TCM
    "PRPERM": pl.UInt8,  # Permanence de la personne de référence
    "PRAN": pl.UInt8,  # Principal apporteur de ressources sur l'année (dans/hors ménage)
    "NPGREF": pl.UInt8,  # Nombre de personnes du groupe de référence
    "PREF": pl.UInt8,  # Numéro d'ordre de la personne de référence (PR)
    "SEXEPR": pl.UInt8,  # Sexe de la PR
    "AGEPR": pl.UInt8,  # Age de la PR au moment de l'enquête
    "AGPR": pl.UInt8,  # Age de la PR au 31 décembre de l'année de l'enquête
    "NAIS7PR": pl.UInt8,  # Lieu de naissance de la PR (code regroupé)
    "COUPLEPR": pl.UInt8,  # Vie en couple de la PR
    "SITUAPR": pl.UInt8,  # Situation de la PR vis-Ã -vis du travail
    "CS42PR": pl.UInt8,  # Catégorie socioprofessionnelle détaillée de la PR
    "CS24PR": pl.UInt8,  # Catégorie socioprofessionnelle regroupée de la PR
    "CODCSPR": pl.UInt8,  # Catégorie socio-professionnelle (CS) de la PR en activité
    "NATIO7PR": pl.UInt8,  # Nationalité de la PR (code regroupé)
    "DIPDETPR": pl.UInt8,  # Diplôme le plus élevé de la PR (code regroupé)
    "CSCJDCD": pl.UInt8,  # Catégorie socioprofessionnelle du conjoint décédé de la PR
    "PCONJ": pl.UInt8,  # Numéro d'ordre du conjoint de la personne de référence (PR)
    "SEXECJ": pl.UInt8,  # Sexe du conjoint de la PR
    "AGECJ": pl.UInt8,  # Age du conjoint de la PR au moment de l'enquête
    "AGCJ": pl.UInt8,  # Age du conjoint de la PR au 31 décembre de l'année de l'enquête
    "NAIS7CJ": pl.UInt8,  # Lieu de naissance du conjoint de la PR (code regroupé)
    "SITUACJ": pl.UInt8,  # Situation du conjoint de la PR vis-à-vis du travail
    "CS42CJ": pl.UInt8,  # Catégorie socioprofessionnelle détaillée du conjoint de la PR
    "CS24CJ": pl.UInt8,  # Catégorie socioprofessionnelle regroupée du conjoint de la PR
    "CODCSCJ": pl.UInt8,  # Catégorie socio-professionnelle (CS) du conjoint de la PR en activité
    "NATIO7CJ": pl.UInt8,  # Nationalité du conjoint de la PR (code regroupé)
    "DIPDETCJ": pl.UInt8,  # Diplôme le plus élevé du conjoint de la PR (code regroupé)
    "TYPLOGIND": pl.UInt8,  # Type de logement indépendant
    "CATLOGA": pl.UInt8,  # Catégorie du logement au sens du recensement
    "CATLOGB": pl.UInt8,  # Catégorie du logement au sens du TCM
    "NBANNLOG": pl.UInt8,  # Nombre d'années dans le logement pour le ménage
    "STOC": pl.UInt8,  # Statut d'occupation
    "STOCP": pl.UInt8,  # Statut d'occupation (propriétaire)
    "CATLOGAC": pl.UInt8,  # Catégorie du logement au sens du recensement déclarée par le ménage
    "EMMENAG": pl.UInt16,  # Année d'emménagement
    "PROPRI": pl.UInt8,  # Propriétaire du logement
    "NRH": pl.UInt8,  # Nombre de résidences habituelles du ménage
    "NRHC": pl.UInt8,  # Nombre de résidences habituelles communes du ménage
    "NCONTAML": pl.UInt8,  # Nombre de contacts possibles du ménage dans les logements
    "ENFHORS": pl.UInt8,  # Existence d'enfants hors domicile
    "NENFHORS": pl.UInt8,  # Nombre d'enfants hors domicile
    "HANDIC1E": pl.UInt8,  # Existence de personnes handicapées ou gênées dans le ménage
    "NHANDIC": pl.UInt8,  # Nombre de personnes handicapées dans le ménage
    "NGENE": pl.UInt8,  # Nombre de personnes gênées dans le ménage
    "ACHARGE": pl.UInt8,  # Existence de personnes à charge
    "quartile_rev": pl.UInt8,  # Quartile de revenu consolidé
    "decile_rev": pl.UInt8,  # Décile de revenu consolidé
    "COEFFUC": pl.Float64,  # Somme des unités de consommation
    "quartile_rev_uc": pl.UInt8,  # Quartile de revenu par UC consolidé
    "decile_rev_uc": pl.UInt8,  # Décile de revenu par UC consolidé
    "CSMEN": pl.UInt8,  # Catégorie socioprofessionnelle du ménage
    "DEP_RES": pl.String,  # Département de résidence
    "NUTS_res": pl.String,  # Code NUTS de la commune de résidence
    "REG_res": pl.String,  # Région de la commune de résidence
    "oldREG_res": pl.String,  # Ancienne région de la commune de résidence
    "lqpv": pl.UInt8,  # Le ménage est dans un QPV
    "TUU2017_RES": pl.UInt8,  # Tranche d'unité urbaine de la commune de résidense
    "STATUTCOM_UU_RES": pl.String,  # Statut de la commune de résidense
    "TYPE_UU_RES": pl.UInt8,  # Type de l'unité urbaine de la commune de résidense
    "TAA2017_RES": pl.UInt8,  # Tranche d'aire d'attraction des villes 2020 de la commune de résidense
    "CATCOM_AA_RES": pl.UInt8,  # Catégorie de la commune de résidense dans l'aire d'attraction des villes 2020
    "DENSITECOM_RES": pl.UInt8,  # Degré de densité de la commune de résidense
    "pop_10min_pieton_tram_metro_res": pl.UInt8,  # Part de la population de la commune du domicile à moins de 10 min à pied d'une station de métro ou de tram
    "pop_10min_pieton_train_res": pl.UInt8,  # Part de la population de la commune du domicile à moins de 10 min à pied d'une station de train (TER, RER et grande ligne)
    "pop_10min_voiture_tram_metro_res": pl.UInt8,  # Part de la population de la commune du domicile à moins de 10 min en voiture d'une station de métro ou de tram
    "pop_10min_voiture_train_res": pl.UInt8,  # Part de la population de la commune du domicile à moins de 10 min en voiture d'une station de train (TER, RER et grande ligne)
    "dist_res_metro": pl.String,  # Distance à vol d'oiseau du domicile à la station la plus proche de métro
    "dist_res_tram": pl.String,  # Distance à vol d'oiseau du domicile à la station la plus proche de tramway
    "dist_res_train": pl.String,  # Distance à vol d'oiseau du domicile à la gare la plus proche
    "dist_res_tgv": pl.String,  # Distance à vol d'oiseau du domicile à la gare TGV la plus proche
    "classement_littoral_res": pl.String,  # Statut de la commune du domicile par rapport à la loi littoral
    "classement_montagne_res": pl.String,  # Statut de la commune du domicile par rapport à la loi montagne
}

SCHEMA2 = {
    "IDENT_MEN": pl.String,  # Identifiant ménage
    "pond_menC": pl.Float64,  # Poids ménage
    "JNBVEH": pl.UInt8,  # Nb voitures particulières, VUL et camping-cars à disposition du ménage
    "JNBVHS": pl.UInt8,  # Possession de véh. hors d'usage (détention carte grise) parmi ceux à disposition
    "JNBVPHS": pl.UInt8,  # Nb voitures hors d'usage
    "JNBCCHS": pl.UInt8,  # Nb camping-cars hors d'usage
    "JNBVULHS": pl.UInt8,  # Nb VUL hors d'usage
    "JNBMOTO": pl.UInt8,  # Nb motos, scooters y.c. à trois roues (> 50 cm3) à disposition du ménage
    "JNBCYCLO": pl.UInt8,  # Nb cyclomoteurs (<= 50 cm3) à disposition du ménage
    "JNBAUTVEH": pl.UInt8,  # Nb voiturettes et quads à disposition du ménage
    "JNBVELOAD": pl.UInt8,  # Nb vélos d'adulte (y.c. à assistance électrique) à disposition du ménage
    "JNBVELOENF": pl.UInt8,  # Nb vélos d'enfant à disposition du ménage
    "JUTILMOTO": pl.UInt8,  # Nb motos ou scooters +50 cm3 utilisés (parmi dispo) 12 dern. mois
    "JUTILCYCLO": pl.UInt8,  # Nb cyclomoteurs -50 cm3 utilisés (parmi dispo) 12 dern. mois
    "JUTILAUTVEH": pl.UInt8,  # Nb voiturettes et quads utilisés (parmi dispo) 12 dern. mois
    "JUTILVELOAD": pl.UInt8,  # Nb vélos d'adulte utilisés (parmi dispo) 12 dern. mois
    "JUTILVELOENF": pl.UInt8,  # Nb vélos d'enfant utilisés (parmi dispo) 12 dern. mois
    "JVOLVELO": pl.UInt8,  # Le ménage s'est fait voler un vélo au cours des 12 derniers mois
    "JPLUSVELO": pl.UInt8,  # Un membre du ménage a renoncé à utiliser un vélo après le vol
    "JNBKVM": pl.UInt8,  # Nb voit. particulières, VUL et camping-cars du ménage en état de marche
    "JUTIL2RM": pl.UInt8,  # Nb deux-roues motorisés utilisés 12 dern. mois
    "BLOGDIST": pl.UInt8,  # Distance du domicile : arrêt bus, tram, métro
}

# Housing status is read from variable STOC (multiplied by 10) and variable PROPRI (with 0 for null
# values).
HOUSING_STATUS_MAP = {
    10: "owner:ongoing_loan",  # STOC = 1 & PROPRI = null
    20: "owner:fully_repaid",  # STOC = 2 & PROPRI = null
    30: "owner:usufructuary",  # STOC = 3 & PROPRI = null
    40: "tenant:unspecified",  # STOC = 4 & PROPRI = null
    41: "tenant:private",  # STOC = 4 & PROPRI = 1
    42: "tenant:public_housing",  # STOC = 4 & PROPRI = 2
    43: "tenant:unspecified",  # STOC = 4 & PROPRI = 3
    44: "tenant:unspecified",  # STOC = 4 & PROPRI = 4
    45: "tenant:private",  # STOC = 4 & PROPRI = 5
    46: "tenant:private",  # STOC = 4 & PROPRI = 6
    47: "tenant:unspecified",  # STOC = 4 & PROPRI = 7
    50: "rent_free",  # STOC = 5 & PROPRI = null
    51: "rent_free",  # STOC = 5 & PROPRI = 1
    52: "rent_free",  # STOC = 5 & PROPRI = 2
    53: "rent_free",  # STOC = 5 & PROPRI = 3
    54: "rent_free",  # STOC = 5 & PROPRI = 4
    55: "rent_free",  # STOC = 5 & PROPRI = 5
    56: "rent_free",  # STOC = 5 & PROPRI = 6
    57: "rent_free",  # STOC = 5 & PROPRI = 7
}


def scan_households(filename1: str, filename2: str):
    lf = pl.scan_csv(
        filename1, separator=",", encoding="utf8-lossy", schema_overrides=SCHEMA1
    ).join(
        pl.scan_csv(
            filename2,
            separator=";",
            encoding="utf8-lossy",
            schema_overrides=SCHEMA2,
            null_values=["-1"],
        ),
        left_on="ident_men",
        right_on="IDENT_MEN",
        coalesce=False,
    )
    return lf


def standardize_households(filename1: str, filename2: str):
    lf = scan_households(filename1, filename2)
    lf = lf.rename(
        {
            "pond_menC": "sample_weight",
            "DEP_RES": "home_dep",
            "NPERS": "nb_persons",
            "JNBVEH": "nb_cars",
        }
    )
    lf = lf.with_columns(
        original_household_id=pl.struct("IDENT_MEN"),
        survey_method=pl.lit("face_to_face"),
        housing_status=(10 * pl.col("STOC") + pl.col("PROPRI").fill_null(0)).replace_strict(
            HOUSING_STATUS_MAP
        ),
        # There should be no null values so we can safely sum the two columns without facing null
        # propagation.
        nb_motorcycles=pl.col("JNBMOTO") + pl.col("JNBCYCLO"),
        nb_bicycles=pl.col("JNBVELOAD") + pl.col("JNBVELOENF"),
    )
    lf = clean(lf)
    return lf

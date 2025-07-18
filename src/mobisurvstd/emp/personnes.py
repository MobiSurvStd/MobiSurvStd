import polars as pl

from mobisurvstd.common.persons import clean

SCHEMA1 = {
    "ident_ind": pl.String,  # Identifiant de l'individu dans le logement
    "ident_men": pl.String,  # Identifiant du ménage
    "ident_log": pl.String,  # Identifiant du logement
    "NOI": pl.String,  # Numéro d'ordre de l'individu dans le logement
    "SEXE": pl.UInt8,  # Sexe
    "tr_age": pl.String,  # Age au moment de l'enquête
    "LIEN_01": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 1
    "LIEN_02": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 2
    "LIEN_03": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 3
    "LIEN_04": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 4
    "LIEN_05": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 5
    "LIEN_06": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 6
    "LIEN_07": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 7
    "LIEN_08": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 8
    "LIEN_09": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 9
    "LIEN_10": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 10
}

SCHEMA2 = {
    "ident_ind": pl.String,  # Identifiant de l'individu dans le logement
    "ident_men": pl.String,  # Identifiant du ménage
    "ident_log": pl.String,  # Identifiant du logement
    "NOI": pl.UInt8,  # Numéro d'ordre de l'individu dans le logement
    "BS": pl.UInt8,  # Numéro de ménage dans le logement
    "HABRP": pl.UInt8,  # Habitant du logement au sens du recensement
    "vague_enq": pl.UInt8,  # Numéro de vague
    "SEXE": pl.UInt8,  # Sexe
    "ANAIS": pl.UInt32,  # Année de naissance
    "AGE": pl.UInt8,  # Age au moment de l'enquête
    "AGEJANV": pl.UInt8,  # Age au 1er janvier de l'année de l'enquête
    "AG": pl.UInt8,  # Age au 31 décembre de l'année de l'enquête
    "AGEQ": pl.UInt8,  # Age quinquennal au moment de l'enquête
    "AGQ": pl.UInt8,  # Age quinquennal au 31 décembre de l'année de l'enquête
    "AGE6": pl.UInt8,  # Age au moment de l'enquête (6 postes)
    "AG6": pl.UInt8,  # Age au 31 décembre de l'année de l'enquête (6 postes)
    "LNAIS": pl.UInt8,  # Indicateur de lieu de naissance
    "NAIS7": pl.UInt8,  # Code regroupé du lieu de naissance
    "ANARRIV": pl.UInt16,  # Année d'installation en France
    "INATIO": pl.UInt8,  # Indicateur de nationalité
    "NATIO7": pl.UInt8,  # Nationalité regroupée
    "COUPLE": pl.UInt8,  # Vie en couple
    "COUPLRP": pl.UInt8,  # Vie en couple au sens du RP
    "CONJOINT": pl.UInt8,  # Numéro d'ordre du conjoint dans le logement
    "ETAMATRI": pl.UInt8,  # Etat matrimonial légal
    "PACS": pl.UInt8,  # Existence d'un PACS
    "LIENTYP": pl.UInt8,  # Nature du lien
    "LIENPERS": pl.UInt8,  # Numéro d'ordre de la personne du lien dans le logement
    "ENFANT": pl.UInt8,  # Enfant du ménage
    "ENFRP": pl.UInt8,  # Enfant au sens du recensement
    "LIEN_01": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 1
    "LIEN_02": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 2
    "LIEN_03": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 3
    "LIEN_04": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 4
    "LIEN_05": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 5
    "LIEN_06": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 6
    "LIEN_07": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 7
    "LIEN_08": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 8
    "LIEN_09": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 9
    "LIEN_10": pl.UInt8,  # Lien de chaque habitant du logement avec l'individu 10
    "AIDE1E": pl.UInt8,  # Personne aidée dans le logement
    "IDENTAID": pl.UInt8,  # Identifiant de la personne aidée
    "TYPOLOG": pl.UInt8,  # Type d'occupation du logement
    "JOURAN": pl.UInt8,  # Nombre de jours d'occupation/an du logement
    "JOURSEM": pl.UInt8,  # Nombre de jours d'occupation/semaine du logement
    "MOISAN": pl.UInt8,  # Nombre de mois d'occupation dans l'année du logement
    "JOUR2AN": pl.UInt8,  # Nombre de jours d'occupation depuis un an du logement
    "DOLOG": pl.UInt8,  # Durée d'occupation du logement
    "IDOLOG": pl.UInt8,  # Indicateur de durée d'occupation du logement
    "IPROPLOC": pl.UInt8,  # Indicateur d'occupant principal
    "AUTLOG": pl.UInt8,  # Existence d'autres logements
    "LOGCOL": pl.UInt8,  # Existence d'un logement collectif
    "TYPLOGCO": pl.UInt8,  # Type de logement collectif
    "TYPLOGCO_A": pl.UInt8,  # Caserne, camp
    "TYPLOGCO_B": pl.UInt8,  # Internat
    "TYPLOGCO_C": pl.UInt8,  # Résidence universitaire
    "TYPLOGCO_D": pl.UInt8,  # Foyer de jeunes travailleurs
    "TYPLOGCO_E": pl.UInt8,  # Etablissement pénitentiaire
    "TYPLOGCO_F": pl.UInt8,  # Etablissement de soins
    "TYPLOGCO_G": pl.UInt8,  # Maison de retraite, hospice
    "TYPLOGCO_H": pl.UInt8,  # Chantier temporaire de travaux publics
    "LOGIND": pl.UInt8,  # Existence d'un logement individuel
    "NAUTLOG_IND": pl.UInt8,  # Nombre d'autres logements
    "NOLOG1_IND": pl.UInt8,  # Numéro d'ordre du logement
    "TYPOLOGD1": pl.UInt8,  # Type d'occupation du logement (autre logement)
    "JOURAND1": pl.UInt16,  # Nombre de jours d'occupation/an dans l'autre logement
    "JOURSEMD1": pl.UInt8,  # Nombre de jours d'occupation/semaine dans l'autre logement
    "MOISAND1": pl.UInt8,  # Nombre de mois d'occupation dans l'année dans l'autre logement
    "JOUR2AND1": pl.UInt16,  # Nombre de jours d'occupation depuis un an dans l'autre logement
    "DOLOGD1": pl.Float64,  # Durée d'occupation dans l'autre logement
    "NOLOG2_IND": pl.UInt8,  # Numéro d'ordre du logement
    "TYPOLOGD2": pl.UInt8,  # Type d'occupation du logement (autre logement)
    "JOURAND2": pl.UInt16,  # Nombre de jours d'occupation/an dans l'autre logement
    "JOURSEMD2": pl.UInt8,  # Nombre de jours d'occupation/semaine dans l'autre logement
    "MOISAND2": pl.UInt8,  # Nombre de mois d'occupation dans l'année dans l'autre logement
    "JOUR2AND2": pl.UInt16,  # Nombre de jours d'occupation depuis un an dans l'autre logement
    "DOLOGD2": pl.Float64,  # Durée d'occupation dans l'autre logement
    "HANDICAP": pl.UInt8,  # Indicateur d'handicap
    "IGREF": pl.UInt8,  # Indicateur d'appartenance au groupe de référence du ménage
    "PRACT": pl.UInt8,  # Indicateur de principal apporteur de ressources actuel du ménage
    "IPRAN": pl.UInt8,  # Indicateur de principal apporteur de ressources du ménage sur l'année
    "LIENPREF": pl.UInt8,  # Lien avec la personne de référence du ménage
    "LIENPRRP": pl.UInt8,  # Lien avec la personne de référence au sens du recensement
    "FAMPRINC": pl.UInt8,  # Indicateur d'appartenance à la famille principale
    "CS42": pl.UInt8,  # Catégorie socioprofessionnelle détaillée
    "CS24": pl.UInt8,  # Catégorie socioprofessionnelle regroupée
    "SITUA": pl.UInt8,  # Situation principale vis-à-vis du travail
    "ACTIF": pl.UInt8,  # Actif
    "ACTOCCUP": pl.UInt8,  # Actif occupé
    "ACTOCCUPE": pl.UInt8,  # Actif occupé, déterminée pour Conditions De Travail
    "TRAVAIL": pl.UInt8,  # Existence d'une activité productive rémunérée
    "TRAVAILNR": pl.UInt8,  # Existence d'une activité productive non rémunérée
    "ACTIVANTE": pl.UInt8,  # Activité antérieure
    "STATUT": pl.UInt8,  # Statut dans l'emploi principal
    "RECHEMPLOI": pl.UInt8,  # Recherche d'un (autre) emploi
    "CS_ACT": pl.UInt8,  # Code final de la CS actuelle
    "TYPEMPLOI": pl.UInt8,  # Type d'emploi
    "TITULAIREFP": pl.UInt8,  # Titulaire de la fonction publique
    "TEMPTRAV": pl.UInt8,  # Temps de travail (partiel ou complet)
    "SUPERVISION": pl.UInt8,  # Supervision d'autres salariés
    "CLASSIF": pl.UInt8,  # Classification dans l'emploi
    "FONCTION": pl.UInt8,  # Fonction principale
    "SALARIES": pl.UInt8,  # Nombre de salariés
    "STATUTANTE": pl.UInt8,  # Statut dans le dernier emploi
    "SUPERVISANTE": pl.UInt8,  # Supervision d'autres salariés dans le dernier emploi
    "CLASSIFANTE": pl.UInt8,  # Classification dans le dernier emploi
    "CS_ANTE": pl.UInt8,  # Code final de la CS antérieure
    "STATUTCD": pl.UInt8,  # Statut dans l'emploi du conjoint décédé
    "CLASSIFCD": pl.UInt8,  # Classification dans l'emploi du conjoint décédé
    "CS_DCD": pl.UInt8,  # Code final de la CS du conjoint décédé
    "DIP11": pl.UInt8,  # diplôme le plus élevé agrégé en 11 postes
    "DDIPL": pl.UInt8,  # diplôme le plus élevé
    "MER1E": pl.UInt8,  # Présence de la mère dans le logement
    "MER2E": pl.UInt8,  # Numéro d'ordre de la mère dans le logement
    "PER1E": pl.UInt8,  # Présence du père dans le logement
    "PER2E": pl.UInt8,  # Numéro d'ordre du père dans le logement
    "APART": pl.UInt8,  # Existence de budgets séparés
    "TYPFAM": pl.UInt8,  # Type de famille avec enfant
}

SCHEMA3 = {
    "IDENT_MEN": pl.String,  # Identifiant ménage
    "IDENT_IND": pl.String,  # Identifiant individu
    "NOIK": pl.UInt8,  # Numéro du Kish dans le ménage
    "pond_indC": pl.Float64,  # Poids individu Kish
    "TRAVAILLE": pl.UInt8,  # A un emploi actuellement
    "ETUDIE": pl.UInt8,  # Etudes en cours
    "BTRAVFIX": pl.UInt8,  # Type de lieu de travail
    "BTRAVTEL": pl.UInt8,  # Pratique du télétravail
    "BTRAVNBJ": pl.UInt8,  # Nb de jours/semaine déplacement lieu de travail
    "BTRAVEMPL": pl.UInt8,  # Participation de l'employeur frais de transports
    "BTRAVELEC_FLAG": pl.Int8,  # Variable drapeau du SetOf BTRAVELEC
    "BTRAVELEC_A": pl.UInt8,  # Existence prise électrique ordinaire près du lieu de travail
    "BTRAVELEC_B": pl.UInt8,  # Existence prise spéciale de recharge électrique près du lieu de travail
    "BPERMIS": pl.UInt8,  # Possession du permis voiture (permis B)
    "BCARTABON": pl.UInt8,  # Possession de cartes d'abonnement, réduction - déplacements TC
    "BTYP1CART": pl.String,  # Type de la carte de transport 1
    "BTYP1RES_FLAG": pl.UInt8,  # Variable drapeau du SetOf BTYP1RES
    "BTYP1RES_A": pl.UInt8,  # Carte 1 valide sur réseau urbain, suburbain
    "BTYP1RES_B": pl.UInt8,  # Carte 1 valide sur réseau cars interurbains, ruraux
    "BTYP1RES_C": pl.UInt8,  # Carte 1 valide sur réseau SNCF
    "BTYP1RES_D": pl.UInt8,  # Carte 1 valide sur réseau SNCF et réseau urbain
    "BTYP1RES_E": pl.UInt8,  # Carte 1 valide sur réseau urbain, cars interurbains
    "BTYP1RES_F": pl.UInt8,  # Carte 1 valide sur réseau aérien
    "BTYP1RES_G": pl.UInt8,  # Carte 1 valide sur réseau maritime
    "BTYP2CART": pl.String,  # Type de la carte de transport 2
    "BTYP2RES_FLAG": pl.UInt8,  # Variable drapeau du SetOf BTYP2RES
    "BTYP2RES_A": pl.UInt8,  # Carte 2 valide sur réseau urbain, suburbain
    "BTYP2RES_B": pl.UInt8,  # Carte 2 valide sur réseau cars interurbains, ruraux
    "BTYP2RES_C": pl.UInt8,  # Carte 2 valide sur réseau SNCF
    "BTYP2RES_D": pl.UInt8,  # Carte 2 valide sur réseau SNCF et réseau urbain
    "BTYP2RES_E": pl.UInt8,  # Carte 2 valide sur réseau urbain, cars interurbains
    "BTYP2RES_F": pl.UInt8,  # Carte 2 valide sur réseau aérien
    "BTYP2RES_G": pl.UInt8,  # Carte 2 valide sur réseau maritime
    "BTYP3CART": pl.String,  # Type de la carte de transport 3
    "BTYP3RES_FLAG": pl.UInt8,  # Variable drapeau du SetOf BTYP3RES
    "BTYP3RES_A": pl.UInt8,  # Carte 3 valide sur réseau urbain, suburbain
    "BTYP3RES_B": pl.UInt8,  # Carte 3 valide sur réseau cars interurbains, ruraux
    "BTYP3RES_C": pl.UInt8,  # Carte 3 valide sur réseau SNCF
    "BTYP3RES_D": pl.UInt8,  # Carte 3 valide sur réseau SNCF et réseau urbain
    "BTYP3RES_E": pl.UInt8,  # Carte 3 valide sur réseau urbain, cars interurbains
    "BTYP3RES_F": pl.UInt8,  # Carte 3 valide sur réseau aérien
    "BTYP3RES_G": pl.UInt8,  # Carte 3 valide sur réseau maritime
    "BTYP4CART": pl.String,  # Type de la carte de transport 4
    "BTYP4RES_FLAG": pl.UInt8,  # Variable drapeau du SetOf BTYP4RES
    "BTYP4RES_A": pl.UInt8,  # Carte 4 valide sur réseau urbain, suburbain
    "BTYP4RES_B": pl.UInt8,  # Carte 4 valide sur réseau cars interurbains, ruraux
    "BTYP4RES_C": pl.UInt8,  # Carte 4 valide sur réseau SNCF
    "BTYP4RES_D": pl.UInt8,  # Carte 4 valide sur réseau SNCF et réseau urbain
    "BTYP4RES_E": pl.UInt8,  # Carte 4 valide sur réseau urbain, cars interurbains
    "BTYP4RES_F": pl.UInt8,  # Carte 4 valide sur réseau aérien
    "BTYP4RES_G": pl.UInt8,  # Carte 4 valide sur réseau maritime
    "BABONNVLS": pl.UInt8,  # Possession d'un abonnement VLS ou location vélos de courte durée
    "BNBVLS": pl.UInt8,  # Nb d'utilisation d'un VLS ou d'un vélo location de courte durée sur les 7 derniers jours
    "BCARTPEAGE": pl.UInt8,  # Possession d'un abonnement pour autoroute ou péage
    "BCARTPTYPE_FLAG": pl.UInt8,  # Variable drapeau du SetOf BCARTPTYPE
    "BCARTPTYPE_A": pl.UInt8,  # Abonnement national (toutes autoroutes France)
    "BCARTPTYPE_B": pl.UInt8,  # Abonnement régional (certaines autoroutes France)
    "BCARTPTYPE_C": pl.UInt8,  # Abonnement urbain, périurbain ou local (section précise)
    "BCARTPTYPE_D": pl.UInt8,  # Abonnement ouvrage particulier (tunnel, viaduc)
    "BCARTPTYPE_E": pl.UInt8,  # Abonnement pays étranger
    "BCARTPTYPE_F": pl.UInt8,  # Autre abonnement
    "BABONNAUTOP": pl.UInt8,  # Possession d'un abonnement pour un service d'autopartage
    "BAUTOPTYP": pl.UInt8,  # Type du service d'autopartage
    "BNBAUTOP": pl.UInt8,  # Nb d'utilisation du service d'autopartage au cours de la dernière semaine
    "GAGENE": pl.UInt8,  # Gêne physique dans déplacements hors du domicile
    "GADIFFI_FLAG": pl.UInt8,  # Variable drapeau du SetOf GADFIFI
    "GADIFFI_A": pl.UInt8,  # Gêne : pb santé longue durée
    "GADIFFI_B": pl.UInt8,  # Gêne : pb santé temporaire, grossesse
    "GADIFFI_C": pl.UInt8,  # Gêne : difficultés en langue française
    "GADIFFI_D": pl.UInt8,  # Gêne : âge
    "GADIFFI_E": pl.UInt8,  # Gêne : autre raison
    "GADIFFI_F": pl.UInt8,  # Refus de réponse sur raison de gêne dans déplacements
    "GAGENE1CIRC": pl.UInt8,  # Circonstance gêne : marcher qqs centaines de mètres
    "GAGENE2CIRC": pl.UInt8,  # Circonstance gêne : monter ou descendre des marches
    "GAGENE3CIRC": pl.UInt8,  # Circonstance gêne : accéder à certains lieux en fauteuil roulant
    "GAGENE4CIRC": pl.UInt8,  # Circonstance gêne : tenir debout sans appui
    "GAGENE5CIRC": pl.UInt8,  # Circonstance gêne : ouvrir portes d'entrée, de sortie
    "GAGENE6CIRC": pl.UInt8,  # Circonstance gêne : appuyer sur des boutons d'appel
    "GAGENE7CIRC": pl.UInt8,  # Circonstance gêne : rouler à vélo ou en moto
    "GAGENE8CIRC": pl.UInt8,  # Circonstance gêne : monter et descendre d'une voiture
    "GAGENE9CIRC": pl.UInt8,  # Circonstance gêne : rester assis pendant long trajet
    "GAGENE10CIRC": pl.UInt8,  # Circonstance gêne : conduire et garder la maîtrise du véhicule
    "GAGENE11CIRC": pl.UInt8,  # Circonstance gêne : accéder à station, quai
    "GAGENE12CIRC": pl.UInt8,  # Circonstance gêne : demander renseignement sur itinéraire
    "GAGENE13CIRC": pl.UInt8,  # Circonstance gêne : utiliser billetterie automatique
    "GAGENE14CIRC": pl.UInt8,  # Circonstance gêne : lire un plan, un horaire
    "GAGENE15CIRC": pl.UInt8,  # Circonstance gêne : composter billet
    "GAGENE16CIRC": pl.UInt8,  # Circonstance gêne : se diriger dans gare, station
    "IMMODEP_FLAG": pl.Int8,  # Variable drapeau du SetOf IMMODEP
    "IMMODEP_A": pl.UInt8,  # Immobilité jour J-1 avant l'enquête
    "IMMODEP_B": pl.UInt8,  # Immobilité jour J-2 avant l'enquête
    "IMMODEP_C": pl.UInt8,  # Immobilité jour J-3 avant l'enquête
    "IMMODEP_D": pl.UInt8,  # Immobilité jour J-4 avant l'enquête
    "IMMODEP_E": pl.UInt8,  # Immobilité jour J-5 avant l'enquête
    "IMMODEP_F": pl.UInt8,  # Immobilité jour J-6 avant l'enquête
    "IMMODEP_G": pl.UInt8,  # Immobilité jour J-7 avant l'enquête
    "MIMMOSAM": pl.UInt8,  # Immobilité samedi
    "MIMMODIM": pl.UInt8,  # Immobilité dimanche
    "MIMMOSEM": pl.UInt8,  # Immobilité depuis 1 semaine
    "MDATE_jour": pl.String,  # Jour de la semaine du jour tiré (de mobilité locale)
    "MDATE_mois": pl.String,  # Mois du jour tiré (de mobilité locale)
    "MDATE_delai": pl.UInt8,  # Délai (en jours) entre la date d'enquête et le jour tiré (de mobilité locale)
    "MRAISIMMOJOUV": pl.UInt8,  # Raison immobilité depuis une semaine
    "MRAISIMMOSAM_FLAG": pl.UInt8,  # Variable drapeau du SetOf MRAISIMMOSAM
    "MRAISIMMOSAM_A": pl.UInt8,  # Raison immobilité samedi : pas besoin
    "MRAISIMMOSAM_B": pl.UInt8,  # Raison immobilité samedi : trop jeune pour se déplacer seul
    "MRAISIMMOSAM_C": pl.UInt8,  # Raison immobilité samedi : incapacité provisoire
    "MRAISIMMOSAM_D": pl.UInt8,  # Raison immobilité samedi : incapacité permanente
    "MRAISIMMOSAM_E": pl.UInt8,  # Raison immobilité samedi : nécessité rester sur place
    "MRAISIMMOSAM_F": pl.UInt8,  # Raison immobilité samedi : pas de véhicule
    "MRAISIMMOSAM_G": pl.UInt8,  # Raison immobilité samedi : véhicule en panne
    "MRAISIMMOSAM_H": pl.UInt8,  # Raison immobilité samedi : aucune personne pour conduire
    "MRAISIMMOSAM_I": pl.UInt8,  # Raison immobilité samedi : mauvaises conditions météo
    "MRAISIMMOSAM_J": pl.UInt8,  # Raison immobilité samedi : autre raison
    "MRAISIMMODIM_FLAG": pl.UInt8,  # Variable drapeau du SetOf MRAISIMMODIM
    "MRAISIMMODIM_A": pl.UInt8,  # Raison immobilité dimanche : pas besoin
    "MRAISIMMODIM_B": pl.UInt8,  # Raison immobilité dimanche : trop jeune pour se déplacer seul
    "MRAISIMMODIM_C": pl.UInt8,  # Raison immobilité dimanche : incapacité provisoire
    "MRAISIMMODIM_D": pl.UInt8,  # Raison immobilité dimanche : incapacité permanente
    "MRAISIMMODIM_E": pl.UInt8,  # Raison immobilité dimanche : nécessité rester sur place
    "MRAISIMMODIM_F": pl.UInt8,  # Raison immobilité dimanche : pas de véhicule
    "MRAISIMMODIM_G": pl.UInt8,  # Raison immobilité dimanche : véhicule en panne
    "MRAISIMMODIM_H": pl.UInt8,  # Raison immobilité dimanche : aucune personne pour conduire
    "MRAISIMMODIM_I": pl.UInt8,  # Raison immobilité dimanche : mauvaises conditions météo
    "MRAISIMMODIM_J": pl.UInt8,  # Raison immobilité dimanche : autre raison
    "BTCSATISF": pl.UInt8,  # Opinion sur offre de transports collectifs proche du domicile
    "BTCRAISINSATISF_FLAG": pl.UInt8,  # Variable drapeau du SetOf BTCRAISINSATISF
    "BTCRAISINSATISF_A": pl.UInt8,  # Raison insatisfaction TC : arrets trop éloignés du domicile
    "BTCRAISINSATISF_B": pl.UInt8,  # Raison insatisfaction TC : horaires/frequence pas adaptés
    "BTCRAISINSATISF_C": pl.UInt8,  # Raison insatisfaction TC : pas ponctuels
    "BTCRAISINSATISF_D": pl.UInt8,  # Raison insatisfaction TC : tarifs trop élevés
    "BTCRAISINSATISF_E": pl.UInt8,  # Raison insatisfaction TC : pas accessibles
    "BTCRAISINSATISF_F": pl.UInt8,  # Raison insatisfaction TC : conditions transport pas confortables
    "BTCRAISINSATISF_G": pl.UInt8,  # Raison insatisfaction TC : sentiment d'insécurité
    "BTCRAISINSATISF_H": pl.UInt8,  # Raison insatisfaction TC : autre raison
    "BCOVLDF": pl.UInt8,  # Covoiturage conducteur LD avec contrep. financière 3 dern. mois
    "BCV1MOT_FLAG": pl.UInt8,  # Variable drapeau du SetOf BCV1MOT
    "BCV1MOT_A": pl.UInt8,  # Motif covoit. cond. LD avec contrep. fin. : travail ou études
    "BCV1MOT_B": pl.UInt8,  # Motif covoit. cond. LD avec contrep. fin. : loisirs
    "BCV1MOT_C": pl.UInt8,  # Motif covoit. cond. LD avec contrep. fin. : autre
    "BCV1REL_FLAG": pl.UInt8,  # Variable drapeau du SetOf BCV1REL
    "BCV1REL_A": pl.UInt8,  # Mise en relation avec covoiturés- trajets cond. avec contrep. fin. (3 mois) : site internet ou application smartphone
    "BCV1REL_B": pl.UInt8,  # Mise en relation avec covoiturés- trajets cond. avec contrep. fin. (3 mois) : travail (collègues)
    "BCV1REL_C": pl.UInt8,  # Mise en relation avec covoiturés- trajets cond. avec contrep. fin. (3 mois) : relation personnelle
    "BCV1REL_D": pl.UInt8,  # Mise en relation avec covoiturés- trajets cond. avec contrep. fin. (3 mois) : autostop
    "BCV1NB": pl.UInt8,  # Nb de covoit. cond. LD avec contrep. fin. au cours des 3 dern. mois
    "BCOVLDNF": pl.UInt8,  # Covoiturage conducteur LD sans contrep. financière 3 dern. mois
    "BCV2MOT_FLAG": pl.UInt8,  # Variable drapeau du SetOf BCV2MOT
    "BCV2MOT_A": pl.UInt8,  # Motif covoit. cond. LD sans contrep. fin. : travail ou études
    "BCV2MOT_B": pl.UInt8,  # Motif covoit. cond. LD sans contrep. fin. : loisirs
    "BCV2MOT_C": pl.UInt8,  # Motif covoit. cond. LD sans contrep. fin. : autre
    "BCV2REL_FLAG": pl.UInt8,  # Variable drapeau du SetOf BCV2REL
    "BCV2REL_A": pl.UInt8,  # Mise en relation avec covoiturés- trajets cond. sans contrep. fin. (3 mois) : site internet ou application smartphone
    "BCV2REL_B": pl.UInt8,  # Mise en relation avec covoiturés- trajets cond. sans contrep. fin. (3 mois) : travail (collègues)
    "BCV2REL_C": pl.UInt8,  # Mise en relation avec covoiturés- trajets cond. sans contrep. fin. (3 mois) : relation personnelle
    "BCV2REL_D": pl.UInt8,  # Mise en relation avec covoiturés- trajets cond. sans contrep. fin. (3 mois) : autostop
    "BCV2NB": pl.UInt16,  # Nb de covoit. cond. LD sans contrep. fin. au cours des 3 dern. mois
    "BCVTV": pl.UInt8,  # Covoiturage passager pour travail ou études 4 dern. semaines
    "BCVTVFQ": pl.UInt8,  # Fréquence de covoit. passager pour travail ou études (4 dern. sem)
    "BCVTVREL_FLAG": pl.UInt8,  # Variable drapeau du SetOf BCVTVREL
    "BCVTVREL_A": pl.UInt8,  # Mise en relation avec conduct. pour covoit. passager travail ou études (4 dern. sem.) : site internet ou application smartphone
    "BCVTVREL_B": pl.UInt8,  # Mise en relation avec conduct. pour covoit. passager travail ou études (4 dern. sem.) : travail (collègues)
    "BCVTVREL_C": pl.UInt8,  # Mise en relation avec conduct. pour covoit. passager travail ou études (4 dern. sem.) : relation personnelle
    "BCVTVREL_D": pl.UInt8,  # Mise en relation avec conduct. pour covoit. passager travail ou études (4 dern. sem.) : autostop
    "BCVTVFIN": pl.UInt8,  # Contrepartie financière covoiturage passager pour travail ou études
    "FCMMODIF_A": pl.UInt8,  # Annulation de projets de voyage LD au cours des 12 dern. mois
    "FCMMODIF_B": pl.UInt8,  # Modification de projets de voyage LD au cours des 12 dern. mois
    "FCMANURAIS_A": pl.UInt8,  # Raison annulat. projet de voy. (12 dern. mois) : suppression ou modificat. offre de transp.
    "FCMANURAIS_B": pl.UInt8,  # Raison annulat. projet de voy. (12 dern. mois) : pbs de sécurité
    "FCMANURAIS_C": pl.UInt8,  # Raison annulat. projet de voy. (12 dern. mois) : situat. financière
    "FCMANURAIS_D": pl.UInt8,  # Raison annulat. projet de voy. (12 dern. mois) : pbs personnels
    "FCMANURAIS_E": pl.UInt8,  # Raison annulat. projet de voy. (12 dern. mois) : autre raison
    "FCMANUOU_A": pl.UInt8,  # Annulation de voy. prévus en France métropolitaine (12 dern. mois)
    "FCMANUOU_B": pl.UInt8,  # Annulation de voy. prévus en France outre-mer (12 dern. mois)
    "FCMANUOU_C": pl.UInt8,  # Annulation de voy. prévus à l'étranger (12 dern. mois)
    "FCMMODRAIS_A": pl.UInt8,  # Raison modificat. projet de voy. (12 dern. mois) : suppression ou modificat. offre de transp.
    "FCMMODRAIS_B": pl.UInt8,  # Raison modificat. projet de voy. (12 dern. mois) : pbs de sécurité
    "FCMMODRAIS_C": pl.UInt8,  # Raison modificat. projet de voy. (12 dern. mois) : situat. financière
    "FCMMODRAIS_D": pl.UInt8,  # Raison modificat. projet de voy. (12 dern. mois) : pbs personnels
    "FCMMODRAIS_E": pl.UInt8,  # Raison modificat. projet de voy. (12 dern. mois) : autre raison
    "FCMMODQUOI_A": pl.UInt8,  # Modification projet de voy. : en le reportant
    "FCMMODQUOI_B": pl.UInt8,  # Modification de projet de voy. : en changeant d'itinéraire
    "FCMMODQUOI_C": pl.UInt8,  # Modification de projet de voy. : en changeant de moyen de transport
    "FCMMODMOYINI": pl.String,  # Moyen de transport initialement envisagé pour dernier voyage modifié
    "FCMMODMOYFIN": pl.String,  # Moyen de transport finalement retenu pour dernier voyage modifié
    # NOTE. These variables should probably not be used for `work_commute_euclidean_distance_km` and
    # `study_commute_euclidean_distance_km` because they are based on an observed trip (not on the
    # usual work / study location).
    "dist_ign_trav": pl.Float64,  # Distance routière domicile – travail (si au moins un déplacement recensé vers lieu de travail)
    "dist_vo_trav": pl.Float64,  # Distance VO domicile – travail (si au moins un déplacement recensé vers lieu de travail)
    "dist_ign_etude": pl.Float64,  # Distance routière domicile – étude (si au moins un déplacement recensé vers lieu d'étude)
    "dist_vo_etude": pl.Float64,  # Distance VO domicile – étude (si au moins un déplacement recensé vers lieu d'étude)
}

AGE_CLASS_MAP = {
    "Moins de 18 ans": "17-",
    "De 18 à 25 ans": "18-24",
    "De 25 à 34 ans": "25-34",
    "De 35 à 49 ans": "35-49",
    "De 50 à 64 ans": "50-64",
    "De 65 à 74 ans": "65-74",
    "75 ans et plus": "75+",
}

REFERENCE_PERSON_LINK_MAP = {
    0: "reference_person",
    1: "spouse",
    2: "child",
    3: "other:relative",
    4: "child",
    5: "other:relative",
    10: "other:relative",
    21: "other:relative",
    22: "other:relative",
    31: "other:relative",
    32: "other:relative",
    40: "other:relative",
    50: "other:relative",
    60: "other:non_relative",
    90: "other:non_relative",
}

DRIVING_LICENSE_MAP = {
    1: "yes",
    2: "no",
}

EDUCATION_LEVEL_MAP = {
    10: "higher:at_least_bac+3",
    11: "higher:at_least_bac+3",
    30: "higher:at_most_bac+2",
    31: "higher:at_most_bac+2",
    33: "higher:at_most_bac+2",
    41: "secondary:bac",
    42: "secondary:bac",
    50: "secondary:no_bac",
    60: "secondary:no_bac",
    70: "primary",
    71: "no_studies_or_no_diploma",
}

DETAILED_EDUCATION_LEVEL_MAP = {
    10: "higher:at_least_bac+3:universite",
    11: "higher:at_least_bac+3:ecole",
    30: "higher:at_most_bac+2:DEUG",
    31: "higher:at_most_bac+2:BTS/DUT",
    33: "higher:at_most_bac+2:paramedical_social",
    41: "secondary:bac:general",
    42: "secondary:bac:techno_or_pro",
    50: "secondary:no_bac:CAP/BEP",
    60: "secondary:no_bac:college",
    70: "primary:CEP",
    71: "no_diploma",
}

# Detailed professional occupation is read from SITUA * 10 and TEMPTRAV.
DETAILED_PROFESSIONAL_OCCUPATION_MAP = {
    10: "worker:unspecified",
    11: "worker:full_time",
    12: "worker:part_time",
    20: "student:apprenticeship",  # Apprenti sous contrat ou stagiaire rémunéré
    21: "student:apprenticeship",
    22: "student:apprenticeship",
    30: "student:unspecified",  # Étudiant, élève, en formation ou stagiaire non rémunéré
    31: "student:unspecified",
    32: "student:unspecified",
    40: "other:unemployed",
    41: "other:unemployed",
    42: "other:unemployed",
    50: "other:retired",
    51: "other:retired",
    52: "other:retired",
    60: "other:homemaker",
    61: "other:homemaker",
    62: "other:homemaker",
    70: "other:unspecified",  # Inactif pour cause d'invalidité
    71: "other:unspecified",
    72: "other:unspecified",
    80: "other:unspecified",  # Autre situation d'inactivité
    81: "other:unspecified",
    82: "other:unspecified",
}

TELEWORK_MAP = {
    1: "yes:monthly",  # Quelques jours ou demi-journées par mois
    2: "yes:weekly",  # 1 jour par semaine
    3: "yes:weekly",  # 2 jours par semaine
    4: "yes:weekly",  # 3 jours ou plus par semaine
    5: "no",  # Jamais
}

# Car sharing subscription type is computed from 10 * BABONNAUTOP + BAUTOPTYP.
CAR_SHARING_MAP = {
    1: "yes:unspecified",  # BABONNAUTOP = 1, BAUTOPTYP = null
    2: "yes:organized",  # BABONNAUTOP = 1, BAUTOPTYP = 1
    3: "yes:peer_to_peer",  # BABONNAUTOP = 1, BAUTOPTYP = 2
    20: "no",  # BABONNAUTOP = 2, BAUTOPTYP = null
}

WORKPLACE_SINGULARITY_MAP = {
    1: "unique:outside",
    2: "variable",
    3: "variable",
    4: "variable",
    5: "unique:home",
}

RESIDENT_TYPE_MAP = {
    1: "permanent_resident",
    2: "mostly_weekends",
    3: "mostly_weekdays",
    4: None,
    5: None,
}


def scan_persons(filename1: str, filename2: str, filename3: str):
    lf = (
        pl.read_csv(filename1, separator=";", encoding="latin1", schema_overrides=SCHEMA1)
        .lazy()
        .join(
            pl.scan_csv(filename2, separator=";", encoding="utf8-lossy", schema_overrides=SCHEMA2),
            on="ident_ind",
            how="left",
        )
        .join(
            pl.scan_csv(
                filename3,
                separator=";",
                encoding="utf8-lossy",
                schema_overrides=SCHEMA3,
                null_values=["Z"],
            ),
            left_on="ident_ind",
            right_on="IDENT_IND",
            how="left",
            coalesce=False,
        )
    )
    return lf


def standardize_persons(filename1: str, filename2: str, filename3: str, households: pl.LazyFrame):
    lf = scan_persons(filename1, filename2, filename3)
    # Add household_id.
    lf = lf.with_columns(original_household_id=pl.struct(IDENT_MEN="ident_men")).join(
        households.select("original_household_id", "household_id"),
        on="original_household_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename(
        {
            "NOI": "person_index",
            "AGE": "age",
            "pond_indC": "sample_weight_surveyed",
        }
    )
    lf = lf.with_columns(
        original_person_id=pl.struct("IDENT_IND"),
        reference_person_link=pl.col("LIEN_01").replace_strict(REFERENCE_PERSON_LINK_MAP),
        resident_type=pl.col("TYPOLOG").replace_strict(RESIDENT_TYPE_MAP),
        woman=pl.col("SEXE") == 2,
        age_class=pl.col("tr_age").replace_strict(AGE_CLASS_MAP),
        education_level=pl.col("DIP11").replace_strict(EDUCATION_LEVEL_MAP),
        detailed_education_level=pl.col("DIP11").replace_strict(DETAILED_EDUCATION_LEVEL_MAP),
        detailed_professional_occupation=(
            pl.col("SITUA") * 10 + pl.col("TEMPTRAV").fill_null(0)
        ).replace_strict(DETAILED_PROFESSIONAL_OCCUPATION_MAP),
        # Set pcs_group_code to NULL when CS24 is 0.
        pcs_group_code=pl.when(pl.col("CS24") > 0).then(pl.col("CS24") // 10),
        # Set pcs_category_code2003 to NULL when CS24 is 0.
        pcs_category_code2003=pl.when(pl.col("CS24") > 0).then("CS24"),
        workplace_singularity=pl.col("BTRAVFIX").replace_strict(WORKPLACE_SINGULARITY_MAP),
        telework=pl.col("BTRAVTEL").replace_strict(TELEWORK_MAP),
        has_driving_license=pl.col("BPERMIS").replace_strict(DRIVING_LICENSE_MAP),
        has_public_transit_subscription=pl.any_horizontal(
            pl.col(f"BTYP{i}RES_{a}").eq(1)
            & pl.col(f"BTYP{i}CART").is_in(("1.1", "2.1", "2.2", "2.5"))
            for i in range(1, 5)
            for a in ("A", "D", "E")
        ),
        has_car_sharing_subscription=pl.col("BABONNAUTOP") == 1,
        car_sharing_subscription=(
            10 * pl.col("BABONNAUTOP") + pl.col("BAUTOPTYP").fill_null(0)
        ).replace_strict(CAR_SHARING_MAP, default=None),
        has_bike_sharing_subscription=pl.col("BABONNVLS") == 1,
        has_travel_inconvenience=pl.col("GAGENE").is_in((1, 2, 3)),
        is_surveyed=pl.col("NOIK").is_not_null(),
        secondary_professional_occupation=pl.when(
            pl.col("TRAVAILLE").eq(1).and_(pl.col("SITUA").ne(1))
        )
        .then(pl.lit("work"))
        .when(pl.col("ETUDIE").eq(1).and_(pl.col("SITUA").ne(2)))
        .then(pl.lit("education")),
    )
    lf = clean(lf)
    return lf

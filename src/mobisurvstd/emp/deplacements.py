import polars as pl

from mobisurvstd.common.legs import clean as clean_legs
from mobisurvstd.common.trips import clean as clean_trips
from mobisurvstd.resources.nuts import NUTS_DF

SCHEMA = {
    "IDENT_DEP": pl.String,  # Identifiant déplacement
    "IDENT_MEN": pl.String,  # Identifiant ménage
    "IDENT_IND": pl.String,  # Identifiant individu
    "num_dep": pl.UInt8,  # Numéro du déplacement
    "nb_dep": pl.UInt8,  # Nombre de déplacements dans la journée
    "POND_JOUR": pl.Float64,  # Poids du jour
    "mobloc": pl.UInt8,  # Deplct < 80km(vo) du domicile
    "MDATE_jour": pl.String,  # Jour de la semaine du déplacement
    "MDATE_mois": pl.String,  # Mois du déplacement
    "MDATE_delai": pl.UInt8,  # Délai (en jours) entre la date d'enquête et le jour du déplacement
    "TYPEJOUR": pl.UInt8,  # Type du jour de déplacement
    "MORIDOM": pl.UInt8,  # Départ du domicile pour le PREMIER déplacement de la journée
    "MORI1MOTIF": pl.String,  # Motif à l'origine du 1er déplacement
    "MORIHDEP": pl.String,  # Heure de depart du dplct
    "MMOTIFDES": pl.String,  # Motif de déplacement
    "MOTPREC": pl.String,  # Motif à l'origine du déplacement
    "MMOTIFPROFRAB": pl.UInt8,  # L'établissement où l'enquêté s'est rendu appartient à l'entreprise qui l'emploie
    "MMOTIFDACC": pl.String,  # Motif de déplacement du passager
    "NUTS_ORI": pl.String,  # Code NUTS de départ du déplacement
    "REG_ORI": pl.String,  # Région de départ du déplacement
    "oldREG_ORI": pl.String,  # Ancienne région de départ du déplacement
    "PAYS_ORI": pl.String,  # Pays de départ du dplct
    "MEMDESCOM": pl.UInt8,  # Point d'arrivée du déplacement dans la même commune que point de départ
    "NUTS_DES": pl.String,  # Code NUTS d'arrivée du déplacement
    "REG_DES": pl.String,  # Région d'arrivée du déplacement
    "oldREG_DES": pl.String,  # Ancienne région arrivée du déplacement
    "PAYS_DES": pl.String,  # Pays de destination
    "MDESHARR": pl.String,  # Heure d'arrivée à destination
    "DUREE": pl.Float64,  # Durée du dplct
    "DURACT": pl.Float64,  # Durée de l'activite suiv. le dplct
    "MMOY1S": pl.String,  # 1er moyen de transport utilisé
    "MMOY2S": pl.String,  # 2ème moyen de transport
    "MMOY3S": pl.String,  # 3ème moyen de transport
    "MMOY4S": pl.String,  # 4ème moyen de transport
    "MOYS": pl.String,  # Tous moyens utilises
    "mtp": pl.String,  # Mode de transp. princ. du dplct
    "MNBMOD": pl.UInt8,  # Nombre de modes de transport utilisés
    "MNBMODCOND": pl.UInt8,  # Nombre de modes 'conducteur' utilisés
    "MDISTTOT_decl": pl.Float64,  # Distance parcourue déclarée au cours du déplacement
    "dVO_ORIDES": pl.Float64,  # Distance vol d'oiseau comm depart et arrivee
    "MDISTTOT_fin": pl.Float64,  # Distance parcourue consolidée/finale au cours du déplacement
    "indic_dist_corr": pl.UInt8,  # La distance a été corrigé
    "MTPSATTENT": pl.Float64,  # Temps d'attente total des transports en commun
    "MTEMPSMAP": pl.Float64,  # Temps de marche au cours du déplacement
    "MTCCOND": pl.UInt8,  # Place assise pendant trajet en transport en commun
    "MTITR1S": pl.String,  # Titre de transport utilisé pendant le trajet en TC (1er mode)
    "MTITR2S": pl.String,  # Titre de transport utilisé pendant le trajet en TC (2e mode)
    "MTITR3S": pl.String,  # Titre de transport utilisé pendant le trajet en TC (3e mode)
    "MTITR4S": pl.String,  # Titre de transport utilisé pendant le trajet en TC (4e mode)
    "MVEH": pl.UInt8,  # Véhicule utilisé
    "MVEHEXT": pl.UInt8,  # Type de véhicule utilisé
    "MCOVF": pl.UInt8,  # Covoiturage avec contrepartie financière
    "MCOVREL": pl.UInt8,  # Mise en relation avec le conducteur pour covoiturage
    "MVELO": pl.UInt8,  # Vélo utilisé
    "MSTATION": pl.UInt8,  # Stationnement du véhicule
    "MNBARRETT": pl.UInt16,  # Nombre d'arrêts ou de visites de la tournée
    "MACCOMPID": pl.UInt8,  # Accompagnement pendant le déplacement
    "MACCOMPM": pl.UInt8,  # Nombre d'accompagnants appartenant au ménage pendant le déplacement
    "MACCOMPHM": pl.UInt8,  # Nombre d'accompagnants extérieurs au ménage pendant le déplacement
    "MFINCONFIRM": pl.UInt8,  # Dernier déplacement de la journée a une destination autre que domicile
    "dist_ign": pl.Float64,  # Distance routière origine-destination du dplct
    "TUU2017_ORI": pl.UInt8,  # Tranche d'unité urbaine de la commune de départ
    "TUU2017_DES": pl.UInt8,  # Tranche d'unité urbaine de la commune de d'arrivé
    "STATUTCOM_UU_ORI": pl.String,  # Statut de la commune de départ
    "STATUTCOM_UU_DES": pl.String,  # Statut de la commune de d'arrivé
    "TYPE_UU_ORI": pl.UInt8,  # Type de l'unité urbaine de la commune de départ
    "TYPE_UU_DES": pl.UInt8,  # Type de l'unité urbaine de la commune d'arrivé
    "TAA2017_ORI": pl.UInt8,  # Tranche d'aire d'attraction des villes 2020 de la commune de départ
    "TAA2017_DES": pl.UInt8,  # Tranche d'aire d'attraction des villes 2020 de la commune d'arrivé
    "CATCOM_AA_ORI": pl.UInt8,  # Catégorie de la commune de départ dans l'aire d'attraction des villes 2020
    "CATCOM_AA_DES": pl.UInt8,  # Catégorie de la commune d'arrivé dans l'aire d'attraction des villes 2020
    "DENSITECOM_ORI": pl.UInt8,  # Degré de densité de la commune de départ
    "DENSITECOM_DES": pl.UInt8,  # Degré de densité de la commune d'arrivé
    "MEMDESDEP": pl.UInt8,  # Point d'arrivée du déplacement dans le même département que point de départ
    "MEMDESUU": pl.UInt8,  # Point d'arrivée du déplacement dans la même unité urbaine que point de départ
    "MEMDESAA": pl.UInt8,  # Point d'arrivée du déplacement dans la même aire d'attraction que point de départ
    "MEMDESZE": pl.UInt8,  # Point d'arrivée du déplacement dans la même zone d'emploi que point de départ
    "MEMDESBV": pl.UInt8,  # Point d'arrivée du déplacement dans le même bassin de vie que point de départ
    "pop_10min_pieton_tram_metro_ori": pl.UInt8,  # Part de la population de la commune d'origine à moins de 10 min à pied d'une station de métro ou de tram
    "pop_10min_pieton_tram_metro_des": pl.UInt8,  # Part de la population de la commune de destination à moins de 10 min à pied d'une station de métro ou de tram
    "pop_10min_pieton_train_ori": pl.UInt8,  # Part de la population de la commune d'origine à moins de 10 min à pied d'une station de train (TER, RER et grande ligne)
    "pop_10min_pieton_train_des": pl.UInt8,  # Part de la population de la commune de destination à moins de 10 min à pied d'une station de train (TER, RER et grande ligne)
    "pop_10min_voiture_tram_metro_ori": pl.UInt8,  # Part de la population de la commune d'origine à moins de 10 min en voiture d'une station de métro ou de tram
    "pop_10min_voiture_tram_metro_des": pl.UInt8,  # Part de la population de la commune de destination à moins de 10 min en voiture d'une station de métro ou de tram
    "pop_10min_voiture_train_ori": pl.UInt8,  # Part de la population de la commune d'origine à moins de 10 min en voiture d'une station de train (TER, RER et grande ligne)
    "pop_10min_voiture_train_des": pl.UInt8,  # Part de la population de la commune de destination à moins de 10 min en voiture d'une station de train (TER, RER et grande ligne)
    "precipitation_ori": pl.Float64,  # Précipitation du jour à l'origine du déplacement (en mm)
    "temp_mini_ori": pl.Float64,  # Température minimum du jour à l'origine du déplacement (en °C)
    "temp_maxi_ori": pl.Float64,  # Température maximum du jour à l'origine du déplacement (en °C)
    "precipitation_des": pl.Float64,  # Précipitation du jour à la destination du déplacement (en mm)
    "temp_mini_des": pl.Float64,  # Température minimum du jour à la destination du déplacement (en °C)
    "temp_maxi_des": pl.Float64,  # Température maximum du jour à la destniation du déplacement (en °C)
    "saison": pl.String,  # Saison du jour du déplacement
    "jour_nuit_ori": pl.UInt8,  # Position du soleil à l'origine du déplacement
    "jour_nuit_des": pl.UInt8,  # Position du soleil à la destination du déplacement
    "classement_littoral_ori": pl.String,  # Statut de la commune d'origine par rapport à la loi littoral
    "classement_littoral_des": pl.String,  # Statut de la commune de destination par rapport à la loi littoral
    "classement_montagne_ori": pl.String,  # Statut de la commune d'origine par rapport à la loi montagne
    "classement_montagne_des": pl.String,  # Statut de la commune de destination par rapport à la loi montagne
    "NEW_VAC_SCOL": pl.UInt8,  # Période scolaire du dplct
    "densite_7_ORI": pl.String,  # Degré de densité de la commune de départ du déplacement
    "densite_7_DES": pl.String,  # Degré de densité de la commune de destination du déplacement
    "MOT_DEP_COMPL": pl.String,  # Motif corrigé détaillé du déplacement
    "co2_depl": pl.UInt32,  # GCO2 émis lors du déplacement, hors amont et traînées
    "co2_amt_depl": pl.UInt32,  # GCO2 émis lors du déplacement, avec amont et traînées
    "IDENT_SEQ": pl.String,  # Identifiant de la séquence
    "NB_DEPSEQ": pl.UInt8,  # nombre de déplacements de la séquence
    "SEQUENCE_DET": pl.String,  # séquence détaillée en code de motif détaillé
    "MOT_SEQ_COMPL": pl.String,  # Motif corrigé détaillé de la séquence
}


PURPOSE_MAP = {
    "1.1": "home:main",  # Aller au domicile
    "1.2": "home:secondary",  # Retour à la résidence occasionnelle
    "1.3": "home:secondary",  # Retour au domicile de parents (hors ménage) ou d’amis
    "1.4": "education:other",  # Étudier (école, lycée, université)
    "1.5": "education:childcare",  # Faire garder un enfant en bas âge (nourrice, crèche, famille)
    "2.1": "shopping:unspecified",  # Se rendre dans une grande surface ou un centre commercial (y compris boutiques et services)
    "2.2": "shopping:unspecified",  # Se rendre dans un centre de proximité, petit commerce, supérette, boutique, services (banque, cordonnier...) commercial) (hors centre commercial)
    "3.1": "task:healthcare",  # Soins médicaux ou personnels (médecin, coiffeur…)
    "4.1": "task:procedure",  # Démarche administrative, recherche d’informations
    "4.12": "task:other",  # Déchetterie
    "5.1": "leisure:visiting:parents",  # Visite à des parents
    "5.2": "leisure:visiting:friends",  # Visite à des amis
    "6.1": "escort:transport:drop_off",  # Accompagner quelqu’un à la gare, à l’aéroport, à une station de métro, de bus, de car
    "6.2": "escort:activity:drop_off",  # Accompagner quelqu’un à un autre endroit
    "6.3": "escort:transport:pick_up",  # Aller chercher quelqu’un à la gare, à l’aéroport, à une station de métro, de bus, de car
    "6.4": "escort:activity:pick_up",  # Aller chercher quelqu’un à un autre endroit
    "7.1": "leisure:other",  # Activité associative, cérémonie religieuse, réunion
    "7.2": "leisure:sport_or_culture",  # Aller dans un centre de loisir, parc d’attraction, foire
    "7.3": "leisure:restaurant",  # Manger ou boire à l’extérieur du domicile
    "7.4": "leisure:sport_or_culture",  # Visiter un monument ou un site historique
    "7.5": "leisure:sport_or_culture",  # Voir un spectacle culturel ou sportif (cinéma, théâtre, concert, cirque, match), assister à une conférence
    "7.6": "leisure:sport_or_culture",  # Faire du sport
    "7.7": "leisure:walk_or_driving_lesson",  # Se promener sans destination précise
    "7.8": "leisure:walk_or_driving_lesson",  # Se rendre sur un lieu de promenade
    "8.1": "leisure:other",  # Vacances hors résidence secondaire
    "8.2": "home:secondary",  # Se rendre dans une résidence secondaire
    "8.3": "home:secondary",  # Se rendre dans une résidence occasionnelle
    "8.4": "task:other",  # Autres motifs personnels
    "9.1": "work:declared",  # Travailler dans son lieu fixe et habituel
    "9.2": "work:secondary",  # Travailler en dehors d’un lieu fixe et habituel, sauf ients ou visite à des fournisseurs, repas d’affaires, etc.)
    "9.3": "work:other",  # Stages, conférence, congrès, formations, exposition
    "9.4": "work:professional_tour",  # Tournées professionnelles (VRP) ou visites de patients
    "9.5": "work:other",  # Autres motifs professionnels
    "9999": None,
    "9999.0": None,
}

SHOP_TYPE_MAP = {
    "2.1": "supermarket_or_hypermarket",  # Se rendre dans une grande surface ou un centre commercial (y compris boutiques et services)
    "2.2": "small_shop",  # Se rendre dans un centre de proximité, petit commerce, supérette, boutique, services (banque, cordonnier...) commercial) (hors centre commercial)
}

MODE_MAP = {
    # 1 : Piéton
    "1.1": "walking",  # Uniquement marche à pied
    "1.2": "walking",  # Porté, transporté en poussette
    "1.3": "personal_transporter:unspecified",  # Rollers, trottinette
    "1.4": "wheelchair",  # Fauteuil roulant (y compris motorisé)
    # 2 : Deux roues
    "2.1": "bicycle:driver",  # Bicyclette, tricycle (y compris à assistance électrique) sauf vélo en libre-service
    "2.2": "bicycle:driver:shared",  # Vélo en libre-service
    "2.3": "motorcycle:driver:moped",  # Cyclomoteur (2 roues de moins de 50 cm3) – Conducteur
    "2.4": "motorcycle:passenger:moped",  # Cyclomoteur (2 roues de moins de 50 cm3) – Passager
    "2.5": "motorcycle:driver:moto",  # Moto (plus de 50 cm3) – Conducteur (y compris avec side-car et scooter à trois roues)
    "2.6": "motorcycle:passenger:moto",  # Moto (plus de 50 cm3) – Passager (y compris avec side-car et scooter à trois roues)
    "2.7": "motorcycle:driver",  # Motocycles sans précision (y compris quads)
    # 3 : Automobile
    "3.1": "car:driver",  # Voiture, VUL, voiturette… – Conducteur
    "3.2": "car:passenger",  # Voiture, VUL, voiturette… – Passager
    "3.3": "car:driver",  # Voiture, VUL, voiturette… – Tantôt conducteur tantôt passager
    "3.4": "car:driver",  # Trois ou quatre roues sans précision
    # 4 : Transport spécialisé, scolaire, taxi
    "4.1": "taxi_or_VTC",  # Taxi (individuel, collectif), VTC
    "4.2": "reduced_mobility_transport",  # Transport spécialisé (handicapé)
    "4.3": "employer_transport",  # Ramassage organisé par l'employeur
    "4.4": "public_transit:school",  # Ramassage scolaire
    # 5 : Transport en commun urbain ou régional, autocar
    "5.1": "public_transit:urban:bus",  # Autobus urbain, trolleybus
    "5.2": "water_transport",  # Navette fluviale
    "5.3": "public_transit:urban:coach",  # Autocar de ligne (sauf SNCF)
    "5.4": "public_transit:interurban:coach",  # Autre autocar (affrètement, service spécialisé)
    "5.5": "public_transit:urban:coach",  # Autocar TER
    "5.6": "public_transit:urban:tram",  # Tramway
    "5.7": "public_transit:urban:metro",  # Métro, VAL, funiculaire
    "5.8": "public_transit:urban:rail",  # RER, SNCF banlieue
    "5.9": "public_transit:urban:TER",  # TER
    "5.10": "public_transit:urban",  # Autres transports urbains et régionaux (sans précision)
    # 6 : Train grande ligne ou Train à grande vitesse
    "6.1": "public_transit:interurban:TGV",  # Train à grande vitesse, 1ère classe (TGV, Eurostar, etc.)
    "6.2": "public_transit:interurban:TGV",  # Train à grande vitesse, 2ème classe (TGV, Eurostar, etc.)
    "6.3": "public_transit:interurban:other_train",  # Autre train, 1ère classe
    "6.4": "public_transit:interurban:other_train",  # Autre train, 2ème classe
    "6.5": "public_transit:interurban:other_train",  # Train, sans précision
    # 7 : Avion
    "7.1": "airplane",  # Avion, classe première ou affaires
    "7.2": "airplane",  # Avion, classe premium économique
    "7.3": "airplane",  # Avion, classe économique
    "8.1": "water_transport",  # Bateau
    "9.1": "other",  # Autre
    "9999": None,
    "vide": None,
}

WEEKDAY_MAP = {
    "lundi": "monday",
    "mardi": "tuesday",
    "mercredi": "wednesday",
    "jeudi": "thursday",
    "vendredi": "friday",
    "samedi": "saturday",
    "dimanche": "sunday",
}


def scan_trips(filename: str):
    lf = pl.scan_csv(
        filename,
        separator=",",
        encoding="utf8-lossy",
        schema_overrides=SCHEMA,
        null_values=["NA", "Z", "ZZ", "ZZZ", ".", ""],
    )
    return lf


def standardize_trips(filename: str, persons: pl.LazyFrame):
    lf = scan_trips(filename)
    # Add household_id and person_id.
    lf = lf.with_columns(original_person_id=pl.struct("IDENT_IND")).join(
        persons.select("original_person_id", "person_id", "household_id"),
        on="original_person_id",
        how="left",
        coalesce=True,
    )
    lf = lf.rename(
        {
            "NUTS_ORI": "origin_nuts2",
            "NUTS_DES": "destination_nuts2",
            "dVO_ORIDES": "trip_euclidean_distance_km",
            "MDISTTOT_fin": "trip_travel_distance_km",
        }
    )
    lf = lf.with_columns(
        original_trip_id=pl.struct("IDENT_DEP"),
        origin_purpose=pl.col("MOTPREC").replace_strict(PURPOSE_MAP),
        destination_purpose=pl.col("MMOTIFDES").replace_strict(PURPOSE_MAP),
        destination_escort_purpose=pl.col("MMOTIFDACC").replace_strict(PURPOSE_MAP),
        origin_shop_type=pl.col("MOTPREC").replace_strict(SHOP_TYPE_MAP, default=None),
        destination_shop_type=pl.col("MMOTIFDES").replace_strict(SHOP_TYPE_MAP, default=None),
        origin_insee_density=insee_density_col("densite_7_ORI"),
        destination_insee_density=insee_density_col("densite_7_DES"),
        origin_aav_category=pl.col("TAA2017_ORI").replace({0: None, 8: None, 9: None}),
        destination_aav_category=pl.col("TAA2017_DES").replace({0: None, 8: None, 9: None}),
        origin_insee_aav_type=pl.col("CATCOM_AA_ORI").replace({98: None, 99: None}),
        destination_insee_aav_type=pl.col("CATCOM_AA_DES").replace({98: None, 99: None}),
        departure_time=(time_col_to_seconds("MORIHDEP") / 60).round(),
        arrival_time=(time_col_to_seconds("MDESHARR") / 60).round(),
        main_mode=pl.col("mtp").replace_strict(MODE_MAP),
        intra_municipality=pl.col("MEMDESCOM").eq(1),
        intra_aav=pl.col("MEMDESAA").eq(1),
        intra_dep=pl.col("MEMDESDEP").eq(1),
        trip_weekday=pl.col("MDATE_jour").replace_strict(WEEKDAY_MAP),
        trip_perimeter=pl.when(pl.col("PAYS_ORI").eq("FRANCE"), pl.col("PAYS_DES").eq("FRANCE"))
        .then(pl.lit("internal"))
        .when(pl.col("PAYS_ORI").eq("FRANCE") | pl.col("PAYS_DES").eq("FRANCE"))
        .then(pl.lit("crossing"))
        .otherwise(pl.lit("external")),
        nb_tour_stops=pl.col("MNBARRETT").replace({999: None}),
    )
    lf = lf.with_columns(
        # Set `destination_escort_purpose` to NULL when destination purpose is not
        # `escort:*:drop_off`.
        # Note that EMP does not specify the escort purpose for pick-up purposes.
        destination_escort_purpose=pl.when(
            pl.col("destination_purpose").is_in(
                ("escort:transport:drop_off", "escort:activity:drop_off")
            )
        ).then("destination_escort_purpose"),
        # Read the `origin_escort_purpose` from the `destination_escort_purpose` of the previous
        # trip.
        origin_escort_purpose=pl.when(
            pl.col("origin_purpose").is_in(
                ("escort:transport:drop_off", "escort:activity:drop_off")
            )
        ).then(pl.col("destination_escort_purpose").shift(1).over("person_id")),
        # When departure_time or arrival_time is the next day, we need to add 24h (e.g., 03:00 ->
        # 27:00).
        dt_day_shift=pl.col("departure_time") < pl.col("departure_time").shift(1).over("person_id"),
        at_day_shift=pl.col("arrival_time") < pl.col("arrival_time").shift(1).over("person_id"),
    )
    lf = lf.with_columns(
        departure_time=pl.col("departure_time")
        + pl.col("dt_day_shift").fill_null(False).cum_sum().over("person_id") * 24 * 60,
        arrival_time=pl.col("arrival_time")
        + pl.col("at_day_shift").fill_null(False).cum_sum().over("person_id") * 24 * 60,
    )
    lf = lf.with_columns(
        # For 1 person (830000132200002), the trips departure and arrival times are not logical. We
        # set all values to NULL for this person.
        departure_time=pl.when(
            pl.col("arrival_time").shift(1).over("person_id") > pl.col("departure_time")
        )
        .then(pl.lit(None))
        .otherwise("departure_time"),
        arrival_time=pl.when(
            pl.col("arrival_time").shift(1).over("person_id") > pl.col("departure_time")
        )
        .then(pl.lit(None))
        .otherwise("arrival_time"),
    )
    lf = lf.with_columns(
        # For 1 person (830000132200002), the trip's departure is after the trip's arrival. We set
        # all values to NULL for this person.
        departure_time=pl.when(pl.col("arrival_time") < pl.col("departure_time"))
        .then(pl.lit(None))
        .otherwise("departure_time"),
        arrival_time=pl.when(
            pl.col("arrival_time").shift(1).over("person_id") > pl.col("departure_time")
        )
        .then(pl.lit(None))
        .otherwise("arrival_time"),
    )
    # Add NUTS data from the `*_nuts2` columns.
    old_reg_df = (
        NUTS_DF.group_by("NUTS2")
        .agg(pl.col("NUTS2_name").first(), pl.col("NUTS1").first(), pl.col("NUTS1_name").first())
        .lazy()
    )
    for prefix in ("origin", "destination"):
        lf = lf.join(old_reg_df, left_on=f"{prefix}_nuts2", right_on="NUTS2", how="left").rename(
            {
                "NUTS2_name": f"{prefix}_nuts2_name",
                "NUTS1": f"{prefix}_nuts1",
                "NUTS1_name": f"{prefix}_nuts1_name",
            }
        )
    lf = clean_trips(lf, 2019)
    return lf


def standardize_legs(filename: str, trips: pl.LazyFrame):
    lf = scan_trips(filename)
    lf = lf.select(
        "IDENT_DEP",
        pl.col("MMOY1S").alias("1"),
        pl.col("MMOY2S").alias("2"),
        pl.col("MMOY3S").alias("3"),
        pl.col("MMOY4S").alias("4"),
    )
    lf = lf.unpivot(index="IDENT_DEP", variable_name="leg_index", value_name="mode")
    lf = lf.with_columns(pl.col("leg_index").cast(pl.UInt8))
    # Add household_id, person_id, and trip_id.
    lf = lf.with_columns(original_trip_id=pl.struct("IDENT_DEP")).join(
        trips.select("original_trip_id", "household_id", "person_id", "trip_id"),
        on="original_trip_id",
        how="left",
        coalesce=True,
    )
    lf = lf.filter(
        # Drop legs with NULL mode (there is by default 4 legs by trip).
        pl.col("mode").is_not_null()
        # Keep the first leg for the 2 trips for which all mode values are NULL.
        | (pl.col("mode").is_null().all().over("trip_id") & pl.col("leg_index").eq(1))
    )
    lf = lf.with_columns(
        original_leg_id=pl.struct("IDENT_DEP", "leg_index"),
        mode=pl.col("mode").replace_strict(MODE_MAP),
    )
    lf = clean_legs(lf)
    return lf


def time_col_to_seconds(col: str):
    return (
        pl.col(col)
        .str.splitn(":", 3)
        .struct.with_fields(
            seconds=pl.field("field_0").cast(pl.UInt32) * 3600
            + pl.field("field_1").cast(pl.UInt32) * 60
            + pl.field("field_2").cast(pl.UInt32)
        )
        .struct.field("seconds")
    )


def insee_density_col(col: str):
    # The encoding of the file is incorrect so we need to resort to the following function to
    # convert INSEE density names to codes.
    return (
        pl.when(pl.col(col).eq("Grands centres urbains"))
        .then(1)
        .when(pl.col(col).str.starts_with("Centres urbanis interm"))
        .then(2)
        .when(pl.col(col).eq("Ceintures urbaines"))
        .then(3)
        .when(pl.col(col).eq("Petites villes"))
        .then(4)
        .when(pl.col(col).eq("Bourgs ruraux"))
        .then(5)
        .when(pl.col(col).str.contains("habitat dispers"))
        .then(6)
        .when(pl.col(col).str.contains("habitat tr"))
        .then(7)
    )

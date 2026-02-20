# Surveys

This page lists all the survey types which are currently supported by MobiSurvStd.

<div class="warning">
For each type, the expected format (tree structure and filenames) is provided.
If you have a survey with a different format (which can happen if you did not get your survey from
Progedo), then MobiSurvStd will not be able to guess the survey type and to read it (even if you
specify the survey type).
In this case, you can try renaming or moving files to match the expected format.
MobiSurvStd will then be able to properly guess the survey type and read it (assuming the files'
content is the same).

If you are not able to read your survey or if you want MobiSurvStd to support a new survey type /
format, feel free to <a href="https://github.com/MobiSurvStd/MobiSurvStd/issues">open an issue on
GitHub</a>.
</div>

## Enquête mobilité des personnes 2019 (EMP)

Code: `emp2019`

Link: [https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019](https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019)

Tested version: November 2024

Expected format:

```bash
emp_2019/
├── *k_deploc_public_V4.csv  # The `*` character can be anything (there is a typo in the original filename)
├── k_individu_public_V3.csv
├── q_2rmot_public_V3.csv
├── q_menage_public_V3.csv
├── q_voitvul_public_V3.csv
├── tcm_ind_kish_public_V3.csv
├── tcm_ind_public_V3.csv
└── tcm_men_public_V3.csv
```

Notes:

- Many variables from the original survey data are not read because they are not part of any other
  survey type.
- The survey does not guarantee any representativeness at the regional level.
- Only one person per household is surveyed for their trips and additional characteristics.
- The car type is not specified. Cars can include passenger cars, utilitary cars and recreational
  cars.
- The survey includes data on 58 "voiturettes", 59 "quads", and 1 "tricycle" as a special vehicle
  category, which is not read by MobiSurvStd.
- Walking legs are not specified in the survey data for trips combining walking with other modes.

## Enquêtes mobilité certifiés Cerema (EMC²)

Code: `emc2`

Link: [https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2](https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2)

Download link (for researchers): [https://data.progedo.fr/series/adisp/enquetes-menages-deplacements-emd-enquetes-mobilite-certifiee-cerema-emc](https://data.progedo.fr/series/adisp/enquetes-menages-deplacements-emd-enquetes-mobilite-certifiee-cerema-emc)

Expected format:

```bash
my_emc2_survey/
├── Csv
│   └── Fichiers_Standard
│       ├── *_std_depl.csv
│       ├── *_std_men.csv
│       ├── *_std_pers.csv
│       └── *_std_traj.csv
└── Doc
    └── SIG
        ├── *_ZF(_*)?.(TAB|shp)    # Optional "Zones fines" file
        ├── *_GT(_*)?.(TAB|shp)    # Optional "Générateurs de trafic" file
        └── *_DTIR(_*)?.(TAB|shp)  # Optional "Zones de tirage" file
```

Tested surveys:

- Alençon 2018
- Angers 2022
- Besançon 2018
- Bordeaux 2021
- Bouzonville 2019
- Brest 2018
- Chambéry 2022
- Évreux 2018
- Gap 2018
- Grenoble 2020
- Lannion 2022
- Le Havre 2018
- Marseille 2020
- Pointe-à-Pitre 2021
- Poitiers 2018
- Reims 2021
- Rennes 2018
- Sables d'Olonne 2021
- Saint-Étienne 2021
- Tours 2019
- Valenciennes 2019
- Vendée 2020

Notes:

- The survey detailed zones correspond to the "zones fines" ("ZF"), which are usually the size of
  IRIS zones or smaller.
- For most surveys, there are special locations corresponding to "Générateurs de trafic" ("GT"),
  which represent e.g., train stations or hospitals.
- Draw zones correspond to the survey's "zones de tirage".
- For each trips, the non-walking legs are recorded. MobiSurvStd reconstruct the walking legs using
  the access / egress walking time variables. This means that the leg travel time is known only for
  the walking legs (as it is not a recorded variable for the other legs).

## Enquête Globale Transport 2018-2020

Code: `egt2020`

Link: [https://data.progedo.fr/studies/doi/10.13144/lil-1581](https://data.progedo.fr/studies/doi/10.13144/lil-1581)

Expected format:

```bash
egt_2020/
└── Csv
    ├── a_menage_egt1820.csv
    ├── b_individu_egt1820.csv
    ├── c_deplacement_egt1820.csv
    ├── d_trajet_egt1820.csv
    ├── e_voiture_egt1820.csv
    ├── f_drm_egt1820.csv
    └── g_velo_egt1820.csv
```

Notes:

- There is no draw zones because the survey was interrupted before the end due to Covid-19.
- There is no detailed zone but the coordinates of the origins / destinations are known (rounded to
  100 meters).
- The car types are not specified but utilitary cars and recreational cars ar excluded.
- Motorcycles' parking data is not read because the survey's documentation is incorrect.
- Variable `main_mode_group` can differ from the original `MODP_H7` variable because MobiSurvStd
  uses a different definition of mode groups and a different methodology to identify the main mode.
- The `start_insee` and `end_insee` values are derived from the leg's coordinates, using INSEE data
  from 2025.
- The `work_insee` and `study_insee` values are derived from the given coordinates, using INSEE data
  from 2025. There can be some errors because of the 100m rounding.

## Enquête Mobilité par GPS 2023 (EMG)

Code: `emg2023`

Link: [https://www.institutparisregion.fr/mobilite-et-transports/deplacements/enquete-regionale-sur-la-mobilite-des-franciliens/](https://www.institutparisregion.fr/mobilite-et-transports/deplacements/enquete-regionale-sur-la-mobilite-des-franciliens/)

Expected format:

```bash
emg/
├── EMG_BD_Deplacements_*.xlsx
├── EMG_BD_Individus_*.xlsx
└── EMG_Distance.xlsx     # Optional, gives trip euclidean distances.
```

Notes:

- Only one person per household is surveyed. Characteristics of all other members are unknown.
- The number of cars and motorcycles per household is known but their characteristics are unknown.
- The survey is conducted **over a week** (seven days) for each person. The trip-level variable
  `trip_date` can be used to identify the day of the trips. The person might not have traveled each
  day of the surveyed week.
- Trips done before 4 a.m. are usually registered to the previous day, with a departure / arrival
  time value over 24h.
- Origins and destinations are defined at the INSEE level.

_Implementation in MobiSurvStd by Sebastian Hörl_

## Enquêtes Déplacements Grands Territoires (EDGT)

Code: `edgt`

Link: [https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2](https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2)

Download link (for researchers): [https://data.progedo.fr/studies?q=edgt](https://data.progedo.fr/studies?q=edgt)

Expected format:

```bash
my_edgt_survey/
├── Csv
│   ├── Fichiers_Standard_Face_a_face
│   │   ├── *_std_faf_depl.csv
│   │   ├── *_std_faf_men.csv
│   │   ├── *_std_faf_pers.csv
│   │   └── *_std_faf_traj.csv
│   └── Fichiers_Standard_Telephone
│       ├── *_std_tel_depl.csv
│       ├── *_std_tel_men.csv
│       ├── *_std_tel_pers.csv
│       └── *_std_tel_traj.csv
└── Doc
    └── SIG
        ├── *(_ZF|zones_fines).(TAB|shp|MIF)        # Optional "Zones fines" file (the actual regex is more complex)
        ├── *(_GT|générateur*).(TAB|shp|MIF)        # Optional "Générateurs de trafic" file (the actual regex is more complex)
        └── *(_DTIR|_secteurstirage).(TAB|shp|MIF)  # Optional "Zones de tirage" file
```

Tested surveys:

- Amiens 2010
- Angers 2012
- Annecy 2017
- Annemasse 2016
- Bayonne 2010
- Clermont-Ferrand 2012
- Dijon 2016
- Dunkerque 2015
- Lyon 2015
- Marseille 2009
- Metz 2017
- Montpellier 2014
- Nancy 2013
- Nantes 2015 (Also available in an
  [anonymized open-data format](https://www.data.gouv.fr/datasets/enquete-deplacements-2015-en-loire-atlantique))
- Nice 2009
- Saint-Denis-de-la-Réunion 2016
- Saint-Quentin-en-Yvelines 2010
- Valence 2014

Notes:

- The survey detailed zones correspond to the "zones fines" ("ZF"), which are usually the size of
  IRIS zones or smaller.
- For most surveys, there are special locations corresponding to "Générateurs de trafic" ("GT"),
  which represent e.g., train stations or hospitals.
- Draw zones correspond to the survey's "zones de tirage".
- For each trips, the non-walking legs are recorded. MobiSurvStd reconstruct the walking legs using
  the access / egress walking time variables. This means that the leg travel time is known only for
  the walking legs (as it is not a recorded variable for the other legs).

## Enquêtes Déplacements Villes Moyennes (EDVM)

Code: `edvm`

Link: [https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2](https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2)

Download link (for researchers): [https://data.progedo.fr/studies?q=edvm](https://data.progedo.fr/studies?q=edvm)

Expected format:

```bash
my_edvm_survey/
├── Csv
│   └── Fichiers_Standard
│       ├── *_std_depl.csv
│       ├── *_std_men.csv
│       ├── *_std_pers.csv
│       └── *_std_traj.csv
└── Doc
    └── SIG
        ├── *(_ZF|zones_fines).(TAB|shp|MIF)  # Optional "Zones fines" file (the actual regex is more complex)
        ├── *(_GT|générateur*).(TAB|shp|MIF)  # Optional "Générateurs de trafic" file (the actual regex is more complex)
        └── *_DTIR.(TAB|shp|MIF)              # Optional "Zones de tirage" file
```

Tested surveys:

- Ajaccio 2017
- Albi 2011
- Angoulême 2012
- Arras 2014
- Beauvais 2010
- Béziers 2014
- Bourg-en-Bresse 2017
- Carcassonne 2015
- Châlon-sur-Saône 2014
- Cherbourg 2016
- Créil 2017
- Dinan 2010
- La Rochelle 2011
- La-Roche-sur-Yon 2013
- Laval 2011
- Le Creusot 2012
- Les Sables d'Olonne 2011
- Longwy 2014
- Niort 2016
- Puisaye-Forterre et Aillantais 2012
- Quimper 2013
- Roanne 2012
- Saint-Brieuc 2012
- Saintes 2016
- Saint-Louis 2011
- Thionville 2012
- Var 2012

Notes:

- The survey detailed zones correspond to the "zones fines" ("ZF"), which are usually the size of
  IRIS zones or smaller.
- For most surveys, there are special locations corresponding to "Générateurs de trafic" ("GT"),
  which represent e.g., train stations or hospitals.
- Draw zones correspond to the survey's "zones de tirage".
- For each trips, the non-walking legs are recorded. MobiSurvStd reconstruct the walking legs using
  the access / egress walking time variables. This means that the leg travel time is known only for
  the walking legs (as it is not a recorded variable for the other legs).

## Enquêtes Ménages Déplacements (EMD)

Code: `emd`

Link: [https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2](https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2)

Download link (for researchers): [https://data.progedo.fr/studies?q=emd](https://data.progedo.fr/studies?q=emd)

Expected format:

```bash
my_emd_survey/
├── Csv
│   └── Fichiers_Standard
│       ├── *_std_depl.csv
│       ├── *_std_men.csv
│       ├── *_std_pers.csv
│       └── *_std_traj.csv
└── Doc
    └── SIG
        ├── *(_ZF|zones_fines).(TAB|shp|MIF)  # Optional "Zones fines" file (the actual regex is more complex)
        ├── *(_GT|générateur*).(TAB|shp|MIF)  # Optional "Générateurs de trafic" file (the actual regex is more complex)
        └── *(_DTIR|secteur_*).(TAB|shp|MIF)  # Optional "Zones de tirage" file
```

Tested surveys:

- Douai 2012
- Fort-de-France 2014
- Grenoble 2010
- Lille 2016
- Nîmes 2015
- Rouen 2017
- Saint-Étienne 2010
- Strasbourg 2009
- Toulouse 2013
- Valenciennes 2011

Notes:

- The survey detailed zones correspond to the "zones fines" ("ZF"), which are usually the size of
  IRIS zones or smaller.
- For most surveys, there are special locations corresponding to "Générateurs de trafic" ("GT"),
  which represent e.g., train stations or hospitals.
- Draw zones correspond to the survey's "zones de tirage".
- For each trips, the non-walking legs are recorded. MobiSurvStd reconstruct the walking legs using
  the access / egress walking time variables. This means that the leg travel time is known only for
  the walking legs (as it is not a recorded variable for the other legs).


## Enquête Globale Transport 2010

Code: `egt2010`

Link: [https://data.progedo.fr/studies/doi/10.13144/lil-0883](https://data.progedo.fr/studies/doi/10.13144/lil-0883)

Expected format:

```bash
egt_2010/
├── Csv  # Or Format_csv
│   ├── deplacements_semaine.csv  # Filenames are case-insensitive (the first letter can be capitalized).
│   ├── menages_semaine.csv
│   ├── personnes_semaine.csv
│   └── trajets_semaine.csv
├── Doc
│   └── Carreaux_shape_mifmid
│       └── carr100m.shp       # Option 1: Carreaux are in a shapefile within a directory.
└── Carreaux_shape_mifmid.zip  # Option 2: Carreaux are in a zipfile within the parent directory.
```

Notes:

- The detailed zones correspond to the 100m by 100m cells.
- For now, only the weekday trips are standardized.

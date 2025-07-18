# Surveys

## Enquête mobilité des personnes 2019 (EMP)

Code: `emp2019`

Link: [https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019]()

Tested version: November 2024

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

Link: [https://www.cerema.fr/fr/activites/mobilites/connaissance-modelisation-evaluation-mobilite/enquetes-mobilite-emc2]()

Download link (for researchers): [https://data.progedo.fr/series/adisp/enquetes-menages-deplacements-emd-enquetes-mobilite-certifiee-cerema-emc]()

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

- The survey detailed zones ("zones fines") usually correspond to IRIS zones.
- Some surveys include special locations ("GT"), representing e.g., train stations or hospitals.
- Draw zones correspond to the survey's "zones de tirage".
- For each trips, the non-walking legs are recorded. MobiSurvStd reconstruct the walking legs using
  the access / egress walking time variables. This means that the leg travel time is known only for
  the walking legs (as it is not a recorded variable for the other legs).

## Enquête Globale Transport 2018-2020

Code: `egt2020`

Link: [https://data.progedo.fr/studies/doi/10.13144/lil-1581]()

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


## Enquête Globale Transport 2010

Code: `egt2010`

Link: [https://data.progedo.fr/studies/doi/10.13144/lil-0883]()

Notes:

- The detailed zones correspond to the 100m by 100m cells.
- For now, only the weekday trips are standardized.

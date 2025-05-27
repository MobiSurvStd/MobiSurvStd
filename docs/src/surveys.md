# Surveys

## EMC²

- TODO: Information on zoning system (including GT)
- For each trips, the non-walking legs are recorded. MobiSurvStd reconstruct the walking legs using
  the access / egress walking time variables. This means that the leg travel time is known only for
  the walking legs (as it is not a recorded variable for the other legs).

- Brest:
  - The municipality of *Daoulas* is not included in the INSEE shapefile, despite the municipality
    being inside the perimeter.
  - Some special locations are not defined in the shapefile but are used as origin / destination.

## EMP

- Pas de représentativité régionale
- Une seule personne par ménage avec + d'infos (dont les déplacements)
- Type de car pas connu mais peut inclure voiture particulière, VUL et camping-car
- Troisième type de véhicules (58 voiturettes + 59 quads + 1 tricycle) pas lu

## EGT 2020

- Pas de secteur de tirage ni de carreaux (mais coordonnées)
- Pas de type pour les "cars" (mais camping-cars et gros utilitaires exclus)
- Stationnement des motos pas lu car la documentation n'est pas bonne
- `main_mode_group` différent de `MODP_H7` car pas même classification des groups, pas mêmes
  critères
- `start_insee` and `end_insee` are derived from leg's coordinates, using INSEE data from 2025
- `work_insee` and `study_insee` are derived from coordinates, using INSEE data from 2025. There can be some mistakes (e.g., Puteaux when it should be Courbevoie)

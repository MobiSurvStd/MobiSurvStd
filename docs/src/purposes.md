<style>
    .content main {
        max-width: 1400px;
    }
</style>

# Purpose comparison

Each survey uses its own list of trip purposes.
The table below shows, for each MobiSurvStd purpose (variables
[`origin_purpose`](format/trips.md#origin_purpose) and
[`destination_purpose`](format/trips.md#destination_purpose) of trips), the original modalities that
are mapped to it in each survey type.
Original modalities are given as `code` followed by the label from the survey's documentation (in
French).
A dash (–) means that the survey type has no modality mapped to that purpose.

The EMC², EDGT, EDVM, and EMD surveys all share the same purpose definitions.
The same codes are also used for the purpose of the escorted person
([`origin_escort_purpose`](format/trips.md#origin_escort_purpose) and
[`destination_escort_purpose`](format/trips.md#destination_escort_purpose)), when available.

| Purpose | EMC² / EDGT / EDVM / EMD | EGT2010 | EGT2020 | EMP2019 |
| --- | --- | --- | --- | --- |
| `home:main` | `1` Domicile (partir de, se rendre à) | `1` Domicile habituel (celui où la personne est enquêtée) | `11` Mon domicile | `1.1` Aller au domicile |
| `home:secondary` | `2` Résidence secondaire, logement occasionnel, hôtel, autre domicile (partir de, se rendre à) | `2` Un des domiciles correspondant à une garde alternée<br>`3` Résidence secondaire, logement occasionnel, hôtel, autre domicile | `12` Autre domicile de la garde alternée<br>`13` Résidence secondaire, logement occasionnel, hôtel, autre domicile | `1.2` Retour à la résidence occasionnelle<br>`1.3` Retour au domicile de parents (hors ménage) ou d'amis<br>`8.2` Se rendre dans une résidence secondaire<br>`8.3` Se rendre dans une résidence occasionnelle |
| `work:usual` | `11` Travailler sur le lieu d'emploi déclaré | `11` Travail sur le lieu de travail déclaré dans la fiche personne | `21` Travail / Lieu travail précis | `9.1` Travailler dans son lieu fixe et habituel |
| `work:telework` | `12` Travailler sur un autre lieu - télétravail | – | `34` Travail au domicile personnel | – |
| `work:secondary` | `13` Travailler sur un autre lieu hors télétravail | `12` Travail sur un autre lieu (hors affaires professionnelles) | – | `9.2` Travailler en dehors d'un lieu fixe et habituel, sauf clients ou visite à des fournisseurs, repas d'affaires, etc.) |
| `work:business_meal` | – | `15` Repas d'affaires, déjeuner professionnel | `37` Repas d'affaires, déjeuner professionnel | – |
| `work:other` | `14` Travailler sur un autre lieu sans distinction | `13` Affaires professionnelles hors lieu de travail habituel (RV professionnel, réunion, etc.) | `31` Affaires professionnelles (RV pro, réunion, etc.) hors lieu de travail habituel<br>`32` Travail chez des particuliers<br>`33` Travail dans un espace de co-working<br>`35` Travail sur un autre lieu | `9.3` Stages, conférence, congrès, formations, exposition<br>`9.5` Autres motifs professionnels |
| `work:professional_tour` | `81` Réaliser une tournée professionnelle | `14` Tournée professionnelle | `36` Tournée professionnelle | `9.4` Tournées professionnelles (VRP) ou visites de patients |
| `education:childcare` | `21` Être gardé (Nourrice, crèche...) | `21` Nourrice, crèche, garde d'enfants | `41` Garde d'enfants | `1.5` Faire garder un enfant en bas âge (nourrice, crèche, famille) |
| `education:usual` | `22` Étudier sur le lieu d'études déclaré (école maternelle et primaire)<br>`23` Étudier sur le lieu d'études déclaré (collège)<br>`24` Étudier sur le lieu d'études déclaré (lycée)<br>`25` Étudier sur le lieu d'études déclaré (universités et grandes écoles) | `22` Études sur le lieu d'études déclaré (école maternelle et primaire)<br>`23` Études sur le lieu d'études déclaré (enseignement secondaire : collège et lycée)<br>`24` Études sur le lieu d'études déclaré (enseignement supérieur, universités et grandes écoles) | `42` Etudes | – |
| `education:other` | `26` Étudier sur un autre lieu (école maternelle et primaire)<br>`27` Étudier sur un autre lieu (collège)<br>`28` Étudier sur un autre lieu (lycée)<br>`29` Étudier sur un autre lieu (universités et grandes écoles) | `25` Études sur un autre lieu (école maternelle et primaire)<br>`26` Études sur un autre lieu (enseignement secondaire : collège et lycée)<br>`27` Études sur un autre lieu (enseignement supérieur, universités et grandes écoles) | `43` Etudes sur un autre lieu | `1.4` Étudier (école, lycée, université) |
| `shopping:daily` | – | `31` Achats quotidiens (pain, journal, …) | `51` Achats quotidiens | – |
| `shopping:weekly` | – | `32` Achats hebdomadaires ou bi hebdomadaires | `52` Achats hebdomadaires | – |
| `shopping:specialized` | – | `33` Achats occasionnels (livres, vêtements, électroménager, musique, meubles etc.) | `53` Achats occasionnels | – |
| `shopping:unspecified` | `31` Réaliser plusieurs motifs en centre commercial<br>`32` Faire des achats en grand magasin, supermarché, hypermarché et leurs galeries marchandes<br>`33` Faire des achats en petit et moyen commerce et drive in<br>`34` Faire des achats en marché couvert et de plein vent | – | – | `2.1` Se rendre dans une grande surface ou un centre commercial (y compris boutiques et services)<br>`2.2` Se rendre dans un centre de proximité, petit commerce, supérette, boutique, services (banque, cordonnier...) commercial) (hors centre commercial) |
| `shopping:pickup` | `35` Récupérer des achats faits à distance (Drive, points relais) | – | `54` Récupérer un colis | – |
| `shopping:no_purchase` | `30` Visite d'un magasin, d'un centre commercial ou d'un marché de plein vent sans effectuer d'achat | – | `621` Lèche vitrines | – |
| `shopping:tour_no_purchase` | `82` Tournée de magasin sans achat | – | – | – |
| `task:healthcare` | `41` Recevoir des soins (santé) | `52` Aide ou soins à des proches | `73` Aide ou soins à des proches<br>`74` Santé | `3.1` Soins médicaux ou personnels (médecin, coiffeur…) |
| `task:healthcare:hospital` | – | `53` Santé (hôpital, clinique) | – | – |
| `task:healthcare:doctor` | – | `54` Santé autres (consultation professionnel de la santé hors hôpital : médecin, dentiste, kiné, etc.) | – | – |
| `task:procedure` | `42` Faire une démarche autre que rechercher un emploi | `50` Démarches administratives | `71` Démarches administratives | `4.1` Démarche administrative, recherche d'informations |
| `task:job_search` | `43` Rechercher un emploi | `51` Recherche d'emploi (y. entretiens) | `72` Recherche d'emploi | – |
| `task:other` | – | `55` Affaires personnelles autres (avocat, notaire, garage, réunion parents d'élèves, réunion de copropriétaires etc.) | `75` Affaires personnelles autres | `4.12` Déchetterie<br>`8.4` Autres motifs personnels |
| `leisure:sport_or_culture` | `51` Participer à des loisirs, des activités sportives, culturelles ou associatives | `41` Participation à une activité sportive, culturelle, associative ou religieuse<br>`45` Spectacle, exposition, cinéma, musée, théâtre, concert, match de foot…<br>`46` Voyage, sortie touristique | `631` Sortie<br>`651` Faire du sport<br>`652` Participation à une activité artistique ou associative | `7.2` Aller dans un centre de loisir, parc d'attraction, foire<br>`7.4` Visiter un monument ou un site historique<br>`7.5` Voir un spectacle culturel ou sportif (cinéma, théâtre, concert, cirque, match), assister à une conférence<br>`7.6` Faire du sport |
| `leisure:walk_or_driving_lesson` | `52` Faire une promenade, du « lèche-vitrines », prendre une leçon de conduite | `42` Promenade, lèche-vitrines (sans achat), leçons de conduite | `622` Promenade dans / vers un lieu précis (monument, parc, bois…)<br>`623` Promenade sans but précis (dans le quartier…)<br>`624` Leçons de conduite | `7.7` Se promener sans destination précise<br>`7.8` Se rendre sur un lieu de promenade |
| `leisure:lunch_break` | – | `16` Pause déjeuner durant la journée de travail (cantine, cafétéria, restaurant situés hors du lieu de travail…) | – | – |
| `leisure:restaurant` | `53` Se restaurer hors du domicile | `17` Autre restauration hors domicile (restaurant, bar, café, cybercafé…) | `611` Restaurant, cantine, cafétéria, bar, café… | `7.3` Manger ou boire à l'extérieur du domicile |
| `leisure:visiting` | `54` Visiter des parents ou des amis | – | `641` Rendre visite | – |
| `leisure:visiting:parents` | – | `43` Visite à des parents | – | `5.1` Visite à des parents |
| `leisure:visiting:friends` | – | `44` Visite à des amis | – | `5.2` Visite à des amis |
| `leisure:other` | – | `47` Autres loisirs | `690` Autres loisirs | `7.1` Activité associative, cérémonie religieuse, réunion<br>`8.1` Vacances hors résidence secondaire |
| `escort:activity:drop_off` | `61` Accompagner quelqu'un (personne présente)<br>`63` Accompagner quelqu'un (personne absente) | `63` Accompagner quelqu'un dans un lieu autre qu'un mode de transport (école, garderie, amis, cinéma, sport, travail etc.) | `812` Accompagner quelqu'un | `6.2` Accompagner quelqu'un à un autre endroit |
| `escort:activity:pick_up` | `62` Aller chercher quelqu'un (personne présente)<br>`64` Aller chercher quelqu'un (personne absente) | `64` Aller chercher quelqu'un (dans un lieu autre qu'un mode de transport (école, garderie, amis, cinéma, sport, travail etc.) | `822` Aller chercher quelqu'un | `6.4` Aller chercher quelqu'un à un autre endroit |
| `escort:transport:drop_off` | `71` Déposer une personne à un mode de transport (personne présente)<br>`73` Déposer d'une personne à un mode de transport (personne absente) | `61` Dépose d'une personne à un mode de transport (station, gare, arrêt de bus, aéroport…) | `811` Accompagner quelqu'un à un mode de transport | `6.1` Accompagner quelqu'un à la gare, à l'aéroport, à une station de métro, de bus, de car |
| `escort:transport:pick_up` | `72` Reprendre une personne à un mode de transport (personne présente)<br>`74` Reprendre une personne à un mode de transport (personne absente) | `62` Reprise d'une personne à un mode de transport (station, gare, arrêt de bus, aéroport…) | `821` Aller chercher quelqu'un à un mode de transport | `6.3` Aller chercher quelqu'un à la gare, à l'aéroport, à une station de métro, de bus, de car |
| `escort:unspecified:drop_off` | `68` Accompagner quelqu'un ou déposer quelqu'un à un mode de transport (sans info présence personne) | – | – | – |
| `escort:unspecified:pick_up` | `69` Aller chercher quelqu'un ou reprendre quelqu'un à un mode de transport (sans info présence personne) | – | – | – |
| `other` | `91` Autres motifs | `98` Autre motif | `90` Autre lieu | – |

Notes:

- EMC² / EDGT / EDVM / EMD: code `52` is set to `shopping:tour_no_purchase` when the number of
  stops of the tour is defined (the purpose is then known to be « lèche-vitrines »).
- EMC² / EDGT / EDVM / EMD: the shopping codes `31` to `35` are also used to define the shop type
  ([`origin_shop_type`](format/trips.md#origin_shop_type) and
  [`destination_shop_type`](format/trips.md#destination_shop_type)).
  The same applies to EMP2019 codes `2.1` and `2.2`.
- EGT2020: missing purposes are set to `home:main`.
- EMP2019: code `9999` (no answer) is mapped to null.

## Purpose groups (EMG2023)

The EMG2023 survey does not define detailed purposes, only purpose groups.
The table below shows, for each MobiSurvStd purpose group (variables
[`origin_purpose_group`](format/trips.md#origin_purpose_group) and
[`destination_purpose_group`](format/trips.md#destination_purpose_group) of trips), the original
EMG2023 modalities that are mapped to it.
For the other survey types, the purpose group is directly deduced from the detailed purpose.

| Purpose group | EMG2023 |
| --- | --- |
| `home` | `DOMICILE` Retour au domicile |
| `work` | `AFF PRO` Affaires professionnelles, autre lieu de travail (réunion, tournée, colloque ...)<br>`TRAVAIL` Se rendre à son lieu de travail habituel |
| `education` | `ETUDES` Se rendre à son lieu d'enseignement habituel |
| `shopping` | `ACHAT` Achats ou courses : boulangerie, commerce, hypermarché ... |
| `task` | – |
| `leisure` | `LOISIRS` Activité de loisirs (cinéma, restaurant, sports, promenade …), voyage de tourisme |
| `escort` | `ACCOM` Accompagner, déposer ou aller chercher quelqu'un (à l'école, à la garderie, à la gare, au sport, au travail …) |
| `other` | `AUTRE` Visite à la famille ou à des amis, démarche administrative ou personnelle (recherche d'emploi, agence bancaire, avocat, garagiste …), aller déjeuner à midi à l'extérieur<br>`SANTE` Se rendre à l'hôpital, au cabinet médical ou infirmier, au laboratoire d'analyse, dentiste, kiné, pharmacie |

<style>
    .content main {
        max-width: 1400px;
    }
</style>

# Professional occupation comparison

Each survey uses its own list of professional occupations.
The table below shows, for each MobiSurvStd professional occupation (variables
[`professional_occupation`](format/persons.md#professional_occupation) and
[`detailed_professional_occupation`](format/persons.md#detailed_professional_occupation) of
persons), the original modalities that are mapped to it in each survey type.
See [how to read the comparison tables](comparison.md#how-to-read-the-comparison-tables).

The EMC², EDGT, EDVM, and EMD surveys all share the same professional-occupation definitions.

For EMP2019, the codes are those of variable `SITUA` (« Situation principale vis-à-vis du travail »).
For workers, they are combined with variable `TEMPTRAV` (« Temps de travail »).

For EMG2023, the professional occupation is read from the socio-professional category (`PCS_8`).
Therefore, the working time of workers is unknown and unemployed persons cannot be distinguished
from other inactive persons.

| `professional_occupation` | `detailed_professional_occupation` | EMC² / EDGT / EDVM / EMD | EGT2010 | EGT2020 | EMP2019 | EMG2023 |
| --- | --- | --- | --- | --- | --- | --- |
| `worker` | `worker:full_time` | `1` Travail à plein temps | `1` Exerce un métier, a un emploi, aide un membre de sa famille (emploi rémunéré) à plein temps (actif à plein temps) | `11` Emploi + à temps complet | `1` Occupe un emploi (TEMPTRAV `1` Temps complet) | – |
| `worker` | `worker:part_time` | `2` Travail à temps partiel | `2` Exerce un métier, a un emploi, aide un membre de sa famille (emploi rémunéré) à temps partiel (actif à temps partiel) | `12` Emploi + à temps partiel | `1` Occupe un emploi (TEMPTRAV `2` Temps partiel) | – |
| `worker` | `worker:unspecified` | – | – | `10` Emploi + non-réponse | `1` Occupe un emploi (TEMPTRAV non renseigné) | `1` Artisan, commerçant et chef d'entreprise<br>`2` Cadre et profession intellectuelle supérieure<br>`3` Professions Intermédiaires<br>`4` Employés<br>`5` Ouvriers |
| `student` | `student:apprenticeship` | `3` Formation en alternance (apprentissage, professionnalisation), stage | `4` Elève d'un centre d'apprentissage avec contrat de qualification | `20` Apprentissage sous contrat ou stage rémunéré | `2` Apprenti sous contrat ou stagiaire rémunéré | – |
| `student` | `student:higher` | `4` Étudiant | `3` Etudiant | `32` Etudiant ou stage non rémunéré | – | – |
| `student` | `student:primary_or_secondary` | `5` Scolaire jusqu'au bac | `5` Elève du primaire ou du secondaire | `31` Scolaire (école, collège, lycée) ou stage non rémunéré | – | – |
| `student` | `student:unspecified` | – | – | – | `3` Étudiant, élève, en formation ou stagiaire non rémunéré | `7` Étudiant ou lycée |
| `other` | `other:unemployed` | `6` Chômeur, recherche un emploi | `6` Chômeur ayant déjà travaillé<br>`8` Chômeur n'ayant jamais travaillé | `40` Chômage (inscrit ou non à Pôle Emploi) | `4` Chômeur | – |
| `other` | `other:retired` | `7` Retraité | `7` Retraité, ancien salarié, retiré des affaires | `50` Retraite ou pré-retraite (ancien salarié ou ancien indépendant) | `5` Retraité | `6` Retraité ou pré-retraité |
| `other` | `other:homemaker` | `8` Reste au foyer | `9` Reste au foyer, personne sans profession | `60` Femme ou homme au foyer | `6` Femme ou homme au foyer | – |
| `other` | `other:unspecified` | `9` Autre | `0` Inactif, pensionné | `90` Autre | `7` Inactif pour cause d'invalidité<br>`8` Autre situation d'inactivité | `8` Au chômage ou en inactivité |

Notes:

- `professional_occupation` is always equal to the first part of `detailed_professional_occupation`.
- EMC² / EDGT / EDVM / EMD: some persons are reclassified when their occupation is inconsistent
  with their [`student_group`](format/persons.md#student_group) and age (e.g., in Nice 2009,
  Toulouse 2013, Douai 2015, and Strasbourg 2009).
- EGT2020: persons whose socio-professional group is "Retraités" are always classified as
  `other:retired`.
- EMP2019: persons with no `SITUA` value but who are studying (`ETUDIE` = 1) are classified as
  `student:unspecified`.

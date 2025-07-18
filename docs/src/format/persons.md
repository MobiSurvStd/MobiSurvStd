# Persons

Sort order: `person_id`

## Indexing

### `person_id`

Unique identifier of the person.

- **Type:** UInt32
- **Guarantees:**
  - Values range from 1 to the number of persons.

### `household_id`

Identifier of the household the person belongs to.

- **Type:** UInt32
- **Guarantees:**
  - The value is not null.
  - There exists a household with this `household_id`.
  - The values are stored in increasing order (i.e., the persons from households with a smaller id
    are shown first).

### `person_index`

Index of the person within the household's persons.

- **Type:** UInt8
- **Guarantees:**
  - The value is not null.
  - Values are unique *within a household* and range from 1 to the number of persons in the
    household.
  - The values are stored in increasing order *within a household* (i.e., the persons with smaller
    indices are shown first).

### `original_person_id`

Identifier of the person in the original data.

- **Type:** Struct whose fields depend on the survey

## Demographic characteristics

### `reference_person_link`

Link of the person relative to the reference person of the household.

- **Modalities:**
  - `"reference_person"`: this person is the reference person of the household
  - `"spouse"`: this person is the spouse (husband or wife) of the reference person
  - `"child"`: this person is a child of the reference person
  - `"roommate_or_tenant"`: this person is a roommate or tenant in the household, with no family
    link to the reference person
  - `"other:relative"`: this person is a relative of the reference person (but not spouse or child)
  - `"other:non_relative"`: other link to the reference person (excluding relatives)
- **Guarantees:**
  - If the values are not null for all persons within a household, then there is exactly
    one person defined as the `"reference_person"` for this household.

### `resident_type`

Whether the person is living in the household home for most of the year.

- **Modalities:**
  - `"permanent_resident"`: the person is living in the household for most of the year
  - `"mostly_weekends"`: the person is usually only living in the household during weekends (with
    another location during weekdays for work or study reasons)
  - `"mostly_weekdays"`: the person is usually only living in the household during weekdays (for
    work or study reasons)

### `woman`

Whether the person is a woman.

- **Type:** Boolean

### `age`

Age of the person.

- **Type:** UInt8
- **Guarantees:**
  - The value is not larger than 125.
  - Persons whose `reference_person_link` is `"child"` are not older than the household reference
    person.

### `age_class`

Age of the person in 7 classes.

- **Modalities:**
  - `"17-"`: 17 or less
  - `"18-24"`: 18 to 24
  - `"25-34"`: 25 to 34
  - `"35-49"`: 35 to 49
  - `"50-64"`: 50 to 64
  - `"65-74"`: 65 to 74
  - `"75+"`: 75 or more
- **Guarantees:**
  - The class is compatible with the value of `age`.

### `age_class_code`

Age of the person in 7 classes.

Value 1 is for `"17-"`, 2 is for `"18-24"`, ..., 7 is for `"75+"`.

- **Type:** UInt8
- **Guarantees:**
  - The value is consistent with `age_class`.

### `education_level`

Highest education level reached by the person.

Note that given the diversity of the surveys regarding this question, some modalities might have
different meanings depending on the survey (e.g., `"primary"` can mean either that the person did
go to school after primary education or that their highest diploma earned is "Certificat d'études
primaires").
Also see [`detailed_education_level`](#detailed_education_level).

- **Modalities:**
  - `"no_studies_or_no_diploma"`: the person did no go to school or did not get any diploma
  - `"primary"`: the person has stopped going to school after primary education ("école primaire")
    or their highest diploma is "Certificat d'études primaires"
  - `"secondary:no_bac"`: the person has stopped going to school after middle-school ("collège") or
    high-school ("lycée") and did not get the baccalauréat
  - `"secondary:bac"`: the person has stopped going to school after high-school ("lycée") with
    the baccalauréat diploma
  - `"higher:at_most_bac+2"`: the person has stopped going to school after at most 2 years of
    higher education
  - `"higher:at_least_bac+3"`: the person has stopped going to school after at least 3 years of
    higher education

### `detailed_education_level`

Highest education level reached by the person, in detailed categories.

The modalities try to reproduce as best as possible the large diversity of the modalities observed
in the surveys without having too many modalities and without losing too much information.

- **Modalities:**
  - `"no_studies"`: the person did not go to school
  - `"no_diploma"`: the person did not get any diploma
  - `"primary:unspecified"`: the person has stopped going to school after primary education ("école
    primaire"), it is unknown whether they get the "Certificat d'études primaires"
  - `"primary:CEP"`: the person's highest diploma is the "Certificat d'études primaires"
  - `"secondary:no_bac:college"`: the person has stopped going to school after middle-school
    ("collège") or their highest diploma is "Brevet des collèges"
  - `"secondary:no_bac:CAP/BEP"`: the person's highest diploma is "CAP", "BEP", or an equivalent
    diploma
  - `"secondary:bac:techno_or_pro"`: the person's highest diploma is "Baccalauréat
    technologique", "Baccalauréat professionnel", or an equivalent diploma
  - `"secondary:bac:general"`: the person's highest diploma is "Baccalauréat général"
  - `"secondary:bac:unspecified"`: the person's highest diploma is "Baccalauréat" (without further
    specification)
  - `"higher:at_most_bac+2:DEUG"`: the person's highest diploma is "DEUG" (BAC+2)
  - `"higher:at_most_bac+2:BTS/DUT"`: the person's highest diploma is "BTS", "DUT", or an equivalent
    diploma (BAC+2)
  - `"higher:at_most_bac+2:paramedical_social"`: the person's highest diploma is at BAC+2 level
    ("formation paramédical et social")
  - `"higher:at_most_bac+2:unspecified"`: the person's highest diploma is at BAC+2 level
    (unspecified diploma)
  - `"higher:at_least_bac+3:universite"`: the person's highest diploma is at least BAC+3 in a
    university ("Licence", "Maîtrise", "Master", "DEA", "DESS", "Doctorat")
  - `"higher:at_least_bac+3:ecole"`: the person's highest diploma is at least BAC+3 in a "Grande
    École"
  - `"higher:at_least_bac+3:unspecified"`: the person's highest diploma is at least BAC+3 (without
    further specification)
  - `"higher:bac+3_or_+4"`: the person's highest diploma is at level BAC+3 or BAC+4
  - `"higher:at_least_bac+5"`: the person's highest diploma is at least BAC+5

## Occupancy

### `professional_occupation`

Professional status of the person.

Note these categories cannot represent some mixed situations (e.g., students with week-end jobs,
students in apprenticeship, retired people with small jobs).
Also see `detailed_professional_occupation` and `secondary_professional_occupation` for more
details.

- **Modalities:**
  - `"worker"`: the person has a full-time or part-time job
  - `"student"`: the person is a student
  - `"other"`: other status
- **Guarantees:**
  - The value is `"student"` *if and only if* `education_level` is `"in_school"`

### `detailed_professional_occupation`

Detailed professional status of the person.

- **Modalities:**
  - `"worker:full_time"`: the person has a full-time job
  - `"worker:part_time"`: the person has a part-time job
  - `"worker:unspecified"`: the person has a job with no further specification
  - `"student:primary_or_secondary"`: the person is a student in primary or secondary education
  - `"student:higher"`: the person is a student in higher education ("enseignement supérieur")
  - `"student:apprenticeship"`: the person is in apprenticeship training
  - `"student:unspecified"`: the person is a student (unspecifide level)
  - `"other:unemployed"`: the person is unemployed, looking for a job
  - `"other:retired"`: the person is retired
  - `"other:homemaker"`: the person is not working and not looking for a job
  - `"other:unspecified"`: other unspecified situation
- **Guarantees:**
  - The values are consistent with `professional_occupation`.

### `secondary_professional_occupation`

Secondary professional occupation of the person (if any).

This is useful for students with part-time student job or workers with continuous training
("formation continue") for example.

- **Modalities:**
  - `"work"`
  - `"education"`
- **Guarantees:**
  - The value is not `"work"` if `"professional_occupation"` is `"worker"`
  - The value is not `"education"` if `"professional_occupation"` is `"student"`

## Work status

### `pcs_group`

Group of "Professions et Catégories Socioprofessionnelles" the person belongs to.

The groups are defined by
[INSEE](https://www.insee.fr/fr/information/6208292).
Some surveys follow the
[INSEE 2003 definition](https://www.insee.fr/fr/metadonnees/pcs2003/categorieSocioprofessionnelleAgregee/1),
while others follow the
[2020 definition](https://www.insee.fr/fr/metadonnees/pcs2020/groupeSocioprofessionnel/1).
This means that the two last groups ("retraités" and
"autres_personnes_sans_activité_professionnelle") might not be used for some surveys.
The `detailed_professional_occupation` variable should be used instead if you need to access job
status.
Note that unemployed and retired people might still be assigned to the group corresponding to their
previous jobs.

- **Modalities:**
  - `"agriculteurs_exploitants"`
  - `"artisans_commerçants_chefs_d'entreprise"`
  - `"cadres_et_professions_intellectuelles_supérieures"`
  - `"professions_intermédiaires"`
  - `"employés"`
  - `"ouvriers"`
  - `"retraités"`
  - `"autres_personnes_sans_activité_professionnelle"`
- **Guarantees:**
  - If the `professional_occupation` is `"student"`, then `pcs_group` is null.

### `pcs_group_code`

Code of the group of "Professions et Catégories Socioprofessionnelles" the person belongs to.

The codes follow the
[2003 definition of the groups](https://www.insee.fr/fr/metadonnees/pcs2003/categorieSocioprofessionnelleAgregee/1).

- **Type:** UInt8
- **Guarantees:**
  - All values are between 1 and 8.
  - The values are consistent with variable `pcs_group` (e.g., value is 5 if and only if
    `pcs_group` is `"employés"`).
  - The value is null *if and only if* `pcs_group` is `"no_answer"` or null.

### `pcs_category_code2020`

Code of the category of "Professions et Catégories Socioprofessionnelles" the person belongs to.

This variable is used when the codes from the survey follow the
[INSEE 2020 definition](https://www.insee.fr/fr/metadonnees/pcs2020/groupeSocioprofessionnel/1).

- **Type:** UInt8
- **Guarantees:**
  - Possible values: 10, 21, 22, 23, 31, 33, 34, 35, 37, 38, 42, 43, 44, 45, 46, 47, 47, 52, 53,
    54, 55, 56, 62, 63, 64, 65, 67, 68, 69.
  - If `pcs_group_code` is null, then the value is null.
  - If the value is not null, then its first digit is equal to the value of `pcs_group_code`.

### `pcs_category_code2003`

Code of the category of "Professions et Catégories Socioprofessionnelles" the person belongs to.

This variable is used when the codes from the survey follow the
[INSEE 2003 definition](https://www.insee.fr/fr/metadonnees/pcs2003/categorieSocioprofessionnelleAgregee/1).

- **Type:** UInt8
- **Guarantees:**
  - Possible values: 10, 21, 22, 23, 31, 32, 36, 41, 46, 47, 48, 51, 54, 55, 56, 61, 66, 69, 71,
    72, 73, 76, 81, 82.
  - If `pcs_group_code` is null, then the value is null.
  - If the value is not null, then its first digit is equal to the value of `pcs_group_code`.

## Workplace location

### `work_only_at_home`

Whether the person works only at home.

- **Type:** Boolean
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.

### `workplace_singularity`

Whether the person has a unique, fixed workplace location.

- **Modalities:**
  - `"unique:outside"`: the person has a unique workplace location, outside home
  - `"unique:home"`: the person is working only at home
  - `"variable"`: the person has multiple usual workplace location or no usual workplace location
    (e.g., moving from client to client)
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - If `work_only_at_home` is true, then the value is `"unique:home"`.

### `work_lng`

Longitude of the usual workplace.

The accuracy depends on the survey type.
For EGT surveys, the coordinates are guaranteed to be within 100 meters of the actual location.
For other surveys, the coordinates represent the centroid of `work_detailed_zone` (or the exact
coordinates defined by `work_special_location` when it is non-null).

- **Type:** Float64

### `work_lat`

Latitude of the usual workplace.

See [`work_lng`](#work_lng) for details on the accuracy of the value.

- **Type:** Float64

### `work_special_location`

Identifier of the special location where the person usually works.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - The work special location intersects with the work detailed zone, draw zone, and INSEE zone
    (only checked if the zones are known).
  - If `work_only_at_home` is true, then the value is null.

### `work_detailed_zone`

Identifier of the detailed zone where the person usually works.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - The work detailed zone intersects with the work draw zone and INSEE zone (only checked if the
    zones are known).
  - If `work_only_at_home` is true, then the value is null.

### `work_draw_zone`

Identifier of the draw zone where the person usually works.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - The work draw zone intersects with the work INSEE zone (only checked if the zones are known).
  - If `work_only_at_home` is true, then the value is null.

### `work_insee`

INSEE code of the municipality where the person usually works.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - String is a [valid INSEE code](TODO).
  - If `work_only_at_home` is true, then the value is null.

### `work_insee_name`

Name of the municipality where the person usually works.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.

### `work_dep`

_Département_ code of the usual workplace.

- **Type:** String
- **Guarantees:**
  - The value is a valid _département_ code.
  - If `work_insee` is not null, then the value is equal to the _département_ of the work INSEE
    municipality.

### `work_dep_name`

Name of the _département_ of the usual workplace.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `work_dep`.

### `work_nuts2`

NUTS 2 code of the usual workplace.

In France, NUTS 2 corresponds to the 22 old administrative regions (and 5 overseas departments).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 2 code.
  - If `work_dep` is not null, then the value is equal to the NUTS 2 code corresponding to the work
    _département_.

### `work_nuts2_name`

Name of the NUTS 2 region of the usual workplace.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `work_nuts2`.

### `work_nuts1`

NUTS 1 code of the usual workplace.

In France, NUTS 1 corresponds to the 13 administrative regions (and 1 overseas region).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 1 code.
  - If `work_nuts2` is not null, then the value is equal to the NUTS 1 code corresponding to the
    work NUTS 2.

### `work_nuts1_name`

Name of the NUTS 1 region of the usual workplace.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `work_nuts1`.

## Work commute

### `work_commute_euclidean_distance_km`

Euclidean distance, in kilometers, between the person's home location and usual work location.

- **Type:** Float64
- **Guarantees:**
  - All values are non-negative.
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - If `work_only_at_home` is false, then the value is zero.

### `has_car_for_work_commute`

Whether the person has a car they can use to commute to work.

- **Modalities:**
  - `"yes:full_commute"`: the person has a car that they use for the full trip
  - `"yes:partial_commute"`: the person has a car that they use for a part of the trip
  - `"yes:not_used"`: the person has a car that they could use to commute to work but they do not
  - `"yes:partial_or_not_used"`: the person has a car but it is not used or only for a part of the
    trip
  - `"yes:full_or_partial"`: the person has a car that they use partially or fully to commute to
    work
  - `"no"`: no
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - If `work_only_at_home` is true, then the value is null.

### `telework`

Whether and frequency at which the person teleworks.

Note that persons who reported to only work at home (e.g., many farmers) are not considered to be
telework each day (the value is null for them).

- **Modalities:**
  - `"yes:weekly"`: the person teleworks at least once a week
  - `"yes:monthly"`: the person teleworks at least once a month
  - `"yes:occasionally"`: the person teleworks but only occasionally (less than once a month)
  - `"no"`: the person never telework
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - If `work_only_at_home` is true, then the value is null.

## Workplace parking

### `work_car_parking`

Whether the person has access to a car parking spot at the usual work location.

- **Modalities:**
  - `"yes:reserved"`: the person has (or could have) a reserved car spot at work
  - `"yes:many_spots"`: the person can park their car at work because they are many spots available
  - `"yes:compatible_schedule"`: the person can park their car at work because their work schedule
    allow them to easily find spots
  - `"yes:unspecified"`: the person can park their car at work (no further specification)
  - `"no"`: the person cannot park their car at work
  - `"dont_know"`: the person does not know whether they can park their car at work
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - If `work_only_at_home` is true, then the value is null.

### `work_bicycle_parking`

Whether the person has access to a bicycle parking spot at the usual work location.

- **Modalities:**
  - `"yes:on_site:sheltered"`: the person has access to a sheltered bicycle parking at workplace
  - `"yes:on_site:unsheltered"`: the person has access to an unsheltered bicycle parking at
    workplace
  - `"yes:on_site"`: the person has access to a bicycle parking at workplace (unknown whether it is
    sheltered)
  - `"yes:nearby:sheltered"`: the person has access to a sheltered bicycle parking nearby work
  - `"yes:nearby:unsheltered"`: the person has access to an unsheltered bicycle parking nearby work
  - `"yes:nearby"`: the person has access to a bicycle parking nearby work (unknown whether it is
    sheltered)
  - `"no"`: the person does not have access to a bicycle parking at workplace or nearby work
  - `"no_answer"`: the person did not answer that question
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - If `work_only_at_home` is true, then the value is null.

## Student status

### `student_group`

Group indicating the current education level for students.

- **Modalities:**
  - `"primaire"`: "maternelle" or primary school
  - `"collège"`: middle-school
  - `"lycée"`: high-school
  - `"supérieur"`: higher education
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - The values are consistent with `detailed_professional_occupation` (`"student:higher"` implies
    `"supérieur"`; `"student:primary_or_secondary"` implies `"primaire"`, `"collège"`, or `"lycée"`;
    `"student:apprenticeship"` implies `"lycée"` or `"supérieur"`).

### `student_category`

Category indicating the detailed current education level for students.

- **Modalities:**
  - `"maternelle"`
  - `"primaire"`: "école primaire" excluding "maternelle"
  - `"collège:6e"`
  - `"collège:5e"`
  - `"collège:4e"`
  - `"collège:3e"`
  - `"collège:SEGPA"`
  - `"lycée:seconde"`
  - `"lycée:première"`
  - `"lycée:terminale"`
  - `"lycée:CAP"`: "lycée professionelle ou CFA, préparation du CAP"
  - `"supérieur:technique"`: "IUT / BTS"
  - `"supérieur:prépa1"`: "Classe préparatoire, première année"
  - `"supérieur:prépa2"`: "Classe préparatoire, deuxième année"
  - `"supérieur:BAC+1"`: Other higher education training, "niveau BAC+1"
  - `"supérieur:BAC+2"`: Other higher education training, "niveau BAC+2"
  - `"supérieur:BAC+3"`: Other higher education training, "niveau BAC+3"
  - `"supérieur:BAC+4"`: Other higher education training, "niveau BAC+4"
  - `"supérieur:BAC+5"`: Other higher education training, "niveau BAC+5"
  - `"supérieur:BAC+6&+"`: Other higher education training, "niveau BAC+6 et plus"
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - The values are consistent with `student_group` (e.g., if `student_category` is
    `"collège:6e"`, then `student_group` is `"collège"`).

## Study location

### `study_only_at_home`

Whether the person studies only at home.

- **Type:** Boolean
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.

### `study_lng`

Longitude of the usual study location.

The accuracy depends on the survey type.
For EGT surveys, the coordinates are guaranteed to be within 100 meters of the actual location.
For other surveys, the coordinates represent the centroid of `study_detailed_zone` (or the exact
coordinates defined by `study_special_location` when it is non-null).

- **Type:** Float64

### `study_lat`

Latitude of the usual study_location.

See [`study_lng`](#study_lng) for details on the accuracy of the value.

- **Type:** Float64

### `study_special_location`

Identifier of the special location zone where the person usually studies.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - The study special location intersects with the study detailed zone, draw zone, and INSEE zone
    (only checked if the zones are known).
  - If `study_only_at_home` is true, then the value is null.

### `study_detailed_zone`

Identifier of the detailed zone where the person usually studies.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - The study detailed zone intersects with the study draw zone and INSEE zone (only checked if the
    zones are known).
  - If `study_only_at_home` is true, then the value is null.

### `study_draw_zone`

Identifier of the draw zone where the person usually studies.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - The study draw zone intersects with the study INSEE zone (only checked if the zones are known).
  - If `study_only_at_home` is true, then the value is null.

### `study_insee`

INSEE code of the municipality where the person usually studies.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - String is a [valid INSEE code](TODO).
  - If `study_only_at_home` is true, then the value is null.

### `study_insee_name`

Name of the municipality where the person usually studies.

- **Type:** String
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.

### `study_dep`

_Département_ code of the usual study location.

- **Type:** String
- **Guarantees:**
  - The value is a valid _département_ code.
  - If `study_insee` is not null, then the value is equal to the _département_ of the study INSEE
    municipality.

### `study_dep_name`

Name of the _département_ of the usual study location.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `study_dep`.

### `study_nuts2`

NUTS 2 code of the usual study location.

In France, NUTS 2 corresponds to the 22 old administrative regions (and 5 overseas departments).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 2 code.
  - If `study_dep` is not null, then the value is equal to the NUTS 2 code corresponding to the
    study _département_.

### `study_nuts2_name`

Name of the NUTS 2 region of the usual study location.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `study_nuts2`.

### `study_nuts1`

NUTS 1 code of the usual study location.

In France, NUTS 1 corresponds to the 13 administrative regions (and 1 overseas region).

- **Type:** String
- **Guarantees:**
  - The value is a valid NUTS 1 code.
  - If `study_nuts2` is not null, then the value is equal to the NUTS 1 code corresponding to the
    study NUTS 2.

### `study_nuts1_name`

Name of the NUTS 1 region of the usual study location.

- **Type:** String
- **Guarantees:**
  - The value is consistent with `study_nuts1`.

## Study commute

### `study_commute_euclidean_distance_km`

Euclidean distance, in kilometers, between the person's home location and usual study location.

- **Type:** Float64
- **Guarantees:**
  - All values are non-negative.
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - If `study_only_at_home` is false, then the value is zero.

### `has_car_for_study_commute`

Whether the person has a car they can use to commute to study.

- **Modalities:**
  - `"yes:full_commute"`: the person has a car that they use for the full trip
  - `"yes:partial_commute"`: the person has a car that they use for a part of the trip
  - `"yes:not_used"`: the person has a car that they could use to commute to study but they do not
  - `"yes:partial_or_not_used"`: the person has a car but it is not used or only for a part of the
    trip
  - `"yes:full_or_partial"`: the person has a car that they use partially or fully to commute to
    study
  - `"no"`: no
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - If `study_only_at_home` is true, then the value is null.

## Study location parking

### `study_car_parking`

Whether the person has access to a car parking spot at the usual study location.

- **Modalities:**
  - `"yes:reserved"`: the person has (or could have) a reserved car spot at study
  - `"yes:many_spots"`: the person can park their car at study because they are many spots available
  - `"yes:compatible_schedule"`: the person can park their car at study because their study schedule
    allow them to easily find spots
  - `"no"`: the person cannot park their car at study
  - `"dont_know"`: the person does not know whether they can park their car at study
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - If `study_only_at_home` is true, then the value is null.

### `study_bicycle_parking`

Whether the person has access to a bicycle parking spot at the usual study location.

- **Modalities:**
  - `"yes:on_site:sheltered"`: the person has access to a sheltered bicycle parking at study
    location
  - `"yes:on_site:unsheltered"`: the person has access to an unsheltered bicycle parking at study
    location
  - `"yes:on_site"`: the person has access to a bicycle parking at study location (unknown whether
    it is sheltered)
  - `"yes:nearby:sheltered"`: the person has access to a sheltered bicycle parking nearby study
    location
  - `"yes:nearby:unsheltered"`: the person has access to an unsheltered bicycle parking nearby study
    location
  - `"yes:nearby"`: the person has access to a bicycle parking nearby study location (unknown
    whether it is sheltered)
  - `"no"`: the person does not have access to a bicycle parking at or near study location
  - `"no_answer"`: the person did not answer that question
- **Guarantees:**
  - If `professional_occupation` is *not* `"student"`, then the value is null.
  - If `study_only_at_home` is true, then the value is null.

## Mobility

### `has_driving_license`

Whether the person has a driving license (for car vehicles).

- **Modalities:**
  - `"yes"`: the person has a driving license
  - `"no"`: the person does not have a driving license
  - `"in_progress"`: the person is taking driving lessons or learning through accompanied driving
    ("conduite accompagnée")
- **Guarantees:**
  - If the value is `"yes"`, then the person is not younger than 17.
  - If the value is `"in_progress"`, then the person is not younger than 15.

### `has_motorcycle_driving_license`

Whether the person has a driving license for motorcycles.

- **Modalities:**
  - `"yes"`: the person has a driving license for motorcycles
  - `"no"`: the person does not have a driving license for motorcycles
  - `"in_progress"`: the person is taking driving lessons
- **Guarantees:**
  - If the value is `"yes"`, then the person is not younger than 17.
  - If the value is `"in_progress"`, then the person is not younger than 15.

### `has_public_transit_subscription`

Whether the person owns a valid public-transit subscription.

Usually, the question asked is "did you have a valid public-transit subscription yesterday?" which
means that the subscription was valid during the person's surveyed trips.

- **Type:** Boolean

### `public_transit_subscription`

Type of public-transit subscription that the person owns.

- **Modalities:**
  - `"yes:free"`: the person owns a free public-transit subscription
  - `"yes:paid:with_employer_contribution"`, the person owns a paid public-transit subscription
    that is partially borne by the employer
  - `"yes:paid:without_employer_contribution"`, the person owns a paid public-transit subscription
    that is not borne by the employer
  - `"yes:paid"`: the person owns a paid public-transit subscription (with unspecified cost
    bearing)
  - `"yes:unspecified"`: the person owns a public-transit subscription with unspecified cost)
  - `"no"`: the person does not own a public-transit subscription
- **Guarantees:**
  - The values are consistent with `has_public_transit_subscription`.

### `has_car_sharing_subscription`

Whether the person has a subscription for a car-sharing service ("autopartage").

- **Type:** Boolean

### `car_sharing_subscription`

Type of car-sharing service subscription that the person has.

- **Modalities:**
  - `"yes:organized"`: the person has a car-sharing subscription for a short-term rental service
    proposed by a firm or a public organization (e.g., Citiz)
  - `"yes:peer_to_peer"`: the person has a car-sharing subscription for a peer-to-peer service
    ("partage entre particuliers")
  - `"yes:unspecified"`: the person has a car-sharing subscription (no further details)
  - `"no"`: the person does not have a car-sharing subscription
- **Guarantees:**
  - The values are consistent with `has_car_sharing_subscription`.

### `has_bike_sharing_subscription`

Whether the person has a subscription for a bike-sharing service ("vélo libre service").

- **Type:** Boolean

### `has_travel_inconvenience`

Whether the person has reported having travel inconveniences (e.g., wheelchair, blindness,
pregnancy).

- **Type:** Boolean

## Trip survey

### `is_surveyed`

Whether the person was surveyed for their trips over a day (usually the previous day of the
interview).

Note that a surveyed person might have no trip if they did not travel during that day.

- **Type:** Boolean
- **Guarantees:**
  - The value is not null.
  - When set to `false`, there is no trip and leg for this person.

### `traveled_during_surveyed_day`

Whether the person performed at least one trip during the surveyed day (usually the day before
the interview).

- **Modalities:**
  - `"yes"`: the person did at least one trip
  - `"no"`: the person did not travel
  - `"away"`: the person was away from home during that day
- **Guarantees:**
  - The value is null *if and only if* `is_surveyed` is false.
  - There is at least one trip defined for this person if the value is `"yes"`.
  - There is no trip defined for this person if the value is `"no"` or `"away"`.

### `worked_during_surveyed_day`

Whether the person worked during the surveyd day (usually the day before the interview).

- **Modalities:**
  - `"yes:outside"`: the person worked outside from home
  - `"yes:home:usual"`: the person worked from home, as usual
  - `"yes:home:telework"`: the person teleworked
  - `"yes:home:other"`: the person worked from home for another reason than telework
  - `"yes:unspecified"`: the person worked (with no specification where)
  - `"no:weekday"`: the person never work during that weekday
  - `"no:reason"`: the person did not work *exceptionally* due to holidays, sickness, strike, or any
    other reason
  - `"no:unspecified"`: the person did not work, for unspecified reason
- **Guarantees:**
  - If `professional_occupation` is *not* `"worker"`, then the value is null.
  - If the value is `"yes:home:usual"`, then `work_only_at_home` must be true.
  - If the value is `"no:weekday"`, then there is not trip with work purpose for that person (for
    `"no:reason"` and `"no:unspecified"` it might happen that the person went to work and realised
    that they could not work because of a strike for example).
  - If the value is `"yes:outside"` and `is_surveyed` is true, then there is at least one trip with
    work purpose for that person.

### `nb_trips`

Number of trips that the person performed.

- **Type:** UInt8
- **Guarantees:**
  - The value is null *if and only if* `is_surveyed` is false.
  - The value is equal to the number of trips in `trips.parquet` for the person.
  - If `traveled_during_surveyed_day` is `"no"` or `"away"`, then the value is zero.
  - If `traveled_during_surveyed_day` is `"yes"`, then the value is positive.

## Sample weights

### `sample_weight_all`

Sample weight of the person among all the persons interviewed.

The sum of the values is supposed to be approximately equal to the number of persons in the survey
area.

- **Type:** Float64
- **Guarantees:**
  - The value is non-negative.

### `sample_weight_surveyed`

Sample weight of the person among all the persons whose trips were surveyed.

The sum of the values is supposed to be approximately equal to the number of persons in the survey
area.
Note that the sum of `sample_weight_surveyed` might differ from the sum of `sample_weight_all`
because the former usually excludes children below 5.

- **Type:** Float64
- **Guarantees:**
  - The value is non-negative.
  - If `is_surveyed` is false, then the value is null.

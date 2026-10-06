<style>
    .content main {
        max-width: 1400px;
    }
</style>

# Education level comparison

Each survey uses its own list of education levels.
The table below shows, for each MobiSurvStd education level (variables
[`education_level`](format/persons.md#education_level) and
[`detailed_education_level`](format/persons.md#detailed_education_level) of persons), the original
modalities that are mapped to it in each survey type.
Original modalities are given as `code` followed by the label from the survey's documentation (in
French).
EMG2023 has no codes: the labels are the values found in the data.
A dash (–) means that the survey type has no modality mapped to that education level.

Note that the surveys do not ask the same question:

- The EMC², EDGT, EDVM, EMD, and EGT2010 surveys ask for the last **school stage** attended
  (e.g., « Primaire », « Secondaire, titulaire du bac »).
- The EGT2020, EMP2019, and EMG2023 surveys ask for the highest **diploma** obtained (e.g., «
  Certificat d'études primaires », « CAP, BEP et équivalent »).

The EMC², EDGT, EDVM, and EMD surveys all share the same education-level definitions.

| `education_level` | `detailed_education_level` | EMC² / EDGT / EDVM / EMD | EGT2010 | EGT2020 | EMP2019 | EMG2023 |
| --- | --- | --- | --- | --- | --- | --- |
| `no_studies_or_no_diploma` | `no_studies` | `9` Pas d'études | `0` La personne n'est jamais allée à l'école même en primaire | – | – | – |
| `no_studies_or_no_diploma` | `no_diploma` | – | – | `0` Aucun diplôme | `71` Aucun diplôme reconnu | Aucun diplôme |
| `primary` | `primary:unspecified` | `1` Primaire | `2` Primaire | – | – | – |
| `primary` | `primary:CEP` | – | – | – | `70` Certificat d'études primaires | – |
| `secondary:no_bac` | `secondary:no_bac:college` | `2` Secondaire (de la 6e à la 3e, CAP) | `3` Secondaire (de la 6ème à la 3ème) | `1` CEP (certificat d'études primaires), BEPC, brevet élémentaire, brevet des collèges | `60` BEPC, DNB, brevet des collèges | Brevet des collèges ou de niveau équivalent |
| `secondary:no_bac` | `secondary:no_bac:CAP/BEP` | `3` Secondaire (de la seconde à la terminale, BEP), non titulaire du bac<br>`7` Apprentissage (école primaire ou secondaire uniquement) | `4` Secondaire (de la seconde à la terminale, BEP, CAP) et non titulaire du bac | `2` CAP, BEP ou diplôme de niveau équivalent | `50` CAP, BEP et équivalent | CAP, BEP ou de niveau équivalent |
| `secondary:no_bac` | *(null)* | `93` Secondaire (sans distinction titulaire du bac ou non)<br>`97` Apprentissage (sans distinction) | – | – | – | – |
| `secondary:bac` | `secondary:bac:techno_or_pro` | – | – | – | `42` Bac technologique, professionnel ou équivalent | – |
| `secondary:bac` | `secondary:bac:general` | – | – | – | `41` Bac général | – |
| `secondary:bac` | `secondary:bac:unspecified` | `4` Secondaire, titulaire du bac | `5` Secondaire et titulaire du bac | `3` Baccalauréat général ou technologique ou diplôme de niveau équivalent | – | Baccalauréat général, technologique ou de niveau équivalent |
| `higher:at_most_bac+2` | `higher:at_most_bac+2:paramedical_social` | – | `9` Autre formation postsecondaire (sanitaire et social ou artistique, …) | – | `33` Diplôme paramédical et social niveau bac+2 | – |
| `higher:at_most_bac+2` | `higher:at_most_bac+2:BTS/DUT` | – | – | – | `31` DUT, BTS et équivalent | – |
| `higher:at_most_bac+2` | `higher:at_most_bac+2:DEUG` | – | – | – | `30` Deug | – |
| `higher:at_most_bac+2` | `higher:at_most_bac+2:unspecified` | `5` Supérieur jusqu'à bac + 2<br>`8` Apprentissage (études supérieures) | `6` Supérieur jusqu'à BAC + 2 (y compris BTS - DUT) | `4` BAC+2 : BTS, DUT, DEUG… | – | Bac +2 : BTS, DUT, DEUG… |
| `higher:at_least_bac+3` | `higher:at_least_bac+3:ecole` | – | – | – | `11` École niveau licence et au-delà | – |
| `higher:at_least_bac+3` | `higher:at_least_bac+3:universite` | – | – | – | `10` Doctorat, master, licence et équivalent | – |
| `higher:at_least_bac+3` | `higher:at_least_bac+3:unspecified` | `6` Supérieur, bac + 3 et plus | `7` Supérieur BAC + 3 et plus | – | – | – |
| `higher:at_least_bac+3` | `higher:bac+3_or_+4` | – | – | `5` BAC+3 ou BAC+4 : licence, licence pro, maîtrise… | – | Bac +3 ou +4 : Licence, Licence professionnelle, Maîtrise, Master 1… |
| `higher:at_least_bac+3` | `higher:at_least_bac+5` | – | – | `6` Bac+5 et plus : Master, DEA, DESS, diplôme de grandes écoles, doctorat… | – | Bac + 5 et plus : Master 2, DEA, DESS, Diplôme de grande école, Doctorat… |

Notes:

- The education level is always null for students
  ([`professional_occupation`](format/persons.md#professional_occupation) is `"student"`).
- The following modalities are mapped to null:
  - EMC² / EDGT / EDVM / EMD: `0` En cours de scolarité, `90` autre (egt)
  - EGT2010: `1` Personne en cours de scolarité, `8` Apprentissage (54 observations only)
  - EMP2019: empty values (« Autre : Indéterminé »)
  - EMG2023: NR (no answer)
- Some mappings are assumptions made by MobiSurvStd:
  - EMC² / EDGT / EDVM / EMD: code `2` includes CAP but is mapped to `secondary:no_bac:college`.
  - EMC² / EDGT / EDVM / EMD: apprenticeship codes `7` and `8` are assumed to be at most CAP / BEP
    and at most BAC+2, respectively.
  - EMC² / EDGT / EDVM / EMD: codes `93` and `97` are assumed to be `secondary:no_bac`, with no
    detailed level.
  - EGT2020: code `1` includes the « Certificat d'études primaires » but is mapped to
    `secondary:no_bac:college` (the « Brevet des collèges » is assumed to be the most common answer).

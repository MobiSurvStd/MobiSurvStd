# MobiSurvStd

## MobiSurvStd: Mobility Surveys Standardized

MobiSurvStd is an easy-to-use Python command line interface to convert any French mobility survey
(EMC², EGT, EMD, etc.) to a unique standardized format.

## Mobility Surveys in France

In France, despite recent efforts by CEREMA to create a standard format for mobility surveys – with
the EMC² surveys – various formats co-exist:

- **EMC²** (Enquête mobilité certifiée CEREMA): mobility surveys for many French territories (since
  2018);
- **EGT H2020** (Enquête Globale Transport, Île-de-France Mobilités): mobility survey for
  Île-de-France (2018–2020; incomplete due to COVID-19);
- **EMP** (Enquête mobilité des personnes, SDES): national mobility survey (2019).

Also surveys based on previous formats are still in use today:

- **EDVM** (Enquêtes Déplacements Villes Moyennes, CEREMA): mobility surveys for medium-size cities
  (until 2018);
- **EDGT** (Enquêtes Déplacements Grands Territoires, CEREMA): mobility surveys for periphery areas
  (until 2018);
- **EGT 2010** (Enquête Globale Transport, Île-de-France Mobilités): previous version of the
  Île-de-France mobility survey;
- **ENTD** (Enquête nationale transports et déplacements, SDES): former national mobility survey
  (2008).

## Why MobiSurvStd?

The existing formats all have the same drawbacks:

- Data are sorted in CSV files which are not always straightforward to read (Which separator?
  Which encoding? What are the variable datatypes?).
- Variable names and modalities are not always clear (e.g., in the EMC² format, variable "P2"
  represents the gender of the person, with modality 1 for a man and 2 for a woman).
- Joining two datasets is hard and not well documented (e.g., in the EMC² format, to join the
  persons with their household, the variables to use are "METH", "ZFM" and "ECH" for the households
  and "DMET", "ZFD" and "ECH" for the persons).

Additionally, when working with different territories / periods, it is often necessary to write a
similar code multiple times due to the extistence of different formats.

MobiSurvStd solves all these issues by being able to convert all survey formats to a well-defined
format.

Check TODO to see how MobiSurvStd can help you write fewer and cleaner codes.

## How to use?

Install the library with

```bash
pip install mobisurvstd
```

Convert your survey to the standard format with

```bash
python -m mobisurvstd -i original_survey/ -o std_survey/
```

## What about other countries?

MobiSurvStd covers only French mobility survey formats.
If other countries have similar survey formats, they might be easily integrated into MobiSurvStd.
If you found a format that could be integrated, feel free to open an issue on GitHub.

## Issues and Contributions

If you think you found a bug, if you have a suggestion, or if you want to integrate a new format,
feel free to open an issue on GitHub and even to open a Pull Request.

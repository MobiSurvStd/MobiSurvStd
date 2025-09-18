# Miscellaneous

## Note on zones

In MobiSurvStd, locations (e.g., home, work, origin, destination) are specified as special location,
detailed zone, draw zone, INSEE municipality, département, NUTS2 and NUTS1.
Unfortunately, given the poor quality of some spatial definitions, MobiSurvStd cannot guarantee the
consistency between all these locations, i.e., the home detailed zone of a household might not be
within its home INSEE municipality.

## INSEE codes

The original surveys and MobiSurvStd rely heavily on the INSEE "Codes Commune" which are used to
identify the French municipalities ("Communes").
These INSEE codes are all composed of 5 characters, with the first 2 characters representing the
"département" where the municipality is located (the first 3 characters for oversea territories).
The 5 characters are all numbers, except for Corsica municipalities ("2A" and "2B" are the codes for
the Corsica départements).
The municipality corresponding to each code can be found on the
[INSEE website](https://www.insee.fr/fr/information/7766585).

The INSEE code can also represent the "arrondissements municipaux" for Paris, Lyon and Marseille.
Depending on the surveys, either the municipalities or the "arrondissements municipaux" are used to
define the locations.

Note that some special codes are also used by MobiSurvStd to identify foreign countries.
They all start by "99":

- `"99001"`: Sea / Ocean
- `"99010"`: Germany
- `"99020"`: Andorra
- `"99030"`: Belgium
- `"99040"`: Spain
- `"99050"`: Italy
- `"99060"`: Luxembourg
- `"99070"`: Monaco
- `"99080"`: United-Kingdom
- `"99090"`: Switzerland
- `"99100"`: Other country (not listed above)
- `"99200"`: *Any* country

## External data and cache

MobiSurvStd relies on external data from INSEE (municipality densities, AAV definitions) and IGN
(municipality boundaries) to generate all required variables for certain surveys.
On first access, MobiSurvStd automatically downloads this data from official sources and stores it
in a local cache.
This cache speeds up subsequent operations by avoiding repeated downloads.

The cache is usually located at:

- Windows: `[UserDir]\AppData\Local\mobisurvstd\Cache`
- Linux: `~/.cache/mobisurvstd`

The cache typically uses less than 200 MB of storage. To clear it, run:

```python
python -m mobisurvstd --clear-cache
```

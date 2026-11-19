[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

[![GPL v3][license-shield]][license-url]
[![PyPI][pypi-shield]][pypi-url]
[![DOI][doi-shield]][doi-url]

# Nemobi

> [!NOTE]
> **MobiSurvStd s'appelle désormais Nemobi.** À partir de la version 2.0.0, le paquet est publié
> sous le nom `nemobi` (`pip install nemobi`, `import nemobi`, commande `nemobi`). Les enquêtes
> standardisées avec MobiSurvStd restent lisibles par Nemobi. Voir le
> [guide de migration](https://nemobi.lucasjavaudin.com/migration.html) (en anglais).

*Un outil pour convertir les enquêtes de mobilité françaises (EMC², EGT, EMP, etc.) dans un format
standardisé, clair et homogène.*

📚 [Documentation](https://nemobi.lucasjavaudin.com)

## Sommaire
- [Introduction](#introduction)
- [Contexte](#contexte)
- [Pourquoi utiliser Nemobi ?](#pourquoi-utiliser-nemobi-)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Enquêtes prises en charge](#enquêtes-prises-en-charge)
- [Mentions légales](#mentions-légales)
- [Contribuer](#contribuer)

## Introduction

Nemobi (*Normalisation des enquêtes mobilités*) est un outil simple à utiliser, qui permet de convertir plusieurs enquêtes de mobilité
françaises dans un format unique et standardisé.

---

## Contexte

En France, plusieurs formats d'enquêtes coexistent encore, même si des efforts de normalisation ont
été faits par le CEREMA avec les enquêtes EMC².

Voici quelques exemples :

- **EMC²** : Enquêtes mobilité certifiées CEREMA (depuis 2018)
- **EGT H2020** : Enquête globale transport en Île-de-France (2018–2020)
- **EMP** : Enquête mobilité des personnes (enquête nationale, 2019)
- **EMG** : Enquête par GPS en Île-de-France (2022–2023)
- et d'autres plus anciennes : EDVM, EDGT, EMD, ENTD, etc.

---

## Pourquoi utiliser Nemobi ?

💡 Les problèmes fréquents des enquêtes actuelles :

- Fichiers CSV difficiles à lire : mauvais séparateur, encodage inconnu...
- Variables mal nommées (ex. : "P2" = genre, 1 = homme, 2 = femme)
- Fichiers à relier entre eux sans documentation
- Codes à adapter pour chaque nouvelle enquête ou territoire

✅ Nemobi simplifie tout cela en vous proposant un
[format Parquet commun et documenté](https://nemobi.lucasjavaudin.com/format/index.html).

👉 [Exemple concret ici](https://nemobi.lucasjavaudin.com/problem-example.html)

---

## Installation

1. Ouvrez un terminal (ou invite de commandes Windows)
2. Installez l’outil avec cette commande :

```bash
pip install nemobi
```

---

## Utilisation

1. Téléchargez l’enquête EMP 2019 [ici](https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019)
2. Lancez la commande suivante :

```bash
nemobi emp_2019_donnees_individuelles_anonymisees_novembre2024.zip standardized_emp2019
```

Un dossier `standardized_emp2019` sera créé avec les fichiers Parquet au format standard.

Ces fichiers Parquet peuvent ensuite être analysés avec, par exemple, les librairies Python
[polars](https://pola.rs/) et [pandas](https://pandas.pydata.org) ou le package R
[arrow](https://arrow.apache.org/docs/r/).

🔎 Consultez le [Guide utilisateur](https://nemobi.lucasjavaudin.com/howto.html) pour plus
de détails.

📌 **Citation**

Si vous utiliser Nemobi dans une publication ou un projet, merci de citer l'outil comme
suit :
```
Javaudin, L. (2025). Nemobi. Zenodo. https://doi.org/10.5281/zenodo.17710203
```
Un fichier [CITATION.bib](CITATION.bib) est également disponible.


---

## Étude de cas : Usage du vélo

Le graphe ci-dessous représente la part de déplacements à vélo pour chaque enquête EMC², EDGT, EDVM,
EMD et EGT.
La couleur des cercles représente le numbre moyen de vélo par ménage enquêté.
La taille des cercles représente le nombre estimé de déplacements dans l'aire d'enquête.

Le graphe a été généré à partir du code [analyses/bicycle_shares.py](analyses/bicycle_shares.py).

![Graphe de la parte de déplacements à vélo par enquête](https://raw.githubusercontent.com/LucasJavaudin/Nemobi/main/docs/src/images/bicycle_shares.png)

La carte ci-dessous représente la part de déplacements à vélo au sein des municipalités.
Seules les municipalités avec plus de 30 déplacements observés sont représentées.

La carte a été générée à partir du code
[analyses/bicycle_shares_by_insee.py](analyses/bicycle_shares_by_insee.py).

![Carte de la parte de déplacements à vélo par municipalité](https://raw.githubusercontent.com/LucasJavaudin/Nemobi/main/docs/src/images/bicycle_shares_by_insee.png)

---

## Enquêtes prises en charge

Actuellement :

* `emp2019`
* `emc2`
* `emg2023` (merci à @sebhoerl)
* `egt2020`
* `egt2010`
* `edgt` (y compris [la version open-data de Nantes 2015](https://www.data.gouv.fr/datasets/enquete-deplacements-2015-en-loire-atlantique))
* `edvm`
* `emd`

Plus d'information dans [la documentation](https://nemobi.lucasjavaudin.com/surveys.html).

![Cartes de toutes les enquêtes locales prises en charge](https://raw.githubusercontent.com/LucasJavaudin/Nemobi/main/docs/src/images/survey_map.jpg)

À venir : `entd`

📬 Vous connaissez un autre format ? Ouvrez un ticket sur GitHub.

---

## Mentions légales

<span style="color:red">
⚠️ <strong>Nemobi ne rend pas les données anonymes.</strong>
Si vous travaillez avec des données confidentielles (par exemple EMC² ou EGT), vous devez respecter
les mêmes règles de confidentialité que pour les données originales.

En particulier, <strong>vous ne devez pas partager les données standardisées</strong> si votre
contrat ne vous y autorise pas.
</span>

---

## Contribuer

Une idée ? Un bug ? Une nouvelle enquête à intégrer ?
👉 Ouvrez une *issue* ou une *pull request* sur GitHub.

Merci pour votre contribution 🚀

[contributors-shield]: https://img.shields.io/github/contributors/LucasJavaudin/Nemobi.svg?style=for-the-badge
[contributors-url]: https://github.com/LucasJavaudin/Nemobi/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/LucasJavaudin/Nemobi.svg?style=for-the-badge
[forks-url]: https://github.com/LucasJavaudin/Nemobi/network/members
[stars-shield]: https://img.shields.io/github/stars/LucasJavaudin/Nemobi.svg?style=for-the-badge
[stars-url]: https://github.com/LucasJavaudin/Nemobi/stargazers
[issues-shield]: https://img.shields.io/github/issues/LucasJavaudin/Nemobi.svg?style=for-the-badge
[issues-url]: https://github.com/LucasJavaudin/Nemobi/issues
[license-shield]: https://img.shields.io/github/license/LucasJavaudin/Nemobi.svg?style=for-the-badge
[license-url]: https://github.com/LucasJavaudin/Nemobi/blob/master/LICENSE.txt
[doi-shield]: https://img.shields.io/badge/doi-10.5281/zenodo.17422994-blue?style=for-the-badge
[doi-url]: https://doi.org/10.5281/zenodo.17422993
[pypi-shield]: https://img.shields.io/pypi/v/nemobi.svg?style=for-the-badge
[pypi-url]: https://pypi.org/project/nemobi/

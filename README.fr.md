# MobiSurvStd

*Un outil pour convertir les enquêtes de mobilité françaises (EMC², EGT, EMP, etc.) dans un format
standardisé, clair et homogène.*

📚 [Documentation](https://mobisurvstd.github.io/MobiSurvStd)
📦 [Voir sur PyPI](https://pypi.org/project/mobisurvstd/)

## Sommaire
- [Introduction](#introduction)
- [Contexte](#contexte)
- [Pourquoi utiliser MobiSurvStd ?](#pourquoi-utiliser-mobisurvstd-)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Enquêtes prises en charge](#enquêtes-prises-en-charge)
- [Mentions légales](#mentions-légales)
- [Contribuer](#contribuer)

## Introduction

MobiSurvStd est un outil simple à utiliser, qui permet de convertir plusieurs enquêtes de mobilité
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
- et d'autres plus anciennes : EDVM, EDGT, ENTD, etc.

---

## Pourquoi utiliser MobiSurvStd ?

💡 Les problèmes fréquents des enquêtes actuelles :

- Fichiers CSV difficiles à lire : mauvais séparateur, encodage inconnu...
- Variables mal nommées (ex. : "P2" = genre, 1 = homme, 2 = femme)
- Fichiers à relier entre eux sans documentation
- Codes à adapter pour chaque nouvelle enquête ou territoire

✅ MobiSurvStd simplifie tout cela en vous proposant un
[format Parquet commun et documenté](https://mobisurvstd.github.io/MobiSurvStd/format/index.html).

👉 [Exemple concret ici](https://mobisurvstd.github.io/MobiSurvStd/problem-example.html)

---

## Installation

1. Ouvrez un terminal (ou invite de commandes Windows)
2. Installez l’outil avec cette commande :

```bash
pip install mobisurvstd
```

---

## Utilisation

1. Téléchargez l’enquête EMP 2019 [ici](https://www.statistiques.developpement-durable.gouv.fr/resultats-detailles-de-lenquete-mobilite-des-personnes-de-2019)
2. Lancez la commande suivante :

```bash
python -m mobisurvstd emp_2019_donnees_individuelles_anonymisees_novembre2024.zip standardized_emp2019 --survey-type emp2019
```

Un dossier `standardized_emp2019` sera créé avec les fichiers Parquet au format standard.

Ces fichiers Parquet peuvent ensuite être analysés avec, par exemple, les librairies Python
[polars](https://pola.rs/) et [pandas](https://pandas.pydata.org) ou le package R
[arrow](https://arrow.apache.org/docs/r/).

🔎 Consultez le [Guide utilisateur](https://mobisurvstd.github.io/MobiSurvStd/howto.html) pour plus
de détails.

---

## Étude de cas : Usage du vélo

Le graphe ci-dessous représente la part de déplacements à vélo pour chaque enquête EMC², EDGT, EDVM
et EGT.
La couleur des cercles représente le numbre moyen de vélo par ménage enquêté.
La taille des cercles représente le nombre estimé de déplacements dans l'aire d'enquête.

Le graphe a été généré à partir du code [analyses/bicycle_shares.py](analyses/bicycle_shares.py).

![Graphe de la parte de déplacements à vélo par enquête](https://raw.githubusercontent.com/MobiSurvStd/MobiSurvStd/main/docs/src/images/bicycle_shares.png)

La carte ci-dessous représente la part de déplacements à vélo au sein des municipalités.
Seules les municipalités avec plus de 30 déplacements observés sont représentées.

La carte a été générée à partir du code
[analyses/bicycle_shares_by_insee.py](analyses/bicycle_shares_by_insee.py).

![Carte de la parte de déplacements à vélo par municipalité](https://raw.githubusercontent.com/MobiSurvStd/MobiSurvStd/main/docs/src/images/bicycle_shares_by_insee.png)

---

## Enquêtes prises en charge

Actuellement :

* `emp2019`
* `emc2`
* `egt2020`
* `egt2010`
* `edgt`
* `edvm`

À venir : `entd`, `emg`

📬 Vous connaissez un autre format ? Ouvrez un ticket sur GitHub.

---

## Mentions légales

<span style="color:red">
⚠️ <strong>MobiSurvStd ne rend pas les données anonymes.</strong>
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

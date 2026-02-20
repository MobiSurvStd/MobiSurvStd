import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import polars as pl

from mobisurvstd import SurveyDataReader, read_many
from mobisurvstd.schema import (
    CAR_SCHEMA,
    HOUSEHOLD_SCHEMA,
    LEG_SCHEMA,
    MOTORCYCLE_SCHEMA,
    PERSON_SCHEMA,
    TRIP_SCHEMA,
)
from mobisurvstd.schema.common import Variable
from mobisurvstd.schema.guarantees import Null

SURVEY_TYPES = [
    "EMC2",
    "EMP2019",
    "EGT2020",
    "EMG2023",
    "EDGT",
    "EDVM",
    "EGT2010",
    "EMD",
]

GROUPS = {
    "households": HOUSEHOLD_SCHEMA,
    "persons": PERSON_SCHEMA,
    "trips": TRIP_SCHEMA,
    "legs": LEG_SCHEMA,
    "cars": CAR_SCHEMA,
    "motorcycles": MOTORCYCLE_SCHEMA,
}


def count_nulls(data: SurveyDataReader):
    name = data.metadata["name"]
    print(name)
    output = dict()
    output["name"] = name
    output["type"] = data.metadata["type"]
    for name, schema in GROUPS.items():
        df = getattr(data, name)
        if df.is_empty():
            # Some surveys have empty cars or motorcyles.
            output[name] = {var.name: {"null_count": 0, "max_defined": 0} for var in schema}
            output[name]["count"] = 0
        else:
            output[name] = count_nulls_df(df, schema)
    return [output]


def count_nulls_df(df: pl.DataFrame, schema: list[Variable]):
    output = dict()
    n = len(df)
    output["count"] = n
    for var in schema:
        assert var.name in df.columns
        output[var.name] = dict()
        output[var.name]["null_count"] = df[var.name].null_count()
        filters = list(map(lambda g: g.when, filter(lambda g: isinstance(g, Null), var.guarantees)))
        if filters:
            m = n - len(df.filter(pl.any_horizontal(*filters)))
        else:
            m = n
        output[var.name]["max_defined"] = m
    return output


output = read_many("./output/all/", count_nulls, lambda x, y: x + y)

tables = dict()
for name, schema in GROUPS.items():
    print(name)
    data = dict()
    data["variable"] = list(map(lambda var: var.name, schema))
    for type_code in SURVEY_TYPES:
        data[type_code] = list()
        survey_output = list(filter(lambda d: d["type"] == type_code, output))
        n = sum(map(lambda d: d[name]["count"], survey_output))
        for var in schema:
            null_counts = sum(map(lambda d: d[name][var.name]["null_count"], survey_output))
            max_defined = sum(map(lambda d: d[name][var.name]["max_defined"], survey_output))
            # The NULL that have to be NULL should not be counted.
            true_null_counts = null_counts - (n - max_defined)
            if max_defined == 0:
                # Prevent Div/0.
                ratio = 1.0
            else:
                ratio = true_null_counts / max_defined
            assert ratio >= 0.0
            assert ratio <= 1.0
            data[type_code].append(1.0 - ratio)
    df = pl.DataFrame(data)
    tables[name] = df


def get_text_color(rgb):
    r, g, b, _ = rgb
    brightness = r * 77 + g * 150 + b * 29
    return "black" if brightness > 128 else "white"


htmls = dict()
cmap = plt.get_cmap("RdYlGn")

for name in GROUPS.keys():
    html = '<div class="table-wrapper">\n'
    html += "<table>\n"
    html += "<thead>\n"
    html += "<tr>\n"
    html += "<th></th>\n"
    for survey_type in SURVEY_TYPES:
        html += f"<th>{survey_type}</th>\n"
    html += "</tr>\n"
    html += "</thead>\n"
    html += "<tbody>\n"
    for row in tables[name].iter_rows(named=True):
        quality_variable = all(row[t] > 0.9 for t in SURVEY_TYPES)
        html += "<tr>\n"
        if quality_variable:
            html += f"<td><strong>{row['variable']}</strong></td>\n"
        else:
            html += f"<td>{row['variable']}</td>\n"
        for survey_type in SURVEY_TYPES:
            # Get the share of defined values.
            value = row[survey_type]
            rgb = cmap(value)
            text_color = get_text_color(rgb)
            background_color = mcolors.rgb2hex(rgb)
            html += f'<td style="background-color:{background_color};color:{text_color};text-align:center">\n'
            html += f"{value:.0%}\n"
            html += "</td>\n"
        html += "</tr>\n"
    html += "</tbody>\n"
    html += "</table>\n"
    html += "</div>\n"
    htmls[name] = html
    with open(f"docs/src/tables/{name}.html", "w") as f:
        f.write(html)

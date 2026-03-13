from pathlib import Path

import folium
import polars as pl

OUTPUT_DIR = Path("output/all/EGT2020")
HOUSEHOLD_ID = 2368

ORANGE = "#E69F00"
LIGHTBLUE = "#56B4E9"
GREEN = "#009E73"
YELLOW = "#F0E442"
BLUE = "#0072B2"
RED = "#D55E00"
PINK = "#CC79A7"
BLACK = "#000000"
PURPLE = "#9932CC"
TEAL = "#008080"

MODE_COLOR = {
    "walking": GREEN,
    "bicycle": YELLOW,
    "motorcycle": ORANGE,
    "car_driver": RED,
    "car_passenger": PINK,
    "public_transit": PURPLE,
    "other": BLACK,
}


def fmt_time(mins: int):
    h = mins // 60
    m = mins % 60
    return f"{h:02}:{m:02}"


persons = pl.read_parquet(OUTPUT_DIR / "persons.parquet")
trips = pl.read_parquet(OUTPUT_DIR / "trips.parquet")
legs = pl.read_parquet(OUTPUT_DIR / "legs.parquet")

persons = persons.filter(household_id=HOUSEHOLD_ID)
trips = trips.filter(household_id=HOUSEHOLD_ID)
legs = legs.filter(household_id=HOUSEHOLD_ID)
legs = legs.join(trips.select("trip_id", "trip_index"), on="trip_id")

# Initialize map centered on trips' centroid.
center_lng = trips.select(pl.col("origin_lng").mean()).item()
center_lat = trips.select(pl.col("origin_lat").mean()).item()

m = folium.Map(location=[center_lat, center_lng], zoom_start=12, control_scale=True)

# Drop legs with no coordinates.
nb_legs = len(legs)
legs = legs.drop_nulls(subset=["start_lng", "start_lat", "end_lng", "end_lat"])
if len(legs) < nb_legs:
    print(f"Warning: {len(legs)} / {nb_legs} dropped (no coordinates)")

# Draw legs.
for row in persons.iter_rows(named=True):
    person_id = row["person_id"]
    if row["woman"]:
        characs = "woman"
    else:
        characs = "man"
    characs += f", {row['age']}"
    fg = folium.FeatureGroup(name=f"Person {person_id} ({characs})", show=True)
    for row in legs.filter(person_id=person_id).iter_rows(named=True):
        coords = [(row["start_lat"], row["start_lng"]), (row["end_lat"], row["end_lng"])]
        color = MODE_COLOR.get(row["mode_group"], "gray")
        folium.PolyLine(
            locations=coords,
            color=color,
            weight=8,
            opacity=0.8,
            tooltip=(
                f"Person: {row['person_id']}<br>"
                f"Trip: {row['trip_id']}<br>"
                f"Trip index: {row['trip_index']}<br>"
                f"Leg: {row['leg_index']}<br>"
                f"Mode group: {row['mode_group']}<br>"
                f"Mode: {row['mode']}"
            ),
        ).add_to(fg)

    # Draw origins / destinations.
    for row in trips.filter(person_id=person_id).iter_rows(named=True):
        # Origin
        tooltip = f"Trip {row['trip_index']} Origin<br>Purpose: {row['origin_purpose_group']}<br>"
        if row["origin_activity_duration"]:
            tooltip += (
                f"From: {fmt_time(row['departure_time'] - row['origin_activity_duration'])}<br>"
                f"To: {fmt_time(row['departure_time'])}<br>"
                f"Duration: {row['origin_activity_duration']}min"
            )
        else:
            tooltip += f"Left at: {fmt_time(row['departure_time'])}"
        folium.CircleMarker(
            location=(row["origin_lat"], row["origin_lng"]),
            radius=10,
            color="green",
            fill=True,
            fill_opacity=0.9,
            tooltip=tooltip,
        ).add_to(fg)
        # # Destination
        # folium.CircleMarker(
        #     location=(row["destination_lat"], row["destination_lng"]),
        #     radius=4,
        #     color="red",
        #     fill=True,
        #     fill_opacity=0.9,
        #     tooltip=(
        #         f"Trip {row['trip_index']} Destination<br>"
        #         f"Purpose: {row['destination_purpose_group']}<br>"
        #         f"Arrival: {row['arrival_time']}"
        #     ),
        # ).add_to(fg)

    fg.add_to(m)

# Add legend.
legend_html = """
<div style="
position: fixed;
bottom: 50px; left: 50px; width: 200px; height: auto;
background-color: white;
border:2px solid grey;
z-index:9999;
font-size:14px;
padding:10px;
">
<b>Mode Groups</b><br>
"""

for mg, color in MODE_COLOR.items():
    legend_html += f'<i style="background:{color};width:10px;height:10px;float:left;margin-right:5px;"></i>{mg}<br>'

legend_html += "</div>"

m.get_root().html.add_child(folium.Element(legend_html))

# Fit bounds.
bounds = [
    [
        trips.select(pl.col("origin_lat").min()).item(),
        trips.select(pl.col("origin_lng").min()).item(),
    ],
    [
        trips.select(pl.col("origin_lat").max()).item(),
        trips.select(pl.col("origin_lng").max()).item(),
    ],
]

m.fit_bounds(bounds)

folium.LayerControl(collapsed=False).add_to(m)

m.save("tmp.html")

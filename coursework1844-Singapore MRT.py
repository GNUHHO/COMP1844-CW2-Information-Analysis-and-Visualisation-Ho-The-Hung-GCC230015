import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Button

#DATA SETUP AND CALCULATIONS
print("Singapore MRT Network Visualisation")
print("Which unit do you want to display distances in?")
print("1: Kilometres (km)")
print("2: Miles (mi)")
unit_choice = input("Enter 1 or 2: ")

while unit_choice not in ["1", "2"]:
    print("Invalid input, please enter 1 or 2")
    unit_choice = input("Enter 1 or 2: ")

# Set the default unit based on user input
current_unit = "km" if unit_choice == "1" else "mi"
print(f"Current unit: {current_unit}")

# Function to calculate distance using the Haversine formula (implemented with NumPy)
def get_distance(lon1, lat1, lon2, lat2):
    R = 6371  # Earth's radius in km
    lat1, lat2, lon1, lon2 = np.radians([lat1, lat2, lon1, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    distance_km = round(float(R * c), 2)
    return distance_km, round(distance_km * 0.621371, 2)

# Accurate coordinates extracted from LTA GIS Data
station_coords = {
    # NSL red
    "Bishan":           (103.848144, 1.350839), "Braddell":         (103.846798, 1.340472),
    "Toa Payoh":        (103.847502, 1.332629), "Novena":           (103.843826, 1.320441),
    "Newton":           (103.837985, 1.312320), "Orchard":          (103.832241, 1.303981),
    "Somerset":         (103.839075, 1.300260), "Dhoby Ghaut":      (103.846115, 1.298701),
    "City Hall":        (103.852586, 1.292936), "Raffles Place":    (103.851462, 1.284126),
    # EWL green 
    "Bugis":            (103.855706, 1.300465), "Outram Park":      (103.839126, 1.281405),
    "Tanjong Pagar":    (103.845864, 1.276521),
    "Tiong Bahru":      (103.827019, 1.286193), "Queenstown":       (103.805884, 1.294861),
    "Commonwealth":     (103.798305, 1.302439), "Buona Vista":      (103.790192, 1.307183),
    # CCL orange 
    "Serangoon":        (103.873575, 1.349708), "Lorong Chuan":     (103.864152, 1.351612),
    "Marymount":        (103.839423, 1.348707), "Caldecott":        (103.839530, 1.337675),
    "Botanic Gardens":  (103.814983, 1.322110), "Farrer Road":      (103.807586, 1.317511),
    "Holland Village":  (103.796192, 1.311835),
    # NEL purple
    "Woodleigh":        (103.870818, 1.339190), "Potong Pasir":     (103.869056, 1.331380),
    "Boon Keng":        (103.861687, 1.319396), "Farrer Park":      (103.854177, 1.312360),
    "Little India":     (103.849647, 1.306800), "Clarke Quay":      (103.846555, 1.288386),
    "Chinatown":        (103.843427, 1.284360),
    # DTL blue
    "Beauty World":     (103.775794, 1.341223), "King Albert Park": (103.783807, 1.335665),
    "Sixth Avenue":     (103.797246, 1.330786), "Tan Kah Kee":      (103.807322, 1.325883),
    "Stevens":          (103.826024, 1.320066), "Rochor":           (103.852422, 1.303916),
}

# Configuration for curved track segments 
curved_edges_config = {
    tuple(sorted(["Beauty World", "King Albert Park"])): 0.15, 
    tuple(sorted(["Sixth Avenue", "Tan Kah Kee"])): -0.1, 
    tuple(sorted(["Tan Kah Kee", "Botanic Gardens"])): -0.1, 
    tuple(sorted(["Botanic Gardens", "Stevens"])): -0.05, 
    tuple(sorted(["Stevens", "Newton"])): 0.1, 
    tuple(sorted(["Newton", "Little India"])): -0.05, 
    tuple(sorted(["Toa Payoh", "Novena"])): 0.3, 
    tuple(sorted(["Newton", "Orchard"])): 0.3,         
    tuple(sorted(["Bishan", "Marymount"])): 0.2,        
    tuple(sorted(["Marymount", "Caldecott"])): -0.1, 
    tuple(sorted(["Caldecott", "Botanic Gardens"])): -0.4, 
    tuple(sorted(["Botanic Gardens", "Farrer Road"])): 0.05, 
    tuple(sorted(["Farrer Road", "Holland Village"])): 0.07, 
    tuple(sorted(["Holland Village", "Buona Vista"])): -0.1, 
    tuple(sorted(["Bugis", "City Hall"])): 0.15,
    tuple(sorted(["City Hall", "Raffles Place"])): -0.15,
    tuple(sorted(["Buona Vista", "Commonwealth"])): -0.15,
    tuple(sorted(["Commonwealth", "Queenstown"])): -0.1,
    tuple(sorted(["Queenstown", "Tiong Bahru"])): 0.15,
    tuple(sorted(["Outram Park", "Tiong Bahru"])): 0.15,
    tuple(sorted(["Tanjong Pagar", "Outram Park"])): 0.15,
    tuple(sorted(["Tanjong Pagar", "Raffles Place"])): -0.15,
    tuple(sorted(["Orchard", "Somerset"])): 0.15,
    tuple(sorted(["Braddell", "Toa Payoh"])): 0.15,
    tuple(sorted(["Dhoby Ghaut", "City Hall"])): 0.15,
    tuple(sorted(["Bishan", "Lorong Chuan"])): 0.2,
    tuple(sorted(["Lorong Chuan", "Serangoon"])): -0.15,
    tuple(sorted(["Serangoon", "Woodleigh"])): 0.2,
    tuple(sorted(["Woodleigh", "Potong Pasir"])): 0.15,
    tuple(sorted(["Potong Pasir", "Boon Keng"])): 0.15,
    tuple(sorted(["Dhoby Ghaut", "Clarke Quay"])): 0.15,
}

#Manual adjustment for distance labels on STRAIGHT edges
edge_label_offsets = {
    tuple(sorted(["City Hall", "Raffles Place"])): 0.0035, # Push further out to avoid double lines
    tuple(sorted(["Dhoby Ghaut", "Somerset"])): -0.001,    # Push to opposite side
    tuple(sorted(["Outram Park", "Tiong Bahru"])): -0.002,
    tuple(sorted(["Dhoby Ghaut", "City Hall"])): -0.0015,
    tuple(sorted(["Rochor", "Bugis"])): 0.001,
    tuple(sorted(["Chinatown", "Outram Park"])): -0.002,
    tuple(sorted(["Little India", "Rochor"])): 0.003,
    tuple(sorted(["Farrer Park", "Little India"])): -0.002,
    tuple(sorted(["Sixth Avenue", "Tan Kah Kee"])): -0.002,
    tuple(sorted(["Tan Kah Kee", "Botanic Gardens"])): 0.001,
    tuple(sorted(["King Albert Park", "Sixth Avenue"])): -0.002,
    tuple(sorted(["Beauty World", "King Albert Park"])): -0.002,
    tuple(sorted(["Lorong Chuan", "Serangoon"])): -0.002,
    tuple(sorted(["Boon Keng", "Farrer Park"])): -0.002,
    tuple(sorted(["Botanic Gardens", "Stevens"])): 0.002,
    tuple(sorted(["Newton", "Little India"])): -0.002,
    tuple(sorted(["Newton", "Orchard"])): -0.002,
}

all_lines = {
    "North-South Line": ["Bishan", "Braddell", "Toa Payoh", "Novena", "Newton", "Orchard", "Somerset", "Dhoby Ghaut", "City Hall", "Raffles Place"],
    "East-West Line":   ["Bugis", "City Hall", "Raffles Place", "Tanjong Pagar", "Outram Park", "Tiong Bahru", "Queenstown", "Commonwealth", "Buona Vista"],
    "Circle Line":      ["Serangoon", "Lorong Chuan", "Bishan", "Marymount", "Caldecott", "Botanic Gardens", "Farrer Road", "Holland Village", "Buona Vista"],
    "North East Line":  ["Serangoon", "Woodleigh", "Potong Pasir", "Boon Keng", "Farrer Park", "Little India", "Dhoby Ghaut", "Clarke Quay","Chinatown", "Outram Park"],
    "Downtown Line":    ["Beauty World", "King Albert Park", "Sixth Avenue", "Tan Kah Kee", "Botanic Gardens", "Stevens", "Newton", "Little India", "Rochor", "Bugis"],
}

line_colours = {"North-South Line": "#D42E12", "East-West Line": "#009645", "Circle Line": "#FA9E0D", "North East Line": "#9B26AF", "Downtown Line": "#005EC4"}
line_short = {"North-South Line": "NSL", "East-West Line": "EWL", "Circle Line": "CCL", "North East Line": "NEL", "Downtown Line": "DTL"}

# Build the Graph
G = nx.MultiGraph()
edge_data = {}

for line_name, stations in all_lines.items():
    colour = line_colours[line_name]
    for i in range(len(stations) - 1):
        s1, s2 = stations[i], stations[i + 1]
        lon1, lat1 = station_coords[s1]
        lon2, lat2 = station_coords[s2]
        d_km, d_mi = get_distance(lon1, lat1, lon2, lat2)
        
        G.add_edge(s1, s2, line=line_name, colour=colour, distance_km=d_km, distance_miles=d_mi)
        
        key = tuple(sorted([s1, s2]))
        if key not in edge_data: 
            edge_data[key] = []
        edge_data[key].append({"line": line_name, "colour": colour, "d_km": d_km, "d_mi": d_mi})

# Identify interchange stations
station_line_count = {}
for line_name, stations in all_lines.items():
    for s in stations:
        if s not in station_line_count: 
            station_line_count[s] = []
        station_line_count[s].append(line_name)

interchange_stations = [s for s, lines in station_line_count.items() if len(lines) > 1]

# SIMPLE STATISTICS CALCULATIONS
edge_list = []
for u, v, data in G.edges(data=True):
    edge_list.append({
        "Line": data["line"],
        "KM": data["distance_km"],
        "MI": data["distance_miles"]
    })

df = pd.DataFrame(edge_list)

line_lengths_km = df.groupby("Line")["KM"].sum()
line_lengths_mi = df.groupby("Line")["MI"].sum()

num_lines = len(line_lengths_km)

total_km = round(line_lengths_km.sum(), 2)
total_mi = round(line_lengths_mi.sum(), 2)

avg_per_line_km = round(total_km / num_lines, 2)
avg_per_line_mi = round(total_mi / num_lines, 2)

avg_per_station_km = round(df["KM"].mean(), 2)
avg_per_station_mi = round(df["MI"].mean(), 2)

#UI SETUP
fig = plt.figure(figsize=(14, 9))
fig.patch.set_facecolor("white")

# Map Layer
ax_map = fig.add_axes([0.02, 0.02, 0.96, 0.92])
ax_map.axis("off")

# Stats Layer
ax_stats = fig.add_axes([0.15, 0.2, 0.7, 0.6])
ax_stats.set_visible(False) 

# DRAW THE MAP
lons = [station_coords[s][0] for s in station_coords]
lats = [station_coords[s][1] for s in station_coords]
ax_map.set_xlim(min(lons) - 0.014, max(lons) + 0.014)
ax_map.set_ylim(min(lats) - 0.010, max(lats) + 0.010)
ax_map.set_aspect("equal")

edge_text_objects = [] 

for key, edges in edge_data.items():
    s1, s2 = key
    x1, y1 = station_coords[s1]
    x2, y2 = station_coords[s2]
    num_edges = len(edges)

    dx, dy = x2 - x1, y2 - y1
    length = np.sqrt(dx**2 + dy**2)
    px, py = (-dy / length, dx / length) if length > 0 else (0, 1)

    for i, edge in enumerate(edges):
        offset = 0.00055 * (i - (num_edges - 1) / 2)
        x1_off, y1_off = x1 + px * offset, y1 + py * offset
        x2_off, y2_off = x2 + px * offset, y2 + py * offset

        pair_key = tuple(sorted([s1, s2]))
        if pair_key in curved_edges_config:
            rad = curved_edges_config[pair_key]
            curved_line = mpatches.FancyArrowPatch((x1_off, y1_off), (x2_off, y2_off),
                connectionstyle=f"arc3,rad={rad}", color=edge["colour"], linewidth=3.8, zorder=2, arrowstyle="-")
            ax_map.add_patch(curved_line)
        else:
            ax_map.plot([x1_off, x2_off], [y1_off, y2_off], color=edge["colour"], linewidth=3.8, solid_capstyle="round", zorder=2)

    # CALCULATE LABEL POSITION
    mid_x = (x1 + x2) / 2 
    mid_y = (y1 + y2) / 2 
    pair_key = tuple(sorted([s1, s2]))
    push_dist = edge_label_offsets.get(pair_key, 0.0025)
    
    mid_x += px * push_dist
    mid_y += py * push_dist

    if pair_key in curved_edges_config:
        rad = curved_edges_config[pair_key]
        mid_x += (rad * dy) / 2
        mid_y += (-rad * dx) / 2

    # Get the initial value based on the user's console input
    initial_val = edges[0]['d_km'] if current_unit == "km" else edges[0]['d_mi']
    txt_obj = ax_map.text(mid_x, mid_y, f"{initial_val} {current_unit}", fontsize=5.8, ha="center", va="center", color="#1a1a1a", zorder=6,
                bbox=dict(boxstyle="round,pad=0.14", facecolor="white", alpha=0.88, edgecolor="none"))
    edge_text_objects.append((txt_obj, edges[0]["d_km"], edges[0]["d_mi"]))

# Draw Stations
for station in station_coords:
    x, y = station_coords[station]
    if station in interchange_stations:
        ax_map.scatter(x, y, s=460, c="white", edgecolors="#111111", linewidths=2.5, zorder=8)
        ax_map.scatter(x, y, s=80, c="#111111", edgecolors="none", zorder=9)
    else:
        ax_map.scatter(x, y, s=180, c="white", edgecolors="#333333", linewidths=1.8, zorder=8)

# Manual offsets for station labels
label_offsets = {
    # NSL red
    "Newton":           (-0.0040, -0.0000), "Novena":           (0.0032, 0.0000),
    "Orchard":          (-0.0035, 0.0000),  "Somerset":         (-0.0045, 0.0000),
    "Dhoby Ghaut":      (-0.0060,  -0.0010), "City Hall":        ( 0.0050,  0.0000),
    "Raffles Place":    ( 0.0052, 0.0000), "Braddell":         ( 0.0033,  0.0000),
    "Toa Payoh":        ( 0.0035,  0.0000), "Bishan":           (-0.0020,  0.0023),
    # EWL green
    "Bugis":            ( 0.0035,  0.0000), "Outram Park":      (-0.0050, -0.0035),
    "Tiong Bahru":      (-0.0010, -0.0020), "Queenstown":       ( -0.0020, -0.0020),
    "Commonwealth":     ( -0.0030, -0.0020), "Buona Vista":      (-0.0055,  0.0000),
    "Tanjong Pagar":    (0.0000,  -0.0020), 
    # CCL orange
    "Serangoon":        ( 0.0045,  0.0010), "Lorong Chuan":     ( -0.0003,  0.0030),
    "Marymount":        (-0.0052,  0.0000), "Caldecott":        (-0.0036,  -0.0010),
    "Botanic Gardens":  (0.0035,  -0.0025), "Farrer Road":      (-0.0040, 0.0010),
    "Holland Village":  (0.0045, -0.0010),
    # NEL purple
    "Woodleigh":        ( 0.0040,  0.0000), "Potong Pasir":     ( 0.0052,  0.0000),
    "Boon Keng":        ( 0.0045,  0.0000), "Farrer Park":      ( 0.0045,  0.0000),
    "Little India":     (-0.0045, -0.0010), "Clarke Quay":      (-0.0035, 0.0008),
    "Chinatown":        ( 0.0035, -0.0010), "Outram Park":      (-0.0030, -0.0025),
    # DTL blue
    "Beauty World":     ( 0.0000,  0.0040), "King Albert Park": ( 0.0052,  0.0010),
    "Sixth Avenue":     ( 0.0042,  0.0015), "Tan Kah Kee":      (0.0040,  0.0000),
    "Stevens":          ( 0.0027,  0.0010), "Rochor":           ( 0.0034, 0.0004),
}

for station in station_coords:
    x, y = station_coords[station]
    if station in label_offsets:
        dx, dy = label_offsets[station]
    else:
        neighbours = list(set(G.neighbors(station)))
        if len(neighbours) > 0:
            avg_x = sum(station_coords[n][0] for n in neighbours) / len(neighbours)
            avg_y = sum(station_coords[n][1] for n in neighbours) / len(neighbours)
            vec_x, vec_y = x - avg_x, y - avg_y
            dist = np.sqrt(vec_x**2 + vec_y**2)
            dx, dy = ((vec_x / dist) * 0.0032, (vec_y / dist) * 0.0032) if dist > 0 else (0, 0.003)
        else:
            dx, dy = 0, 0.003

    font_weight = "bold" if station in interchange_stations else "normal"
    ax_map.text(x + dx, y + dy, station, fontsize=6.5, ha="center", va="center", fontweight=font_weight, zorder=10)

# Legend and Title
legend_handles = []
for line_name, colour in line_colours.items():
    h, = ax_map.plot([], [], color=colour, linewidth=3.8, label=f"{line_short[line_name]} - {line_name}")
    legend_handles.append(h)
legend_handles.append(ax_map.plot([], [], "o", markerfacecolor="white", markersize=11, markeredgecolor="#111111", markeredgewidth=2.2, label="Interchange")[0])
legend_handles.append(ax_map.plot([], [], "o", markerfacecolor="white", markersize=8, markeredgecolor="#333333", markeredgewidth=1.5, label="Station")[0])
ax_map.legend(handles=legend_handles, loc="lower left", fontsize=9.5, title="Key", title_fontsize=10.5, frameon=True)

map_title = ax_map.set_title(f"Singapore MRT Network - Central Section\n(Distances displayed in {current_unit})", fontsize=14, fontweight="bold", pad=16)


# DRAW THE BAR CHART
# Fetch the initial data based on the user's console input
initial_data = line_lengths_km if current_unit == "km" else line_lengths_mi
initial_total = total_km if current_unit == "km" else total_mi
initial_avg_line = avg_per_line_km if current_unit == "km" else avg_per_line_mi
initial_avg_station = avg_per_station_km if current_unit == "km" else avg_per_station_mi

bar_colors = [line_colours[line] for line in initial_data.index]
bars = ax_stats.bar(initial_data.index, initial_data.values, color=bar_colors, edgecolor="black")

ax_stats.set_ylim(0, max(initial_data.values) * 1.15)

stats_title = ax_stats.set_title(f"Total Length by MRT Line ({current_unit})", fontsize=14, fontweight="bold", pad=15)
ax_stats.set_xlabel("MRT Line", fontsize=11)
stats_ylabel = ax_stats.set_ylabel(f"Length ({current_unit})", fontsize=11)
ax_stats.tick_params(axis='x', labelsize=10)

bar_text_objects = []
for i, bar in enumerate(bars):
    val = round(initial_data.values[i], 2)
    txt_obj = ax_stats.text(bar.get_x() + bar.get_width()/2, val + 0.2, str(val), ha='center', va='bottom', fontsize=11)
    bar_text_objects.append(txt_obj)

summary_content = (
    f"SUMMARY\n"
    f"Total Network  : {initial_total} {current_unit}\n"
    f"Avg per Line   : {initial_avg_line} {current_unit}\n"
    f"Avg per Station: {initial_avg_station} {current_unit}"
)
box_style = dict(facecolor='white', edgecolor='black', alpha=0.9)
summary_box = ax_stats.text(0.98, 0.95, summary_content, transform=ax_stats.transAxes, 
                            fontsize=11, verticalalignment='top', horizontalalignment='right', bbox=box_style)


# PART 3: INTERACTIVE BUTTONS LOGIC
ax_btn_view = plt.axes([0.82, 0.03, 0.13, 0.05])
btn_view = Button(ax_btn_view, 'View Stats', color='lightgray')

def switch_view(event):
    is_map_showing = ax_map.get_visible()
    ax_map.set_visible(not is_map_showing)
    ax_stats.set_visible(is_map_showing)
    
    if is_map_showing:
        btn_view.label.set_text('Back to Map')
    else:
        btn_view.label.set_text('View Stats')
        
    fig.canvas.draw_idle()

btn_view.on_clicked(switch_view)

ax_btn_unit = plt.axes([0.65, 0.03, 0.15, 0.05])
# Button displays the *opposite* of the current unit
initial_btn_label = 'Switch to Miles' if current_unit == "km" else 'Switch to KM'
btn_unit = Button(ax_btn_unit, initial_btn_label, color='lightgray')

def toggle_unit(event):
    global current_unit
    
    if current_unit == "km":
        current_unit = "mi"
        btn_unit.label.set_text('Switch to KM')
        current_data = line_lengths_mi
        current_total = total_mi
        current_avg_line = avg_per_line_mi
        current_avg_station = avg_per_station_mi
    else:
        current_unit = "km"
        btn_unit.label.set_text('Switch to Miles')
        current_data = line_lengths_km
        current_total = total_km
        current_avg_line = avg_per_line_km
        current_avg_station = avg_per_station_km
        
    map_title.set_text(f"Singapore MRT Network - Central Section\n(Distances displayed in {current_unit})")
    
    for txt_obj, d_km, d_mi in edge_text_objects:
        if current_unit == "km":
            txt_obj.set_text(f"{d_km} km")
        else:
            txt_obj.set_text(f"{d_mi} mi")
        
    stats_title.set_text(f"Total Length by MRT Line ({current_unit})")
    stats_ylabel.set_text(f"Length ({current_unit})")
    ax_stats.set_ylim(0, max(current_data.values) * 1.15)
    
    for i, bar in enumerate(bars):
        new_val = round(current_data.values[i], 2)
        bar.set_height(new_val) 
        bar_text_objects[i].set_text(str(new_val)) 
        bar_text_objects[i].set_position((bar.get_x() + bar.get_width()/2, new_val + 0.2)) 

    summary_box.set_text(
        f"SUMMARY\n"
        f"Total Network  : {current_total} {current_unit}\n"
        f"Avg per Line   : {current_avg_line} {current_unit}\n"
        f"Avg per Station: {current_avg_station} {current_unit}"
    )
        
    fig.canvas.draw_idle()

btn_unit.on_clicked(toggle_unit)

# Auto-maximize the window
manager = plt.get_current_fig_manager()
try:
    manager.window.state('zoomed') 
except AttributeError:
    pass

plt.show()
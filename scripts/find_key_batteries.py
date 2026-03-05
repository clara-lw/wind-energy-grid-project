import pandas as pd
import geopandas as gpd
from wind_grid.uk_plot import plot_map_log_stations
import matplotlib.pyplot as plt

grid_boundaries = gpd.read_file("data/clean_data/wind_capacity_by_boundary.geojson")
areas_cap = grid_boundaries[["area_id", "wind_gw", "geometry"]].to_crs(epsg=4326)

battery_storage_df = pd.read_csv('data/clean_data/clean_bess_data.csv')
planned_batt = battery_storage_df[battery_storage_df["Development Status (short)"].isin(["Awaiting Construction", "Application Submitted"])]
batt_gdf = gpd.GeoDataFrame(
    planned_batt,
    geometry=gpd.points_from_xy(planned_batt["Longitude"], planned_batt["Latitude"]),
    crs="EPSG:4326"
)

batt_with_region = gpd.sjoin(
    batt_gdf,
    areas_cap,
    how="left",
    predicate="within"
).drop(columns=["index_right"])

limit = 5.0
subset = batt_with_region[batt_with_region["wind_gw"] >= limit]
subset = subset[subset["Installed Capacity (MWelec)"] > 10]

lats = subset["Latitude"]
lons = subset["Longitude"]
caps = subset["Installed Capacity (MWelec)"]

fig, ax = plot_map_log_stations(caps, lons, lats)
ax.set_title("Optimal Planned BESS Units")
plt.savefig('outputs/figures/optimal_planned_bess_units_map.png', dpi=300, bbox_inches='tight')

cols = [
    "Site Name",             
    "Longitude",
    "Latitude",
    "Installed Capacity (MWelec)",
    "Development Status (short)",
    "Country",
]

subset_table = subset[cols]

subset_table.to_csv("outputs/tables/optimal_planned_bess_units.csv", index=False)



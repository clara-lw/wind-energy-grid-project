import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import cartopy.crs as ccrs
from wind_grid.uk_plot import plot_map_basic, plot_map_log_stations
from wind_grid.regions import load_boundaries_lines_csv

#wind farm plot
wind_data = pd.read_csv('data/clean_data/wind_farms_data.csv')
lat = wind_data['Latitude'].to_numpy()
lon = wind_data['Longitude'].to_numpy()
capacity = wind_data['Installed Capacity (MWelec)'].to_numpy()

fig1, ax1 = plot_map_log_stations(capacity, lon, lat)
ax1.set_title('Wind farm locations and capacity')
plt.savefig('outputs/figures/wind_farm_map.png', dpi=300, bbox_inches='tight')

#battery plots
battery_storage_df = pd.read_csv('data/clean_data/clean_bess_data.csv')

#current
current_battery_storage_df = battery_storage_df[battery_storage_df["Development Status (short)"] == "Operational"]
current_bat_lats = current_battery_storage_df["Latitude"]
current_bat_lons = current_battery_storage_df["Longitude"]
current_bat_cap = current_battery_storage_df["Installed Capacity (MWelec)"]

fig2, ax2 = plot_map_log_stations(current_bat_cap, current_bat_lons, current_bat_lats)
ax2.set_title('Current battery storage locations and capacity')
plt.savefig('outputs/figures/current_battery_storage_map.png', dpi=300, bbox_inches='tight')

#planned
planned_battery_storage_df = battery_storage_df[battery_storage_df["Development Status (short)"].isin(["Awaiting Construction", "Application Submitted"])]
planned_bat_lats = planned_battery_storage_df["Latitude"]
planned_bat_lons = planned_battery_storage_df["Longitude"]
planned_bat_cap = planned_battery_storage_df["Installed Capacity (MWelec)"]

fig3, ax3 = plot_map_log_stations(planned_bat_cap, planned_bat_lons, planned_bat_lats)
ax3.set_title('Planned battery storage locations and capacity')
plt.savefig('outputs/figures/planned_battery_storage_map.png', dpi=300, bbox_inches='tight')


#transmission boundaries + wind capacity by area plot
transmission_boundaries_gdf = load_boundaries_lines_csv("data/clean_data/transmission_boundaries.csv")

areas_cap = gpd.read_file("data/clean_data/wind_capacity_by_boundary.geojson")

fig, ax = plot_map_basic()

transmission_boundaries_gdf.plot(
    ax=ax,
    column="Limit GW",
    cmap="viridis",
    linewidth=1.0,
    legend=False,
    transform=ccrs.PlateCarree()
)

sm = plt.cm.ScalarMappable(
    cmap="viridis",
    norm=plt.Normalize(
        vmin=transmission_boundaries_gdf["Limit GW"].min(),
        vmax=transmission_boundaries_gdf["Limit GW"].max()
    )
)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.02, shrink=0.7)
cbar.set_label("Power Transmission Limit (GW)")

for _, row in areas_cap.iterrows():
    x = row["label_x"]
    y = row["label_y"]
    val = row["wind_gw"]  

    if val <= 0:
        continue

    ax.text(
        x, y,
        f"{val:.1f}",             
        transform=ccrs.PlateCarree(),
        ha="center", va="center",
        fontsize=8,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7)
    )

plt.title("Transmission System Boundaries + Wind Capacity per Area (GW)")
plt.savefig('outputs/figures/transmission_boundaries_wind_capacity_map.png', dpi=300, bbox_inches='tight')
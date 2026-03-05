import pandas as pd
from wind_grid.regions import (
    load_boundaries_lines_csv,
    build_areas_from_boundaries,
    capacity_sum_within_areas,
    attach_capacity_and_labels,
)

boundaries = load_boundaries_lines_csv("data/clean_data/transmission_boundaries.csv")
areas = build_areas_from_boundaries(boundaries, pad_m=5000)


wind = pd.read_csv("data/clean_data/wind_farms_data.csv")
wind_sum = capacity_sum_within_areas(
    points_df=wind,
    lon_col="Longitude",
    lat_col="Latitude",
    value_col="Installed Capacity (MWelec)",
    areas_gdf=areas,
)


offshore = pd.read_csv("data/clean_data/offshore_wind_bus_locations.csv")
off_lon, off_lat = "bus_x", "bus_y"


offshore_sum = capacity_sum_within_areas(
    points_df=offshore,
    lon_col=off_lon,
    lat_col=off_lat,
    value_col="wind_mw",
    areas_gdf=areas,
)

total_mw = wind_sum.add(offshore_sum, fill_value=0.0)
areas_cap = attach_capacity_and_labels(areas, total_mw, capacity_name="wind_mw")

areas_cap.to_file("data/clean_data/wind_capacity_by_boundary.geojson", driver="GeoJSON")
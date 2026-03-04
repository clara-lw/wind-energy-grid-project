import pandas as pd
from wind_grid.matching import match_nearest_points

wind_data = pd.read_csv("../data/clean_data/wind_farms_data.csv").set_index("Ref ID")
buses = pd.read_csv("../data/raw/gb_buses_clean.csv")  

offshore = wind_data[wind_data["Region"] == "Offshore"].copy()

matches = match_nearest_points(
    left_df=offshore,
    right_df=buses,
    left_x="Longitude", left_y="Latitude",
    right_x="x", right_y="y",
    left_id=None,          
    right_id=None,         
    suffix_right="bus"
)


matches["wind_mw"] = offshore["Installed Capacity (MWelec)"].to_numpy(dtype=float)

matches.to_csv("../data/clean_data/offshore_wind_bus_locations.csv", index=False)
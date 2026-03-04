import pandas as pd
import geopandas as gpd

messy_wind_data = pd.read_csv("data/raw/REPD_Publication_Q4_2025.csv",
    encoding="latin1")

messy_wind_data = messy_wind_data[messy_wind_data["Technology Type"].str.contains("Wind", case=False, na=False)]

keep_cols = [
    "Ref ID",
    "Site Name",
    "Operator (or Applicant)",
    "Technology Type",
    "Installed Capacity (MWelec)",
    "Development Status (short)",
    "X-coordinate",
    "Y-coordinate",
    "Region",
    "Country",
    "Offshore Wind Round"
]

df_clean = messy_wind_data[keep_cols]

df_clean = df_clean[df_clean["Development Status (short)"]=="Operational"]

df_clean = df_clean.dropna(subset=["X-coordinate", "Y-coordinate"])

gdf = gpd.GeoDataFrame(
    df_clean,
    geometry=gpd.points_from_xy(df_clean["X-coordinate"], df_clean["Y-coordinate"]),
    crs="EPSG:27700"
)

gdf = gdf.to_crs(epsg=4326)


gdf["Longitude"] = gdf.geometry.x
gdf["Latitude"] = gdf.geometry.y
gdf = gdf.drop(columns=["X-coordinate", "Y-coordinate", "geometry"])
gdf.to_csv("data/clean_data/wind_farms_data.csv")
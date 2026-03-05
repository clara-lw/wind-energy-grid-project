import pandas as pd
import geopandas as gpd

battery = pd.read_csv('data/raw/REPD_Publication_Q4_2025.csv', encoding='latin1')

battery = battery[battery['Technology Type'].str.contains('Battery', case=False, na=False)]

keep_cols =  ["Ref ID",
    "Old Ref ID",
    "Site Name",
    "Operator (or Applicant)",
    "Technology Type",
    "Installed Capacity (MWelec)",
    "Development Status",
    "Development Status (short)",
    "Operational",
    "Under Construction",
    "X-coordinate",
    "Y-coordinate",
    "Region",
    "Country"]

df_clean = battery[keep_cols]
df_clean = df_clean[df_clean["Country"]!="Northern Ireland"]
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
gdf = gdf[gdf["Development Status"]!="Abandoned"]
gdf = gdf[gdf["Development Status"]!="Decommissioned"]
gdf = gdf[gdf["Installed Capacity (MWelec)"]!=0]
gdf["Installed Capacity (MWelec)"] = (
    gdf["Installed Capacity (MWelec)"]
    .astype(str)
    .str.replace(",", "", regex=False)     
    .str.replace("\xa0", "", regex=False)  
    .str.strip()
)

most_common = gdf["Installed Capacity (MWelec)"].dropna().mode().iloc[0]
gdf["Installed Capacity (MWelec)"] = gdf["Installed Capacity (MWelec)"].fillna(most_common)

gdf.to_csv("data/clean_data/clean_bess_data.csv", index=False)
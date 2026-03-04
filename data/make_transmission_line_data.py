import geopandas as gpd
import pandas as pd

trans_regions = gpd.read_file('data/raw/ETYS boundary GIS data Mar25.shp')

trans_regions = trans_regions.to_crs(epsg=4326)

limits = pd.Series({
    'EC5' : 3.3, 
    'B9' : 12,
    'NW1' : 1.8,
    'NW2' : 1.4,
    'NW3' : 5.5,
    'B7a' : 9.4,
    'B8' : 11,
    'B0' : 1.1,
    'B1a' : 2,
    'B2' : 2.9,
    'B3b' : 0.45,
    'B4' : 4,
    'B5' : 3.9,
    'B6' : 6.7,
    'B13' : 3.5,
    'B14' : 11.6,
    'SC1' : 3.9,
    'SC1.5' : 5.4,
    'SC2' : 3.8,
    'SC3' : 6.7,
    'LE1' : 10.2,
    'SW1' : 3.8
})

limits_df = (
    limits
    .rename("Limit GW")          
    .reset_index()                
    .rename(columns={"index": "Boundary_n"})
)

merged = trans_regions.merge(limits_df)

merged.to_csv('data/clean_data/transmission_boundaries.csv', index=False)
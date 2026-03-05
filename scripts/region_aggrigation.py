import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union, polygonize
from wind_grid.regions import clip_to_frame_as_lines, bounds_are_finite

transmission_boundaries_df = pd.read_csv("data/clean_data/transmission_boundaries.csv")
transmission_boundaries_df["geometry"] = transmission_boundaries_df["geometry"].apply(wkt.loads)
transmission_boundaries_gdf = gpd.GeoDataFrame(transmission_boundaries_df, geometry="geometry", crs="EPSG:4326")

gdf_m = transmission_boundaries_gdf.to_crs(epsg=27700)

url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url).to_crs(epsg=27700)
gb = world[world["ISO_A3"] == "GBR"]

pad_m = 5000  
frame_poly = gb.unary_union.buffer(pad_m)  
frame_line = frame_poly.boundary            


cut_lines = []
for geom in gdf_m.geometry:
    clipped = clip_to_frame_as_lines(geom, frame_poly)
    if not clipped.is_empty:
        cut_lines.append(clipped)

linework = cut_lines + [frame_line]
merged = unary_union(linework)
polys = list(polygonize(merged))

areas_m = gpd.GeoDataFrame(geometry=polys, crs="EPSG:27700")
areas_m["geometry"] = areas_m.geometry.intersection(frame_poly)
areas_m = areas_m[~areas_m.geometry.is_empty & areas_m.geometry.notna()].copy()
areas_m = areas_m[areas_m.geometry.apply(bounds_are_finite)].copy()

areas = areas_m.to_crs(epsg=4326)
areas = areas.reset_index(drop=True)
areas["area_id"] = areas.index

wind_data = pd.read_csv("data/clean_data/wind_farms_data.csv")

wind_gdf = gpd.GeoDataFrame(
    wind_data,
    geometry=gpd.points_from_xy(wind_data["Longitude"], wind_data["Latitude"]),
    crs="EPSG:4326"
)

wind_with_boundary = gpd.sjoin(
    wind_gdf,
    areas[["area_id", "geometry"]],
    how="left",
    predicate="within"
)

wind_capacity_per_boundary = (
    wind_with_boundary
    .groupby("area_id")["Installed Capacity (MWelec)"]
    .sum()
)


offshore = pd.read_csv('data/clean_data/offshore_wind_bus_locations.csv')

offshore_gdf = gpd.GeoDataFrame(
    offshore,
    geometry=gpd.points_from_xy(offshore["bus_x"], offshore["bus_y"]),
    crs="EPSG:4326"
)

offshore_with_boundary = gpd.sjoin(
    offshore_gdf,
    areas[["area_id", "geometry"]],
    how="left",
    predicate="within"
)

offshore_capacity_per_boundary = (
    offshore_with_boundary
    .groupby("area_id")["wind_mw"]
    .sum()
)

capacity_per_boundary = wind_capacity_per_boundary.add(offshore_capacity_per_boundary, fill_value=0)

cap_df = capacity_per_boundary.rename("wind_mw").reset_index()  

areas_cap = areas.merge(cap_df, on="area_id", how="left")
areas_cap["wind_mw"] = areas_cap["wind_mw"].fillna(0.0)

areas_cap["wind_gw"] = areas_cap["wind_mw"] / 1000.0
areas_cap["label_pt"] = areas_cap.geometry.representative_point()

areas_cap["label_x"] = areas_cap["label_pt"].x
areas_cap["label_y"] = areas_cap["label_pt"].y
areas_cap = areas_cap.drop(columns="label_pt")

areas_cap.to_file(
    "data/clean_data/wind_capacity_by_boundary.geojson",
    driver="GeoJSON"
)
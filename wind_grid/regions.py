import pandas as pd
import geopandas as gpd
import numpy as np

from shapely import wkt
from shapely.geometry import LineString, MultiLineString
from shapely.ops import unary_union, polygonize


def extend_linestring(ls: LineString, extend_m=30000):
    coords = list(ls.coords)
    if len(coords) < 2:
        return ls

    x0, y0 = coords[0]
    x1, y1 = coords[1]
    v0 = np.array([x0 - x1, y0 - y1], dtype=float)
    n0 = np.linalg.norm(v0)
    if n0 == 0:
        v0 = np.array([0.0, 0.0])
    else:
        v0 /= n0

    xe, ye = coords[-1]
    xprev, yprev = coords[-2]
    v1 = np.array([xe - xprev, ye - yprev], dtype=float)
    n1 = np.linalg.norm(v1)
    if n1 == 0:
        v1 = np.array([0.0, 0.0])
    else:
        v1 /= n1

    new_start = (x0 + extend_m * v0[0], y0 + extend_m * v0[1])
    new_end   = (xe + extend_m * v1[0], ye + extend_m * v1[1])

    return LineString([new_start] + coords + [new_end])


def clip_to_frame_as_lines(geom, frame_poly):
    
    if geom.geom_type == "LineString":
        ext = extend_linestring(geom)
        return ext.intersection(frame_poly)

    if geom.geom_type == "MultiLineString":
        parts = []
        for seg in geom.geoms:
            ext = extend_linestring(seg)
            inter = ext.intersection(frame_poly)
            if not inter.is_empty:
                parts.append(inter)
        if len(parts) == 0:
            return geom.intersection(frame_poly)
        return unary_union(parts)

    return geom.intersection(frame_poly)


def bounds_are_finite(g):
    if g is None or g.is_empty:
        return False
    minx, miny, maxx, maxy = g.bounds
    return np.isfinite([minx, miny, maxx, maxy]).all()


def load_boundaries_lines_csv(path, crs="EPSG:4326"):
    df = pd.read_csv(path)
    df["geometry"] = df["geometry"].apply(wkt.loads)
    return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)


def load_gb_frame(pad_m=5000, epsg=27700):
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    world = gpd.read_file(url).to_crs(epsg=epsg)
    gb = world[world["ISO_A3"] == "GBR"]
    if gb.empty:
        raise ValueError("GBR not found in Natural Earth dataset.")
    frame_poly = gb.unary_union.buffer(pad_m)
    frame_line = frame_poly.boundary
    return frame_poly, frame_line


def build_areas_from_boundaries(boundaries_gdf_4326, pad_m=5000):
    boundaries_m = boundaries_gdf_4326.to_crs(epsg=27700)
    frame_poly, frame_line = load_gb_frame(pad_m=pad_m, epsg=27700)

    cut_lines = []
    for geom in boundaries_m.geometry:
        clipped = clip_to_frame_as_lines(geom, frame_poly)
        if clipped is not None and (not clipped.is_empty):
            cut_lines.append(clipped)

    linework = cut_lines + [frame_line]
    merged = unary_union(linework)
    polys = list(polygonize(merged))

    areas_m = gpd.GeoDataFrame(geometry=polys, crs="EPSG:27700")
    areas_m["geometry"] = areas_m.geometry.intersection(frame_poly)
    areas_m = areas_m[areas_m.geometry.notna()]
    areas_m = areas_m[~areas_m.geometry.is_empty].copy()
    areas_m = areas_m[areas_m.geometry.apply(bounds_are_finite)].copy()

    areas = areas_m.to_crs(epsg=4326).reset_index(drop=True)
    areas["area_id"] = areas.index.astype(int)
    return areas


def capacity_sum_within_areas(points_df, lon_col, lat_col, value_col, areas_gdf):
    points_gdf = gpd.GeoDataFrame(
        points_df.copy(),
        geometry=gpd.points_from_xy(points_df[lon_col], points_df[lat_col]),
        crs="EPSG:4326",
    )

    joined = gpd.sjoin(
        points_gdf,
        areas_gdf[["area_id", "geometry"]],
        how="left",
        predicate="within",
    )

    joined[value_col] = pd.to_numeric(joined[value_col], errors="coerce")
    return joined.groupby("area_id")[value_col].sum()


def attach_capacity_and_labels(areas_gdf, capacity_series, capacity_name="wind_mw"):
    cap_df = capacity_series.rename(capacity_name).reset_index()

    out = areas_gdf.merge(cap_df, on="area_id", how="left")
    out[capacity_name] = out[capacity_name].fillna(0.0)
    out["wind_gw"] = out[capacity_name] / 1000.0

    label_pt = out.geometry.representative_point()
    out["label_x"] = label_pt.x
    out["label_y"] = label_pt.y
    return out
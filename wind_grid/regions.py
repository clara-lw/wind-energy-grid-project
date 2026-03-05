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
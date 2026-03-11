import pandas as pd
import numpy as np

def match_nearest_points(left_df, right_df, left_x, left_y, right_x, right_y, left_id=None, right_id=None, suffix_right="right"):
    
    """Method to match objects in the left data frame to the nearest objects in the right data frame,
    through their coordinates.

    Returns
    -------
    DataFrame
        A data frame with the following columns:
        - left_id: the identifier of the object in the left data frame (or the index if left_id is None)
        - {suffix_right}_id: the identifier of the nearest object in the right data frame (or the index if right_id is None)
        - distance: the distance between the two objects
        - {suffix_right}_x: the x coordinate of the nearest object in the right data frame
        - {suffix_right}_y: the y coordinate of the nearest object in the right data frame
    """
    
    left_ids = left_df[left_id].values if left_id else left_df.index.values
    right_ids = right_df[right_id].values if right_id else right_df.index.values

    Lx = left_df[left_x].to_numpy(dtype=float)
    Ly = left_df[left_y].to_numpy(dtype=float)
    Rx = right_df[right_x].to_numpy(dtype=float)
    Ry = right_df[right_y].to_numpy(dtype=float)

    out = []

    for i in range(len(left_df)):
        dx = Rx - Lx[i]
        dy = Ry - Ly[i]
        dist = np.sqrt(dx*dx + dy*dy)

        j = dist.argmin()

        out.append({
            "left_id": left_ids[i],
            f"{suffix_right}_id": right_ids[j],
            "distance": float(dist[j]),
            f"{suffix_right}_x": float(Rx[j]),
            f"{suffix_right}_y": float(Ry[j]),
        })

    return pd.DataFrame(out)
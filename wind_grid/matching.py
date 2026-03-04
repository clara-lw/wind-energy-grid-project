import pandas as pd
import numpy as np

def match_nearest_points(left_df, right_df, left_x, left_y, right_x, right_y, left_id=None, right_id=None, suffix_right="right"):
    
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
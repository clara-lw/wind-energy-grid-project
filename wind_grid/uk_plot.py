import matplotlib.pyplot as plt
import numpy as np

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as mcolors

def plot_map_basic():
    """Method to plot a simple map of the UK.

    Returns
    -------
    figure
        The figure object.
    axes
        The axes object.
    """
    
    fig = plt.figure(figsize=(9,10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)

    ax.set_extent([-9, 3, 49, 61], crs=ccrs.PlateCarree())

    gl = ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.6)
    gl.top_labels = False
    gl.right_labels = False

    return fig, ax



def plot_map_log_stations(cap, lons, lats):
    """Method to plot a map of the UK with specific locations colored and sized by their value.
    Returns
    -------
    figure
        The figure object.
    axes
        The axes object.
    """
    fig, ax = plot_map_basic()
    sizes = 20 + 180 * (np.sqrt(cap) / np.sqrt(np.nanmax(cap) if np.nanmax(cap) > 0 else 1))

    norm = mcolors.LogNorm(
    vmin=np.nanmin(cap[cap > 0]),  
    vmax=np.nanmax(cap)
    )

    sc = ax.scatter(
        lons, lats,
        s=sizes,
        c=cap,               
        cmap='viridis',
        norm=norm,
        alpha=0.75,
        edgecolors='k',
        linewidth=0.2,
        transform=ccrs.PlateCarree()
    )

    cbar = plt.colorbar(sc, ax=ax, orientation='vertical', pad=0.02, shrink=0.7)
    cbar.set_label('Installed Capacity (MW)', fontsize=10)

    return fig, ax
"""
Cartographic output for suitability analysis results.
"""
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib_scalebar.scalebar import ScaleBar
import rasterio
import numpy as np
import geopandas as gpd


def plot_suitability_map(suitability_path, boundary_path, output_png):
    """Generate a publication-quality suitability map."""
    boundary = gpd.read_file(boundary_path)

    with rasterio.open(suitability_path) as src:
        data = src.read(1).astype(float)
        nodata = src.nodata if src.nodata else -9999
        data[data == nodata] = np.nan
        extent = [
            src.bounds.left, src.bounds.right,
            src.bounds.bottom, src.bounds.top,
        ]
        crs = src.crs

    fig, ax = plt.subplots(figsize=(12, 10))

    cmap = plt.cm.YlOrRd.copy()
    cmap.set_bad(color="#DCDCDC")  # gray for excluded/nodata areas

    img = ax.imshow(
        data,
        cmap=cmap,
        extent=extent,
        origin="upper",
        vmin=0,
        vmax=1,
    )

    boundary.to_crs(crs).boundary.plot(
        ax=ax, color="black", linewidth=0.8, zorder=5
    )

    cbar = plt.colorbar(img, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label("Suitability Score (0 = low, 1 = high)", fontsize=11)

    ax.set_title(
        "Solar Energy Siting Suitability — Colorado\n"
        "GHI (60%) + Terrain Slope (40%) | Protected Areas Excluded",
        fontsize=13, pad=12
    )
    ax.set_xlabel("Easting (m, UTM Zone 13N)", fontsize=10)
    ax.set_ylabel("Northing (m, UTM Zone 13N)", fontsize=10)

    # Data source annotation
    ax.annotate(
        "Data: NREL NSRDB (GHI), USGS PAD-US 3.0 (exclusions), USGS 3DEP (slope)",
        xy=(0.01, 0.01), xycoords="axes fraction",
        fontsize=8, color="gray"
    )

    plt.tight_layout()
    plt.savefig(output_png, dpi=150, bbox_inches="tight")
    print(f"Map saved → {output_png}")
    return fig, ax
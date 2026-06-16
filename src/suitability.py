"""
Multi-criteria suitability scoring for solar energy siting.
Weights: GHI 60%, terrain slope 40%. Protected areas applied as hard mask.
"""
import rasterio
import geopandas as gpd
import numpy as np
from rasterio.features import rasterize

TARGET_CRS = "EPSG:32613"


def load_raster(path):
    """Load raster as float array, replacing nodata with NaN."""
    with rasterio.open(path) as src:
        arr = src.read(1).astype(float)
        if src.nodata is not None:
            arr[arr == src.nodata] = np.nan
        return arr, src.transform, src.crs, src.meta.copy()


def normalize(arr):
    """Min-max normalize to 0–1, ignoring NaN."""
    valid = arr[~np.isnan(arr)]
    if valid.max() == valid.min():
        return np.zeros_like(arr)
    return (arr - valid.min()) / (valid.max() - valid.min())


def rasterize_exclusions(exclusion_vector_path, ref_raster_path):
    """Burn exclusion zones (protected areas) into a boolean mask."""
    with rasterio.open(ref_raster_path) as src:
        shape = (src.height, src.width)
        transform = src.transform
        crs = src.crs

    excl = gpd.read_file(exclusion_vector_path).to_crs(crs)
    shapes = [(geom, 1) for geom in excl.geometry if geom is not None]

    if not shapes:
        print("Warning: no exclusion geometries found")
        return np.zeros(shape, dtype=bool)

    exclusion_mask = rasterize(
        shapes,
        out_shape=shape,
        transform=transform,
        fill=0,
        dtype="uint8",
    )
    pct = exclusion_mask.mean() * 100
    print(f"Exclusion mask: {pct:.1f}% of area excluded")
    return exclusion_mask.astype(bool)


def compute_suitability(ghi_path, exclusion_path, slope_path=None):
    """
    Compute weighted suitability score.
    GHI weight: 60% | Slope weight: 40% (if slope provided, else 100% GHI)
    Exclusions applied as hard no-go zones (NaN).
    """
    ghi, transform, crs, meta = load_raster(ghi_path)
    ghi_norm = normalize(ghi)

    if slope_path:
        slope, _, _, _ = load_raster(slope_path)
        # Invert slope: flat terrain (low slope) = high suitability
        slope_clipped = np.clip(slope, 0, 30)
        slope_norm = 1 - normalize(slope_clipped)
        suitability = 0.6 * ghi_norm + 0.4 * slope_norm
        print("Suitability: 60% GHI + 40% slope")
    else:
        suitability = ghi_norm
        print("Suitability: 100% GHI (no slope data)")

    exclusions = rasterize_exclusions(exclusion_path, ghi_path)
    suitability[exclusions] = np.nan

    valid = suitability[~np.isnan(suitability)]
    print(f"Score range: {valid.min():.3f} – {valid.max():.3f} | mean: {valid.mean():.3f}")
    return suitability, transform, crs, meta


def save_suitability(suitability, transform, crs, meta, output_path):
    """Write suitability raster to disk."""
    meta.update({"dtype": "float32", "count": 1, "nodata": -9999})
    out = suitability.astype("float32")
    out[np.isnan(out)] = -9999
    with rasterio.open(output_path, "w", **meta) as dst:
        dst.write(out, 1)
    print(f"Saved → {output_path}")
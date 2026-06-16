"""
Full pipeline: solar siting suitability analysis for Colorado.
Run from project root: python src/main.py
"""
import sys
from pathlib import Path

# Allow importing from src/ when run from project root
sys.path.insert(0, str(Path(__file__).parent))

from data_prep import reproject_raster, clip_raster_to_boundary
from suitability import compute_suitability, save_suitability
from visualize import plot_suitability_map

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW        = Path("data/raw")
PROCESSED  = Path("data/processed")
OUTPUTS    = Path("data/outputs")

PROCESSED.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

GHI_RAW    = RAW / "ghi_col.tif"        # rename your downloaded file
BOUNDARY   = RAW / "colorado_boundary.shp"
EXCLUSIONS = RAW / "PADUS3_0Geopackage.gpkg"
SLOPE_RAW  = RAW / "dem_tiles"                     # folder of tiles

GHI_REPROJ = PROCESSED / "ghi_utm13n.tif"
GHI_CLIP   = PROCESSED / "ghi_clipped.tif"
SUITABILITY= PROCESSED / "suitability.tif"
OUTPUT_MAP = OUTPUTS   / "solar_suitability_colorado.png"

# ── Pipeline ──────────────────────────────────────────────────────────────────
print("\n[1/5] Reprojecting GHI raster to UTM Zone 13N...")
reproject_raster(str(GHI_RAW), str(GHI_REPROJ))

print("\n[2/5] Clipping to Colorado boundary...")
clip_raster_to_boundary(str(GHI_REPROJ), str(BOUNDARY), str(GHI_CLIP))

print("\n[3/5] Computing suitability scores...")
suitability, transform, crs, meta = compute_suitability(
    ghi_path=str(GHI_CLIP),
    exclusion_path=str(EXCLUSIONS),
    slope_path=None,   # set to str(SLOPE_CLIP) once you compute slope
)

print("\n[4/5] Saving suitability raster...")
save_suitability(suitability, transform, crs, meta, str(SUITABILITY))

print("\n[5/5] Generating map...")
plot_suitability_map(str(SUITABILITY), str(BOUNDARY), str(OUTPUT_MAP))

print("\n✓ Pipeline complete. Map saved to:", OUTPUT_MAP)
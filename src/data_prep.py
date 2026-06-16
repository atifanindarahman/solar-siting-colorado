"""
Data preparation: reprojection and clipping for solar siting analysis.
"""
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import mapping
import numpy as np

TARGET_CRS = "EPSG:32613"  # UTM Zone 13N — appropriate for Colorado


def reproject_raster(src_path, dst_path, target_crs=TARGET_CRS):
    """Reproject a raster to target CRS with bilinear resampling."""
    with rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()
        kwargs.update({
            "crs": target_crs,
            "transform": transform,
            "width": width,
            "height": height,
        })
        with rasterio.open(dst_path, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.bilinear,
                )
    print(f"Reprojected → {dst_path}")


def clip_raster_to_boundary(raster_path, boundary_path, output_path):
    """Clip raster to a vector polygon boundary."""
    boundary = gpd.read_file(boundary_path).to_crs(TARGET_CRS)
    geoms = [mapping(geom) for geom in boundary.geometry]

    with rasterio.open(raster_path) as src:
        out_image, out_transform = mask(src, geoms, crop=True, nodata=-9999)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "nodata": -9999,
        })
        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)
    print(f"Clipped → {output_path}")
# Solar Energy Siting Suitability Model — Colorado

Multi-criteria geospatial suitability analysis for utility-scale solar energy
deployment across Colorado using open-source Python and publicly available datasets.

## Results

![Solar Suitability Map](data/outputs/solar_suitability_colorado.png)

High-suitability zones (red/orange) in southeastern Colorado plains.
Protected areas and steep terrain correctly excluded.

## Methods

| Criterion         | Weight | Source               |
|-------------------|--------|----------------------|
| GHI (irradiance)  | 60%    | SOLARGIS GHI         |
| Slope (terrain)   | 40%    | USGS 3DEP 1/3 arc-sec |
| Exclusion zones   | Hard mask | USGS PAD-US 3.0      |

**CRS:** EPSG:32613 (UTM Zone 13N)
**Resolution:** 1 km
**Extent:** Colorado state boundary (US Census TIGER 2022)

## Repository Structure
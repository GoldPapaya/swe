import netCDF4 as nc
import numpy as np
from rasterio.features import geometry_mask
from rasterio.transform import Affine
from shapely.geometry import mapping
import cartopy.io.shapereader as shpreader
import csv
import glob
import os

# File paths
nc_pattern = 'visualizer_input/swemap/2000_2001/*.nc'  # Wildcard for all NetCDF files
shp_file = 'visualizer_input/mask/southernontariomask.shp'  # Red polygon mask
csv_file = 'swe_summary.csv'  # Output CSV file

# Load the red polygon shapefile once
shp_reader = shpreader.Reader(shp_file)
shapes = list(shp_reader.geometries())

# Open CSV in write mode and add header
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['File', 'SWE_Sum_mm'])

# Process each NetCDF file
for nc_file in glob.glob(nc_pattern):
    # Open the NetCDF file
    dataset = nc.Dataset(nc_file, 'r')
    x = dataset.variables['x'][:]
    y = dataset.variables['y'][:]
    swe = dataset.variables['swe'][:]

    # Calculate the affine transform
    dx = (x[-1] - x[0]) / (len(x) - 1)
    dy = (y[-1] - y[0]) / (len(y) - 1)
    transform = Affine(dx, 0, x[0], 0, dy, y[0])

    # Create 2D grid and mask
    X, Y = np.meshgrid(x, y)
    mask = geometry_mask(
        [mapping(geom) for geom in shapes],
        transform=transform,
        out_shape=swe.shape,
        all_touched=True,
        invert=True  # True inside polygon
    )

    # Calculate sum of SWE within the red polygon
    swe_masked = np.where(mask, swe, np.nan)
    swe_sum = np.nansum(swe_masked)
    if swe_sum < 0:
        swe_sum = 0
    print(f"{nc_file}: Total SWE = {swe_sum:.2f} mm")

    # Append to CSV
    filename = os.path.basename(nc_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([filename, f"{swe_sum:.2f}"])

    dataset.close()

print(f"All data written to {csv_file}")
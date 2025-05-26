import netCDF4 as nc
import numpy as np
from rasterio.features import geometry_mask
from rasterio.transform import Affine
from shapely.geometry import mapping
import cartopy.io.shapereader as shpreader
import csv
import glob
import os
from dotenv import load_dotenv

load_dotenv()

nc_pattern = os.getenv("NC_PATTERN") # (*Important*) input file path format: "file_input/data_range/*.nc"
shp_file = os.getenv("SHP_FILE") # Polygon mask
csv_file = os.getenv("CSV_FILE")  # Output .csv file

shp_reader = shpreader.Reader(shp_file)
shapes = list(shp_reader.geometries())

with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['File', 'SWE_Sum_mm'])

for nc_file in glob.glob(nc_pattern):
    dataset = nc.Dataset(nc_file, 'r')
    x = dataset.variables['x'][:]
    y = dataset.variables['y'][:]
    swe = dataset.variables['swe'][:]

    dx = (x[-1] - x[0]) / (len(x) - 1)
    dy = (y[-1] - y[0]) / (len(y) - 1)
    transform = Affine(dx, 0, x[0], 0, dy, y[0])

    X, Y = np.meshgrid(x, y)
    mask = geometry_mask(
        [mapping(geom) for geom in shapes],
        transform=transform,
        out_shape=swe.shape,
        all_touched=True,
        invert=True
    )

    # Calculate sum of SWE within the polygon
    swe_masked = np.where(mask, swe, np.nan)
    swe_sum = np.nansum(swe_masked)
    if swe_sum < 0:
        swe_sum = 0
    print(f"{nc_file}: Total SWE = {swe_sum:.2f} mm")
    #swe_count = np.sum(mask)
    #print(f"Total SWE cells within polygon: {swe_count:.2f} cells") 

    filename = os.path.basename(nc_file)
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([filename, f"{swe_sum:.2f}"])

    dataset.close()

print(f"All data written to {csv_file}")
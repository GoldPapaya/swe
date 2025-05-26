import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import os
from dotenv import load_dotenv

load_dotenv()

nc_file = os.getenv('NC_FILE') # Reference to single NetCDF file
shp_file = os.getenv('SHP_FILE') # Polygon mask (optional)
prov_file = os.getenv('PROV_FILE') # Geographic boundary mask

dataset = nc.Dataset(nc_file, 'r')
x = dataset.variables['x'][:]
y = dataset.variables['y'][:]
swe = dataset.variables['swe'][:]

# Lambert Azimuthal Equal Area projection
proj = ccrs.LambertAzimuthalEqualArea(
    central_longitude=0,
    central_latitude=90,
    false_easting=0,
    false_northing=0,
    globe=ccrs.Globe(semimajor_axis=6371228.0, semiminor_axis=6371228.0)
)

plt.figure(figsize=(12, 8))
ax = plt.axes(projection=proj)
ax.set_global()
ax.coastlines()

mesh = ax.pcolormesh(x, y, swe, cmap='Blues', zorder=1)
plt.colorbar(mesh, label='Snow Water Equivalent (mm)')

# Overlay shapefile
try:
    shp_reader = shpreader.Reader(shp_file)
    shapes = list(shp_reader.geometries())
    print(f"Loaded southernontariomask.shp")
    ax.add_geometries(
        shapes,
        crs=proj,
        edgecolor='red',
        facecolor='none',
        linewidth=1.5,
        zorder=2
    )
except ValueError as e:
    print(f"Shapefile error (southernontariomask): {e}")

# Overlay borders
try:
    shp_reader = shpreader.Reader(prov_file)
    shapes = list(shp_reader.geometries())
    print(f"Loaded provinceboundaries.shp")
    ax.add_geometries(
        shapes,
        crs=proj,
        edgecolor='black',
        alpha=0.1,
        facecolor='none',
        linewidth=1,
        zorder=2
    )
except ValueError as e:
    print(f"Shapefile error (provinceboundaries): {e}")

plt.title('SWE Map (Feb 2, 2017)')
plt.show()

dataset.close()
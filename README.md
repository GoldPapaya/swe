# Snow Water Equivalent (SWE) Preprocessor & Visualizer
This repository contains two scripts -- bulkProcessor.py and Visualizer.py -- which were created for a capstone research project investigating the climatology of Southern Ontario. The former overlays a polygon mask over a gridded plane containing 25km x 25km cells, and outputs the only the cell data contained within the mask to a .csv. The latter simply visualizes NetCDF files, similar to the viewer in ESRI and ESRI adjacent products, where you can pan, zoom, etc..

Additionally the bulk processor supports operations on several files at once, so if you have a bunch of NetCDF files without a time dimension (as is the case with the GlobSnow v3.0 dataset) this application handles all of that for you.

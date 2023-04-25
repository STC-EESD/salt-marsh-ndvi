# Salt Marsh NDVI - 903-CODR

The processing method for the Salt Marsh NDVI is split up into two portions:
	- the Earth Engine portion
	- the Downstream portion

Processing starts with the Earth Engine portion called through the run-main-earthengine.sh script, which creates an NDVI growing season composite, classifies the NDVI and then calculates the area of each class within Salt Marsh polygons. The result is output as CSV files in a Google Drive cloud folder (shared folder "earthengine/patrick".

After the first script is completed, the CSV files need to be downloaded and stored locally for the next script to use. The expected folder is [...]salt-marsh-ndvi/000-data/sample-gee-output/.

The processing continues in the downstream portion called through the run-main-downstream.sh script, using the CSV outputs from the first portion saved locally. The data is then combined and processed into summary tables contaning the areas of each NDVI class for salt marshes at the each of the four Ecological Framework levels. The summary tables are created as CSV files stored locally in the [...]/gittmp/[...]/903-codr/output/ folder.

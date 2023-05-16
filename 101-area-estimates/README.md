# Salt Marsh NDVI - 903-CODR (multi-year)

The processing method for the Salt Marsh NDVI is split up into two portions:
	- the Earth Engine portion
	- the Downstream portion

USER NOTE:
The processing requires User input to define the Analysis Years - the Year values to use must be defined in the "run-main-earthengine.sh" file (specific instructions are included in the file - current years are 2019 and 2021). 
The downstream processing is designed to account for the specified years without further user input.

Processing starts with the Earth Engine portion called through the run-main-earthengine.sh script, which creates an NDVI growing season composite, classifies the NDVI and then calculates the area of each class within Salt Marsh polygons. The result is output a series of CSV files in a Google Drive cloud folder (the shared folder "earthengine/patrick").

After the first script is completed, the CSV files need to be downloaded and stored locally for the next script to use. The expected data folder is [...]salt-marsh-ndvi/000-data/sample-gee-output/. (This portion is expected to eventually be automated.)

The processing continues in the downstream portion called through the run-main-downstream.sh script, using the CSV outputs from the first portion saved locally. The data is then combined and processed into summary tables contaning the areas of each NDVI class for salt marshes at the each of the four Ecological Framework levels. 
Four summary tables are created in total - if multiple years were analysed, the results for each year are labelled but are grouped by ECF level (i.e. ecozone summary data for multiple years is contained in the same file). The summary tables are created as CSV files, and stored locally in the [...]/gittmp/[...]/903-codr/output/ folder.

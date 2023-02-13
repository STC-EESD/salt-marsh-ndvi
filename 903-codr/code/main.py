#!/usr/bin/env python

import os, sys, shutil, getpass
import pprint, logging, datetime
import stat

dir_data            = os.path.realpath(sys.argv[1])
dir_code            = os.path.realpath(sys.argv[2])
dir_output          = os.path.realpath(sys.argv[3])
google_drive_folder = sys.argv[4]

if not os.path.exists(dir_output):
    os.makedirs(dir_output)

os.chdir(dir_output)

myTime = "system time: " + datetime.datetime.now().strftime("%c")
print( "\n" + myTime + "\n" )

print( "\ndir_data: "            + dir_data            )
print( "\ndir_code: "            + dir_code            )
print( "\ndir_output: "          + dir_output          )
print( "\ngoogle_drive_folder: " + google_drive_folder )

print( "\nos.environ.get('GEE_ENV_DIR'):")
print(    os.environ.get('GEE_ENV_DIR')  )

print( "\n### python module search paths:" )
for path in sys.path:
    print(path)

print("\n####################")

logging.basicConfig(filename='log.debug',level=logging.DEBUG)

##################################################
##################################################
# import seaborn (for improved graphics) if available
# import seaborn as sns

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
from batchExport              import batchExportByYear;
from eeFeatureCollectionUtils import featureCollectionGetBatches;
from eeImageCollectionUtils   import imageCollectionGetYearRange;
from test_eeAuthenticate      import test_eeAuthenticate;

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
S2SR                = 'COPERNICUS/S2_SR_HARMONIZED'; #'COPERNICUS/S2_SR';
saltMarshGeometries = 'users/tasharabinowitz/SaltmarshpolyByBioregion_v2';
minShapeArea        = 100;
batchSize           = 500;
gridScale           = 1e4;

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
test_eeAuthenticate();

### Fix batchExportByYear() so that main.py works (in the sense that we get
### good output files in the designated Google Drive folder).
### Then, uncomment the code segments below ... it should work by then.
# batchExportByYear(
#     batchSize             = batchSize,
#     batchID               = 0,
#     year                  = 2020,
#     featureCollectionName = saltMarshGeometries,
#     minShapeArea          = minShapeArea,
#     imageCollectionName   = S2SR,
#     google_drive_folder   = google_drive_folder
#     );

batchIDs = featureCollectionGetBatches(
    featureCollectionName = saltMarshGeometries,
    minShapeArea          = minShapeArea,
    batchSize             = batchSize,
    google_drive_folder   = google_drive_folder,
    exportDescription     = 'DF-saltMarsh-batch-codr',
    exportFileNamePrefix  = 'DF-saltMarsh-batch-codr'
    );
print("\nbatchIDs:\n",batchIDs,"\n");

referenceYears = [2020,2021];

# for batchID in batchIDs:
for batchID in batchIDs[:3]:
    for year in referenceYears:
        batchExportByYear(
            batchSize             = batchSize,
            batchID               = batchID,
            year                  = year,
            featureCollectionName = saltMarshGeometries,
            minShapeArea          = minShapeArea,
            imageCollectionName   = S2SR,
            google_drive_folder   = google_drive_folder
            );

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###

##################################################
##################################################
print("\n####################\n")
myTime = "system time: " + datetime.datetime.now().strftime("%c")
print( myTime + "\n" )

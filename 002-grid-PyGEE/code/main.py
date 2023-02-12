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
from batchExportTiff          import batchExportTiff;
from eeFeatureCollectionUtils import featureCollectionGetBatches;
from eeImageCollectionUtils   import imageCollectionGetYearRange;
from test_eeAuthenticate      import test_eeAuthenticate;

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
saltMarshGeometries = 'users/tasharabinowitz/SaltmarshpolyByBioregion_v2';
minShapeArea        = 100;
batchSize           = 1000;
gridScale           = 1e4;

stringCanadaAlbersEqualAreaConic = 'PROJCS[\
    "Canada_Albers_Equal_Area_Conic",\
    GEOGCS[\
        "GCS_North_American_1983",\
        DATUM[\
            "D_North_American_1983",\
            SPHEROID["GRS_1980",6378137,298.257222101]\
            ],\
        PRIMEM["Greenwich",0],\
        UNIT["Degree",0.0174532925199433]\
        ],\
    PROJECTION["Albers"],\
    PARAMETER["False_Easting",0],\
    PARAMETER["False_Northing",0],\
    PARAMETER["Central_Meridian",-96],\
    PARAMETER["Standard_Parallel_1",50],\
    PARAMETER["Standard_Parallel_2",70],\
    PARAMETER["Latitude_Of_Origin",40],\
    UNIT["Meter",1],\
    AUTHORITY["EPSG","102001"]\
    ]';

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
test_eeAuthenticate();

batchIDs = featureCollectionGetBatches(
    featureCollectionName = saltMarshGeometries,
    minShapeArea          = minShapeArea,
    batchSize             = batchSize,
    google_drive_folder   = google_drive_folder,
    exportDescription     = 'DF-saltMarsh-batch',
    exportFileNamePrefix  = 'DF-saltMarsh-batch'
    );
print("\nbatchIDs:\n",batchIDs,"\n");

# for batchID in batchIDs[:10]:
for batchID in batchIDs:
    batchExportTiff(
        batchSize             = batchSize,
        batchID               = batchID,
        gridScale             = gridScale,
        featureCollectionName = saltMarshGeometries,
        minShapeArea          = minShapeArea,
        stringMapProjection   = stringCanadaAlbersEqualAreaConic,
        # imageCollectionName = modis_061_11A1,
        google_drive_folder   = google_drive_folder
        );

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###

##################################################
##################################################
print("\n####################\n")
myTime = "system time: " + datetime.datetime.now().strftime("%c")
print( myTime + "\n" )

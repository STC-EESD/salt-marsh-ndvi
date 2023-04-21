#!/usr/bin/env python

import os, sys, shutil, getpass
import pprint, logging, datetime
import stat

# get values from shell script arguments
dir_data            = os.path.realpath(sys.argv[1])
dir_code            = os.path.realpath(sys.argv[2])
dir_output          = os.path.realpath(sys.argv[3])
google_drive_folder = sys.argv[4]

# create output directory and set as working directory
if not os.path.exists(dir_output):
    os.makedirs(dir_output)

os.chdir(dir_output)

#print script start time and input prameters to output file
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
# Custom imports
from test_eeAuthenticate            import test_eeAuthenticate
from ee_Saltmarsh_NDVI_composite    import tabulate_ndvi_class
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
#Authenticate Earth Engine
test_eeAuthenticate();

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Set up variables for input to GEE scripts
ee_saltmarsh_collection_name = "projects/patrickgosztonyi-lst/assets/2023-02-21_SaltMarshBySLC_ToGEE_V2"
ee_image_collection_name = 'COPERNICUS/S2_SR_HARMONIZED'
min_shape_are = 100 #meters

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Call the GEE function to create tables
tabulate_ndvi_class(
        feature_collection_name =   ee_saltmarsh_collection_name,
        image_collection_name =     ee_image_collection_name,
        google_drive_folder =       google_drive_folder
        )


##################################################
##################################################
print("\n####################\n")
myTime = "system time: " + datetime.datetime.now().strftime("%c")
print( myTime + "\n" )

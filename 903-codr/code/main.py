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
from test_eeAuthenticate            import test_eeAuthenticate;
from combine_csv                    import combine_csv_from_dir
from process_saltmarsh_gee_output   import prepare_dataframe_from_list

import numpy as np
import pandas as pd

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###


### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Authenticate Earth Engine
#test_eeAuthenticate();

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Specify the subfolder for the input data
subdir = "sample_gee_output"
newdir = os.path.join(dir_data, subdir)

# Call function to combine simillar CSVs
fulldata_list = combine_csv_from_dir(newdir)

# Pass data to function to clean/prepare dataset (as a pandas dataframe)
ndvidata = prepare_dataframe_from_list(fulldata_list)

print("First rows of converted dataframe:")
print(ndvidata.head())

# Create the output summary files
#   Set parameters for grouping
column_names_to_sum = ['NDVI_C0_area_km2', 'NDVI_C1_area_km2',
                    'NDVI_C2_area_km2', 'NDVI_C3_area_km2',
                    'all_area', 'veg_area']
precision = 4 #parameter to round output value - 4 points after the decimal


#   Create tables groubed by ecological framework level
ndvi_ecozone     = ndvidata.groupby(['Ecozone_id'])[column_names_to_sum].sum().round(precision)
ndvi_ecoprovince = ndvidata.groupby(['Ecoprovince_id'])[column_names_to_sum].sum().round(precision)
ndvi_ecoregion   = ndvidata.groupby(['Ecoregion_id'])[column_names_to_sum].sum().round(precision)
ndvi_ecodistrict = ndvidata.groupby(['Ecodistrict_id'])[column_names_to_sum].sum().round(precision)

#print("Eco geography NDVI summary tables:")
output_subfolder = "saltmarsh_ndvi_summary_csv"
#create output subfolder if needed
if not os.path.exists(output_subfolder):
    os.makedirs(output_subfolder)
#end if

ndvi_ecozone.to_csv(os.path.join(dir_output,output_subfolder,'ndvi_class_areas_by_eco{}.csv'.format('zones')))
ndvi_ecoprovince.to_csv(os.path.join(dir_output,output_subfolder,'ndvi_class_areas_by_eco{}.csv'.format('province')))
ndvi_ecoregion.to_csv(os.path.join(dir_output,output_subfolder,'ndvi_class_areas_by_eco{}.csv'.format('region')))
ndvi_ecodistrict.to_csv(os.path.join(dir_output,output_subfolder,'ndvi_class_areas_by_eco{}.csv'.format('district')))


### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###

##################################################
##################################################
print("\n####################\n")
myTime = "system time: " + datetime.datetime.now().strftime("%c")
print( myTime + "\n" )

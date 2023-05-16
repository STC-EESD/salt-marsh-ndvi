#!/usr/bin/env python

import os, sys, shutil, getpass
import pprint, logging, datetime
import stat

# get values from shell script arguments
dir_data   = os.path.realpath(sys.argv[1])
dir_code   = os.path.realpath(sys.argv[2])
dir_output = os.path.realpath(sys.argv[3])

# create output directory and set as working directory
if not os.path.exists(dir_output):
    os.makedirs(dir_output)

os.chdir(dir_output)

#print script start time and input prameters to output file
myTime = "system time: " + datetime.datetime.now().strftime("%c")
print( "\n" + myTime + "\n" )

print( "\ndir_data: "   + dir_data   )
print( "\ndir_code: "   + dir_code   )
print( "\ndir_output: " + dir_output )

#print( "\nos.environ.get('GEE_ENV_DIR'):")
#print(    os.environ.get('GEE_ENV_DIR')  )

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
from combine_csv                  import combine_csv_from_dir
from process_saltmarsh_gee_output import prepare_dataframe_from_list

import numpy  as np
import pandas as pd

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
# Specify the subfolder for the input data
input_subdir = "multiyear_sample_gee_output"
# input_newdir = os.path.join(dir_data, input_subdir)
input_newdir = input_subdir
print("Gathering GEE output CSVs from following folder: ")
print(os.path.abspath(input_newdir))

# Call function to combine simillar CSVs
fulldata_list = combine_csv_from_dir(input_newdir)

# Pass data to function to clean/prepare dataset (as a pandas dataframe)
ndvidata = prepare_dataframe_from_list(fulldata_list)

# Get a list of unique years from the dataset
year_list = ndvidata.year.unique()


# Create the output summary files
#   Set parameters for grouping
column_names_to_sum = [
    'NDVI_C0_area_km2',
    'NDVI_C1_area_km2',
    'NDVI_C2_area_km2',
    'NDVI_C3_area_km2',
    'veg_area',
    'all_area'
    ]
precision = 4 #parameter to round output value - 4 points after the decimal

# create empty lists to store the dataframes output from the summary-by-year loop (more efficient to concatenate a list of dataframes once)
ecz_summary_dfs = []
ecp_summary_dfs = []
ecr_summary_dfs = []
ecd_summary_dfs = []

# loop through year list
for year in year_list:
    
    # select only the data for the given year
    year_ndvidata = ndvidata.loc[ndvidata['year'] == year]

    #   Create summary tables groubed by ecological framework level
    ndvi_ecozone     = year_ndvidata.groupby(['Ecozone_id'])[column_names_to_sum].sum().round(precision)
    ndvi_ecoprovince = year_ndvidata.groupby(['Ecoprovince_id'])[column_names_to_sum].sum().round(precision)
    ndvi_ecoregion   = year_ndvidata.groupby(['Ecoregion_id'])[column_names_to_sum].sum().round(precision)
    ndvi_ecodistrict = year_ndvidata.groupby(['Ecodistrict_id'])[column_names_to_sum].sum().round(precision)
    
    #add the current year to the summary datasets
    ndvi_ecozone['year']     = year
    ndvi_ecoprovince['year'] = year
    ndvi_ecoregion['year']   = year
    ndvi_ecodistrict['year'] = year

    #add the single-year summary dataframes into a list for each ECF level
    ecz_summary_dfs.append(ndvi_ecozone)
    ecp_summary_dfs.append(ndvi_ecoprovince)
    ecr_summary_dfs.append(ndvi_ecoregion)
    ecd_summary_dfs.append(ndvi_ecodistrict)

#end for


# write out the combined summary datasets

#print("Eco geography NDVI summary tables:")
output_subfolder = "saltmarsh_ndvi_summary_csv"
#create output subfolder if needed
if not os.path.exists(output_subfolder):
    os.makedirs(output_subfolder)
#end if

print("\nSaving Salt Marsh NDVI Summary tables to following folder: ")
print(os.path.abspath(output_subfolder))
    
# concatenate the list of dataframes to create a single dataframe for output
ecozone_summary     = pd.concat(ecz_summary_dfs)
ecoprovince_summary = pd.concat(ecp_summary_dfs)
ecoregion_summary   = pd.concat(ecr_summary_dfs)
ecodistrict_summary = pd.concat(ecd_summary_dfs)

# output the combined dataframes to CSV
ecozone_summary.to_csv(os.path.join(dir_output,output_subfolder,
                                        'ndvi_class_areas_by_eco{}.csv'.format('zones')))
ecoprovince_summary.to_csv(os.path.join(dir_output,output_subfolder,
                                        'ndvi_class_areas_by_eco{}.csv'.format('province')))
ecoregion_summary.to_csv(os.path.join(dir_output,output_subfolder,
                                        'ndvi_class_areas_by_eco{}.csv'.format('region')))
ecodistrict_summary.to_csv(os.path.join(dir_output,output_subfolder,
                                        'ndvi_class_areas_by_eco{}.csv'.format('district')))


### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###

##################################################
##################################################
print("\n####################\n")
myTime = "system time: " + datetime.datetime.now().strftime("%c")
print( myTime + "\n" )

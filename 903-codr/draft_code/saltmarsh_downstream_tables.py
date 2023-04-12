"""
Statistics Canada
Patrick Gosztonyi
2023 March

Census of Environment - Salt Marsh Project
Downstream processing of GEE outputs - creating tables/data to present NDVI class area values for each level of the Ecological Framework

"""

# === Import block ===
import csv
import re
import ast
from pprint import pprint
from pathlib import Path
import pandas as pd

#getting single file for testing
filename = 'data/saltmarsh_NDVIclass_areas-ECOZONE-groupby-SLC_ID_1-part6of8.csv'

data_file = open(filename)
data_reader = csv.reader(data_file)
data_list = list(data_reader)

#create a list of the new columns for laters
#colnames = ['ECOZONE_id', 'ECODISTRICT','NDVI_C0_area',
#           'NDVI_C1_area', 'NDVI_C2_area', 'NDVI_C3_area']

#"""
# processing structure:
# 1 - Get list of input CSVs
input_dir = 'data'
filelist = []
for path in Path(input_dir).glob('*.csv'):
    filelist.append(path)
#en dloop
#print(filelist)

# 2 - combine all the lists from the CSVs together
alldata_list = []
for index,filepath in enumerate(filelist):
    #create a list from the CSV
    data_file = open(filepath)
    data_reader = csv.reader(data_file) #small enough files to open them all atonce
    data_list = list(data_reader)
    
    nogeo = []
    
    if index == 0:
        #keep names in first row
        for row in data_list:
            row = row[1:-1] #remove the geo column at the last position
            nogeo.append(row)
    elif index > 0:
        for ri, row in enumerate(data_list):
            if ri == 0:
                pass #skip the header row
            else:
                #process values
                row = row[1:-1] #remove the geo column
                nogeo.append(row)
                
    # remove the system index
            
    # append the output to the full dataset
    alldata_list.extend(nogeo) 

#end loop

'''
# checking progress
print('aggregated file list:')
pprint(alldata_list[:20])
print('\n====================\n')
'''

# 3 -  parse the NDVI values from GEE output into seprate columns for each NDVI class
newdata = []
newdata.append(alldata_list[0]) # get the headers
for index,row in enumerate(alldata_list[1:]):
    

        # get the values
        gee_vals = row[-1] # the last cell contains the values

        def _parse_gee_vals_to_dictionary(gee_val_str):
            '''
            Goal is to parse the pure string values output by GEE into 
            python-compatible objects (lists and dictionaries)
            '''
            dict_list = [] #generate an empty list

            #first isolate the dictionary-like strings
            item = re.findall(r'\{.*?\}',gee_val_str)

            # replace the equals in the string to colons
            item = re.sub(r'=',':', gee_val_str)
            # put quotes around the dictonary keys so they appear as strings
            item = re.sub(r'NDVI_Class',"'NDVI_Class'", item)
            item = re.sub(r'sum',"'sum'",item)

            # 
            dict_item = ast.literal_eval(item)
            dict_list.append(dict_item)

            return dict_list
        #end function

        #use the function to replace the value
        data = _parse_gee_vals_to_dictionary(gee_vals)
        row[-1] = data[0]
        
        newdata.append(row)
#end loop
#print('adjusted GEE output val list: ')
#pprint(newdata)

# 4 - parse the full dataset into the new columns for further tables
'''
To do:
    - split the ecodistrict ID into its four components (?)
    - create columns for each of the NDVI classes

'''



#Adjust the headers
old_headers = newdata[0][0:3]
ndvi_class_names = ['NDVI_C0_area_km2', 'NDVI_C1_area_km2',
                    'NDVI_C2_area_km2', 'NDVI_C3_area_km2']
#create new output, with new headers
finaldata = []
finaldata.append(old_headers)
finaldata[0].extend(ndvi_class_names)

# parse the NDVI columns
for row in newdata[1:]:
    
    ndvi_dictlist = row[3]
    
    def _ndvi_dicts_to_list(dict_list):
        #create list to store the ourput values
        #create list with 4 positions, one for each NDVI class (0/None, 1/Low, 2/Med, 3/High)
        listvals = [0,0,0,0]
        
        
        for ndvidict in dict_list:
            #get the values from each part of the dictionary
            ndviclass = ndvidict['NDVI_Class'] 
            classarea = ndvidict['sum']

            # assign the values to the correct class
            if ndviclass == 0:
                listvals[0] = classarea
            elif ndviclass == 1:
                listvals[1] = classarea
            elif ndviclass == 2:
                listvals[2] = classarea
            elif ndviclass == 3:
                listvals[3] = classarea

        return listvals
        #end looop
    
    ndvi_class_areas = _ndvi_dicts_to_list(ndvi_dictlist)
    
    finalrow = row[:3]
    finalrow.extend(ndvi_class_areas)
    
    finaldata.append(finalrow)
    #end function
#end loop

#pprint(finaldata[:10])

# 5 - calculate the area sums for each of the area classes
# still need to find a way to create columns for each of the framework levels

#create a pandas dataframe with the cleaned-up list
ndvi_df = pd.DataFrame.from_records(finaldata[1:], columns= finaldata[0])
ndvi_df = ndvi_df.round(8) #evening out the number of decimals. eliminate floating point noise for 0 values
pprint(ndvi_df)

#testing out getting the sum of group values
precision = 4 # 0.0001 square km is equal to 100 square m, or one sentinel-2 pixel. No finer presision needed in output tables
ndvi_group_ecodist = ndvi_df.groupby(['ECOZONE','Ecodistrict_id'])[ndvi_class_names].sum().round(precision)
ndvi_group_ecozone = ndvi_df.groupby(['ECOZONE'])[ndvi_class_names].sum().round(precision)

print("Writing output tables...")

print("   - SLC data table...")
ndvi_df.to_csv('output/output_ndvi_class_area_data.csv', index=False)
print("   - Group by ecozone table...")
ndvi_group_ecozone.to_csv('output/output_ndvi_class_area_groupby_ecozones.csv')
print("   - Group by ecodistrict table...")
ndvi_group_ecodist.to_csv('output/output_ndvi_class_area_groupby_ecodistrict.csv')
print("All tables done.")

#"""


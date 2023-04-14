import numpy as np
import pandas as pd
import re
import ast

def prepare_dataframe_from_list(datalist):
    """
    Purpose: Take a list of saltmarsh data, convert it to a pandas data frame 
        and parse the contents in preparation for creating summary tables

    Input: A dataset (list of lists) whose first row is column names
    Output: A pandas dataframe (?)
    """
    
    # Convert the input into a pandas dataframe
    #   First row (row 0) is column names, data is everything after (row 1:)
    df = pd.DataFrame.from_records(datalist[1:], columns = datalist[0])
    
    # Remove the system:index and geo columns (not needed)
    # Note that the SLC_ID column is the unique identifier 
    df = df.drop(columns = ['system:index','ECOZONE','.geo'])

    # Convert the NDVI_class cell-value into a proper python dictionary
    
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

        # can now evaluate the dictionary-like string into a python dictionary
        dict_item = ast.literal_eval(item)
        dict_list.append(dict_item)
        
        # Now convert the dict list into a dictionary with the new columns names
        ndviclass_dict = {'NDVI_C0_area_km2': 0,
                          'NDVI_C1_area_km2': 0,
                          'NDVI_C2_area_km2': 0,
                          'NDVI_C3_area_km2': 0}

        for ndvidict in dict_list[0]:
            #get the values from each part of the dictionary
            ndviclass = ndvidict['NDVI_Class']
            classarea = ndvidict['sum']

            # assign the values to the correct class
            if ndviclass == 0:
                ndviclass_dict['NDVI_C0_area_km2'] = classarea
            elif ndviclass == 1:
                ndviclass_dict['NDVI_C1_area_km2'] = classarea
            elif ndviclass == 2:
                ndviclass_dict['NDVI_C2_area_km2'] = classarea
            elif ndviclass == 3:
                ndviclass_dict['NDVI_C3_area_km2'] = classarea
        #end loop 

        return ndviclass_dict
    #end function
    
    df['ndvi_class_area_km2'] = df['ndvi_class_area_km2'].apply(_parse_gee_vals_to_dictionary)


    # Split the NDVI class area values into seperate columns
    #   Since the cell value for ndvi_class_arae_km2 is now a dictionary with appropriate column names, 
    #   can apply the series to the dataframe, which should expand the values into their own column

    df[['NDVI_C0_area_km2','NDVI_C1_area_km2','NDVI_C2_area_km2','NDVI_C3_area_km2']] = df['ndvi_class_area_km2'].apply(pd.Series)
    df = df.drop(columns = 'ndvi_class_area_km2')

    # ---
    return df

#end function

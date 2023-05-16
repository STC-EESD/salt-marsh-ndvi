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
    
    # Remove the system:index and geo columns created by Earth Engine (not needed)
    # Note that the SLC_ID column is the unique identifier 
    df = df.drop(columns = ['system:index','ECOZONE','.geo'])

    # Create columns for the remaining Ecological Framework levels from the heirarchical Ecodistrict ID
    #   To do so, only remove one set of right-hand period-seperated numbers for each framework level, starting with Ecodistrict IDs
    def _split_eco_heirarchy_id(input_value):
        '''
        Purpose: rome the right-hand, period separated portion of the ecological framework ID to define         the next more generalised framework level ID
        '''
        val = str(input_value)
        val = val.rsplit('.', maxsplit = 1)
        output = val[0] #ignore the portion that was split off

        return output
    #end subfunction

    df['Ecoregion_id']   = df['Ecodistrict_id'].apply(_split_eco_heirarchy_id)
    df['Ecoprovince_id'] = df['Ecoregion_id'].apply(_split_eco_heirarchy_id)
    df['Ecozone_id']     = df['Ecoprovince_id'].apply(_split_eco_heirarchy_id)


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
    #   can apply the series to the dataframe, which expands the values into their own column

    ndvi_class_names = ['NDVI_C0_area_km2','NDVI_C1_area_km2','NDVI_C2_area_km2','NDVI_C3_area_km2']

    df[ndvi_class_names] = df['ndvi_class_area_km2'].apply(pd.Series)
    df = df.drop(columns = 'ndvi_class_area_km2')

    # Calcualte row sums of: a) all area, b) vegetation-only area

    def _sum_rows_by_columns(pd_dataframe,
                             new_col_name,
                             list_of_cols_sum):

        pd_dataframe[new_col_name] = pd_dataframe[list_of_cols_sum].astype(float).sum('columns')

        return pd_dataframe
    #end subfunction
    
    # Sum the total area of all classes for the row (all classes, 0+1+2+3)
    df = _sum_rows_by_columns(df, "all_area", ndvi_class_names)

    # Sum the total of vegetated areas only (classes 1+2+3)
    df = _sum_rows_by_columns(df, "veg_area", ndvi_class_names[1:])

    # ---
    return df

#end function

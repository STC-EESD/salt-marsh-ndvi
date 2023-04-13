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

        return dict_list
    #end function
    
    df['ndvi_class_area_km2'] = df['ndvi_class_area_km2'].apply(_parse_gee_vals_to_dictionary)


    # Split the NDVI class area values into seperate columns

    # Create new columns for each NDVI class
    df = pd.concat([df,pd.DataFrame(columns=['NDVI_C0_area_km2','NDVI_C1_area_km2','NDVI_C2_area_km2','NDVI_C3_area_km2'])])
    
    '''
    def _split_ndvi_class_areas(ndvi_class_cell):
        """
        Purpose: Take the list ofdictionaries in the cell, and transfer the contents to new rows

        Input:
        Output:
        """
        # Assumes that the input is a list of dictionaries

        # transfer the list of dictionaries into new rows

        for ndvidict in ndvi_class_cell:
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

        #end looop

    #end subfunction
    '''
    #apply function to dataframe
    


    # ---
    return df

#end function

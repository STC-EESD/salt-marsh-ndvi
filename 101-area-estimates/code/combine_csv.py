from    pathlib import Path
import  csv

def combine_csv_from_dir(directory):
    """
    This function combines several simillar CSVs in a directory into one list

    Input:  directory, as a path
    Output: a list with the combined datasets

    """
    
    # Given a directory, get a list of CSV files
    filelist = []
    for path in Path(directory).glob('*.csv'):
        filelist.append(path)
    #endloop

    # Create lists from each CSV, and combine them
    alldata_list = []
    
    for index, filepath in enumerate(filelist):

        # Create a list from the CSV
        data_file =  open(filepath)
        data_reader = csv.reader(data_file) # files are small enough to read in all at once
        data_list = list(data_reader)

        if index == 0: #if the first file
            # use all rows, including row of columns names
            for row in data_list:
                alldata_list.append(row)

        elif index > 0: #files after the first
            #need to skip the first row, which has column names
            for rowindex, row in enumerate(data_list):
                if rowindex == 0:
                    pass # skip this row
                else:
                    alldata_list.append(row)
                #endif
            #endloop
        #endif
    #endloop

    return(alldata_list)

#end function



import ee

def tabulate_ndvi_class(
        feature_collection_name,
        groupby_attribute = 'SLC_ID_1', #default for the salt marsh polygons
        image_collection_name = 'COPERNICUS/S2_SR_HARMONIZED', #assumes Sentinel-2 data 
        min_feature_size = 100, #square meters
        year = '', #single year input
        google_drive_folder = ''
        ):

    """
    Purpose: Use Earth Engine to classify a growing season NDVI composite, calcualte the area by NDVI class
        and create CSV files with the information.
    Assumptions:
        - The input feature collection contains polygons with attributes 'ECOZONE' and 'SLC_ID'
        - The input image collection is Sentinel-2 surface reflectance data

    Notes:
        - This script divides the output results by ecozone, and the region statistics calculated by Soil Landscape classification (SLC), in order for the computations to complete within Earth Engines batch processing time and memory limits. This combination was determined as the best balance between processing time and avoiding splitting the dataset output unnecessarily 
    """
    
    thisFunctionName = 'tabulate_ndvi_class'
    print(f"\n### {thisFunctionName}() starts (feature_collection_name: {feature_collection_name}, groupby_attribute: {groupby_attribute}, image_collection_name: {image_collection_name}, min_feature_size: {min_feature_size}, year: {year}, google_drive_folder: {google_drive_folder})... \n")

    # get the salt marsh polygons above 100m2 (larger than 1 sentinel-2 pixel) 
    fc_saltmarsh = ee.FeatureCollection(feature_collection_name).filter(ee.Filter.gt('Shape_Area',100))

    ### REPLACE THIS WITH COMPLETED NDVI COMPOSITE METHOD ###
    # create a one-year NDVI composite image with pixel areas for given features
    s2_ndvi_areas = _create_test_ee_ndvi_raster(feature_collection_name,image_collection_name, year)

    # from the input feature collection, get a list of unique ecozones
    ecozone_colname = 'ECOZONE'
    unique_ecozones = fc_saltmarsh.distinct(ecozone_colname).aggregate_array(ecozone_colname).getInfo() #retreive the actual values to use in python iterator

    # iterate through ecozone list, and create one file per ecozone

    for i, geo in enumerate(unique_ecozones):

        # get a subset of the slatmarsh polygons for the current ecozone
        subset_fc = fc_saltmarsh.filter(ee.Filter.eq(ecozone_colname,geo))

        # get the unique list of the grouping attribute subgeographies
        unique_group_geo = ee.List(subset_fc.distinct(groupby_attribute).aggregate_array(groupby_attribute))

        #create a mappable function
        def _saltmarsh_NDVI_by_area(subgeo_name):

            # given the name of a single ecogeography (from a list), calculate the area of NDVI classes
    
            # first filter to get a subset all the polygons for that ecogeography
            subset = ee.FeatureCollection(subset_fc.filter(ee.Filter.eq(groupby_attribute,subgeo_name)))
            ecodistrict_name = ee.String(subset.first().get('Ecodistr_1')) #gets the ecodistrict name for the given SLC in the subset

            #next use reduce regions to get the NDVI class areas for the subset
            reduced = s2_ndvi_areas.reduceRegion(
                reducer = ee.Reducer.sum().group(
                    groupField = 1,
                    groupName ='NDVI_Class'
                ),
                geometry= subset,
                scale= 10,
                maxPixels = 10e9
                #tileScale = 3 #setting this can help with out of memory issues, but takes more time
            )
            #convert the list output from the reducer into a feature
            # Takes two dictionaries as input, first is the Key, second is the Value of the key/value pairs
            output = ee.Feature(None, ee.Dictionary.fromLists( \
                [ee.String(ecozone_colname),'Ecodistrict_id',ee.String(groupby_attribute),'ndvi_class_area_km2', 'year'], \
                [geo, ecodistrict_name, ee.String(subgeo_name), reduced.get('groups'), year]))
    
            #return the output
            return output
        # end function
    
        # call the mapped function to get the feature collection
        fc_for_table = ee.FeatureCollection(unique_group_geo.map(_saltmarsh_NDVI_by_area))
        #print("output table",fc_for_table.limit(10).getInfo())
    
        # export the reduced feature collection
        # create the table name programatically
        task_name = f"saltmarsh_NDVIclass_areas_{year}-{ecozone_colname}-groupby-{groupby_attribute}-part{i+1}of{len(unique_ecozones)}"

        #Define the task to Export the table to drive
        mytask = ee.batch.Export.table.toDrive(
          collection = fc_for_table,
          description = task_name,
          fileNamePrefix= task_name,
          folder= google_drive_folder,
          fileFormat = 'CSV'
        )
        print("task defined: {}".format(task_name))

        #start the task
        mytask.start();print("task submitted")

    #end loop

    print(f"\n### {thisFunctionName}() exits...")

    return(None)

    #func
#end function

def _create_test_ee_ndvi_raster(
        feature_collection_name,
        image_collection_name = 'COPERNICUS/S2_SR_HARMONIZED',
        year = ''):
    """
    Purpose: create an image collection of Sentinel-2 imagery to be used for testing
    """
    ### ------------------------- ###
    # Define utility functions
    # (This is not the final masking function!)

    #cloud masking function
    def maskS2clouds(image):
      qa = image.select('QA60')
      # Bits 10 and 11 are clouds and cirrus, respectively.
      cloudBitMask = 1 << 10;
      cirrusBitMask = 1 << 11;
      # Both flags should be set to zero, indicating clear conditions.
      mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
      return image.updateMask(mask).divide(10000)
    #end function

    # calculate NDVI for images (mappable function)
    def addBandNDVI(image):
      ndvi = image.normalizedDifference(['B8','B4']).rename('NDVI')
      return image.addBands(ndvi)
    #end finction

    # Classsify the NDVI into three classes (mappable function)
    def addBanddiscretizedNDVI(image) :
      ndvi = image.select('NDVI')
      discretizedNDVI = (ndvi
        .where(ndvi.lt( 0.10),                 0)
        .where(ndvi.gte(0.10).And(ndvi.lt(0.33)), 1)
        .where(ndvi.gte(0.33).And(ndvi.lt(0.66)), 2)
        .where(ndvi.gte(0.66),                 3)
        .rename('discretizedNDVI'))
      return image.addBands(discretizedNDVI)
    #end function
    
    ### ----------------------------- ###
    # Preparing imagery
    
    #create feature collection 
    input_fc = ee.FeatureCollection(feature_collection_name)
    #input_fc = ee.FeatureCollection("projects/patrickgosztonyi-lst/assets/2023-02-21_SaltMarshBySLC_ToGEE_V2")
    
    #create the date variables for the growing season
    startdate = ee.Date.fromYMD(year, 5, 1) # May 1st
    enddate = ee.Date.fromYMD(year, 9, 30) # September 30th

    #getting the imagery
    s2 = (ee.ImageCollection(image_collection_name)
                  .filterDate(startdate, enddate)
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',30))
                  .filterBounds(input_fc.geometry().bounds())
                  .map(maskS2clouds))

    # applying NDVI and NDVI classification
    s2_ndvi = s2.map(addBandNDVI)
    annualAverageNDVI = addBanddiscretizedNDVI(s2_ndvi.select('NDVI').mean())

    # getting the pixel area raster and adding the NDVI band info
    # first create the area raster (km2), then add the NDVI class band
    sm_area_ndvi_bin = ee.Image.pixelArea().divide(1e6).addBands(annualAverageNDVI.select("discretizedNDVI"))
    
    return(sm_area_ndvi_bin)
    
#end function



def _create_ee_saltmarsh_ndvi_image(
        feature_collection_name,
        image_collection_name = 'COPERNICUS/S2_SR_HARMONIZED',
        year = '')):

    '''
    Purpose: create an NDVI composite for a single year growing season (May 1st to Oct 31st) that includes image filtering appropriate for analysing salt marsh vegetation.

    '''
    # Define the date range
    startdate = ee.Date.fromYMD(year,  5, 1) #May 1st
    enddate =   ee.Date.fromYMD(year, 11, 1) #Oct 31st 

    # Define cloud masking parameters

    # Get imagery collection and run the cloud masking algorithm

    # Calcualte Vegetation Indices and Water Indices

    # Calculate the Tidal Marsh Innundation Index (TMII)

    # Apply the TMII and NDVI masks to image collection

    # Create the annual/growing season average NDVI

    # Apply the NDVI classification to average dataset

    # Create an area raster and add in the classified annual average NDVI

    #return the classified average NDVI image
    return()

#end function

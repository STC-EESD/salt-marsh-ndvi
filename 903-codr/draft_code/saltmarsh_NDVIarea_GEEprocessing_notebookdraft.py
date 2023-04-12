#Tested/developped in a Google Colab notebook (simplifies authentication)

# imports and other setup
import ee
ee.Authenticate()
ee.Initialize()

# === Preparing the input Salt Marsh data ===

# Salt Marsh polygons
fcSaltMarsh = ee.FeatureCollection("projects/patrickgosztonyi-lst/assets/2023-02-21_SaltMarshBySLC_ToGEE_V2") \
  .filter(ee.Filter.gt('Shape_Area',100))

print("fcSaltMarsh polygon count:", fcSaltMarsh.size().getInfo())
print("salt marsh polys: \n", fcSaltMarsh.limit(10).getInfo())

# === Preparing Sentinel-2 imagery ===
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

#getting the imagery  
s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') 
                  .filterDate('2020-05-01', '2020-10-01') 
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',30)) 
                  .filterBounds(fcSaltMarsh.geometry().bounds()) 
                  .map(maskS2clouds))


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
 
# applying NDVI and NDVI classification
s2_ndvi = s2.map(addBandNDVI)
annualAverageNDVI = addBanddiscretizedNDVI(s2_ndvi.select('NDVI').mean())

# getting the pixel area raster and adding the NDVI band info
# first create the area raster (km2), then add the NDVI class band
sm_area_ndvi_bin = ee.Image.pixelArea().divide(1e6).addBands(annualAverageNDVI.select("discretizedNDVI"));

#print('image properties',sm_area_ndvi_bin.getInfo())


# === Calculating NDVI Class Areas in Salt Marsh polgons ===

#creating function 
def calc_ndvi_areas(input_fc, fc_colname, fc_subcolname, input_ndvi):
  '''
  input_fc: a feature collection (ee.FeatureCollection) with columns of attributes (ideally representing ecogeographies (ecozones, etc))
  fc_colname: the column name to use as the batch variable (ex: ecozone)
  fc_subcolname: the column name for the grouping variable (ex: SLC)
  input_ndvi: image (ee.Image) with pixel area, ndvi and ndvi classes
    - Assumes that the pixel area band is the first, and contains classified NDVI values
  filterinfo: optional parameter to provide filter info to output table

  '''
  # from the input feature collection, get the list of unique ecogeography names
  unique_ecogeo = input_fc.distinct(fc_colname).aggregate_array(fc_colname).getInfo() #need getInfo(), to use values as iterator
  unique_ecogeos = ee.List(input_fc.distinct(fc_colname).aggregate_array(fc_colname))
  print("unique ecogeos ({0}): {1}".format(fc_colname,unique_ecogeo))

  for i,geo in enumerate(unique_ecogeo):

    subset_fc = input_fc.filter(ee.Filter.eq(fc_colname,geo))

    #get list of subgeos for one ecozone
    unique_subecogeo = ee.List(subset_fc.distinct(fc_subcolname).aggregate_array(fc_subcolname))

    #print("geo:",geo,", subgeos: ",unique_subecogeo.getInfo())

    # === SUBFUNCTION DEFINITIONS ===
    #create a mappable function
    def _saltmarsh_NDVI_by_area(subgeo_name):
      # given the name of a single ecogeography (from a list), calculate the area of NDVI classes
      
      # first filter to get a subset all the polygons for that ecogeography
      subset = ee.FeatureCollection(subset_fc.filter(ee.Filter.eq(fc_subcolname,subgeo_name)))
      ecodistrict_name = ee.String(subset.first().get('Ecodistr_1')) #gets the ecodistrict name for the given SLC in the subset
      
      #next use reduce regions to to get the NDVI class areas for the subset
      reduced = input_ndvi.reduceRegion(
          reducer = ee.Reducer.sum().group(
              groupField = 1,
              groupName ='NDVI_Class'
          ),
          geometry= subset,
          scale= 10,
          maxPixels = 10e9
          #tileScale = 3 #setting this can help with out of memory issues, but takes more time
        )
      #convert the list output from the reducer into a feature (dictionaries are pairs of key/value lists)
      output = ee.Feature(None, ee.Dictionary.fromLists( \
          [ee.String(fc_colname),'Ecodistrict_id',ee.String(fc_subcolname),'ndvi_class_area_km2'], \
          [geo, ecodistrict_name, ee.String(subgeo_name), reduced.get('groups')])) 

      #return the output
      return output
    # end function

    # call the mapped function to get the feature collection
    fc_for_table = ee.FeatureCollection(unique_subecogeo.map(_saltmarsh_NDVI_by_area))
    #print("output table",fc_for_table.limit(10).getInfo())

    # export the reduced feature collection
    # create the table name programatically
    #task_name = ('saltmarsh_NDVI_class_area_' + fc_colname + '-' + + '_by_' + fc_subcolname + 's')
    task_name = f"saltmarsh_NDVIclass_areas-{fc_colname}-groupby-{fc_subcolname}-part{i+1}of{len(unique_ecogeo)}"

    #Define the task to Export the table to drive
    mytask = ee.batch.Export.table.toDrive(
      collection = fc_for_table,
      description = task_name,
      fileNamePrefix= task_name,
      folder= 'saltmarsh_slc',
      fileFormat = 'CSV'
    )
    print("task defined: {}".format(task_name))

    #start the task
    mytask.start();print("task submitted")

#end function

#Call the function
calc_ndvi_areas(fcSaltMarsh,'ECOZONE','SLC_ID_1',sm_area_ndvi_bin)


print('all tasks submitted')


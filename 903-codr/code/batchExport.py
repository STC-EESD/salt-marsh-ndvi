
import ee, math;
from coe import eeCollection_addIndexes, eeCollection_addBatchIDs;

def batchExportByYear(
    batchSize,
    batchID,
    year,
    featureCollectionName,
    minShapeArea,
    imageCollectionName,
    google_drive_folder
    ):

    thisFunctionName = "batchExportByYear";
    print( "\n### " + thisFunctionName + " starts (batchID:" + str(batchID) + ", year:" + str(year) + ") ..." );

    # ####################################
    fcSaltMarsh = ee.FeatureCollection(
        ee.FeatureCollection(featureCollectionName) \
        .filterMetadata('Shape_Area','greater_than',minShapeArea) \
        .toList( batchSize, batchID * batchSize )
        );
    print( "fcSaltMarsh.size().getInfo():", fcSaltMarsh.size().getInfo() );

    # ####################################
    def _addBand_NDVI(image):
        ndvi = image.normalizedDifference(['B8','B4']).rename('NDVI');
        return image.addBands(ndvi);

    def _addBand_discretizedNDVI(image):
        ndvi = image.select('NDVI');
        discretizedNDVI = ndvi \
            .where( ndvi.lt( 0.10),                    0) \
            .where( ndvi.gte(0.10).And(ndvi.lt(0.33)), 1) \
            .where( ndvi.gte(0.33).And(ndvi.lt(0.66)), 2) \
            .where( ndvi.gt( 0.66),                    3) \
            .rename('discretizedNDVI');
        return image.addBands(discretizedNDVI);

    # ####################################
    startDate = ee.Date.fromYMD(year, 1, 1);
    endDate   = ee.Date.fromYMD(year,12,31).advance(1,'day');
    S2SR      = ee.ImageCollection(imageCollectionName) \
        .filter(ee.Filter.date(startDate,endDate)) \
        .filterBounds(fcSaltMarsh) \
        .map(_addBand_NDVI);
    # print( "S2SR.size().getInfo():" , S2SR.size().getInfo() );

    annualAverageNDVI = _addBand_discretizedNDVI(S2SR.select('NDVI').mean());
    # print( "annualAverageNDVI.bandNames().getInfo():" , annualAverageNDVI.bandNames().getInfo() );

    areaImage = ee.Image.pixelArea().divide(1e6) \
        .addBands(annualAverageNDVI.select('discretizedNDVI'));
    print( "areaImage.bandNames().getInfo():" , areaImage.bandNames().getInfo() );

    areasByDiscretizedNDVI = areaImage.reduceRegion(
        reducer = ee.Reducer.sum().group(
            groupField = 1,
            groupName  = 'discretizedNDVI'
            ),
        geometry  = fcSaltMarsh.geometry(),
        scale     = 1000, # 100,
        tileScale = 4,
        maxPixels = 1e10
        );
    # classAreas = ee.List(areas.get('groups'));
    # print("classAreas:",classAreas);

    ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
    exportString = 'area_by_discretizedNDVI_' + '{:04d}'.format(batchID) +'_'+ str(year);
    temp_task = ee.batch.Export.table.toDrive(
        collection     = areasByDiscretizedNDVI,
        folder         = google_drive_folder,
        description    = exportString,
        fileNamePrefix = exportString,
        fileFormat     = 'CSV'
        );
    print("### batch export task defined ...");

    temp_task.start();
    print("### batch export task started ...");

    # ####################################
    print( "### " + thisFunctionName + " exits (batchID:" + str(batchID) + ", year:" + str(year) + ") ..." );
    return( None );

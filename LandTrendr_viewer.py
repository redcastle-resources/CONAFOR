from geeViz import changeDetectionLib
import ee 
ee.Initialize() 
import geeViz.getImagesLib as getImagesLib
Map = getImagesLib.Map
ee = getImagesLib.ee

startYear = 1989
endYear = 2023


lt_fit = ee.ImageCollection('projects/ee-jheyer2325/assets/lcms-training_module-3_landTrendr')

# Convert into fitted, annual outputs: e.g., magnitude of change, slope of change, duration of change for each year
lt_fit = changeDetectionLib.batchSimpleLTFit(lt_fit,startYear,endYear,None,bandPropertyName='band',arrayMode=True)

#Add to the map
Map.clearMap()


Map.addLayer(lt_fit,{'bands':'swir2_LT_fitted,nir_LT_fitted,red_LT_fitted','min':0.15,'max':0.6},'LandTrendr All Predictors Time Series')



Map.turnOnInspector()
Map.view()
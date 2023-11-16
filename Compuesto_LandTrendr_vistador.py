'''
Este script utiliza módulos de geeViz para mapear series de tiempo y lapsos de tiempo compuestos y landtrendr.
'''

# Módulos de geeViz 
from geeViz import changeDetectionLib
import ee 
ee.Initialize() 
import geeViz.getImagesLib as getImagesLib
Map = getImagesLib.Map
ee = getImagesLib.ee

# Seleccionar rango de años para mapear. 
# Seleccionar menos años para mapear más rápido
startYear = 1985
endYear = 2023

# Parámetros de visualización. No cambies
vizParamsFalse10k = {\
  'min': 0.05*10000,
  'max': [0.5*10000,0.6*10000,0.6*10000],
  'bands': 'swir1,nir,red',
  'gamma': 1.6\
}

vizParamsTrue10k = {\
  'min': 0,
  'max': [0.2*10000,0.2*10000,0.2*10000],
  'bands': 'red,green,blue'\
}

vizParamsFalse = {\
  'min': 0.05,
  'max': [0.5,0.6,0.6],
  'bands': 'swir1_LT_fitted,nir_LT_fitted,red_LT_fitted',
  'gamma': 1.6\
}

# Importar conjuntos de datos
lt_fit = ee.ImageCollection('projects/ee-jheyer2325/assets/lcms-training_module-3_landTrendr')
composites = ee.ImageCollection('projects/ee-jheyer2325/assets/lcms-training_module-2_composites') 

# Convertir en productos anuales ajustados: por ejemplo, magnitud del cambio, pendiente del cambio, duración del cambio para cada año
lt_fit = changeDetectionLib.batchSimpleLTFit(lt_fit,startYear,endYear,None,bandPropertyName='band',arrayMode=True)

# Filtrar fechas
composite_tlps = composites.filter(ee.Filter.calendarRange(startYear,endYear,'year'))
lt_tlps = lt_fit.filter(ee.Filter.calendarRange(startYear,endYear,'year'))

# Añadir al mapa
Map.clearMap()

Map.addLayer(composite_tlps,vizParamsFalse10k,'Composites series de tiempo') 
Map.addTimeLapse(composite_tlps,vizParamsFalse10k,'Composites lapso de tiempo') 
Map.addLayer(lt_fit,vizParamsFalse,'LandTrendr series de tiempo')
Map.addTimeLapse(lt_tlps,vizParamsFalse,'LandTrendr lapso de tiempo')


Map.turnOnInspector()
Map.view()
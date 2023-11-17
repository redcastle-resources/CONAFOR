"""
   Copyright 2023 Ian Housman

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

#Ejemplo de cómo visualizar salidas CCDC usando las herramientas de visualización de Python
#Agrega productos de cambio y armónicos instalados desde la salida CCDC al visor
#El flujo de trabajo general para CCDC es ejecutar el script CCDCWrapper.py y luego utilizar el modelo armónico para una fecha determinada.
#o utilizar los rompes para la detección de cambios. Todo esto se demuestra en este ejemplo.
####################################################################################################
import os,sys
sys.path.append(os.getcwd())

#Module imports
import geeViz.getImagesLib as getImagesLib
import geeViz.changeDetectionLib as changeDetectionLib
ee = getImagesLib.ee
Map = getImagesLib.Map
Map.clearMap()
####################################################################################################
#Traer recurso de imagen CCDC
#Se supone que es una imagen de matrices devuelta por el método ee.Algorithms.TemporalSegmentation.Ccdc
ccdcImg = ee.ImageCollection('projects/ee-jheyer2325/assets/lcms-training_module-3_CCDC')\
          .select(['tStart','tEnd','tBreak','changeProb','red.*','nir.*','swir1.*','swir2.*','NDVI.*']).mosaic()
# ccdcImg = ee.ImageCollection('projects/lcms-292214/assets/R8/PR_USVI/Base-Learners/CCDC-Landsat_1984_2020').mosaic()
#Especifique qué armónicos usar al predecir el modelo CCDC
#CCDC exporta los primeros 3 armónicos (1 ciclo/año, 2 ciclos/año y 3 ciclos/año)
#Si solo desea ver patrones anuales, especifique [1]
#Si desea un ajuste más preciso en el valor predicho, incluya también el segundo o tercer armónico [1,2,3]
whichHarmonics = [1,2,3]

#Whether to fill gaps between segments' end year and the subsequent start year to the break date
fillGaps = False

#Specify which band to use for loss and gain. 
#This is most important for the loss and gain magnitude since the year of change will be the same for all years
changeDetectionBandName = 'NDVI'


# Choose whether to show the most recent ('mostRecent') or highest magnitude ('highestMag') CCDC break
sortingMethod = 'mostRecent'
####################################################################################################
#Pull out some info about the ccdc image
startJulian = 1
endJulian = 365
startYear = 1984
endYear = 2023

#Add the raw array image
Map.addLayer(ccdcImg,{'opacity':0},'Raw CCDC Output',False)

#Extract the change years and magnitude
changeObj = changeDetectionLib.ccdcChangeDetection(ccdcImg,changeDetectionBandName);
changeDetectionLib.lossMagPalette = changeDetectionLib.lossMagPalette.split(',')
changeDetectionLib.lossMagPalette.reverse()
Map.addLayer(changeObj[sortingMethod]['loss']['year'],{'min':startYear,'max':endYear,'palette':changeDetectionLib.lossYearPalette},'Loss Year')
Map.addLayer(changeObj[sortingMethod]['loss']['mag'],{'min':-0.5,'max':-0.1,'palette':changeDetectionLib.lossMagPalette},'Loss Mag',False);
Map.addLayer(changeObj[sortingMethod]['gain']['year'],{'min':startYear,'max':endYear,'palette':changeDetectionLib.gainYearPalette},'Gain Year');
Map.addLayer(changeObj[sortingMethod]['gain']['mag'],{'min':0.05,'max':0.2,'palette':changeDetectionLib.gainMagPalette},'Gain Mag',False);

#Apply the CCDC harmonic model across a time series
#First get a time series of time images 
yearImages = changeDetectionLib.getTimeImageCollection(startYear,endYear,startJulian,endJulian,0.1);

#Then predict the CCDC models
fitted = changeDetectionLib.predictCCDC(ccdcImg,yearImages,fillGaps,whichHarmonics)
Map.addLayer(fitted.select(['.*_fitted']),{'opacity':0},'Fitted CCDC',True);
Map.addLayer(fitted.filter(ee.Filter.calendarRange(1990,1990,'year')).select(['.*_fitted']),{'opacity':0},'Fitted CCDC 1990',True);

# Synthetic composites visualizing
# Take common false color composite bands and visualize them for the next to the last year

# First get the bands of predicted bands and then split off the name
fittedBns = fitted.select(['.*_fitted']).first().bandNames()
bns = fittedBns.map(lambda bn: ee.String(bn).split('_').get(0))

# Filter down to the next to the last year and a summer date range
syntheticComposites = fitted.select(fittedBns,bns)\
    .filter(ee.Filter.calendarRange(endYear-1,endYear-1,'year'))\
    .filter(ee.Filter.calendarRange(190,250)).first()

# Visualize output as you would a composite
Map.addLayer(syntheticComposites,getImagesLib.vizParamsFalse,'Synthetic Composite')
####################################################################################################
#Load the study region
studyArea = ccdcImg.geometry()
Map.addLayer(studyArea, {'strokeColor': '0000FF'}, "Study Area", False)
# Map.centerObject(studyArea)
####################################################################################################
Map.turnOnInspector()
Map.view()
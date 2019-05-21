import arcpy

class demOps():
    
    ''' This class will perform a few operations on
    the DEMs created in the water_level_predictor script'''
    
    def __init__(self, demDir, inputDEM, dataDir, dataFrame, liveStaID):

        self.demDir = demDir
        self.inputDEM = inputDEM
        self.dataDir = dataDir
        self.dataFrame = dataFrame
        self.liveStaID = liveStaID

    def rastBounds(self):

        ''' Get the bounding box for the DEM '''

        rastBoundsList = []

        rastTOPRes = arcpy.GetRasterProperties_management(self.demDir+\
                                                      self.inputDEM,'TOP')
        rastBoundsList.append(float(rastTOPRes.getOutput(0)))

        rastBOTRes = arcpy.GetRasterProperties_management(self.demDir+\
                                                      self.inputDEM,'BOTTOM')
        rastBoundsList.append(float(rastBOTRes.getOutput(0)))

        rastLEFTRes = arcpy.GetRasterProperties_management(self.demDir+\
                                                           self.inputDEM,'LEFT')
        rastBoundsList.append(float(rastLEFTRes.getOutput(0)))

        rastRIGHTRes = arcpy.GetRasterProperties_management(self.demDir+\
                                                        self.inputDEM,'RIGHT')
        rastBoundsList.append(float(rastRIGHTRes.getOutput(0)))
    
        return rastBoundsList # list goes top, bottom, left, right

    def addToMap(self):

        ''' Add the new rasters to the map.'''

        addLayerDEMc = arcpy.mapping.Layer(self.dataDir+'/mapOutputs/DEMc{}.tif'\
                                           .format(self.liveStaID))
        
        DEMcLayer = arcpy.mapping.AddLayer(self.dataFrame,addLayerDEMc)
        
        addLayerWL = arcpy.mapping.Layer(self.dataDir+'/mapOutputs/WL{}.tif'\
                                         .format(self.liveStaID))

        WLLayer = arcpy.mapping.AddLayer(self.dataFrame,addLayerWL)

        return DEMcLayer, WLLayer



        
        
# -*- coding: utf-8 -*-
"""
Created by: Johnathan Woodruff
Unity ID: jlwoodr3

This code can be used to show real time water levels
extracted from NOAA tidal gages during a storm event
such as a hurricane or NorEaster. These water levels
are in the form of raster elevation files laid over
topobathy rasters for a specific area along the coast
surrounding a tide gage.
"""
import csv
import pandas as pd
import requests
from pandas.io.json import json_normalize
import arcpy
from arcpy.sa import *
import os
import sys
from mapOperations import demOps


# set environmental workspace

arcpy.env.workspace = sys.argv[1]
dataDir = sys.argv[1]+'/data'

# Thanks to https://github.com/GClunies/py_noaa
# for the following code: ***
# rank data from NOAA Tides and Currents website

def build_query_url(
        date, stationid, product, datum,
        units, time_zone):
    """
    Build an URL to be used to fetch data from the NOAA CO-OPS API
    (see https://tidesandcurrents.noaa.gov/api/)
    """
    base_url = 'http://tidesandcurrents.noaa.gov/api/datagetter?'

    # Compile parameter string for use in URL
    parameters = {'date' : date,
                    'station': stationid,
                    'product': product,
                    'datum': datum,
                    'units': units,
                    'time_zone': time_zone,
                    'application': 'py_noaa',
                    'format': 'json'}

    # Build URL with requests library
    query_url = requests.Request(
        'GET', base_url, params=parameters).prepare().url

    return query_url

# end of Github snippet

# get desired time range
# for this project just do the 'latest' time
timerange = sys.argv[2]

# read in station id csv with list of stations

station_list = sys.argv[3]
stationids = [] # store list of ids

with open(dataDir+'/stationInfo/'+station_list) as noaastats:
    readnoaa = csv.reader(noaastats, delimiter = ',')
    count = 0
    for row in readnoaa:
        if count > 0: # skips first row
            stationids.append(str(row[0]))
        count = count + 1

# grab DEM

myDEMs = os.listdir(dataDir+'/DEM')

# input other noaa params

product = sys.argv[4]
datum = sys.argv[5]
units = sys.argv[6]
timezone = sys.argv[7]
radius = float(sys.argv[8])

# initialize lists of data

data_url = []
dataList = [] 
wl = []
lon = []
lat = []
time = []
liveStatIDs = [] # keep a list of stations IDs that actually
                 # have data

# loop through station IDs

#import data_yanker


for i in range(len(stationids)):
    data_url.append(build_query_url(timerange\
                                    ,stationids[i],product,\
                                    datum,units,timezone))

    response = requests.get(data_url[i])
    dataList.append(response.json())

for i in range(len(stationids)):

# read water levels in
# if for some reason a station is down, I want to pass over that station
# otherwise I would get a key error because there is no data from the
# website

    try:
        wl.append(float(dataList[i]['data'][0]['v']))
        lat.append(float(dataList[i]['metadata']['lat']))
        lon.append(float(dataList[i]['metadata']['lon']))
        liveStatIDs.append(int(dataList[i]['metadata']['id']))
        time.append(dataList[i]['data'][0]['t'])
        
        
    except KeyError:
        # make sure to delete the station with no data from the
        # station id dataset
        pass      
    

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
        

# create map to add layers to

mxd = arcpy.mapping.MapDocument('CURRENT')
dfs = arcpy.mapping.ListDataFrames(mxd)
df = dfs[0]

for i in range(len(liveStatIDs)):

    # get raster bounds

    for DEM in myDEMs:

        # implement class 

        demProps = demOps(dataDir+'/DEM/',DEM,dataDir,df,liveStatIDs[i])

        # get the bounds of the DEM

        demBounds = demProps.rastBounds()
        
        if lat[i] <= demBounds[0] and lat[i] >= demBounds[1] \
           and lon[i] >= demBounds[2] and lon[i] <= demBounds[3]:
            
            arcpy.AddMessage('Extracting water levels for time: {}'.format(time[i]))
            arcpy.AddMessage('Extracting circular DEM surrounding tidal station {}...'\
                            .format(liveStatIDs[i]))
            

            # extract only a circle with radius in degrees (range set in toolbox script)
            
            circleDEMCut = arcpy.sa.ExtractByCircle(dataDir+'/DEM/'+\
                                                    DEM,arcpy.Point(lon[i],\
                                                    lat[i]),radius, "INSIDE")
            # save the clipped DEM

            circleDEMCut.save(dataDir+'/mapOutputs/DEMc{}.tif'.format(liveStatIDs[i]))

            arcpy.AddMessage('Building water level raster...')

            # build water level raster for clipped DEM
            
            watLevRas = arcpy.sa.Con(circleDEMCut < wl[i], wl[i])
            watLevRas.save(dataDir+'/mapOutputs/WL{}.tif'.format(liveStatIDs[i]))

            # add new rasters to the map
            
            demProps.addToMap()

            # print statements for whether or not the code is
            # finished
            
            if i < len(liveStatIDs)-1:
                arcpy.AddMessage('On to the next station!')
            else:
                arcpy.AddMessage('Finished!')

del mxd









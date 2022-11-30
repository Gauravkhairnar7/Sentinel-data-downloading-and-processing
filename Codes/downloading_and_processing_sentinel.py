# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 21:28:34 2022

@author: Gaurav
"""

from sentinelhub import SHConfig
import datetime
import os
import geojson
from shapely.geometry import shape
import rasterio as rio
import rioxarray as rxr
import json
import numpy as np
import pandas as pd
 

from sentinelhub import (
    CRS,
    BBox,
    DataCollection, 
    MimeType, 
    SentinelHubRequest,
    bbox_to_dimensions,
)



config = SHConfig()

config.sh_client_id='338d899f-eff5-458b-ae1b-3c##########'
config.sh_client_secret='0GFzDK%D}O{](sdMwx_oM,(~Rf7gjc%,######' 



start = datetime.datetime(2022,11, 1)
end = datetime.datetime(2022, 11, 30)


path = r'../'
path = os.path.abspath(path)

if not os.path.isdir(path+'/Images'):
    os.mkdir(path+'/Images')
    
if not os.path.isdir(path+'/NDVI'):
    os.mkdir(path+'/NDVI')

with open(os.path.join(path,'AOI','Karaikal.geojson'), 'r') as p:
                        geo_json = geojson.load(p)
for  coordinates in geo_json['features']:
    AOI = shape(coordinates['geometry'])
    
box = BBox(AOI, crs=CRS.WGS84)  
 
  

resolution = 10
BoundingBox = BBox(bbox=box, crs=CRS.WGS84)
BoundingBox_size = bbox_to_dimensions(BoundingBox, resolution=resolution)
 


evalscript_bands = """
    //VERSION=3
    function setup() {
        return {
            input: [{
                bands: ["B02","B03","B04","B08"],
                units: "DN"
            }],
            output: {
                bands: 4,
                sampleType: "INT16"
            }
        };
    }

    function evaluatePixel(sample) {
        return [
                sample.B02,
                sample.B03,
                sample.B04,
                sample.B08,
               ];
    }
"""
 
def request_true_color(date1,date2) :
    date = (date1,date2)
    return SentinelHubRequest(
    data_folder=r"../Images/",
    evalscript=evalscript_bands,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L1C,
            time_interval=date,
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=BoundingBox,
    size=BoundingBox_size,
    config=config,
)
 
    

day=pd.Timedelta('1 day')
i = start
ii = i+day
while ii < end:
    
    
    bands_response = request_true_color(i,ii)
    bands_response.get_data(save_data=True)
    i = i + day
    ii = i+day
     





for images in os.listdir(path+'/Images/'):
     
    image = rxr.open_rasterio(path+'/Images/'+images+'/'+'response.tiff',masked=True).squeeze()
     
    if np.array(image[0]).max() != 0.0:
        with open(path+'/Images/'+images+'/'+'request.json', 'r') as p:
            jsondata = json.load(p)
            
        date = jsondata['payload']['input']['data'][0]['dataFilter']['timeRange']['from'].split('T')[0]
        
        """ index 3 is NIR and index 2 is RED """
        NDVI = (image[3] - image[2])/(image[3] + image[2]) 
        
        NDVI.rio.to_raster(path+'/NDVI/'+date+'_NDVI.tif')










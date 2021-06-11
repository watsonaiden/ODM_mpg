import numpy as np
import matplotlib.pyplot as pyplot
import rasterio
from rasterio.plot import show
import pandas as pd


'''
SHOWS ORTHOPHOTO WITH GCP
'''

df = pd.read_csv('../Datasets/MPG_Biomass_Pre_GCP.csv')
img = rasterio.open('../outputs/odm_orthophoto.wgs84.tif')
print(img.crs)
x_val, y_val = [], []
'''
NOTE:
    geotiff has x:long and y:lat 
'''
for i,j in df.iterrows():
    lon = j['Longitude']
    lat = j['Latitude']
    x, y = img.index(lon, lat)    
    if x < img.shape[0] and y < img.shape[1]:
        print(j['Name'])
        x_val.append(x)
        y_val.append(y)
print(x_val)
print(y_val)

arr = img.read()
arr = arr[:3]
shape = arr.shape
rgb_arr = np.transpose(arr, (1,2,0))
print(rgb_arr.shape)
pyplot.imshow(rgb_arr)
pyplot.scatter(y_val, x_val)
pyplot.show()


import numpy as np
import matplotlib.pyplot as pyplot
import rasterio as rio
import pandas as pd
from GCP import convert_coordinate_UTM


# shows orthophoto with gcp plotted
def show_orthophoto():
    df = pd.read_csv('../Datasets/MPG_Biomass_Pre_GCP.csv')
    img = rio.open('../Datasets/project/odm_orthophoto/odm_orthophoto.tif')

    x_val, y_val = [], []
    
    print('GCP set', flush=True)    
    for i,j in df.iterrows():
        lon = j['Longitude']
        lat = j['Latitude']
        z = 0
        
        # convert the lat lon coordinates to the UTM system ODM uses
        x1,y1,_= convert_coordinate_UTM((lat,lon, z))
        

        # gives pixel value of specific value in coordinate system
        x, y = img.index(x1, y1)    
        
        # check if pixel value is within range of picture
        if x < img.shape[0] and y < img.shape[1]:
            print(j['Name'], flush=True)
            x_val.append(x)
            y_val.append(y)

    # convert rasterio img to np array
    arr = img.read()
    arr = arr[:3]
    # move color layer to the back
    # before change is 3,l,w needs to be l,w,3
    rgb_arr = np.transpose(arr, (1,2,0))
    pyplot.imshow(rgb_arr)
    # note pyplot inverts axis here so must feed it y,x instead of x,y
    pyplot.scatter(y_val, x_val)
    pyplot.show()


show_orthophoto()


import rasterio as rio
from PIL import Image
import numpy as np

with rio.open('C:/Users/Hypnotic/Desktop/ODM/test_setup/odm_orthophoto/odm_orthophoto.tif') as f:
    data= f.read()
    data = data[:3]
    rgb_arr = np.transpose(data, (1,2,0))

    print(data.shape)
    im = Image.fromarray(rgb_arr)
    im.save('C:/Users/Hypnotic/Desktop/ODM/test_setup/odm_orthophoto/odm_orthophoto.png')


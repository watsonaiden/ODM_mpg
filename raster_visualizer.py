import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np

'''
SHOWS terrian - ground model
'''


def find_volume(CHM, bounds):
    # ordering of bounds tuple is 0 left, 1 bottom, 2 right, 3 top
    width = bounds[2]- bounds[0]
    length = bounds[3] - bounds[1]
    print(CHM.shape) 
    width_pixels, length_pixels = CHM.shape
    pixel_height = 0
    num_good_values = 0
    for row in CHM:
        for item in row:
            # checks for nonexistent values
            if not np.ma.is_masked(item):
                # count number of good tiles to find actual area used
                num_good_values += 1
                #
                pixel_height += item
    pixel_area = (width* length) / (width_pixels * length_pixels)
    print(f'{pixel_height=}, {pixel_area=}')
    print(f'area of base, area ={num_good_values*pixel_area}, num of valid pixels = {num_good_values}')
    '''
    VOLUME = pixel_area * pixel_height
    pixel_area = (metric_length*metric_height) / (num_length_pixel *num_width_pixel)
    '''
    return pixel_height * pixel_area



with rasterio.open('../outputs/dsm.tif') as dataset: 
    # Mask removes all -9999 whice are unusable data
    # mask only necessry for visualizing data before combination
    print(dataset.crs)
    with rasterio.open('../outputs/dtm.tif') as terrian_dataset:
        bounds = dataset.bounds
        # ordering of bounds box is left, bottom, right, top
        # base coordinate system (EPSG:32611) is in metrics
        print(bounds)
        print('width = ', bounds[2]- bounds[0])
        print('height = ', bounds[3] - bounds[1])
        band_nomask = dataset.read(1)
        band = dataset.read(1, masked=True)
        band_t = terrian_dataset.read(1, masked=True)
        CHM = band_nomask - band_t
        print(CHM)

        print('volume = ', find_volume(CHM, bounds))
        '''
        print('max', band.max()) 
        print('min', band.min())

        print('max no mask', band_nomask.max())
        print('min no mask', band_nomask.min())
        ''' 
        plt.imshow(CHM)
        plt.colorbar()
        #plt.show()
        


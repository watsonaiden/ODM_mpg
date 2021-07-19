import numpy as np
import matplotlib.pyplot as pyplot
import rasterio as rio
import pandas as pd
import os
from GCP import convert_coordinate_UTM
from writer import save_image, save_data
import json


class ODMEval:
    def __init__(self, project_location):
        self.project_location = project_location
        self.scrap_project_data()
        #self.show_orthophoto()
        print('volume = ', self.find_volume())
          
    
    def save(self):
        # save the masked versions of dsm and dtm since normal tif version is not easily readable
        print('Saving Tiffs as jpgs for human readability')
        save_image(self.dsm, 'masked_dsm.jpg', self.project_location)
        save_image(self.dtm, 'masked_dtm.jpg', self.project_location)
        print('Saving canopy model')
        save_image(self.canopy_model, 'canopy.jpg', self.project_location)


    # get all data from project:
    def scrap_project_data(self):
        print('Getting data generated by the ODM')
        dsm_path = self.project_location + '/odm_dem/dsm.tif'
        dtm_path = self.project_location + '/odm_dem/dtm.tif'


        with rio.open(dsm_path) as dsm_dataset:
            with rio.open(dtm_path) as dtm_dataset:
                 
                # should be equal size otherwise something went wrong
                assert dsm_dataset.bounds == dtm_dataset.bounds

                self.bounds = dsm_dataset.bounds
                # read the dsm_dataset into np array form
                # use read(1) since shape is (1, x, y) read(1) causes output to be (x,y) removing need for a reshape
                self.dsm = dsm_dataset.read(1, masked=True)  # masked makes unknown data NaN instead of -9999, if not used causes strange looking picture
                self.dtm = dtm_dataset.read(1, masked=True)

                # find the element by element difference of the models to detect object heights
                print('Creating canopy model', flush=True)
                self.canopy_model = self.dsm - self.dtm


    def find_volume(self):
        # check if volume has already been calculated
        try:
            
            json_location = self.project_location + '/python_output/odm_output.txt'
            with open(json_location) as j_file:
                print('found odm_output json file, scraping found data')
                data = json.load(j_file)
            self.volume = data['volume']
            self.area_of_pixel = data['area_of_pixel']
            self.base_area = data['base_area']
            return self.volume

        except FileNotFoundError:
            print('Calculating volume of GeoTiff, may take a some time', flush=True)
            # ordering of bounds tuple is 0 left, 1 bottom, 2 right, 3 top
            width = self.bounds[2]- self.bounds[0]
            length = self.bounds[3] - self.bounds[1]

            print(self.canopy_model.shape) 
            width_pixels, length_pixels = self.canopy_model.shape
            
            sum_pixel_height = 0
            num_good_values = 0
            for row in self.canopy_model:
                for item in row:
                    # checks for nonexistent values
                    if not np.ma.is_masked(item):
                        # count number of good tiles to find actual area used
                        num_good_values += 1
                        #
                        sum_pixel_height += item

            # area of each individual pixel = total area / # of pixels
            area_of_pixel = (width* length) / (width_pixels * length_pixels)

            print('num of good pixels =', num_good_values)
            print(f'{sum_pixel_height=}, {area_of_pixel=}')
            print(f'area of base, area ={num_good_values*area_of_pixel}, num of valid pixels = {num_good_values}', flush=True)
            '''
            VOLUME = area_of_pixel * sum_pixel_height
            area_of_pixel = (metric_length*metric_height) / (num_length_pixel *num_width_pixel)
            '''
            self.area_of_pixel = area_of_pixel
            self.volume = sum_pixel_height * area_of_pixel
            self.base_area = num_good_values*area_of_pixel



            # send data to writer to be saved
            data_dict ={}
            data_dict['area_of_pixel'] = self.area_of_pixel
            data_dict['base_area'] = self.base_area
            data_dict['valid_pixels'] = num_good_values
            data_dict['volume'] = self.volume

            save_data(data_dict, self.project_location)

            return self.volume


    # shows orthophoto with gcp plotted
    def show_orthophoto(self):
        if 'GCP_location' not in self.locations:
            print('no GCP file to compare with')
            return -1
        unique_GCP = [] 
        with open(self.locations['GCP_location'], 'r') as gcp:
            Lines = gcp.readlines()
            # first line is identification string so remove
            utm_string = Lines.pop(0)
            for line in Lines:
                # split line on spaces
                splits = line.split()
                # first two items are the coordinates
                x,y  = splits[0], splits[1]
                if (x,y) not in unique_GCP:
                    # if x,y pair first of its kind then append to list, convert from string to float for indexing later
                    unique_GCP.append((float(x),float(y)))
        # unique GCP is a list of all unique GCP that should be in orthophoto


        orthophoto_path = self.locations['project_location'] + '/odm_orthophoto/odm_orthophoto.tif'
        img = rio.open(orthophoto_path)

        x_val, y_val = [], []
        for gcp in unique_GCP:
            # index converts the coordinate to pixel value in the given picture
            x_pix, y_pix = img.index(gcp[0], gcp[1])
            x_val.append(x_pix)
            y_val.append(y_pix)

        # convert rasterio img to np array
        arr = img.read()
        arr = arr[:3]
        # move color layer to the back
        # before change is 3,l,w needs to be l,w,3
        rgb_arr = np.transpose(arr, (1,2,0))
        pyplot.imshow(rgb_arr)
        # note pyplot inverts axis here so must feed it y,x instead of x,y
        pyplot.plot(y_val, x_val, '.', color='red')
        pyplot.savefig(self.locations['project_location']+'/python_output/orthophoto.jpg')
        pyplot.show()

if __name__ == '__main__':
    loc = 'C:/Users/Hypnotic/Desktop/ODM/test_setup'
    odm = ODMEval(loc)


import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from math import sqrt
import os
from pyproj import Transformer
from scipy import spatial
'''
TODO

'''

class GCP_pic:
    def __init__(self, filename):
        self.filename = filename
        self.GCP = False # set to false until user verifys gcp in pic
        self.set_gps() # set lat and lon coordinates

    def gps_tuple(self):
        return (self.lat, self.lon)
            
    
    def GCP_gps(self, gps, distance):
        self.gcp_dict = {}
        self.gcp_dict['distance'] = distance
        
        self.gcp_dict['gps'] = convert_coordinate_UTM(gps)

    def GCP_link(self, pixel_x, pixel_y):
        # set GCP to true since GCP is in pic
        self.GCP = True
        #convert to int since pyplot gives pixel location with float which ODM does not use
        self.gcp_dict['pixel_x'] = int(pixel_x)
        self.gcp_dict['pixel_y'] = int(pixel_y)

    #get GPS data from files EXIF
    def set_gps(self):
        exif_table = {}
        with Image.open(self.filename) as image:
            info = image.getexif()
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                exif_table[decoded] = value
            gps_info = {}
            for key in exif_table['GPSInfo'].keys():
                decode = GPSTAGS.get(key,key)
                gps_info[decode] = exif_table['GPSInfo'][key]
            lon = -1 * convert_to_dec(gps_info['GPSLongitude'])
            lat = convert_to_dec(gps_info['GPSLatitude'])
            self.lat = lat
            self.lon = lon
        
    def GCP_file_string(self):
       # Should not be getting file string if no GCP in picture
        assert self.GCP == True
        '''
        ODM wants string in this format
        geo_x geo_y geo_z im_x im_y image_name [gcp_name] [extra1] [extra2]
        '''
        geo_x, geo_y, geo_z = self.gcp_dict['gps']
        im_x = self.gcp_dict['pixel_x']
        im_y = self.gcp_dict['pixel_y']
        image_name = self.filename.split('/')[-1] # filename has / acutal filename is last part
        return (f'{geo_x} {geo_y} {geo_z} {im_x} {im_y} {image_name}')



    def __str__(self):
        split_filename = self.filename.split('/')[-1]
        return f'{split_filename}'

    def __repr__(self):
        return f'GCP_Object({self})'

    def __lt__(self,other):
        return (self.gcp_dict['distance'] < other.gcp_dict['distance'])


#get GCP gps values from excel fil
# returns dictionary with key = group value = array of gps tuples
def get_GCP_GPS(filename):

    df = pd.read_csv(filename)
    GCP_dict = {}

    for i, j in df.iterrows():
        lat_long_z_tuple = (j['Latitude'],j['Longitude'], j['Ellipsoidal height'])
        name = j['Name']
        # GCP in groups of 4> with a number distinguishing them i.e 46_**** 
        # some groups have more than 2 indexs and thus must index to only get 2
        group, num = name.split('_')[:2]

        if group not in GCP_dict: 
            GCP_dict[group] = []


        GCP_dict[group].append(lat_long_z_tuple)
    return GCP_dict



def convert_to_dec(coor_tuple):
    return float(coor_tuple[0] + coor_tuple[1]/60 + coor_tuple[2]/3600)

# get distance between 2 lat long coordinates
def distance(tup_1, tup_2):
    length = tup_2[0] - tup_1[0] 
    height = tup_2[1] - tup_1[1]
    distance = sqrt(length**2 + height**2)
    return distance

# find min distance of point to dic of GCP
def find_min(dic, lat_long):
    min_distance = float('inf')
    min_name = ''
    for name, coordinates in dic.items():
        for coor in coordinates:
            if distance(lat_long, coor) < min_distance:
                min_name = name
                min_distance = distance(lat_long, coordinates[0]) 
    return min_name

# return list of Pics ordered by distance to any GCP
def order_pic(GCP_dict, images_directory):
   # pass dictionary from get_GCP_GPS function
    order = []



    points = []
    #convert dict to np array for KDTree
    list_dict = []
    for arr in GCP_dict.values():
        for gcp in arr:
            list_dict.append(gcp) 
            gcp = gcp[:2] 
            points.append(gcp)

    points = np.array(points)
    

    kdTree = spatial.KDTree(points)


    
    # this is the slowest part of the code
    print('sorting images by distance to a GCP', flush=True)
    for filename in os.listdir(images_directory):
        GCP = GCP_pic(images_directory+filename)
        np_gps = np.array(GCP.gps_tuple())
        # get closest point
        dist, ind = kdTree.query(np_gps, 1)
        #print(GCP,points[ind])
        GCP.GCP_gps(list_dict[ind], dist)
        order.append(GCP)
        
    sorted_order = sorted(order) 
    print('Finished sorting', flush=True)
    return sorted_order

# allow users to select pixel of GCP and returns a array of GCP_img classes with GCP in them
def user_GCP_select(sorted_GCP, skip_threshold=4):
    print('*'*40)
    print('INSTRUCTIONS')
    print('If image has a GCP then double click on its location')
    print('If image does not contain GCP please just exit out')
    print('*'*40, flush=True)

    pixel_x, pixel_y = 0,0
    GCP_img_list = []
    count = 0
    for GCP_img in sorted_GCP:

        # number of concurrent skips before exiting
        if count >= skip_threshold:
            print(f'{skip_threshold} skipped in row and thus exited')
            break
        image =plt.imread(GCP_img.filename)
        # get actual filename since filename includes the path
        split_filename = GCP_img.filename.split('/')[-1]

        fig, ax = plt.subplots()
        fig.canvas.set_window_title(split_filename)
        # pyplot has origin in top left while most programs expect bottom left thus need to flip
        # https://stackoverflow.com/questions/56916638/invert-the-y-axis-of-an-image-without-flipping-the-image-upside-down 
        ax.imshow(image)
        
        def onclick(event):
            nonlocal pixel_x
            nonlocal pixel_y

            if event.dblclick:
                # reset count every time ground control point double clicked
                print(GCP_img)
                print('double click recieved')
                nonlocal count
                count = 0
                pixel_x = event.xdata
                pixel_y = event.ydata
                print(f'click at {pixel_x=}, {pixel_y=}')
                #   print('data', event.xdata, event.ydata)
                #    GCP_list[-1].append((int(event.xdata),int(event.ydata)))
                print('_'*40, flush=True) 
                plt.close()
                
        count += 1
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        plt.show()
        # count only 0 if user double clicked and thus must store value 
        if count == 0:
            GCP_img.GCP_link(pixel_x, pixel_y)
            GCP_img_list.append(GCP_img)

    return GCP_img_list

# for converting from lat long to UTM which ODM requires
def convert_coordinate_UTM(gps):
    x,y,z = gps
    transformer = Transformer.from_crs('epsg:4326', 'epsg:32611')
    x1, y1 = transformer.transform(x,y)
    return  x1, y1, z


def create_GCP_file(GCP_list, coor_system='+proj=utm +zone=11 +ellps=WGS84 +datum=WGS84 +units=m +no_defs' , filename='gcp_list.txt'):
    # ODM looks for this filename
    with open(filename, 'w') as f:
        f.write(f'{coor_system}\n')
        for GCP_img in GCP_list:
            f.write(GCP_img.GCP_file_string()+'\n')



if __name__ == '__main__':

    # get all files GPS
    GCP_dict = get_GCP_GPS()

    # order files by closeness to a control point
    sorted_GCP = order_pic(GCP_dict)
    
    # user manually selects GCP location in files
    GCP_img_list = user_GCP_select(sorted_GCP)    
    
    # write GCP to file using ODM required style
    create_GCP_file(GCP_img_list, filename='txt_output/test_gcp.txt')    



import matplotlib.pyplot as plt
import os
import numpy as np
import json


'''
TODO
create_report
---want to include the command that was run to be able to recreate results if neeeed
---write all general info, area + volume 
'''
'''
class Writer:
    def __init__(self, project_path):
        self.writer_path = project_path + '/python_outputs'
        #make the directory for saving results, prevents errors since writeing a file doesnt make dir
        os.mkdir(self.writer_path)
'''       



def save_image(img_arr, name, project_path):
    # directory to write to
    write_dir = project_path + '/python_output'
    os.makedirs(write_dir, exist_ok=True) # create dir, no error if already exists
     
    path = write_dir+ '/' + name  # path to newely created image 
    plt.imsave(path, img_arr, cmap='magma')



def save_data(data_dict, project_path):
    location = project_path + '/python_output/odm_output.txt'

    with open(location, 'w') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=4)

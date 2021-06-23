import GCP
import os



def getGCP(locations):
    '''
    GCP setup
    '''

    # get all files GPS
    GCP_dict = GCP.get_GCP_GPS(locations['all_gcp_location'])

    # order files by closeness to a control point
    sorted_GCP = GCP.order_pic(GCP_dict, locations['images_location'])
    
    # user manually selects GCP location in files
    GCP_img_list = GCP.user_GCP_select(sorted_GCP)    
    
    # write GCP to file using ODM required style
    gcp_location = locations['project_location'] + '/gcp_list.txt'
    GCP.create_GCP_file(GCP_img_list, filename=gcp_location)    



# return dict with location of files in project
def get_location():
    location_dict = {} 


    project_location = input('full path of project folder: ')
    # cleanup of string
    project_location = project_location.strip('"')  # remove possible trailing and leading quotes
    project_location = project_location.replace('\\', '/') # replace windows \ with linux filesystem /
    print(project_location)

    location_dict['project_location'] = project_location

    directory = os.listdir(project_location)

    # check if images file exists
    if 'images' in directory:
        location_dict['images_location'] = project_location +'/images/' # add path of images to location_dict
    else: # could not find images directory
        print('could not find images directory')
        print('make sure the folder with the images is in the base of the project folder and named "images"')
        print('found items', directory)
        exit()
     

    # check if there is already a gcp file
    
    if 'gcp_list.txt' in directory:
        new_GCP = input('gcp_list found, use current file?(Y/N) ')
        if new_GCP == 'Y':
            location_dict['GCP_location'] = project_location + '/gcp_list.txt'
            # if GCP will be used then can return now since all_gcp file not necessary
            return  location_dict 


    # check for all_gcp.csv, if does not exist then do not use gcp 
    # if new GCP needs to be created then check if all_GCP available to create new one
    if 'all_gcp.csv' in directory:
        print('"all_gcp" csv found')
        print('continuing with GCP') 
        location_dict['all_gcp_location'] = project_location+'/all_gcp.csv'
    else:
        print('*'*40)
        print('WARNING')
        print('could not find "all_gcp.csv" file')
        print('to continue with GCP, make sure all_gcp.csv file is named correctly and in base of project folder')
        cont = input('continue without GCP?(Y/N) ')
        if cont == 'N':
            exit()
        print('*'*40)


    return location_dict 

# runs the odm
def run_odm(locations):
    command = f'docker run -ti --rm -v {locations["project_location"]}:/datasets/code opendronemap/odm --project-path /datasets --dsm --dtm --force-gps'
    os.system(command)

def startup():
    locations = get_location()

    # all_gcp_location only in dict when new gcp is to be created
    new_GCP = 'all_gcp_location' in locations
    if new_GCP is True: 
        print('creating new GCP file', flush=True)
        getGCP(locations)

    print('end of startup, running odm with outputs')
    run_odm(locations) 



if __name__ == '__main__':
    startup()

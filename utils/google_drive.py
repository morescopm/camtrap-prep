# Get list of Files in a Google Drive folder
# From https://www.geeksforgeeks.org/get-list-of-files-and-folders-in-google-drive-storage-using-python/

import os.path 
import pickle
import utils.csv_tools as uc
from dotenv import dotenv_values
from googleapiclient.discovery import build 
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request 
from pandas import DataFrame
    
# Define the SCOPES. 
# If modifying it, delete the token.pickle file. 
SCOPES = ['https://www.googleapis.com/auth/drive'] 
config = dotenv_values()
  
# Create a function getFileList with  
# parameter N which is the length of  
# the list of files. 
def getFileList(
        N:int=10, 
        query:str=f"name contains '{config['GOOGLE_IMAGE_DIR']}'"):
  
    # Variable creds will store the user access token. 
    # If no valid token found, we will create one. 
    creds = None
  
    # The file token.pickle stores the user's access and refresh tokens. It is 
    # created automatically when the authorization flow completes for the first time. 
  
    # Check if file token.pickle exists 
    if os.path.exists('token.pickle'): 
  
        # Read the token from the file and  
        # store it in the variable creds 
        with open('token.pickle', 'rb') as token: 
            creds = pickle.load(token) 
  
    # If no valid credentials are available,  
    # request the user to log in. 
    if not creds or not creds.valid: 
  
        # If token is expired, it will be refreshed, 
        # else, we will request a new one. 
        if creds and creds.expired and creds.refresh_token: 
            creds.refresh(Request()) 
        else: 
            flow = InstalledAppFlow.from_client_secrets_file( 
                'temp/credentials.json', 
                SCOPES
                ) 
            creds = flow.run_local_server(port=0) 
  
        # Save the access token in token.pickle  
        # file for future usage 
        with open('token.pickle', 'wb') as token: 
            pickle.dump(creds, token) 
  
    # Connect to the API service 
    service = build('drive', 'v3', credentials=creds) 

    resource = service.files()

    result = resource.list(
        corpora = 'allDrives',  # 'drive'
        pageSize = N,
        q = query,  # sharedWithMe = true and
        includeItemsFromAllDrives = True,
        supportsAllDrives = True,
        fields = "nextPageToken, files(driveId, id, name, thumbnailLink, webContentLink, parents, createdTime, md5Checksum)",
        orderBy = "recency",
        ).execute() 

    # return the result dictionary containing  
    # the information about the files 
    return result 


def get_images_in_folder(N:int=10, parent_id:str=None) -> list:
    '''return list of image file names & corresponding thumbnail URLs given a google folder'''

    # test first
    file_list = []
    file_list = getFileList(N, query=f"'{parent_id}' in parents")

    print(file_list)

    return file_list


def get_starred_files(N:int=10, star_query:str='starred = true', out_name_id:str=None) -> list:
    '''return list of image file names & corresponding thumbnail URLs given a google folder'''

    # test first
    file_list = {}
    file_list = getFileList(N, query=star_query)

    if 'files' in file_list.keys():
        if len(file_list['files']) > 0:

            print(f"retrieved {len(file_list['files'])} files")

            uc.write_list_of_dict_to_csv(
                input_records = file_list['files'], 
                field_names = file_list['files'][0].keys(), 
                output_csv_file_name = f'gdrive_list_{out_name_id}.csv'
                )

    return file_list


def get_google_file_list(N_folders:int=5, N_files:int=200):
    # Get list of the first N files (default 200) or  
    # folders (default 5) from Google Drive Storage 
    input_folder_id = config['GOOGLE_IMAGE_DIR'] # '100DSCIM_20240306'

    result_dict = getFileList(
        N = N_folders,
        query=f"name contains '{input_folder_id}'"
        )

    print(result_dict)
    
    # Extract the list from the dictionary 
    folder_data = result_dict.get('files')
    print(f'folder_data = {folder_data}')

    folder_df = DataFrame(folder_data)
    first_folder_id = folder_df.loc[folder_df['createdTime'] == folder_df['createdTime'].min(), 'id'].item()
    # first_folder_id = folder_data[0]['id'] 
    print(f"first folder id == {first_folder_id}")

    if len(result_dict) > 0:
        file_list = get_images_in_folder(
            N = N_files, # 10 or 200,
            parent_id = first_folder_id
            )
  
    # Print every file's name 
    for file in file_list: 
        print(file) 
    
    uc.write_list_of_dict_to_csv(
        input_records = file_list['files'], 
        field_names = file_list['files'][0].keys(), 
        output_csv_file_name = f'gdrive_list_{input_folder_id}.csv'
        )
    
    return(file_list['files'])

if __name__ == '__main__':
    get_google_file_list()
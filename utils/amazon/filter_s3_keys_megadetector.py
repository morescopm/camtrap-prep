import sys
import requests
import ast
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO

# Usage: python filter_s3_keys.py <deploymentID> <optional: media>
# IF specifying string 'media' as argv[1] then a media.csv file will be created (slow)

def main():
    # Idenfiy bucket and base url
    bucket_name = 'urbanriverrangers'
    base_url = f'https://{bucket_name}.s3.amazonaws.com'
    filterID = 'megadetector'

    # Read in the master list of all s3_keys
    df_a = pd.read_csv("s3_keys.csv")
    df_a = df_a.sort_values(by='Key')

    # Filter the df to only the deploymentID and no sendlist
    # Also only contains images
    filtered_df, json_df = filter_s3_keys(df_a, filterID)

    # Parse the json_df into a csv
    mega_json = read_mega_json(json_df, base_url)

    if len(sys.argv) > 1 and sys.argv[1] == "verbose":
        # Save the json_csv
        mega_json.to_csv(f'./processed/{filterID}_json_verbose.csv', index=False)
        print(f"Image Observations saved to {filterID}_json_verbose.csv")
    else:
        # Save the json_csv
        mega_json.to_csv(f'./processed/{filterID}_json_details.csv', index=False)
        print(f"Image Observations saved to {filterID}_json_details.csv")


    # Generate observation base information for upload to google sheets
    images_df = create_obs_csv(filtered_df, base_url)

    # Save the Images DataFrame to a CSV file
    images_df.to_csv(f'./processed/{filterID}_images.csv', index=False)
    print(f"Image Observations saved to {filterID}_images.csv")

    
    if len(sys.argv) == 2:
        if sys.argv[1] == 'media':
            # Generate the media.csv df
            media_df = create_media_csv(filtered_df, base_url)

            # Save the media DataFrame to a CSV file
            media_df.to_csv(f'{filterID}_media.csv', index=False)
            print(f"Media Records saved to {filterID}_media.csv")


    return print('Job Complete')


def filter_s3_keys(df: pd.DataFrame, filterID: str):
    """ 
    Focuses on a specific deployment_id and return the filtered df.
    Ignores all images with sendlist in key path. 
    """
    # List of valid image and video extensions
    valid_extensions = ('.jpg', '.jpeg', '.json')

    filter1_df = df[df['Key'].str.contains(filterID) &\
                     ~df['Key'].str.contains("sendlist") &\
                          ~df['Key'].str.contains("THUMB")]
    filter2_df = filter1_df[filter1_df['Key'].str.lower().str.endswith(valid_extensions)]

    json_filter = filter2_df[filter2_df['Key'].str.lower().str.endswith('.json')]

    return filter2_df, json_filter

def read_mega_json(json_df, base_url):

    print('Parsing json content')

    # Define the megadetector category mapping
    category_mapping = {
        '1': 'Animal',
        '2': 'Person',
        '3': 'Vehicle'
    }

    # URL of the JSON file in the public S3 bucket
    for index, row in json_df.iterrows():
        key = row['Key']
        json_file_url = f'{base_url}/{key}'

        # Make an HTTP GET request to fetch the JSON file
        response = requests.get(json_file_url)

        # Check if the request was successful
        if response.status_code == 200:
            json_content = response.json()  # Parse the JSON content

            # Only grab the images content
            images_content = json_content['images']

        # Prepare a list to hold the parsed data
        data = []
        
        if len(sys.argv) > 1 and sys.argv[1] == "verbose":
        # Iterate over each entry in images_content
            for item in images_content:
                file_name = item['file']
                if 'detections' in item:
                    detections = item['detections']

                    # Convert the detections string to a list of dictionaries
                    if len(detections) > 0:
                        # Split out detection list of dicts            
                        for detection in detections:
                            category_num = detection['category']
                            category = category_mapping.get(category_num, 'Unknown')
                            conf = detection['conf']
                            bboxX = detection['bbox'][0]
                            bboxY = detection['bbox'][1]
                            bboxWidth = detection['bbox'][2]
                            bboxHeight = detection['bbox'][3]
                            
                            # Append the parsed data to the list
                            data.append([file_name, category, conf, bboxX, bboxY, bboxWidth, bboxHeight])
                    else:
                        data.append([file_name, 'No detections', None, None, None, None, None])
            
            # Create a DataFrame from the parsed data
            df = pd.DataFrame(data, columns=['file', 'category', 'conf', 'bboxX','bboxY','bboxWidth','bboxHeight'])            
        
        else:
            for item in images_content:
                file_name = item['file']
                if 'detections' in item:
                    detections = item['detections']
                    if len(detections) == 0:
                        detections = "blank"
                else:
                    detections = "blank"
                data.append([file_name, detections])

            # Create a DataFrame from the parsed data
            df = pd.DataFrame(data, columns=['file', 'detections'])

    return df



def create_media_csv(df: pd.DataFrame, base_url: str):
    """ Generates media.csv file for the deploymentID """
    # mediaID: s3 ETag, or other random unique ID, or s3 'Key'
    # deploymentID	
    # captureMethod	
    # timestamp	
    # filePath: URL to s3 Bucket
    # filePublic: TRUE
    # fileName: last of split '/'	
    # fileMediatype: mimeType eg image/jpeg | image/jpg | video/mp4 | video/mov
    # exifData: JSON pulled by pillow function
    # favorite	
    # mediaComments

    # Notify Script is Running
    print("Building media.csv table with Exif Information")

    # List of valid image and video extensions
    image_extensions = ['jpg', 'jpeg' ,'json']

    media = []
    for index, row in df.iterrows():
        key = row['Key']
        fileType = key.lower().split('.')[-1]

        if fileType in image_extensions:
            mimeType = f'image/{fileType}'
            exif_data = generate_Exif_JSON(key, base_url)

        fileName = key.split('/')[-1]
        deploymentID = key.split('/')[2:-2]

        # add a row to media with all of the media information
        media.append({
            'mediaID': row['ETag'],
            'deploymentID': deploymentID,
            'captureMethod': "activityDetection",
            'timestamp': "",
            'filePath': f'{base_url}/{key}',
            'filePublic': True,
            'fileName': fileName,
            'fileMediatype': mimeType,
            'exifData': exif_data,
            'favorite': "",
            'mediaComments': ""

            })
        
    media_df = pd.DataFrame(media)

    return media_df

def extract_Exif(image):
    """ returns JSON of Exif Data """
    exif_data = {}
    if hasattr(image, '_getexif'):  # Check if image has EXIF data
        exif_info = image._getexif()
        if exif_info is not None:
            for tag, value in exif_info.items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value

    return exif_data

def generate_Exif_JSON(key, base_url):
    exif_JSON = []
    # Download the image from the public S3 URL into memory
    response = requests.get(f'{base_url}/{key}')
    response.raise_for_status()  # Ensure the request was successful
    file_content = response.content
    
    try:
        # Open the image using Pillow
        image = Image.open(BytesIO(file_content))
        
        # Check if the image format is supported
        if image.format is None:
            raise ValueError("Unsupported image format")
        
        # Extract metadata
        exif_JSON = extract_Exif(image)

    except (IOError, ValueError) as e:
        print(f"Error processing image '{key}': {e}")

    return exif_JSON



def create_obs_csv(df: pd.DataFrame, base_url: str):
    """ Generates first 4 columns of observations for google sheets """
    # observationID: None until observations made
    # deploymentID: matches the folder name saved by SDUploader
    # mediaID: needs to match media.mediaID - maybe s3 ETag

    # Notify User of Starting Script
    print("Building megadetector image observation lookups ")

    # List of valid image and video extensions
    image_extensions = ['jpg', 'jpeg', 'json']

    filtered_images = []

    for index, row in df.iterrows():
        key = row['Key']
        fileType = key.lower().split('.')[-1]
        deploymentID = '/'.join(key.split('/')[2:-1])
        if fileType in image_extensions:
            filtered_images.append({
                'observationID': '', # Assigning an observation ID should happen after observing
                'deploymentID': deploymentID,
                'mediaID': row['ETag'],
                'filePath': f'{base_url}/{key}'

                })
            
    images_df = pd.DataFrame(filtered_images)

    return images_df


if __name__ == "__main__":
    main()
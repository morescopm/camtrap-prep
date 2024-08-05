import pandas as pd
# Get the list of recently uploaded folders / buckets to amazone s3
# In sdUploader, add 'wait for finish upload' then call these functions


def get_xml_df(target_buckets: list):
    # Submit request for xml data with pagination for each recently uploaded folder
    for bucket in target_buckets:
        get_xml(bucket)

    return xml_df

def xml_to_obs(target_bucket: str):
    # For each list of xml image urls (keys), ETags, and filepaths
    return obs_df


def upload_csv_to_drive(bucket_name: str, raw_df: pd.DataFrame)
    
    return print('')
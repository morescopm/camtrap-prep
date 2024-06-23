import pandas as pd

# Specify Deployment Year of interest
deploy_year = '2024'

# Read in the master list of all s3_keys
df_a = pd.read_csv("s3_keys.csv")

unique_deploy = set()

for index, row in df_a.iterrows():
    key = row["Key"]
    key_parts = key.split('/')

    if len(key_parts) > 3 and key_parts[1] == deploy_year:
        unique_deploy.add(key_parts[2])

list_deploys = [deploymentID for deploymentID in unique_deploy]
list_deploys.sort()

for deploymentID in list_deploys:
    print(deploymentID)

# 2024-05-25_WM_Boardwalk_F
# 2024-05-25_WM_Boardwalk_G
# 2024-06-03_UR011
# 2024-06-08_WM_Boardwalk_D
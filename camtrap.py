from dotenv import dotenv_values
import camtrapPackager
import camtrapRepackager
import sys

# Repackager and Packager Globals
# TODO: Pass camtrap_config_urls as argument to packager or repackager
config = dotenv_values()
base_url = f"{config['CAMTRAP_BASE_URL']}/{config['CAMTRAP_VERSION']}"

camtrap_config_urls = {
    'profile_url': f"{base_url}{config['CAMTRAP_PROFILE']}",
    'deployments': f"{base_url}{config['CAMTRAP_DEPLOYMENTS_SCHEMA']}",
    'media': f"{base_url}{config['CAMTRAP_MEDIA_SCHEMA']}",
    'observations': f"{base_url}{config['CAMTRAP_OBSERVATIONS_SCHEMA']}",
    'output': config['CAMTRAP_OUTPUT_DIR']
}


def main():
    if len(sys.argv) < 2:
        return print("Usage: python camtrap.py [packager | repackager]")

    if sys.argv[1] not in ['packager', 'repackager']:
        return print(f'You entered: "{sys.argv[1]}", must use packager or repackager')

    if sys.argv[1] == 'packager':
        camtrapPackager.prep_camtrap_dp()
    else:
        camtrapRepackager.prep_camtrap_dp()

    return


if __name__ == '__main__': 
    main()
Environment Notes  
1. You will need to fork https://github.com/nkwsy/sdUploader  
2. Activate a virtenv or new conda env and install requirements  
    - note if using conda you will need to initialize the new env after activation with 'conda install pip'
    - pip install -r requirements.txt

    - from start this would be:
        - conda create --name camtrap
        - conda install pip (installs latest python with tools - version 3.11 as of 2024-06-11)
        - pip install -r requirements.txt

3. Ensure sdUploader > Setup.py contains a means to load the requirements file.
    - branch wildlife_cam contains the load and .egg information
    - pip install -e /path/to/sdUploader
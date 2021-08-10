# Profiles-Import-Tool

## Upload Tool
This tool is an example how to import profiles to Oncoshot via its API

This tool is written in node.js. The API documentation is available on https://api.oncoshot.com/swagger/index.html

### Getting Started

To run the tool, take the following steps
1. Create an empty folder `logs` in root
2. Run npm install to install packages
3. In the config folder, create an `config.env` file with the following fields. These fields should be filled with the auth info provided by OS based on your organisation.
    * AUTH0_CLIENT_ID= // Client ID provided
    * AUTH0_DOMAIN= // Domain to be authenticated, should be api.oncoshot.com
    * AUTH0_CLIENT_SECRET= // Secret Key provided to you
    * ONCOSHOT_ORGANISATION= // Your organisation name on Oncoshot
    * API_HOSTNAME= // Host nname of the API, typically api.oncoshot.com
WARNING: Do not share the auth.env file or secret key in a public forum or commit it to a public git repo
4. Run the commannd, `npm run upload <Location of File>` to start the tool (eg. `npm run upload data/samples.json`)
5. Logs will be printed to the console and saved in a .txt file in the logs folder

### Function Details
1. `src/auth.js`
    This functions request for a Bearer token from Auth0 with the given authentication details via OAuth2.0
    The Bearer token is passed on to other functions that require authentication
2. `src/upload.js`
    This is the function that makes the request to HTTPS.
    The function accepts a JSON data file and makes PUT request to the OS API with the Bearer token.
    The endpoint being used is `api.oncodevel.com/api/v1/organizations/{organizationId}/profiles`

## sg-cancer-registry-dataset
This tools is an example of generating profiles from a dataset to generate a JSON file that can be uploaded.
The tool is written in Python3 and ultilises the Singapore Cancer Report 2018 as its source data.
SCR 2018 is summarised in the Distributions.xlsx and converted to a CSV file to be read by the program.

### Getting Started
1. Run the command `python sg-cancer-registry-dataset/main.py`
2. The `model.csv`, `samples.csv` file and `samples.json` file will be generated
    * `model.csv` contains the statistical model that will be used to generate the data
    * `samples.csv` contains the profiles generated from the model
    * `samples.json` contains the profiles formatted to be uploaded to the Oncoshot API
3. Upload the `samples.json` file

### Function Details
1. `sg-cancer-registry-dataset/main.py`
The python script uses pandas dataframes to format, rename and calculate data.
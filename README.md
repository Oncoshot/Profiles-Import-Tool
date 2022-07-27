# Profiles-Import-Tool

## Upload Tool
This tool is an example how to import profiles to Oncoshot via its API

This tool is implemented in both node.js and python. Implementation details for both languages are given below. The API documentation is available on https://apisite.oncoshot.com/swagger/index.html

### Getting Started

To run the tool, take the following steps
1. Create an empty folder `logs` in root
2. Run npm install to install packages **(JavaScript implementatino only)**
3. Install the dotenv package using `pip install python-dotenv` **(Python implementation only)**
4. In the root folder, create an `config.env` file with the following fields. These fields should be filled with the auth info provided by OS based on your organisation.
    * AUTH0_CLIENT_ID= // Client ID provided
    * AUTH0_DOMAIN= // Domain to be authenticated, should be api.oncoshot.com
    * AUTH0_CLIENT_SECRET= // Secret Key provided to you
    * AUTH0_URL = // Location to authenticate, typically https://auth.oncoshot.com/oauth/token
    * ONCOSHOT_ORGANISATION= // Your organisation name on Oncoshot
    * API_HOSTNAME= // Host name of the API, typically api.oncoshot.com
    * SALT= // A secret string associated with your organization, used in the de-identification of patient IDs. This salt is case-sensitive.
WARNING: Do not share the auth.env file or secret key in a public forum or commit it to a public git repo
    
To run the tool in JavaScript,
1. Run the commannd, `npm run upload <Location of File>` to start the tool (eg. `npm run upload data/samples.json`)
2. Logs will be printed to the console and saved in a .txt file in the logs folder

To run the tool in Python,
1. `cd` into the `src` folder using the command, `cd src`
2. Run the command, `python upload.py <Location of File>` to start the tool (eg. `python upload.py ../data/samples.json`)

### Function Details

1. `src/auth.js`/`src/auth.py`
    This functions request for a Bearer token from Auth0 with the given authentication details via OAuth2.0
    The Bearer token is passed on to other functions that require authentication
2. `src/upload.js`/`src/upload.py`
    This is the function that makes the request to HTTPS.
    The function accepts a JSON data file and makes PUT request to the OS API with the Bearer token.
    The endpoint being used is `api.oncodevel.com/api/v1/organizations/{organizationId}/profiles`

## De-identification of Patient IDs
This hashing tool implemented in Python helps you de-identify patient IDs. Hashing refers to transforming a given key to another value
and hence is useful for de-identifying patient IDs. This tool uses the SHA256 hashing implementation, for which more details
can be found [here](https://en.wikipedia.org/wiki/SHA-2).

To run the tool from the command line, run the command, 

`python src/deidentify.py <patientID>`(eg. `python src/deidentify.py abc123`)

You can corroborate the results by using online tools such as [this SHA256 Online Hashing Tool](https://emn178.github.io/online-tools/sha256.html),
and also a sample Excel workbook (De-identify patient ID.xlsm) provided in the `src` folder. Details on the usage of this
workbook are mentioned within. To use the online tool, concatenate your salt to your patient id, and enter it into the
tool. For example, if your salt is "abc", and your patient ID is 1234, you should enter 1234abc. The online tool will return the hashed result,
which in this case, is dd130a849d7b29e5541b05d2f7f86a4acd4f1ec598c1c9438783f56bc4f0ff80. The first 12 characters of this result form your de-identified id,
making it dd130a849d7b.

## sg-cancer-registry-dataset
This tools is an example of generating profiles from a dataset to generate a JSON file that can be uploaded.
The tool is written in Python3 and ultilises the Singapore Cancer Report 2018 as its source data.
SCR 2018 is summarised in the source-data.xlsx and converted to a CSV file to be read by the program.

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

## mskcc-dataset
The tool is written in Python3 and ultilises the MSKCC Impact Report 2017 as its source data.
The files used is in mskcc-dataset/source-data and will be used by the program to produce patients JSON.
http://www.cbioportal.org/study/summary?id=msk_impact_2017
### Getting Started
1. Run the command `python mskcc-dataset/main.py`
2. The `patients.csv` file and `patients.json` file will be generated
    * `patients.csv` contains the profiles generated from the source information
    * `patients.json` contains the profiles formatted to be uploaded to the Oncoshot API
3. Upload the `patients.json` file

### Function Details
1. `mskcc-dataset/main.py`
The python script uses pandas dataframes to format, rename and calculate data.

# Profile-Delete-Tool
## Delete Tool
This tool is an example how to delete profiles from Oncoshot via its DELETE API
This tool is written in node.js. The API documentation is available on https://apisite.oncoshot.com/swagger/index.html

### Getting Started
To run the tool, take the following steps
1. Prepare a Json file to include ONLY profiles need to be deleted.
2. Run the commannd, `npm run delete <Location of Json file>` to start the tool (eg. `npm run delete data/profiles_to_be_deleted_samples.json`)
3. Logs will be printed to the console and saved in a .txt file in the logs folder


# Profiles-Import-Tool
This tool is an example how to import profiles to Oncoshot via its API

This tool is written in node.js. The API documentation is available on https://api.oncodevel.com/swagger/index.html

### Getting Started

To run the tool, take the following steps
1. Create an empty logs in root
2. Run npm install to install packages
3. In the config folder, create an ```auth.env``` file with the following fields. These fields should be filled with the auth info provided by OS based on your organisation.
    AUTH0_CLIENT_ID= // Client ID provided
    AUTH0_DOMAIN= // Domain to be authenticated, should be api.oncoshot.com
    AUTH0_CLIENT_SECRET= // Secret Key provided to you
    ONCOSHOT_ORGANISATION= // Your organisation name on Oncoshot
WARNING: Do not share the auth.env file or secret key in a public forum or commit it to a public git repo
4. Run the commannd, ```npm run upload``` to start the tool

### Function Details
1. src/auth.js
    This functions request for a Bearer token from Auth0 with the given authentication details via OAuth2.0
    The Bearer token is passed on to other functions that require authentication
2. src/upload.js
    This is the function that makes the request to HTTPS.
    The function accepts a JSON data file and makes PUT request to the OS API with the Bearer token.
    The endpoint being used is api.oncodevel.com/api/v1/organizations/{organizationId}/profiles
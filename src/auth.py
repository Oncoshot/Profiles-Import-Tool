import http.client
import json
import os
from dotenv import load_dotenv

# load environment variables from config.env example file
load_dotenv("config.env")

AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_URL = os.getenv('AUTH0_URL')
AUTH0_URL = AUTH0_URL.replace("https://", "").replace("/oauth/token", "")

# authenticate connection
def authenticate():
    conn = http.client.HTTPSConnection(AUTH0_URL)

    payload = "{\"client_id\":\"%s\",\"client_secret\":\"%s\",\"audience\":\"%s\",\"grant_type\":\"client_credentials\"}" \
              % (AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN)
    headers = {'content-type': "application/json"}

    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    respBody = res.read()
    respJson = json.loads(respBody)

    return respJson['access_token']

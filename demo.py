import http.client
import json

conn = http.client.HTTPSConnection("auth.oncodevel.com")

payload = "{\"client_id\":\"rcU\",\"client_secret\":\"S9\",\"audience\":\"https://api.oncoshot.com\",\"grant_type\":\"client_credentials\"}"

headers = { 'content-type': "application/json" }

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
respBody = res.read()

respJson = json.loads(respBody)

print(respJson['access_token'])

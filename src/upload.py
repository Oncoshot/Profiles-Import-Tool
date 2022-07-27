import json
import os
import sys
import errno
import auth
import http
import http.client
from dotenv import load_dotenv

load_dotenv("../config.env")

onlyProfilesIds = []
API_HOSTNAME = os.getenv('API_HOSTNAME')
ONCOSHOT_ORGANISATION = os.getenv('ONCOSHOT_ORGANISATION')

def retrieveFile():
    try:
        if len(sys.argv) < 2:
            raise Exception("No file")
        inputFileName = sys.argv[1]
        openInputFileName = open(inputFileName)
        results = json.load(openInputFileName)
        uploadFile(results)
        print(results)
        print("Profiles to upload : %d" % len(results))
    except (IOError, OSError) as e:
        if e.errno == errno.ENOENT:
            print("%s is not a valid json file location" % inputFileName)
        else:
            print(e)


def uploadFile(results):
    try:
        token = auth.authenticate()
    except:
        print("Authentication Failed")
        raise Exception("Authentication Failed")

    print("Authentication Successful")

    successCount = 0
    failureCount = 0

    if len(onlyProfilesIds):
        results = filter(lambda item: item['id'] in onlyProfilesIds, results)

    conn = http.client.HTTPSConnection(API_HOSTNAME)

    headers = {
        'Content-Type': 'application/json-patch+json',
        'authorization': 'Bearer ' + token
    }

    for i in range(len(results)):
        id = results[i]['id']
        del results[i]['id']
        data = json.dumps(results[i])
        url = '/api/v1/organizations/%s/profiles/%s/import' % (ONCOSHOT_ORGANISATION, id)
        conn.request('PUT', url, headers=headers, body=str(data))

        res = conn.getresponse()

        print(res.status)

        if res.status in [201, 204]:
            successCount += 1
        else:
            failureCount += 1

        data = res.read()

        # print(data.decode('utf-8'))

    print("Successfully imported %d profiles" % successCount)


print("This tool uploads the formatted JSON file to the Oncoshot API.\n")
print("Guide to statusCodes:")
print("201: Success, created new profile")
print("204: Success, updated existing profile")
print("401: Failure, authentication failed")
print("403: Failure, no access to organisation")
print("422: Failure, data is wrongly formatted\n")

retrieveFile()

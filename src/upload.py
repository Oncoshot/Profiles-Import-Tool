import json
import os
import sys
import errno
import uuid

import auth
import http
import http.client
from dotenv import load_dotenv
from datetime import date

# load environment variables from config.env example file
load_dotenv("../config.env")

onlyProfilesIds = []
API_HOSTNAME = os.getenv('API_HOSTNAME')
ONCOSHOT_ORGANISATION = os.getenv('ONCOSHOT_ORGANISATION')

# open data file and retrieve json data
def retrieveFile():
    try:
        if len(sys.argv) < 2:
            raise Exception("No file")
        inputFileName = sys.argv[1]
        openInputFileName = open(inputFileName)
        results = json.load(openInputFileName)
        print("Profiles to upload : %d" % len(results))
        uploadFile(results)
        openInputFileName.close()
    except (IOError, OSError) as e:
        if e.errno == errno.ENOENT:
            print("%s is not a valid json file location" % inputFileName)
        else:
            print(e)

# upload data to the Oncoshot system
def uploadFile(results):
    # check authentication
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

    log_file = "../logs/" + date.today().strftime("%d-%m-%Y") + "-" + uuid.uuid4().__str__() + "-upload-log.txt"

    with open(log_file, 'w') as f:
        f.write("")

    # upload data to Oncoshot
    for i in range(len(results)):
        id = results[i]['id']
        del results[i]['id']
        data = json.dumps(results[i])
        url = '/api/v1/organizations/%s/profiles/%s/import' % (ONCOSHOT_ORGANISATION, id)
        conn.request('PUT', url, headers=headers, body=str(data))

        res = conn.getresponse()

        with open(log_file, 'a') as f:
            f.write("%d Profile %s: statusCode: %d\n" % (i, id, res.status))

        print("%d Profile %s: statusCode: %d" % (i, id, res.status))

        if res.status in [201, 204]:
            successCount += 1
        else:
            failureCount += 1

        data = res.read()

        # print(data.decode('utf-8'))
    if failureCount > 0:
        with open(log_file, 'a') as f:
            f.write("Error")
        print("Error")
    else:
        with open(log_file, 'a') as f:
            f.write("Upload complete\n")
            f.write("Successful: %d\n" % successCount)
            f.write("Failed: %d\n" % failureCount)
        print("Upload complete")
        print("Successful: %d" % successCount)
        print("Failed: %d" % failureCount)


print("This tool uploads the formatted JSON file to the Oncoshot API.\n")
print("Guide to statusCodes:")
print("201: Success, created new profile")
print("204: Success, updated existing profile")
print("401: Failure, authentication failed")
print("403: Failure, no access to organisation")
print("422: Failure, data is wrongly formatted\n")

retrieveFile()

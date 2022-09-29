import json
import os
import sys
import errno

import auth
import http
import http.client
from dotenv import load_dotenv
import time
from pathlib import Path

# load environment variables from config.env example file
load_dotenv("config.env")

onlyProfilesIds = []
API_HOSTNAME = os.getenv('API_HOSTNAME')
ONCOSHOT_ORGANISATION = os.getenv('ONCOSHOT_ORGANISATION')

def authenticate():
    # check authentication
    try:
        token = auth.authenticate()
    except:
        print("Authentication Failed")
        raise Exception("Authentication Failed")

    print("Authentication Successful")
    print("")

    return token

# open data file and retrieve json data and upload to Oncoshot API
def processFile(inputFileName, log_file_path, token):
    try:
        openInputFileName = open(inputFileName)
        results = json.load(openInputFileName)
        print("Profiles to upload : %d" % len(results))
        uploadFile(results, log_file_path, token)
        openInputFileName.close()
    except (IOError, OSError) as e:
        if e.errno == errno.ENOENT:
            print("%s is not a valid json file location" % inputFileName)
        else:
            print(e)

# upload data to the Oncoshot system
def uploadFile(results, log_file_path, token):

    successCount = 0
    failureCount = 0

    if len(onlyProfilesIds):
        results = filter(lambda item: item['id'] in onlyProfilesIds, results)

    conn = http.client.HTTPSConnection(API_HOSTNAME)

    headers = {
        'Content-Type': 'application/json-patch+json',
        'authorization': 'Bearer ' + token
    }

    with open(log_file_path, 'a+') as f:
        f.write("")

    # upload data to Oncoshot
    for i in range(len(results)):
        id = results[i]['id']
        del results[i]['id']
        data = json.dumps(results[i])
        url = '/api/v1/organizations/%s/profiles/%s/import' % (ONCOSHOT_ORGANISATION, id)
        conn.request('PUT', url, headers=headers, body=str(data))

        res = conn.getresponse()

        with open(log_file_path, 'a') as f:
            f.write("%d Profile %s: statusCode: %d\n" % (i, id, res.status))

        print("%d Profile %s: statusCode: %d" % (i, id, res.status))

        if res.status in [201, 204]:
            successCount += 1
        else:
            failureCount += 1

        data = res.read()

        # print(data.decode('utf-8'))
    if failureCount > 0:
        with open(log_file_path, 'a') as f:
            f.write("Error")
        print("Error")
    else:
        with open(log_file_path, 'a') as f:
            f.write("Upload complete\n")
            f.write("Successful: %d\n" % successCount)
            f.write("Failed: %d\n" % failureCount)
        print("Upload complete")
        print("Successful: %d" % successCount)
        print("Failed: %d" % failureCount)

#returns a list of all json files in a given folder 
def _read_dir(dir_path):
    json_files = []
    for path in os.listdir(dir_path):
        if path.endswith('.json'):
            json_files.append(path)
    return json_files

print("This tool uploads the formatted JSON file to the Oncoshot API.\n")
print("Guide to statusCodes:")
print("201: Success, created new profile")
print("204: Success, updated existing profile")
print("401: Failure, authentication failed")
print("403: Failure, no access to organisation")
print("422: Failure, data is wrongly formatted\n")


if len(sys.argv) < 2:
    raise Exception("Please specify a path to single JSON file or a folder with JSON files as a parameter")
inputPath = sys.argv[1]

print('Authenticating...')
token = authenticate()

if os.path.isdir(inputPath):
    print('Reading json files from the directory ' + inputPath)

    #arrange log file
    log_file_folder = os.path.join(inputPath, 'logs')
    if not os.path.exists(log_file_folder):
        os.makedirs(log_file_folder)

    log_file_path = os.path.join(log_file_folder, time.strftime("%d-%m-%Y %H %M %S", time.localtime()) + "-upload-log.txt")
    #####

    jsonFiles = _read_dir(inputPath)
    print('Found ' + str(len(jsonFiles)) + ' json files.')

    for jsonFile in jsonFiles:
        print('  Processing ' + jsonFile)

        jsonPath = os.path.join(inputPath, jsonFile)    
        processFile(jsonPath, log_file_path, token)
else:
    print('Reading a single json file ' + inputPath)

    #arrange log file
    path = Path(inputPath)
    input_folder = path.parent
    log_file_folder = input_folder.joinpath('logs')
    if not os.path.exists(log_file_folder):
        os.makedirs(log_file_folder)

    log_file_path = os.path.join(log_file_folder, path.name + " " + time.strftime("%d-%m-%Y %H %M %S", time.localtime()) + "-upload-log.txt")
    #####

    processFile(inputPath, log_file_path, token)



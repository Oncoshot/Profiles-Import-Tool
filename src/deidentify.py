import os
import sys
import hashlib
from dotenv import load_dotenv

load_dotenv("config.env")

# run this file from the command line with the command: `python deidentify.py patientID`, where patientID is the patient identifier

SALT = os.environ.get('SALT')
noOfCharacters = 12

def deidentifyPatient():
    try:
        if len(sys.argv) < 2:
            raise Exception("Please provide an id.")
        id = sys.argv[1]
        concatenatedId = id + "" + SALT
        print(concatenatedId)
        encryptedId = hashlib.sha256(concatenatedId.encode('utf-8')).hexdigest()
        condensedEncryption = encryptedId[0:noOfCharacters]
        print(condensedEncryption)
    except Exception as e:
        print(e)


deidentifyPatient()

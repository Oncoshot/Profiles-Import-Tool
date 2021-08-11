import pandas as pd
import numpy as np
import json

# Loading CSV Data
patients = pd.read_csv('mskcc-dataset/source-data/data_clinical_patient.txt',
                       sep="\t",
                       header=1,
                       usecols=['PATIENT_ID', 'SEX'])

samples = pd.read_csv('mskcc-dataset/source-data/data_clinical_sample.txt',
                      sep="\t",
                      header=4,
                      usecols=['PATIENT_ID', 'SAMPLE_ID', 'CANCER_TYPE'])
# CANCER_TYPE_DETAILED excluded

# Pre-Processing
combined = pd.merge(patients, samples, on=[
                    'PATIENT_ID', 'PATIENT_ID']).groupby(by=["PATIENT_ID"]).agg({'PATIENT_ID': lambda x: x.iloc[0], "SEX": lambda x: x.iloc[0], 'CANCER_TYPE': ' ,'.join}).drop(columns=['PATIENT_ID'])
# 'CANCER_TYPE_DETAILED': ' ,'.join

# Output to CSV
combined.to_csv('mskcc-dataset/patients.csv')

# Processing for JSON
combined.rename(columns={'CANCER_TYPE': 'diagnoses_Cancer_Unstructured',
                         'SEX': 'gender_Unstructured'
                         }, inplace=True)
combined = combined.rename_axis("id")
combined['referenceNo'] = combined.index.get_level_values(level='id').tolist()
combined['firstName'] = 'Imported'
combined['lastName'] = 'Profile'

# Converted all unstructured to items in array


def toArray(data):
    return [data]


combined['diagnoses_Cancer_Unstructured'] = list(
    map(toArray, combined['diagnoses_Cancer_Unstructured']))
combined['gender_Unstructured'] = list(
    map(toArray, combined['gender_Unstructured']))

# Save to JSON
file = open('mskcc-dataset/patients.json', 'w')
file.write(json.dumps(json.loads(
    combined.reset_index().to_json(orient='records')), indent=2))
file.close()

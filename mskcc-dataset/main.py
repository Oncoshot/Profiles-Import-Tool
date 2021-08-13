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
                      usecols=['PATIENT_ID', 'SAMPLE_ID', 'CANCER_TYPE', 'CANCER_TYPE_DETAILED', 'METASTATIC_SITE'])

# Pre-Processing
combined = pd.merge(patients, samples, on=[
                    'PATIENT_ID', 'PATIENT_ID']).groupby(by=["PATIENT_ID"]).agg({
                        'PATIENT_ID': lambda x: x.iloc[0], "SEX": lambda x: x.iloc[0], 'CANCER_TYPE': lambda x: list(x), 'CANCER_TYPE_DETAILED': lambda x: list(x), 'METASTATIC_SITE': lambda x: list(x)}).drop(columns=['PATIENT_ID'])
combined['CANCER_TYPE'] = combined['CANCER_TYPE'] + \
    combined['CANCER_TYPE_DETAILED']

combined = combined.drop(columns=["CANCER_TYPE_DETAILED"])
# Output to CSV
combined.to_csv('mskcc-dataset/patients.csv')

# Processing for JSON
combined.rename(columns={'CANCER_TYPE': 'diagnoses_Cancer_Unstructured',
                         'SEX': 'gender_Unstructured',
                         'METASTATIC_SITE': 'organInvolved_Unstructured'
                         }, inplace=True)
combined = combined.rename_axis("id")
combined['referenceNo'] = combined.index.get_level_values(level='id').tolist()
combined['firstName'] = 'Imported'
combined['lastName'] = 'Profile'


# Save to JSON
file = open('mskcc-dataset/patients.json', 'w')
file.write(json.dumps(json.loads(
    combined.reset_index().to_json(orient='records')), indent=2))
file.close()

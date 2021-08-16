import pandas as pd
import numpy as np
import json

# Loading CSV Data
patients = pd.read_csv('mskcc-dataset/source-data/data_clinical_patient.txt',
                       sep="\t",
                       header=1,
                       keep_default_na=False,
                       usecols=['PATIENT_ID', 'SEX'])

samples = pd.read_csv('mskcc-dataset/source-data/data_clinical_sample.txt',
                      sep="\t",
                      header=4,
                      keep_default_na=False,
                      usecols=['PATIENT_ID', 'SAMPLE_ID', 'CANCER_TYPE', 'CANCER_TYPE_DETAILED', 'METASTATIC_SITE'])

mutation = pd.read_csv('mskcc-dataset/source-data/data_mutations_mskcc.txt',
                       sep="\t",
                       header=1,
                       keep_default_na=False,
                       usecols=['Hugo_Symbol', 'HGVSp_Short', 'Tumor_Sample_Barcode'])

# Pre-Processing

## forming mutation string
mutation['Alteration'] = mutation['HGVSp_Short'].apply(lambda s: s.replace('p.', ''))

mutation['MUTATION'] = mutation[['Hugo_Symbol', 'Alteration']].apply(lambda x: ': '.join(x).strip(': '), axis=1)

## clean up Metastatic Site
samples['METASTATIC_SITE'].loc[(samples['METASTATIC_SITE']=='Not Applicable')]=''

## Combine samples with mutation 
combined_mutations = pd.merge(
    samples, 
    mutation, 
    left_on=['SAMPLE_ID'], 
    right_on=["Tumor_Sample_Barcode"],
    how='left'
    ).groupby(by=["SAMPLE_ID"]).agg({
        'PATIENT_ID': lambda x: x.iloc[0],
        'METASTATIC_SITE': lambda x: x.iloc[0],
        'CANCER_TYPE': lambda x: x.iloc[0],
        'CANCER_TYPE_DETAILED': lambda x: x.iloc[0],
        'MUTATION': lambda x: [] if x.isna().any() else list(x)
    })

combined = pd.merge(
    patients, 
    combined_mutations, 
    on=['PATIENT_ID'],
    how='left'
    ).groupby(by=["PATIENT_ID"]).agg({
        "SEX": lambda x: [x.iloc[0]],
        'CANCER_TYPE': lambda x: list(set(filter(None, x))),
        'CANCER_TYPE_DETAILED': lambda x: list(set(filter(None, x))),
        'METASTATIC_SITE': lambda x: list(set(filter(None, x))),
        'MUTATION': lambda x: list(set(filter(None, [item for sublist in x for item in sublist])))
    })

combined['CANCER_STAGE'] = combined['METASTATIC_SITE'].apply(lambda s: ['Stage 4'] if s else '')
combined['CANCER'] = combined['CANCER_TYPE'] + combined['CANCER_TYPE_DETAILED']

combined = combined.drop(columns=['CANCER_TYPE', "CANCER_TYPE_DETAILED"])

# Output to CSV
combined.to_csv('mskcc-dataset/patients.csv')

# Processing for JSON
combined.rename(columns={'CANCER': 'diagnoses_Cancer_Unstructured',
                         'CANCER_STAGE': 'cancerStage_Unstructured',
                         'SEX': 'gender_Unstructured',
                         'METASTATIC_SITE': 'organInvolved_Unstructured',
                         'MUTATION': 'mutations_Unstructured'
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

import pandas as pd
import numpy as np
import json
number_of_samples = 7000

# loading and data preparation

source_data = pd.read_csv('sg-cancer-registry-dataset/source-data.csv',
                          index_col=['Gender', 'Cancer'],
                          usecols=['Gender', 'Cancer', 'Stage I', 'Stage II', 'Stage III', 'Stage IV', 'Stage NA', '0-29 years', '30-39 years', '40-49 years', '50-59 years', '60-69 years', '70-79 years', '80+ years'])

numbers_by_stages = source_data.drop(columns=['0-29 years', '30-39 years', '40-49 years', '50-59 years',
                                     '60-69 years', '70-79 years', '80+ years']).stack(dropna=False).rename_axis(['Gender', 'Cancer', 'Stage'])

numbers_by_age_groups = source_data.drop(
    columns=['Stage I', 'Stage II', 'Stage III', 'Stage IV', 'Stage NA'])


percentage_by_age_groups = numbers_by_age_groups.div(
    numbers_by_age_groups.sum(axis=1), axis=0)


# statistical model

model = percentage_by_age_groups.mul(numbers_by_stages, axis=0).stack(
).rename_axis(['Gender', 'Cancer', 'Stage', 'Age group'])
model.name = 'No'
model.to_csv('sg-cancer-registry-dataset/model.csv')

# sampling

samples = model.sample(number_of_samples, replace=True,
                       weights=model).to_frame()

# age sampling from age group (assume uniform distribution for all age groups)

def split_func(x):
    x = x.split(" ")[0].split("-")
    if len(x) == 2:
        return x
    else:
        return [x[0].split("+")[0], 100]  # 80-100  


age_group = samples.index.get_level_values(level='Age group').tolist()
age_range = list(map(split_func, age_group))
age = list(map(lambda x: np.random.randint(int(x[0]), int(x[1])), age_range))

samples['Age'] = age

# adding patient identifier column
samples = samples.reset_index().rename_axis(['id'])

# rename and add columns needed to run the tool

samples['Birthyear'] = 2021 - samples['Age']
samples['Location'] = 'Singapore'

# drop columns

samples.drop(columns=['No', 'Age group', 'Age'], inplace=True)

# save samples to CSV (for reference)

samples.to_csv('sg-cancer-registry-dataset/samples.csv')


# Save to json in format compatible with PROFILES IMPORT TOOL

# rename and add columns needed to run the tool

samples.rename(columns={'Birthyear': 'dob_Unstructured',
                        'Stage': 'cancerStage_Unstructured',
                        'Cancer': 'diagnoses_Cancer_Unstructured',
                        'Gender': 'gender_Unstructured',
                        'Location': 'location_Unstructured'
                        }, inplace=True)

samples['referenceNo'] = samples.index.get_level_values(level='id').tolist()
samples['firstName'] = 'Imported'
samples['lastName'] = 'Profile'

# Converted all unstructured to items in array

def toArray(data):
    return [data]


samples['dob_Unstructured'] = list(map(toArray, samples['dob_Unstructured']))
samples['diagnoses_Cancer_Unstructured'] = list(
    map(toArray, samples['diagnoses_Cancer_Unstructured']))
samples['gender_Unstructured'] = list(
    map(toArray, samples['gender_Unstructured']))
samples['location_Unstructured'] = list(
    map(toArray, samples['location_Unstructured']))
samples['cancerStage_Unstructured'] = list(
    map(toArray, samples['cancerStage_Unstructured']))

# save samples to CSV

file = open('sg-cancer-registry-dataset/samples.json', 'w')
file.write(json.dumps(json.loads(
    samples.reset_index().to_json(orient='records')), indent=2))
file.close()

import http.client

conn = http.client.HTTPSConnection('apisite.oncodevel.com')

headers = {
                'Content-Type': 'application/json-patch+json',
                'authorization': 'Bearer ey'
          }

payload =   {
                'id': 111,
                'gender_Unstructured': [
                'Female'
                ],
                'diagnoses_Cancer_Unstructured': [
                'Lung'
                ],
                'cancerStage_Unstructured': [
                'Stage I'
                ],
                'dob_Unstructured': [
                '1959'
                ],
                'location_Unstructured': [
                'Singapore'
                ],
                'referenceNo': 111,
                'firstName': 'Imported',
                'lastName': 'Profile'
            }


conn.request('PUT', '/api/v1/organizations/NCC/profiles/111/import', headers=headers, body=str(payload) )



res = conn.getresponse()

print(res.status)

data = res.read()

print(data.decode('utf-8'))
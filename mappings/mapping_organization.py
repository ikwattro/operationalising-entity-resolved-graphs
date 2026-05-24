import json
import uuid

_ = body['data']

is_graph_editing = '__hume__createdViaHume' in body['data'] and body['data']['__hume__createdViaHume'] is True

record = {}
if is_graph_editing:
  record['DATA_SOURCE'] = 'HUME_GE'
else:
  record['DATA_SOURCE'] = _['source']
record['RECORD_ID'] = _['id']
record['RECORD_TYPE'] = 'ORGANIZATION'
features = []

features.append({'NAME_TYPE': 'PRIMARY', 'NAME_ORG': _['name']})

if 'alias' in _:
  for alias in _['alias']:
    if alias != _['name']:
      features.append({'NAME_TYPE': 'ALIAS', 'NAME_ORG': alias})

if 'nationalIdNumber' in _:
  national_id = {'NATIONAL_ID_NUMBER': _['nationalIdNumber']}
  if 'nationalIdType' in _:
    national_id['NATIONAL_ID_TYPE'] = _['nationalIdType']
  features.append(national_id)

if 'registrationDate' in _:
  features.append({'REGISTRATION_DATE': _['registrationDate']})

if 'registrationCountry' in _:
  features.append({'REG_COUNTRY': _['registrationCountry']})

if 'dissolutionDate' in _:
  features.append({'DISSOLUTION_DATE': _['dissolutionDate']})

if 'address' in _:
  addr = {'ADDRESS_TYPE': 'PRIMARY', 'ADDRESS': _['address']}
  if 'addressCountry' in _:
    addr['ADDR_COUNTRY'] = _['addressCountry']
  features.append(addr)

if 'senzingEntityId' in _:
  features.append({'TRUSTED_ID_TYPE': 'SENZING_ENTITY_ID', 'TRUSTED_ID_NUMBER': _['senzingEntityId']})

if 'manualMergeId' in _:
  features.append({'TRUSTED_ID_TYPE': 'MANUAL_MERGE', 'TRUSTED_ID_NUMBER': _['manualMergeId']})

random_id = str(uuid.uuid4())
features.append({'RANDOM_ID': random_id})

record['FEATURES'] = features

return record

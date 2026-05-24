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
record['RECORD_TYPE'] = 'PERSON'
features = []

features.append({'NAME_TYPE': 'PRIMARY', 'NAME_FULL': _['name']})

if 'alias' in _:
  for alias in _['alias']:
    if alias != _['name']:
      features.append({'NAME_TYPE': 'ALIAS', 'NAME_FULL': alias})

if 'dateofBirth' in _:
  features.append({'DATE_OF_BIRTH': _['dateofBirth']})

if 'gender' in _:
  features.append({'GENDER': _['gender']})

if 'nationality' in _:
  features.append({'NATIONALITY': _['nationality']})

if 'citizenship' in _:
  features.append({'CITIZENSHIP': _['citizenship']})

if 'taxId' in _:
  features.append({'TRUSTED_ID_TYPE': 'TAX_ID', 'TRUSTED_ID_NUMBER': _['taxId']})

if 'passportNumber' in _:
  features.append({'PASSPORT_NUMBER': _['passportNumber']})

if 'nationalIdNumber' in _:
  national_id = {'NATIONAL_ID_NUMBER': _['nationalIdNumber']}
  if 'nationalIdType' in _:
    national_id['NATIONAL_ID_TYPE'] = _['nationalIdType']
  features.append(national_id)

if 'address' in _:
  addr = {'ADDRESS_TYPE': 'PRIMARY', 'ADDRESS': _['address']}
  if 'addressCountry' in _:
    addr['ADDR_COUNTRY'] = _['addressCountry']
  features.append(addr)

if 'url' in _:
  features.append({'WEBSITE_ADDRESS': _['url']})

if 'manualMergeId' in _:
  features.append({'TRUSTED_ID_TYPE': 'MANUAL_MERGE', 'TRUSTED_ID_NUMBER': _['manualMergeId']})

random_id = str(uuid.uuid4())
features.append({'RANDOM_ID': random_id})

record['FEATURES'] = features

return record

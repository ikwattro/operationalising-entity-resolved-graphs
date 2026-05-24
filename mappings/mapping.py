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

name_full = '%s %s %s' % (_['firstName'], _['lastName'], _.get('middleName', ''))
name_full = name_full.replace('  ', ' ')

features.append({'NAME_TYPE':'PRIMARY','NAME_FULL': name_full})
# features.append({'NAME_FIRST': _['firstName']})
# features.append({'NAME_LAST': _['lastName']})
# if 'middleName' in _:
#   features.append({'NAME_MIDDLE': _['middleName']})
if 'alias' in _:
  for alias in _['alias']:
    if alias != name_full:
      features.append({'NAME_TYPE':'ALIAS','NAME_FULL': alias})
if 'dateOfBirth' in _:
  dob = _['dateOfBirth']
  features.append({'DATE_OF_BIRTH': dob})
if 'yearOfBirth' in _ and 'dateOfBirth' not in _:
  features.append({'DATE_OF_BIRTH': _['yearOfBirth']})
if 'nationality' in _:
  features.append({'NATIONALITY': _['nationality']})
if 'gender' in _:
  features.append({'GENDER': _['gender']})
if 'ssn' in _:
  features.append({'TRUSTED_ID_TYPE': 'SSN', 'TRUSTED_ID_NUMBER' : _['ssn']})
if 'passportNumber' in _:
  features.append({'PASSPORT_NUMBER': _['passportNumber']})
if 'nationalId' in _:
  features.append({'NATIONAL_ID_NUMBER': _['nationalId']})
if 'phoneNumber' in _:
  features.append({'PHONE_NUMBER': _['phoneNumber']})
if 'address' in _:
  features.append({'ADDRESS_TYPE': 'PRIMARY', 'ADDRESS': _['address']})
if 'apart_id' in _:
  features.append({'TRUSTED_ID_TYPE': 'FORCED_APART', 'TRUSTED_ID_NUMBER': _['id']})

# for _o in body['orgs']:
#   features.append({'GROUP_ASSOCIATION_TYPE': _o['type'], 'GROUP_ASSN_ID_NUMBER': _o['org']['pk']})

# for _i in _['identifiers']:
#   features.append({'TRUSTED_ID_NUMBER': _i})

random_id = str(uuid.uuid4())
# force senzing to provide updated record
features.append({'RANDOM_ID': random_id })

record['FEATURES'] = features

return record
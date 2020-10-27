import json, os, pdb, requests, configparser
from urllib.parse import urlencode, urljoin

config = configparser.ConfigParser(interpolation=None)
config.read('/usr/share/domain-signup/defaults.ini')

USERNAME = config['NS']['USERNAME']
PASSWORD = config['NS']['PASSWORD']
CLIENT_ID = config['NS']['CLIENT_ID']
CLIENT_SECRET = config['NS']['CLIENT_SECRET']
BASE_URL = config['NS']['NS_URL']
ACCESS_TOKEN_URL = ''.join([BASE_URL, '/oauth2/token'])
AUTH_URL = ''.join([BASE_URL, '/oauth2/auth'])

def get_ns_response_data(parameters, access_token):
  headers = {'Authorization': 'Bearer {}'.format(access_token)}
  response = requests.get(url, params=parameters, headers=headers)
  is_successful = response.ok

  if is_successful:
    data = response.json()
  else:
    raise Exception

  return data

def get_access_token():
  url = ACCESS_TOKEN_URL
  parameters = {
    'username': USERNAME,
    'password': PASSWORD,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'password'
  }
  response = requests.get(url, params=parameters)
  is_successful = response.ok
  
  if is_successful:
    response_data = response.json()
    access_token = response_data['access_token']
  else:
    raise Exception

  return access_token

def check_reseller(reseller, access_token):
  parameters = {
    'obejct': 'reseller',
    'action': 'count',
    'domain': reseller,
    'format': 'json'
  }
  data = get_ns_response_data(parameters, access_token)
  if data['total'] and data['total'] != '1':
    raise Exception
  else:
    reseller = True

  return reseller

def check_domain(domain, access_token):
  parameters = {
    'obejct': 'domain',
    'action': 'count',
    'domain': domain,
    'format': 'json'
  }
  data = get_ns_response_data(parameters, access_token)

  if data['total'] and data['total'] == '1':
    raise Exception
  else:
    domain = True

  return domain

def add_domain(reseller, domain, access_token):
  parameters = {
    'object': 'domain',
    'action': "create",
    'domain': domain,
    'territory': reseller
  }
  data = get_ns_response_data(parameters, access_token)
  
  return data

def add_domain_dial_plan(domain, access_token)
 parameters = {
    'object': 'dialplan',
    'action': "create",
    'domain': domain,
    'dialplan': domain,
    'description': "Dial Plan for " . domain
  }
  data = get_ns_response_data(parameters, access_token)
  
  return data

def add_dial_plan_rule_to_table(domain, access_token):
  parameters = {
    'object': 'dialrule',
    'action': "create",
    'domain': domain,
    'dialplan': domain,
    'matchrule': "*",
    'responder': "<Cloud PBX Features>",
    'matchrule': "*",
    'to_scheme': "[*]",
    'to_user': "[*]",
    'to_host': "[*]",
    'plan_description': "Chain to Default Table"
  }
  data = get_ns_response_data(parameters, access_token)
  
  return data

def find_did(access_token):
  parameters = {
    'object': 'phonenumber',
    'action': "read",
    'responder': "AvailableDID",
    'dialplan': "DID Table",
    'plan_description': "Available",
    'territory': "AakerCo",
    'format': "json"
  }
  data = get_ns_response_data(parameters, access_token)
  did = data[0]['matchrule']
  #error no resource if no matchrule

  return did

def assign_did(domain, DID, access_token):
  parameters = {
        'object': 'phonenumber',
        'matchrule': DID,
        'action': "update",
        'responder': "AvailableDID",
        'dialplan': "DID Table",
        'dest_domain': domain,
        'to_user': "[*]",
        'to_host': domain,
        'plan_description': "Assigned to " . domain
  }
  DIDs = get_ns_response_data(parameters, access_token)
  newDID = DIDs.split(':')[1].split('@')[0]

  return newDID

def add_domain_user(reseller, domain, newDID, access_token):
  area_code = 
  
  parameters = {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'first_name': "Domain",
    'last_name': "User",
    'dial_plan': domain,
    'dial_policy': "US and Canada",
    'user': 'domain',
    'dir_list': "no",
    'dir_anc': "no",
    'srv_code': 'system-user',
    'area_code': areaCode,
    'callid_name': reseller,
    'callid_nmbr': newDID,
    'callid_emgr': newDID,
    'vmail_transcribe': "mutare",
    'subscriber_pin': PASSWORD
  }

  parameters = {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'first_name': "Guest",
    'last_name': "Video",
    'dial_plan': "Video Conference",
    'dial_policy': "US and Canada",
    'user': 'guest',
    'dir_list': "no",
    'dir_anc': "no",
    'srv_code': 'system-user',
    'scope': 'No Portal',
    'area_code': areaCode,
    'callid_name': reseller,
    'callid_nmbr': newDID,
    'callid_emgr': newDID,
    'subscriber_pin': PASSWORD
  }

def add_preferred_domain(reseller, domain, access_token):
  add_domain(reseller, domain, access_token)
  add_domain_dial_plan(domain, access_token)
  add_dial_plan_rule_to_table(domain, access_token)
  DID = find_did(access_token)
  assign_did(domain, did, access_token)
  add_domain_user(reseller, domain, newDID, access_token)
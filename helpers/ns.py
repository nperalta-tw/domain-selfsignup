import json, os, pdb, requests, configparser, random
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
  #error 'no resource' if no matchrule

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
  new_did = DIDs.split(':')[1].split('@')[0]

  return new_did

def add_domain_user(reseller, domain, new_did, pin, access_token):
  area_code = new_did[0:3]
  
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
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'vmail_transcribe': "mutare",
    'subscriber_pin': pin
  }

  data = get_ns_response_data(parameters, access_token)

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
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'subscriber_pin': pin
  }

  data = get_ns_response_data(parameters, access_token)

  return area_code

def add_department(reseller, domain, new_did, department, pin, access_token):
  parameters = {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'dial_plan': domain,
    'scope': "Basic User",
    'name': department['name'],
    'user': department['user'],
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'directory_match': 'departments',
    'dir': 'departments',
    'dir_list': "no",
    'dir_anc': "no",
    'srv_code': 'system-department',
    'vmail_transcribe': "mutare",
    'subscriber_pin': pin
  }
  data = get_ns_response_data(parameters, access_token)

def add_reseller_user(reseller, domain, new_did, pin, access_token):
  #Create user
  parameters = {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'dial_plan': domain,
    'scope': "Reseller",
    'user': '1000',
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'department': 'Tech',
    'vmail_transcribe': "mutare",
    'subscriber_pin': pin
  }

  data = get_ns_response_data(parameters, access_token)

  #Create device
  parameters {
    'object': 'device',
    'action': "create",
    'domain': domain,
    'user': "1000",
    'device': "sip:1000@" + domain,
    'passwordLength': 8
  }

  data = get_ns_response_data(parameters, access_token)

  #Create answerrule
  parameters {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "1000",
    'time_frame': "*",
    'priority': "0",
    'sim_parameters': "<OwnDevices>",
    'sim_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99" 
  }

  data = get_ns_response_data(parameters, access_token)

def add_office_manager_user(reseller, domain, new_did, area_code, pin, access_token):
  parameters {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'dial_plan': domain,
    'email': email,
    'scope': "Office Manager",
    'first_name': "Office",
    'last_name': "Manager",
    'user': '1001',
    'dir_list': "yes",
    'dir_anc': "yes",
    'department': 'Tech',
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'vmail_transcribe': "mutare",
    'subscriber_pin': pin
  }

  data = get_ns_response_data(parameters, access_token)
  
  parameters {
    'object': 'device',
    'action': "create",
    'domain': domain,
    'user': "1001",
    'device': "sip:1001@" + domain,
    'passwordLength': 8
  }

  data = get_ns_response_data(parameters, access_token)

  parameters {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "1001",
    'time_frame': "*",
    'priority': "0",
    'sim_parameters': "<OwnDevices>",
    'sim_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99"   
  }

  data = get_ns_response_data(parameters, access_token)

  return data

def add_supervisor_user(reseller, domain, new_did, area_code, pin, access_token):
  parameters {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'dial_plan': domain,
    'scope': "Call Center Supervisor",
    'first_name': "Call Center",
    'last_name': "Supervisor",
    'user': '1002',
    'dir_list': "yes",
    'dir_anc': "yes",
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'vmail_transcribe': "mutare",
    'subscriber_pin': pin
  }

  data = get_ns_response_data(parameters, access_token)

  parameters {
      'object': 'device',
      'action': "create",
      'domain': domain,
      'user': "1002",
      'device': "sip:1002@" + domain,
      'passwordLength': 8
  }

  data = get_ns_response_data(parameters, access_token)
  
  parameters {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "1002",
    'time_frame': "*",
    'priority': "0",
    'sim_parameters': "<OwnDevices>",
    'sim_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99"
  }

  data = get_ns_response_data(parameters, access_token)

  return data

def add_basic_user(reseller, domain, new_did, area_code, pin, access_token):
  parameters {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'dial_plan': domain,
    'scope': "Basic User",
    'first_name': "Basic",
    'last_name': "User",
    'user': '1003',
    'dir_list': "yes",
    'dir_anc': "yes",
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'department': 'Sales',
    'vmail_transcribe': "mutare",
    'subscriber_pin': pin 
  }
  
  data = get_ns_response_data(parameters, access_token)
  
  parameters {
    'object': 'device',
    'action': "create",
    'domain': domain,
    'user': "1003",
    'device': "sip:1003@" + domain,
    'passwordLength': 8
  }

  data = get_ns_response_data(parameters, access_token)

  parameters {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "1003",
    'time_frame': "*",
    'priority': "0",
    'sim_parameters': "<OwnDevices>",
    'sim_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99"
  }

  data = get_ns_response_data(parameters, access_token)

  return data

def add_route_manager_user(reseller, domain, new_did, area_code, pin, access_token):
  parameters {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'dial_plan': domain,
    'scope': "Route Manager",
    'first_name': "Route",
    'last_name': "Manager",
    'user': '1004',
    'dir_list': "yes",
    'dir_anc': "yes",
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'vmail_transcribe': "mutare",
    'subscriber_pin': pin   
  }

  data = get_ns_response_data(parameters, access_token)

  parameters {
    'object': 'device',
    'action': "create",
    'domain': domain,
    'user': "1004",
    'device': "sip:1004@" + domain,
    'passwordLength': 8
  }

  data = get_ns_response_data(parameters, access_token)

  parameters {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "1004",
    'time_frame': "*",
    'priority': "0",
    'sim_parameters': "<OwnDevices>",
    'sim_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99"
  }

  data = get_ns_response_data(parameters, access_token)

  return data

def add_call_queue_sales(reseller, domain, new_did, area_code, pin, access_token):
  parameters = {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'scope': "Basic User",
    'first_name': "Sales",
    'last_name': "Call Queue",
    'dir_list': "no",
    'dir_anc': "no",
    'user': '2000',
    'srv_code': 'system-queue',
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'subscriber_pin': pin
}

data = get_ns_response_data(parameters, access_token)

parameters = {
    'object': 'callqueue',
    'action': "create",
    'domain': domain,
    'queue': "2000",
    'run_stats': "yes",
    'huntgroup_option': "Ring All",
    'description': "Sales"
}

data = get_ns_response_data(parameters, access_token)

parameters = {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "2000",
    'time_frame': "*",
    'priority': "0",
    'for_parameters': "queue_2000",
    'for_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99"
    
    
}
data = get_ns_response_data(parameters, access_token)

parameters = {
    'object': 'dialrule',
    'action': "create",
    'domain': domain,
    'dialplan': domain,
    'matchrule': "*",
    'responder': "sip:start@call-queuing",
    'matchrule': "queue_2000",
    'to_scheme': "[*]",
    'to_user': "2000",
    'to_host': domain,
    'plan_description': "To Queue"
    
}
data = get_ns_response_data(parameters, access_token)

def add_call_queue_support(reseller, domain, new_did, area_code, pin, access_token):
  parameters = {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'scope': "Basic User",
    'first_name': "Support",
    'last_name': "Call Queue",
    'dir_list': "no",
    'dir_anc': "no",
    'user': '2001',
    'srv_code': 'system-queue',
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'subscriber_pin': pin
  }
  data = get_ns_response_data(parameters, access_token)

  parameters = {
    'object': 'callqueue',
    'action': "create",
    'domain': domain,
    'queue': "2001",
    'huntgroup_option': "1stAvail",
    'run_stats': "yes",
    'description': "Support"
  }
  
  data = get_ns_response_data(parameters, access_token)

  parameters = {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "2001",
    'time_frame': "*",
    'priority': "0",
    'for_parameters': "queue_2001",
    'for_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99"
  }

  data = get_ns_response_data(parameters, access_token)

  parameters = {
    'object': 'dialrule',
    'action': "create",
    'domain': domain,
    'dialplan': domain,
    'matchrule': "*",
    'responder': "sip:start@call-queuing",
    'matchrule': "queue_2001",
    'to_scheme': "[*]",
    'to_user': "2001",
    'to_host': domain,
    'plan_description': "To Queue"
  }

  data = get_ns_response_data(parameters, access_token)

  return data

def add_park_1(reseller, domain, new_did, area_code, pin, access_token):
  parameters = {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'scope': "Basic User",
    'first_name': "Call Park",
    'last_name': "One",
    'dir_list': "no",
    'dir_anc': "no",
    'user': '701',
    'srv_code': 'system-queue',
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'subscriber_pin': pin
  }

  data = get_ns_response_data(parameters, access_token)

  parameters = {
    'object': 'callqueue',
    'action': "create",
    'domain': domain,
    'queue': "701",
    'huntgroup_option': "Call Park",
    'description': "Call Park One"
  }

  data = get_ns_response_data(parameters, access_token)

  parameters = {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "701",
    'time_frame': "*",
    'priority': "0",
    'for_parameters': "queue_701",
    'for_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99"
  }

  data = get_ns_response_data(parameters, access_token)


  parameters = {
    'object': 'dialrule',
    'action': "create",
    'domain': domain,
    'dialplan': domain,
    'matchrule': "*",
    'responder': "sip:start@call-queuing",
    'matchrule': "queue_701",
    'to_scheme': "[*]",
    'to_user': "701",
    'to_host': domain,
    'plan_description': "To Queue"   
  }

  data = get_ns_response_data(parameters, access_token)

  return data

def add_park_2(reseller, domain, new_did, area_code, pin, access_token):
  parameters = {
    'object': 'subscriber',
    'action': "create",
    'domain': domain,
    'scope': "Basic User",
    'first_name': "Call Park",
    'last_name': "Two",
    'dir_list': "no",
    'dir_anc': "no",
    'user': '702',
    'srv_code': 'system-queue',
    'area_code': area_code,
    'callid_name': reseller,
    'callid_nmbr': new_did,
    'callid_emgr': new_did,
    'subscriber_pin': pin
  }

  data = get_ns_response_data(parameters, access_token)

  parameters = {
    'object': 'callqueue',
    'action': "create",
    'domain': domain,
    'queue': "702",
    'huntgroup_option': "Call Park",
    'description': "Call Park Two"
  }

  data = get_ns_response_data(parameters, access_token)

  parameters = {
    'object': 'answerrule',
    'action': "create",
    'domain': domain,
    'user': "702",
    'time_frame': "*",
    'priority': "0",
    'for_parameters': "queue_702",
    'for_control': "e",
    'dnd_enable': "0",
    'enable': "1",
    'order': "99"
  }

  data = get_ns_response_data(parameters, access_token)

  parameters = {
    'object': 'dialrule',
    'action': "create",
    'domain': domain,
    'dialplan': domain,
    'matchrule': "*",
    'responder': "sip:start@call-queuing",
    'matchrule': "queue_702",
    'to_scheme': "[*]",
    'to_user': "702",
    'to_host': domain,
    'plan_description': "To Queue"
  }
  
  data = get_ns_response_data(parameters, access_token)

  return data

def add_preferred_domain(reseller, domain, access_token):
  pin = [random.randint(0,9) for _ in range(8)]
  tech_department = {'name': 'Tech Department', 'user': 'Tech'}
  sales_department = {'name': 'Sales Department', 'user': 'Sales'}
  add_domain(reseller, domain, access_token)
  add_domain_dial_plan(domain, access_token)
  add_dial_plan_rule_to_table(domain, access_token)
  DID = find_did(access_token)
  new_did = assign_did(domain, DID, access_token)
  area_code = add_domain_user(reseller, domain, new_did, pin, access_token)
  add_department(reseller, domain, new_did, tech_department, pin, access_token)
  add_department(reseller, domain, new_did, sales_department, pin, access_token)
  add_reseller_user(reseller, domain, new_did, pin, access_token)
  add_office_manager_user(reseller, domain, new_did, area_code, pin, access_token)
  add_supervisor_user(reseller, domain, new_did, area_code, pin, access_token)
  add_basic_user(reseller, domain, new_did, area_code, pin, access_token)
  add_route_manager_user(reseller, domain, new_did, area_code, pin, access_token)
  add_call_queue_sales(reseller, domain, new_did, area_code, pin, access_token)
  add_call_queue_support(reseller, domain, new_did, area_code, pin, access_token)
  add_park_1(reseller, domain, new_did, area_code, pin, access_token)
  add_park_2(reseller, domain, new_did, area_code, pin, access_token)

  domain_credentials = {
    'new_did': new_did,
    'pin': pin,
  }

  return domain_credentials
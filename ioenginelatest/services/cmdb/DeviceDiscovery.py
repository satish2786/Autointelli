#!/usr/bin/python3.6

# Device  Discovery code 

import json
import requests
from CMDB import *
from sys import exit
import time

# Main Method #
try:
  payload = {'username': 'admin', 'password': 'U2FsdGVkX19cYDKT6jt5zGTUnLEnU2oD8gwwYWNc7WY='}
  headers = {'Content-Type': 'Application/json'}
  r = requests.post("http://localhost:5001/ui/api1.0/login", data=json.dumps(payload), headers=headers)
  if r.status_code == 200:
    data = json.loads(r.text)
    sessionid = data['session_id']
    headers = {'sessionkey': sessionid}
    request1 = requests.get("http://127.0.0.1:5001/ui/api1.0/devicediscoverylist4machine", headers=headers)
    if request1.text == "null":
      print("No New Machines added for discovery")
      exit(0)
    if request1.status_code == 200:
      iplist = json.loads(request1.text)
      for device in iplist['data']:
        cred_id = device['cred_id']
        cred_type = device['cred_type']
        ipaddress = device['ip_address']
        operatingsystem = device['operating_system']
        username = device['username']
        password = device['password']
        sudo = device['sudo_yn']
        if operatingsystem == 'Linux':
          result = insertLinuxHost.apply_async(args=[ipaddress, username, password, cred_id], connect_timeout=3)
          while result.ready() == False:
            time.sleep(2)
            retval = result.get()
            if not retval:
              cur.execute("""UPDATE ai_device_discovery set gf_error='{1}' where ip_address='{0}'""".format(ipaddress, 'Machine Not Reachable or Authentication Problem'))
            else:
              cur.execute("""UPDATE ai_device_discovery set gf_yn='Y', gf_error='Machine Reachable' where ip_address='{0}'""".format(ipaddress))
        elif operatingsystem == 'Windows':
          result = insertWindowsHost.apply_async(args=[ipaddress, username, password, cred_id], connect_timeout=3)
          while result.ready() == False:
            time.sleep(2)
            retval = result.get()
            if not retval:
              cur.execute("""UPDATE ai_device_discovery set gf_error='{1}' where ip_address='{0}'""".format(ipaddress, 'Machine Not Reachable or Authentication Problem'))
            else:
              cur.execute("""UPDATE ai_device_discovery set gf_yn='Y', gf_error='Machine Reachable' where ip_address='{0}'""".format(ipaddress))
        else:
          cur.execute("""UPDATE ai_device_discovery set gf_error='{1}' where ip_address='{0}'""".format(ipaddress, 'Operating System not Supported'))
    else:
      print("Cannnot Access Device Discovery API")
      exit(1)
  else:
    print("Error  Authentication Failed")
    exit(1)
except Exception as e:
  print("Error: " + str(e))

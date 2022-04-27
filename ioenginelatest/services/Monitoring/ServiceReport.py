import requests
import json
import calendar
import time
from requests.auth import HTTPBasicAuth
from datetime import datetime,timedelta
import os

data = json.load(open('/etc/autointelli/autointelli.conf'))
if not os.path.isfile('/etc/autointelli/autointelli.conf'):
  print(" [x] Worker Cannot Start, Config not found")
  sys.exit(1)

monitorurl = data['monitor']['url']


def getServiceReport(hostgroup, startepoch, endepoch, hostname, username):
  totaltime = int(endepoch) - int(startepoch)
  URL = "http://"+monitorurl+"/nagios/cgi-bin/archivejson.cgi?query=availability&availabilityobjecttype=services&hostgroup={2}&starttime={0}&endtime={1}".format(startepoch,endepoch,hostgroup)
  Output = requests.get(URL,auth=HTTPBasicAuth(username, 'nagiosadmin'))
  Output = json.loads(Output.text)
  Output_data = {}
  for service in Output['data']['services']:
    if service['host_name'] == hostname:
      service_name = service['description']
      time_ok_percent = (service['time_ok'] / totaltime) * 100
      time_warning_percent = (service['time_warning'] / totaltime) * 100
      time_critical_percent = (service['time_critical'] / totaltime) * 100
      time_unknown_percent = (service['time_unknown'] / totaltime) * 100
      Output_data[service_name] = {}
      Output_data[service_name]['ok'] = float('%.2f' % time_ok_percent)
      Output_data[service_name]['warning'] = float('%.2f' % time_warning_percent)
      Output_data[service_name]['critical'] = float('%.2f' % time_critical_percent)
      Output_data[service_name]['unknown'] = float('%.2f' % time_unknown_percent)
      Output_data.update()
  return(Output_data)

if __name__ == "__main__":
  getServiceReport("windows-servers", "01-01-2020", "29-02-2020", "aidev-winmem", "nagiosadmin" )

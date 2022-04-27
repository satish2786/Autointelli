#!/usr/bin/env python

import json
from flask import Flask, jsonify, request, Blueprint, make_response, send_file
from requests.auth import HTTPBasicAuth
import requests
import base64
import time
import calendar
import shutil
import os
from jinja2 import Environment
from jinja2 import FileSystemLoader
from datetime import datetime,timedelta
from services.Monitoring import ServiceReport
import services.utils.ConnMQ as connmq
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
from services.utils import ConnPostgreSQL
import sys
import time
from services.utils import sessionkeygen

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar
logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

monitoring_api = Blueprint('monitoring_api', __name__)

data = json.load(open('/etc/autointelli/autointelli.conf'))
if not os.path.isfile('/etc/autointelli/autointelli.conf'):
    print(" [x] Worker Cannot Start, Config not found")
    sys.exit(1)


monitorurl = data['monitor']['url']
get_plugin_output = 'http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=service&formatoptions=whitespace+enumerate+bitmask+duration&hostname={0}&servicedescription={1}'
get_chart = 'http://'+monitorurl+'/nagios/cgi-bin/histogram.cgi?createimage&t1=1562312375&t2=1564990775&host={0}&service={1}&breakdown=dayofmonth&assumestateretention=yes&initialstateslogged=no&newstatesonly=no&graphevents=120&graphstatetypes=3'
fh = open('/tmp/image.png','w')

@monitoring_api.route('/monitoring/getAllApplications/<username>', methods=['GET', 'POST'])
def get_all_Applications(username):
  output = {}
  hostGroup_URL = 'http://'+monitorurl+'/nagios/cgi-bin/objectjson.cgi?query=hostgrouplist&formatoptions=whitespace+enumerate+bitmask+duration&details=true'
  application_list = requests.get(hostGroup_URL,auth=HTTPBasicAuth(username, 'nagiosadmin'))
  app_list_output = json.loads(application_list.text)
  apps = app_list_output['data']['hostgrouplist'].keys()
  for app in apps:
    host_count_URL = 'http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=hostcount&formatoptions=enumerate&hostgroup={0}'.format(app)
    service_count_URL='http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=servicecount&formatoptions=enumerate&hostgroup={0}'.format(app)
    output[app] = {}
    output_service_count = requests.get(service_count_URL,auth=HTTPBasicAuth(username,'nagiosadmin'))
    data = json.loads(output_service_count.text)
    service_count = int(data['data']['count']['ok']) + int(data['data']['count']['warning']) + int(data['data']['count']['critical']) + int(data['data']['count']['unknown']) + int(data['data']['count']['pending']) 
    output[app]['Total Services'] = service_count
    
    output_host_count = requests.get(host_count_URL,auth=HTTPBasicAuth(username,'nagiosadmin'))
    data = json.loads(output_host_count.text)
    host_count = int(data['data']['count']['up']) + int(data['data']['count']['down']) + int(data['data']['count']['unreachable']) + int(data['data']['count']['pending'])
    output[app]['Total Hosts'] = host_count
  return(json.dumps(output))


@monitoring_api.route('/monitoring/getAllHostgroups/<username>', methods=['GET', 'POST'])
def get_all_HostGroups(username):
  headers = {'Content-Type': 'application/json'}
  
  URL = "http://localhost:5001/ui/api1.0/mon_hosts/{0}".format(username)
  
  # payload = {'username': 'admin', 'password': 'U2FsdGVkX19y3NIhUZBzArWrQYPlL4vHo4xjfENBaig='}
  # r = requests.post("http://localhost:5001/ui/api1.0/login", data=json.dumps(payload), headers=headers)
  # if r.status_code == 200:
  #   data = json.loads(r.text)
  #   sessionid = data['session_id']
  #
  # headers = {'sessionkey': sessionid, 'content-type': 'application/json'}
  headers = {'sessionkey': sessionkeygen.createSession('1')['data'], 'content-type': 'application/json'}
  output = requests.get(URL, headers=headers, verify=False)
  data = json.loads(output.text)
  _final = {}
  _final['hostgroups'] = []
  if data['result'] == 'success':
    for hostgroup in data['data']:
      _final['hostgroups'].append(hostgroup['hostgroupname'])
  return(json.dumps(_final))  


@monitoring_api.route('/monitoring/dashboard/api/v1/data', methods=['GET', 'POST'])
def get_main_Dashboard_Data():
  data = request.get_data(as_text=True)
  data = json.loads(data)
  username = data['username']
  hostgroup = data['hostgroup']
  Dashboard_Name = 'Infrastructure Status - '+hostgroup
  host_count_url='http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=hostcount&hostgroup={0}'.format(hostgroup)
  service_count_url='http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=servicecount&hostgroup={0}'.format(hostgroup)
  Get_Host_Count_Data = requests.get(host_count_url,auth=HTTPBasicAuth(username, 'nagiosadmin'))
  Output = json.loads(Get_Host_Count_Data.text)
  HOST_UP = Output['data']['count']['up']
  HOST_DOWN = Output['data']['count']['down']
  HOST_UNREACHABLE = Output['data']['count']['unreachable']
  HOST_PENDING = Output['data']['count']['pending']
  Get_Service_Count_Data = requests.get(service_count_url, auth=HTTPBasicAuth(username, 'nagiosadmin'))
  Output_Service = json.loads(Get_Service_Count_Data.text)
  SERVICE_OK = Output_Service['data']['count']['ok']
  SERVICE_WARNING = Output_Service['data']['count']['warning']
  SERVICE_CRITICAL = Output_Service['data']['count']['critical']
  SERVICE_UNKNOWN =Output_Service['data']['count']['unknown']
  SERVICE_PENDING = Output_Service['data']['count']['pending']
  SERVICE_Last_Data_Update = int(Output_Service['result']['last_data_update']) / 1000
  SERVICE_Last_Data_Update = time.strftime('%H:%M', time.localtime(SERVICE_Last_Data_Update))
  HOST_Last_Data_Update = int(Output['result']['last_data_update']) / 1000
  HOST_Last_Data_Update = time.strftime('%H:%M', time.localtime(HOST_Last_Data_Update))
  pData = jsonify({'Dashboard_Name': Dashboard_Name, 'HOST_LAST_DATA_UPDATE': HOST_Last_Data_Update, 'HOST_UP': HOST_UP, 'HOST_DOWN': HOST_DOWN, 'HOST_UNREACHABLE': HOST_UNREACHABLE, 'HOST_PENDING': HOST_PENDING, 'SERVICE_OK': SERVICE_OK, 'SERVICE_WARNING': SERVICE_WARNING, 'SERVICE_CRITICAL': SERVICE_CRITICAL, 'SERVICE_UNKNOWN': SERVICE_UNKNOWN, 'SERVICE_PENDING': SERVICE_PENDING, 'SERVICE_LAST_DATA_UPDATE': SERVICE_Last_Data_Update})
  return(pData)

@monitoring_api.route('/monitoring/api/v1/data/servicelist/<host>', methods=['GET', 'POST'])
def get_monitoring_data_right_panel(host):
  data = request.get_data(as_text=True)
  data=json.loads(data)
  username = data['username']
  start = 1
  count = 10
  try:
    start = data['start']
    count = data['count']
  except:
    pass
  headers = {'Content-Type': 'application/json'}
  URL = "http://localhost:5001/ui/api1.0/mon_services/{0}/status_a".format(host)
  
  # payload = {'username': 'admin', 'password': 'U2FsdGVkX19y3NIhUZBzArWrQYPlL4vHo4xjfENBaig='}
  # r = requests.post("http://localhost:5001/ui/api1.0/login", data=json.dumps(payload), headers=headers)
  # if r.status_code == 200:
  #   data = json.loads(r.text)
  #   sessionid = data['session_id']
  #
  # headers = {'sessionkey': sessionid, 'content-type': 'application/json'}
  headers = {'sessionkey': sessionkeygen.createSession('1')['data'], 'content-type': 'application/json'}
  output = requests.get(URL, headers=headers, verify=False)
  data = json.loads(output.text)
  _final = {}
  _final[host] = {}
  if data['result'] == 'success':
    for service in data['data']['service']:
      if service[0] == 'service_object_id':
        continue
      _final[host][service[1]] = {}
      _final[host][service[1]]['last_check'] = service[4]
      _final[host][service[1]]['status'] = service[2].lower()
      _final[host][service[1]]['value_description'] = service[3]
  return(json.dumps(_final))

@monitoring_api.route('/monitoring/api/v1/data/hostlist', methods=['GET', 'POST'])
def get_monitoring_data_left_panel():
  data = request.get_data(as_text=True)
  data=json.loads(data)
  username = data['username']
  hostgroup_input = data['hostgroup']
  headers = {'Content-Type': 'application/json'}

  URL = "http://localhost:5001/ui/api1.0/mon_hosts/{0}".format(username)
  
  # payload = {'username': 'admin', 'password': 'U2FsdGVkX19y3NIhUZBzArWrQYPlL4vHo4xjfENBaig='}
  # r = requests.post("http://localhost:5001/ui/api1.0/login", data=json.dumps(payload), headers=headers)
  # if r.status_code == 200:
  #   data = json.loads(r.text)
  #   sessionid = data['session_id']
  #
  # headers = {'sessionkey': sessionid, 'content-type': 'application/json'}
  headers = {'sessionkey': sessionkeygen.createSession('1')['data'], 'content-type': 'application/json'}
  output = requests.get(URL, headers=headers, verify=False)
  data = json.loads(output.text)
  _final = {}
  _final['hostlist'] = []
  if data['result'] == 'success':
    for hostgroup in data['data']:
      if hostgroup['hostgroupname'] == hostgroup_input:
        for host in hostgroup['hosts']:
          _final['hostlist'].append(host['host_name'])
  return(json.dumps(_final))


@monitoring_api.route('/monitoring/dashboard/api/v1/data/<host>', methods=['GET', 'POST'])
def get_monitoring_data_host_service(host):
  data = request.get_data(as_text=True)
  print(data)
  data=json.loads(data)
  username = data['username']
  URL = 'http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=servicelist&formatoptions=enumerate+bitmask+duration&details=true&hostname={0}'
  Get_Host_Service_Data = requests.get(URL.format(host), auth=HTTPBasicAuth(username, 'nagiosadmin'))
  Output = json.loads(Get_Host_Service_Data.text)
  service_data = {}
  service_data['Dashboard_Name'] = "Services in " + host
  Last_Data_Update = int(Output['result']['last_data_update']) / 1000
  Last_Data_Update = time.strftime('%H:%M', time.localtime(Last_Data_Update))
  service_data['last_data_update'] = Last_Data_Update
  service_data['services'] = {}
  if host in Output['data']['servicelist']:
      for service in list(Output['data']['servicelist'][host]):
          service_data['services'][service] = {}
          plugin_output = Output['data']['servicelist'][host][service]['plugin_output']
          status = Output['data']['servicelist'][host][service]['status']
          updated_data = {'plugin_output': plugin_output, 'status': status}
          service_data['services'][service].update(updated_data)
  else:
      pass
  return json.dumps(service_data)

@monitoring_api.route('/monitoring/dashboard/api/v1/data/service', methods=['GET', 'POST'])
def get_monitoring_service_Dashboard():
  data = request.get_data(as_text=True)
  data=json.loads(data)
  username = data['username']
  hostgroup = data['hostgroup']
  filterv = data['filter']
  URL = 'http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=servicelist&formatoptions=enumerate+bitmask+duration&details=true&hostgroup={0}&servicestatus={1}'
  Get_Host_Service_Data = requests.get(URL.format(hostgroup,filterv), auth=HTTPBasicAuth(username, 'nagiosadmin'))
  Output = json.loads(Get_Host_Service_Data.text)
  service_data = {}
  service_data['Dashboard_Name'] = "Services Status : " + filterv
  Last_Data_Update = int(Output['result']['last_data_update']) / 1000
  Last_Data_Update = time.strftime('%H:%M', time.localtime(Last_Data_Update))
  service_data['last_data_update'] = Last_Data_Update
  hostlist = list(Output['data']['servicelist'].keys())
  service_data['hostlist'] = {}
  for host in hostlist:
      service_data['hostlist'][host] = {}
      service_data['hostlist'][host]['services'] = {}
      for service in list(Output['data']['servicelist'][host]):
          service_data['hostlist'][host]['services'][service] = {}
          plugin_output = Output['data']['servicelist'][host][service]['plugin_output']
          status = Output['data']['servicelist'][host][service]['status']
          updated_data = {'plugin_output': plugin_output, 'status': status}
          service_data['hostlist'][host]['services'][service].update(updated_data)
  return json.dumps(service_data)


@monitoring_api.route('/monitoring/dashboard/api/v1/hostdashboard', methods=['GET', 'POST'])
def get_host_dashboard_data():
  data = request.get_data(as_text=True)
  data=json.loads(data)
  username = data['username']
  hostgroup = data['hostgroup']
  filterv = data['filter']
  host_data = {}
  host_data['Dasbhoard_Name'] = 'Host Dashboard'
  Get_Host_Data_URL='http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=servicelist&formatoptions=whitespace+enumerate+bitmask+duration&hostgroup={0}&hoststatus={1}'.format(hostgroup,filterv)
  Get_Host_UP_DOWN_URL='http://'+monitorurl+'/nagios/cgi-bin/statusjson.cgi?query=hostlist&formatoptions=whitespace+enumerate+bitmask+duration&hostgroup={0}&hoststatus={1}'.format(hostgroup,filterv)
  Get_Host_Updown_Data = requests.get(Get_Host_UP_DOWN_URL,auth=HTTPBasicAuth(username, 'nagiosadmin'))
  Get_Host_Count_Data = requests.get(Get_Host_Data_URL,auth=HTTPBasicAuth(username, 'nagiosadmin'))
  Output = json.loads(Get_Host_Count_Data.text)
  Host_UP = json.loads(Get_Host_Updown_Data.text)
  Last_Data_Update = int(Output['result']['last_data_update']) / 1000
  Last_Data_Update = time.strftime('%H:%M', time.localtime(Last_Data_Update))
  HOSTS = list(Host_UP['data']['hostlist'])
  host_data['host_details'] = {}
  for ci in HOSTS:
    update_data = {ci: {}}
    host_data['host_details'].update(update_data)
    up_down = Host_UP['data']['hostlist'][ci]
    if "down" in up_down:
      status = "critical"
    else:
      status = "up"
    HostData = Output['data']['servicelist'].keys()
    if ci in Output['data']['servicelist']:
      service_count = len(Output['data']['servicelist'][ci])
      print(service_count)
      service_status = list(Output['data']['servicelist'][ci].values())
      if "critical" in service_status:
        status = "critical"
      elif "warning" in service_status:
        status = "warning"
      elif "pending" in service_status:
        status = "pending"
      elif "unknown" in service_status:
        status = "unknown"
      else:
        status = "ok"
    else:
      service_count = 0
    update_data = {'status': status, 'service_count': service_count, 'last_data_update': Last_Data_Update}
    host_data['host_details'][ci].update(update_data)
  return(json.dumps(host_data))

@monitoring_api.route('/monitoring/api/v1/getChart/<host>/<service>', methods=['GET'])
def get_monitoring_chart(host, service):
  data = request.get_json()
  username = data['username']
  headers = {'Accept': 'image/png'}
  Get_Chart = requests.get('http://'+monitorurl+'/nagios/cgi-bin/histogram.cgi?createimage&t1=1562742217&t2=1565420617&host={0}&service={1}&breakdown=dayofmonth&assumestateretention=yes&initialstateslogged=no&newstatesonly=no&graphevents=120&graphstatetypes=3'.format(host,service), auth=HTTPBasicAuth(username, 'nagiosadmin'), stream=True)
  with open('/tmp/image.png', 'wb') as out_file:
    shutil.copyfileobj(Get_Chart.raw, out_file)
  with open('/tmp/image.png', 'rb') as imageFile:
    string = base64.b64encode(imageFile.read())
  os.remove('/tmp/image.png')
  return(string)

def register(js):
    meta_json = json.dumps({
      'hostgroup': js['hostgroup'],
      'host': js['host'],
      'start_date': time.strftime('%d-%m-%Y', time.localtime(js['starttime'])), # %H:%M:%S
      'end_date': time.strftime('%d-%m-%Y', time.localtime(js['endtime'])), # %H:%M:%S
      'comment': js['comment']
    })
    sQuery = "insert into availability_reports(fk_user_id, generated_time, status, meta) values({0}, now(), {1}, '{2}') RETURNING pk_avail_rpt_id".format(js['auto_userid'], 0, meta_json)
    dRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sQuery)
    if dRet["result"] == "success":
        return dRet["data"][0]["pk_avail_rpt_id"]
    else:
        return 0

@monitoring_api.route('/monitoring/api/v1/reports/availability/custom', methods=['POST'])
def CustomAvailability():
  data =request.get_json()
  username = data['username']
  hostgroup = data['hostgroup']
  host = data['host']
  start_date = data['startdate']
  end_date = data['enddate']
  comment = data['comment']
  auto_user = data['auto_userid']
  named_tuple = time.localtime()
  starttime_string = time.strftime(start_date + " 00:00:00")
  endtime_string = time.strftime(end_date + " 23:59:59")
  starttime = calendar.timegm(time.strptime(starttime_string, '%d-%m-%Y %H:%M:%S'))
  endtime = calendar.timegm(time.strptime(endtime_string, '%d-%m-%Y %H:%M:%S'))
  totaltime = endtime - starttime

  worker_data = {'monitorurl': monitorurl, 'username': username, 'auto_userid': auto_user, 'hostgroup': hostgroup, 'comment': comment, 'starttime': starttime, 'endtime': endtime, 'totaltime': totaltime, 'host': host}
  pk_avail_id = register(worker_data)
  worker_data['pk_avail_id'] = pk_avail_id
  dRet = connmq.send2MQ(pQueue='availability', pExchange='reports', pRoutingKey='availability', pData=json.dumps(worker_data))
  return logAndRet("success", "Availability Report generation initiated...")

@monitoring_api.route('/monitoring/api/v1/reports/availability/grid/<auto_userid>', methods=['GET'])
def getGeneratedReport(auto_userid):
  try:
    sQuery = "select meta, data, to_char(generated_time, 'DD/MM/YYYY HH24:MI:SS') datetime, status from availability_reports where fk_user_id={0} order by pk_avail_rpt_id desc limit 10".format(auto_userid)
    sRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
    if sRet["result"] == "success":
      return json.dumps(sRet)
    elif sRet["result"] == "failure":
      return json.dumps({"result": "failure", "data": "no data"})
  except Exception as e:
    return logAndRet("failure", "Failed to load grid")


@monitoring_api.route('/monitoring/api/v1/reports/availability/thismonth', methods=['POST'])
def ThisMonth():
  data =request.get_json()
  username = data['username']
  hostgroup = data['hostgroup']
  host = data['host']
  comment = data['comment']
  auto_user = data['auto_userid']
  named_tuple = time.localtime()
  starttime_string = time.strftime("01-%m-%Y 00:00:00")
  endtime_string = time.strftime("%d-%m-%Y 23:59:59")
  starttime = calendar.timegm(time.strptime(starttime_string, '%d-%m-%Y %H:%M:%S'))
  endtime = calendar.timegm(time.strptime(endtime_string, '%d-%m-%Y %H:%M:%S'))
  totaltime = endtime - starttime

  worker_data = {'monitorurl': monitorurl, 'username': username, 'auto_userid': auto_user, 'hostgroup': hostgroup, 'comment': comment, 'starttime': starttime, 'endtime': endtime, 'totaltime': totaltime, 'host': host}
  pk_avail_id = register(worker_data)
  worker_data['pk_avail_id'] = pk_avail_id
  dRet = connmq.send2MQ(pQueue='availability', pExchange='reports', pRoutingKey='availability', pData=json.dumps(worker_data))
  return logAndRet("success", "Availability Report generation initiated...")


@monitoring_api.route('/monitoring/api/v1/reports/availability/last24', methods=['POST'])
def Last24Hours():
  data =request.get_json()
  username = data['username']
  hostgroup = data['hostgroup']
  host = data['host']
  comment = data['comment']
  auto_user = data['auto_userid']
  endtime_string = time.strftime("%d-%m-%Y %H:%M:%S")
  starttime_string = datetime.today() - timedelta(days=1)
  starttime_string = starttime_string.strftime("%d-%m-%Y %H:%M:%S")
  endtime = calendar.timegm(time.strptime(endtime_string, '%d-%m-%Y %H:%M:%S'))
  starttime = calendar.timegm(time.strptime(starttime_string, '%d-%m-%Y %H:%M:%S'))
  totaltime = endtime - starttime

  worker_data = {'monitorurl': monitorurl, 'username': username, 'auto_userid': auto_user, 'hostgroup': hostgroup, 'comment': comment, 'starttime': starttime, 'endtime': endtime, 'totaltime': totaltime, 'host': host}
  pk_avail_id = register(worker_data)
  worker_data['pk_avail_id'] = pk_avail_id
  dRet = connmq.send2MQ(pQueue='availability', pExchange='reports', pRoutingKey='availability', pData=json.dumps(worker_data))
  return logAndRet("success", "Availability Report generation initiated...")


@monitoring_api.route('/monitoring/api/v1/reports/availability/last31', methods=['POST'])
def Last31Days():
  data =request.get_json()
  username = data['username']
  hostgroup = data['hostgroup']
  host = data['host']
  comment = data['comment']
  auto_user = data['auto_userid']
  endtime_string = time.strftime("%d-%m-%Y %H:%M:%S")
  starttime_string = datetime.today() - timedelta(days=31)
  starttime_string = starttime_string.strftime("%d-%m-%Y %H:%M:%S")
  endtime = calendar.timegm(time.strptime(endtime_string, '%d-%m-%Y %H:%M:%S'))
  starttime = calendar.timegm(time.strptime(starttime_string, '%d-%m-%Y %H:%M:%S'))
  totaltime = endtime - starttime

  worker_data = {'monitorurl': monitorurl, 'username': username, 'auto_userid': auto_user, 'hostgroup': hostgroup, 'comment': comment, 'starttime': starttime, 'endtime': endtime, 'totaltime': totaltime, 'host': host}
  pk_avail_id = register(worker_data)
  worker_data['pk_avail_id'] = pk_avail_id
  dRet = connmq.send2MQ(pQueue='availability', pExchange='reports', pRoutingKey='availability', pData=json.dumps(worker_data))
  return logAndRet("success", "Availability Report generation initiated...")


@monitoring_api.route('/monitoring/api/v1/reports/availability/thisyear', methods=['POST'])
def ThisYear():
  data =request.get_json()
  username = data['username']
  hostgroup = data['hostgroup']
  host = data['host']
  comment = data['comment']
  auto_user = data['auto_userid']
  named_tuple = time.localtime()
  starttime_string = time.strftime("01-01-%Y 00:00:00")
  endtime_string = time.strftime("%d-%m-%Y 23:59:59")
  starttime = calendar.timegm(time.strptime(starttime_string, '%d-%m-%Y %H:%M:%S'))
  endtime = calendar.timegm(time.strptime(endtime_string, '%d-%m-%Y %H:%M:%S'))
  totaltime = endtime - starttime

  worker_data = {'monitorurl': monitorurl, 'username': username, 'auto_userid': auto_user, 'hostgroup': hostgroup, 'comment': comment, 'starttime': starttime, 'endtime': endtime, 'totaltime': totaltime, 'host': host}
  pk_avail_id = register(worker_data)
  worker_data['pk_avail_id'] = pk_avail_id
  dRet = connmq.send2MQ(pQueue='availability', pExchange='reports', pRoutingKey='availability', pData=json.dumps(worker_data))
  return logAndRet("success", "Availability Report generation initiated...")


@monitoring_api.route('/monitoring/api/v1/reports/availability/last7', methods=['POST'])
def Last7Days():
  data =request.get_json()
  username = data['username']
  hostgroup = data['hostgroup']
  host = data['host']
  comment = data['comment']
  auto_user = data['auto_userid']
  endtime_string = time.strftime("%d-%m-%Y %H:%M:%S")
  starttime_string = datetime.today() - timedelta(days=7)
  starttime_string = starttime_string.strftime("%d-%m-%Y %H:%M:%S")
  endtime = calendar.timegm(time.strptime(endtime_string, '%d-%m-%Y %H:%M:%S'))
  starttime = calendar.timegm(time.strptime(starttime_string, '%d-%m-%Y %H:%M:%S'))
  totaltime = endtime - starttime

  worker_data = {'monitorurl': monitorurl, 'username': username, 'auto_userid': auto_user, 'hostgroup': hostgroup, 'comment': comment, 'starttime': starttime, 'endtime': endtime, 'totaltime': totaltime, 'host': host}
  pk_avail_id = register(worker_data)
  worker_data['pk_avail_id'] = pk_avail_id
  dRet = connmq.send2MQ(pQueue='availability', pExchange='reports', pRoutingKey='availability', pData=json.dumps(worker_data))
  return logAndRet("success", "Availability Report generation initiated...")


@monitoring_api.route('/monitoring/api/v1/reports/masters', methods=['GET'])
def report_masters():
  data = {'report_period': ['Today', 'Last 24 Hours', 'Last 7 Days', 'This Month', 'Last 31 Days', 'This Year', 'Custom Period']}
  return json.dumps(data)

@monitoring_api.route('/monitoring/api/v1/reports/availability/Today', methods=['POST'])
def Today():
  data =request.get_json()
  username = data['username']
  hostgroup = data['hostgroup']
  host = data['host']
  comment = data['comment']
  auto_user = data['auto_userid']
  named_tuple = time.localtime()
  starttime_string = time.strftime("%d-%m-%Y 00:00:00")
  endtime_string = time.strftime("%d-%m-%Y 23:59:59")
  starttime = calendar.timegm(time.strptime(starttime_string, '%d-%m-%Y %H:%M:%S'))
  endtime = calendar.timegm(time.strptime(endtime_string, '%d-%m-%Y %H:%M:%S'))
  totaltime = endtime - starttime

  worker_data = {'monitorurl': monitorurl, 'username': username, 'auto_userid': auto_user, 'hostgroup': hostgroup, 'comment': comment, 'starttime': starttime, 'endtime': endtime, 'totaltime': totaltime, 'host': host}
  pk_avail_id = register(worker_data)
  worker_data['pk_avail_id'] = pk_avail_id
  dRet = connmq.send2MQ(pQueue='availability', pExchange='reports', pRoutingKey='availability', pData=json.dumps(worker_data))
  return logAndRet("success", "Availability Report generation initiated...")


@monitoring_api.route('/monitoring/api/v1/configuration/linux', methods=['POST'])
def Linux_config():
   data = request.get_json()
   monitoringdata = data["monitoring_data"]

   j2_env = Environment(loader=FileSystemLoader('templates'),
                        trim_blocks=True)
   template = j2_env.get_template('Centos.j2')
   if 'Ping' in monitoringdata:
     Ping=monitoringdata['Ping']

   if 'Load' in monitoringdata:
     Load=monitoringdata['Load']

   if 'Memory' in monitoringdata:
     Memory=monitoringdata['Memory']

   if 'Disk_Usage' in monitoringdata:
     DiskUsage = monitoringdata['Disk_Usage']

   if 'Yum' in monitoringdata:
     Yum=monitoringdata['Yum']

   if 'Swap' in monitoringdata:
     Swap=monitoringdata['Swap']

   if 'Open_Files' in monitoringdata:
     OpenFiles = monitoringdata['Open_Files']

   if 'Users' in monitoringdata:
     Users = monitoringdata['Users']

   if 'Total_Processes' in monitoringdata:
     TotalProcesses = monitoringdata['Total_Processes']

   if 'Processes' in monitoringdata:
     Processes=monitoringdata['Processes']

   if 'Services' in monitoringdata:
     Services=monitoringdata['Services']


   rendered_output = template.render(hostname=monitoringdata['Hostname'], ipaddress=monitoringdata['IPAddress'], Ping=Ping, Yum=Yum, Load=Load, Memory=Memory, Swap=Swap, OpenFiles=OpenFiles, TotalProcesses=TotalProcesses, DiskUsage=DiskUsage, Processes=Processes, Users=Users)

   #print(rendered_output)
   with open('/usr/local/nagios/etc/objects/Servers/'+monitoringdata['Hostname']+'.cfg','w') as f:
     f.write(rendered_output)
   return "success"


@monitoring_api.route('/monitoring/api/v1/configuration/windows', methods=['POST'])
def Windows_config():
   data = request.get_json()
   monitoringdata = data["monitoring_data"]
   j2_env = Environment(loader=FileSystemLoader('templates'),
                        trim_blocks=True)
   template = j2_env.get_template('windows.j2')

   if 'Ping' in monitoringdata:
     Ping=monitoringdata['Ping']

   if 'Load' in monitoringdata:
     Load=monitoringdata['Load']

   if 'Memory' in monitoringdata:
     Memory=monitoringdata['Memory']

   if 'Disk_Usage' in monitoringdata:
     DiskUsage = monitoringdata['Disk_Usage']

   if 'Processes' in monitoringdata:
     Processes=monitoringdata['Processes']

   if 'Services' in monitoringdata:
     Services=monitoringdata['Services']

   if 'Uptime' in monitoringdata:
     Uptime=monitoringdata['Uptime']

   rendered_output = template.render(hostname=monitoringdata['Hostname'], ipaddress=monitoringdata['IPAddress'], Ping=Ping, uptime=Uptime, Load=Load, Memory=Memory, Disk=DiskUsage, Processes=Processes, Services=Services)
   #print(rendered_output)
   with open('/usr/local/nagios/etc/objects/Servers/'+monitoringdata['Hostname']+'.cfg','w') as f:
     f.write(rendered_output)
   return "Sucess"


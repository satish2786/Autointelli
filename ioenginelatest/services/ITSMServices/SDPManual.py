import sys, os, paramiko, pika, json, logging, psycopg2
from logging.handlers import TimedRotatingFileHandler
import requests
import datetime
import urllib
from services.utils.decoder import decode
from flask import Blueprint, jsonify, request


itsmsdp_api = Blueprint('itsmsdp_api', __name__)

# Reading the configuration file for db connection string
conn = ""
data = json.load(open('/etc/autointelli/autointelli.conf'))
if not os.path.isfile('/etc/autointelli/autointelli.conf'):
  print(" [x] Worker Cannot Start, Config not found")
  sys.exit(1)
dbuser = data['maindb']['username']
dbname = data['maindb']['dbname']
dbhost = data['maindb']['dbip']
dbport = data['maindb']['dbport']

# Decoding the Password
maindbpassword = decode('auto!ntell!',data['maindb']['password'])

# Adding the Logging Configurations
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
handler = TimedRotatingFileHandler('logs/SDP.log', when='midnight', interval=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Get MQ Connections
conn = psycopg2.connect(database=dbname, user=dbuser, password=maindbpassword, host=dbhost, port=dbport)
conn.autocommit = True
cur = conn.cursor()
cur.execute('select configip,configport,dbname,username,password from configuration where configname=\'MQ\'')
esbdata = cur.fetchall()
esbdata = esbdata[0]
esbip = esbdata[0]
esbuser = esbdata[3]
esbpass = esbdata[4]
vhost = esbdata[2]
esbpass = decode('auto!ntell!',esbpass)

# Get Connection details
conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
cur = conn.cursor()
cur.execute('select communication_type, ip, port, technician_key, priority, assignment_group_manual, assignment_group_automation, itsm_status, service_category, level, requester, requesttemplate, technician, itsm_wip_status, itsm_res_status from admin_sdp where status=\'{0}\''.format("Enabled"))
connectiondata = cur.fetchall()
connectiondata = connectiondata[0]
communication_type = connectiondata[0]
ip = connectiondata[1]
port = connectiondata[2]
techkey = connectiondata[3]
priority = connectiondata[4]
manualgrp = connectiondata[5]
autogrp = connectiondata[6]
itsm_status = connectiondata[7]
service_category = connectiondata[8]
level = connectiondata[9]
requester = connectiondata[10]
requesttemplate = connectiondata[11]
technician = connectiondata[12]
itsm_wip_status = connectiondata[13]
itsm_res_status = connectiondata[14]

@itsmsdp_api.route('/admin/api/v2/itsm/sdp/createTicket', methods=['POST'])
def sdp_createTicket():
  try:
    data = request.get_json()
    if data['subject'] == '' or data['description'] == '' or data['group'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})

    group = data['group']
    subject = data['subject']
    description = data['description']


    logger.info("Creating Ticket")
    if group == 'automation':
      group = autogrp
    else:
      group = manualgrp

    payload = {'TECHNICIAN_KEY': techkey, 'OPERATION_NAME': 'ADD_REQUEST', 'format': 'json', 'INPUT_DATA': '{"operation": {"details": { "requester": '+"\""+requester+"\""', "subject": '+"\""+subject+"\""', "description": '+"\""+description+"\""', "requesttemplate": '+"\""+requesttemplate+"\""', "priority": '+"\""+priority+"\""', "site": "New York", "group": '+"\""+group+"\""',"technician": '+"\""+technician+"\""',"level": '+"\""+level+"\""', "status": '+"\""+itsm_status+"\""', "service": '+"\""+service_category+"\""' } } } '}
    r = requests.post("{0}://{1}:{2}/sdpapi/request/".format(communication_type, ip, port), params=payload)
    if r.status_code != 200:
      logger.error("Error in Creating Ticket")
      return jsonify({"Message": "Error Creating Ticket", "Status": False})
    else:
      logger.info("Ticket Created")
      output = json.loads(r.text)
      return jsonify({"TID": output['operation']['Details']['WORKORDERID'], "Status": True})
  except Exception as e:
      return jsonify({"Message": "Error Creating Ticket"+str(e), "Status": False})


@itsmsdp_api.route('/admin/api/v2/itsm/sdp/moveTicket', methods=['POST'])
def sdp_moveTicket():
  try:
    data = request.get_json()
    if data['TID'] == '' or data['group'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    logger.info("Changing the Group")
    TID = data['TID']
    group = data['group']
    if group == 'manual':
      group = manualgrp
    else:
      group = autogrp
    headers = {'Content-Type': 'application/json', 'TECHNICIAN_KEY': techkey}
    payload = {'input_data': '{"request":{"group":{"name":%s},"technician":{"name":%s}}}'%(group, technician)}
    r = requests.put("""{0}://{1}:{2}/api/v3/requests/{3}/assign?TECHNICIAN_KEY={4}""".format(communication_type, ip, port,TID,techkey), headers=headers, params=(payload))
    if r.status_code == 200:
      return jsonify({"Message": "Ticket Moved Successfully", "Status": True})
    else:
      return jsonify({"Message": "Error Moving Ticket"+r.text, "Status": False})
  except Exception as e:
    return jsonify({"Message": "Error Moving Ticket"+str(e), "Status": False})


@itsmsdp_api.route('/admin/api/v2/itsm/sdp/updateWorklog', methods=['POST'])
def sdp_updateWorklog():
  try:
    data = request.get_json()
    if data['TID'] == '' or data['description'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    TID = data['TID']
    description = data['description']
    now = datetime.datetime.now()
    starttime = now.strftime("%d %b %Y, %H:%M:%S")
    endtime = now + datetime.timedelta(seconds=3)
    endtime = endtime.strftime("%d %b %Y, %H:%M:%S")
    payload = {'TECHNICIAN_KEY': techkey, 'OPERATION_NAME': 'ADD_WORKLOG', 'format': 'json', 'INPUT_DATA': '{ "operation": { "details": {"worklogs": { "worklog": { "description": '+"\""+description+"\""',"technician": '+"\""+technician+"\""',"starttime": '+"\""+starttime+"\""',"endtime": '+"\""+endtime+"\""' } } } } }'}
    r = requests.post("{0}://{1}:{2}/sdpapi/request/{3}/worklogs".format(communication_type, ip, port, TID), params=payload)
    if r.status_code != 200:
      return jsonify({"Message": "Error updating worklog", "Status": False})
    else:
      return jsonify({"Message": "Worklog updated Successfully"+r.text, "Status": True})
  except Exception as e:
    return jsonify({"Message": "Error updating Worklog", "Status": False})



@itsmsdp_api.route('/admin/api/v2/itsm/sdp/changeResolvedStatus', methods=['POST'])
def changeStatusRES():
  try:
    data = request.get_json()
    if data['TID'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    TID = data['TID']
    payload = {'TECHNICIAN_KEY': techkey, 'OPERATION_NAME': 'EDIT_REQUEST', 'format': 'json', 'INPUT_DATA': '{"operation": {"details": { "status": '+"\""+itsm_res_status+"\""' } } } '}
    r = requests.post("{0}://{1}:{2}/sdpapi/request/{3}".format(communication_type, ip, port, str(TID)), params=payload)
    if r.status_code != 200:
      logger.error("Error in Changing Resolved Status")
      return jsonify({"Message": "Error updating status", "Status": False})
    else:
      return jsonify({"Message": "Status changed to resolved", "Status": True})
  except Exception as e:
    return jsonify({"Message": "Error changing status to resolved", "Status": False})


@itsmsdp_api.route('/admin/api/v2/itsm/sdp/changeWIPStatus', methods=['POST'])
def changeStatusWIP():
  try:
    logger.info("Changing the Status")
    data = request.get_json()
    if data['TID'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    TID = data['TID']
    payload = {'TECHNICIAN_KEY': techkey, 'OPERATION_NAME': 'EDIT_REQUEST', 'format': 'json', 'INPUT_DATA': '{"operation": {"details": { "status": '+"\""+itsm_wip_status+"\""' } } } '}
    r = requests.post("{0}://{1}:{2}/sdpapi/request/{3}".format(communication_type, ip, port, str(TID)), params=payload)
    if r.status_code != 200:
      return jsonify({"Message": "Error updating status", "Status": False})
    else:
      return jsonify({"Message": "Status changed to In Progress", "Status": True})
  except Exception as e:
    return jsonify({"Message": "Error updating Status", "Status": False})


@itsmsdp_api.route('/admin/api/v2/itsm/sdp/addResolution', methods=['POST'])
def addResolution():
  try:
    data = request.get_json()
    if data['TID'] == '' or data['comment'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})

    TID = data['TID']
    comment = data['comment']
    #comment = decode('auto!ntell!', comment)
    comment = comment.replace("\n","")
    payload = {'TECHNICIAN_KEY': techkey, 'OPERATION_NAME': 'ADD_RESOLUTION', 'format': 'json', 'INPUT_DATA': '{"operation": {"details": {"resolution": {"resolutiontext": '+"\""+comment+"\""'}}}}'}
    payload = urllib.parse.urlencode(payload)
    logger.info(payload)
    r = requests.post("{0}://{1}:{2}/sdpapi/request/{3}/resolution".format(communication_type, ip, port, TID), params=payload)
    if r.status_code != 200:
      return jsonify({"Message": "Error updating Resolution", "Status": False})
    else:
      output = json.loads(r.text)
      return jsonify({"Message": "Resolution added to ticket", "Status": True})
  except Exception as e:
    return jsonify({"Message": "Error updating resolution"+str(e), "Status": False})

#!/usr/bin/env python
import sys
import json
import logging
import psycopg2
from services.utils.decoder import decode
from flask import Blueprint, jsonify, request
from logging.handlers import TimedRotatingFileHandler
import os
import requests


itsm_api = Blueprint('itsm_api', __name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])

@itsm_api.route('/admin/api/v2/ticketAutomation', methods=['GET'])
def ticket_automation():
  try:
  #   DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('select automated from ai_ticket_creation_method');
    automated = cur.fetchone()
    automated = automated[0]
    return jsonify({"automated": automated, "Status": True})
  except Exception as e:
    return jsonify({"Message": "Error Processing Request", "Status": False})


@itsm_api.route('/admin/api/v2/ticketAutomation/<automated>', methods=['POST'])
def ticket_automation_add(automated):
  try:
    if automated == '' or ( automated != 'Y' and automated != 'N' ):
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('update ai_ticket_creation_method set automated=\'{0}\''.format(automated))
    return jsonify({"Message": "Details Updated", "Status": False})
  except Exception as e:
    return jsonify({"Message": "Error Processing Request", "Status": False})


@itsm_api.route('/admin/api/v2/getEnabledITSM', methods=['GET'])
def getEnabledITSM():
  try:
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('select integration_name from admin_integration_meta where integration_type=\'itsm\' and status=\'Enabled\'')
    itsm = cur.fetchone()
    itsm = itsm[0]
    return jsonify({"itsm": itsm, "Status": "Success"})
  except Exception as e:
    return jsonify({"Message": "Error Processing Request", "Status": "Error {0}".format(str(e))})


## Function to CreateTicket in ITSM
@itsm_api.route('/admin/api/v2/itsm/createTicket', methods=['POST'])
def createitsmTicket():
  try:
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('select integration_name from admin_integration_meta where integration_type=\'itsm\' and status=\'Enabled\'');
    itsm = cur.fetchone()
    itsm = itsm[0]
    data = request.get_json()
    if data['subject'] == '' or data['description'] == '' or data['group'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    description = data['subject']
    notes = data['description']
    group = data['group']
    if 'customer_id' in data:
      customerid = data['customerid']
    headers = {'Content-Type': 'Application/json'}
    payload = {'subject': description, 'description': notes, 'group': group}
    print(itsm)
    if itsm == 'sdp':
      r = requests.post("http://localhost:3890/admin/api/v2/itsm/sdp/createTicket", headers=headers, data=json.dumps(payload))
      if r.status_code != 200:
        return r.text
      else:
        return r.text
    elif itsm == 'otrs':
      print("Came inside OTRS")
      from services.ITSMServices import otrs
      output = otrs.CreateTicket(description, notes, group)
      return output
    elif itsm == 'freshdesk':
      print('came inside freshdesk')
      from services.ITSMServices import FreshWorksTktMgmt as fapi
      dPayload = {"subject": description, "description": notes, "type": "incident"}
      output = fapi.FDCreateTicket(dPayload)
      return jsonify(output)
    elif itsm == 'nxtgen':
      print('came inside nxtgen itsm')
      from services.ITSMServices import NxtGenTktMgmtAutomatic as napi
      dPayload = {"subject": description, "description": notes, "type": "vmware", "customerid": customerid}
      output = napi.NxtGenCreateTicket(dPayload)
      return jsonify(output)
    else:
      return jsonify({"Message": "No ITSM Integrations Found", "Status": False})
  except Exception as e:
    return jsonify({"Message": "Internal Server Error {0}".format(str(e)), "Status": False})

## Function to CreateTicket in ITSM
@itsm_api.route('/admin/api/v2/itsm/moveTicket', methods=['POST'])
def moveitsmTicket():
  try:
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('select integration_name from admin_integration_meta where integration_type=\'itsm\' and status=\'Enabled\'');
    itsm = cur.fetchone()
    itsm = itsm[0]
    data = request.get_json()
    if data['TID'] == '' or data['group'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    TID = data['TID']
    group = data['group']
    headers = {'Content-Type': 'Application/json'}
    payload = {'TID': TID, 'group': group}
    if itsm == 'sdp':
      r = requests.post("http://localhost:3890/admin/api/v2/itsm/sdp/moveTicket", headers=headers, data=json.dumps(payload))
      if r.status_code != 200:
        return r.text
      else:
        return r.text
    elif itsm == 'freshdesk':
      print('came inside freshdesk')
      from services.ITSMServices import FreshWorksTktMgmt as fapi
      dPayload = {"ticket_id": TID, "group": group}
      output = fapi.FDMoveTicket(dPayload)
      return jsonify(output)
    else:
      return jsonify({"Message": "No ITSM Integrations Found", "Status": False})
  except Exception as e:
    return jsonify({"Message": "Internal Server Error {0}".format(str(e)), "Status": False})


## Function to CreateTicket in ITSM
@itsm_api.route('/admin/api/v2/itsm/updateWorklog', methods=['POST'])
def updateWorklog():
  try:
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('select integration_name from admin_integration_meta where integration_type=\'itsm\' and status=\'Enabled\'');
    itsm = cur.fetchone()
    itsm = itsm[0]
    data = request.get_json()
    if data['TID'] == '' or data['description'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    TID = data['TID']
    description = data['description']
    headers = {'Content-Type': 'Application/json'}
    payload = {'TID': TID, 'description': description}
    if itsm == 'sdp':
      r = requests.post("http://localhost:3890/admin/api/v2/itsm/sdp/updateWorklog", headers=headers, data=json.dumps(payload))
      if r.status_code != 200:
        return r.text
      else:
        return r.text
    elif itsm == 'freshdesk':
      print('came inside freshdesk')
      from services.ITSMServices import FreshWorksTktMgmt as fapi
      dPayload = {"ticket_id": TID, "description": description}
      output = fapi.FDUpdateWorkLog(dPayload)
      return jsonify(output)
    elif itsm == 'nxtgen':
      print('came inside nxtgen itsm ')
      from services.ITSMServices import NxtGenTktMgmtAutomatic as napi
      dPayload = {"ticket_id": TID, "description": description}
      output = napi.NxtGenUpdateWorkLog(dPayload)
      return jsonify(output)
    else:
      return jsonify({"Message": "No ITSM Integrations Found", "Status": False})
  except Exception as e:
    return jsonify({"Message": "Internal Server Error {0}".format(str(e)), "Status": False})


@itsm_api.route('/admin/api/v2/itsm/changeWIPStatus', methods=['POST'])
def changeWIPStatus():
  try:
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('select integration_name from admin_integration_meta where integration_type=\'itsm\' and status=\'Enabled\'');
    itsm = cur.fetchone()
    itsm = itsm[0]
    data = request.get_json()
    if data['TID'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    TID = data['TID']
    if "REFTICKETID" in data:
      REFTICKETID = data['REFTICKETID']
    headers = {'Content-Type': 'Application/json'}
    payload = {'TID': TID}
    if itsm == 'sdp':
      r = requests.post("http://localhost:3890/admin/api/v2/itsm/sdp/changeWIPStatus", headers=headers, data=json.dumps(payload))
      if r.status_code != 200:
        return r.text
      else:
        return r.text
    elif itsm == 'otrs':
      from services.ITSMServices import otrs
      output = otrs.UpdateState(REFTICKETID, 'In Progress')
      return output
    elif itsm == 'freshdesk':
      print('came inside freshdesk')
      from services.ITSMServices import FreshWorksTktMgmt as fapi
      dPayload = {"ticket_id": TID, "status": 2}
      output = fapi.FDUpdateTicket(dPayload)
      return jsonify(output)
    else:
      return jsonify({"Message": "No ITSM Integrations Found", "Status": False})
  except Exception as e:
    return jsonify({"Message": "Internal Server Error {0}".format(str(e)), "Status": False})


@itsm_api.route('/admin/api/v2/itsm/changeResolvedStatus', methods=['POST'])
def changeResolvedStatus():
  try:
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('select integration_name from admin_integration_meta where integration_type=\'itsm\' and status=\'Enabled\'');
    itsm = cur.fetchone()
    itsm = itsm[0]
    data = request.get_json()
    if data['TID'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    TID = data['TID']
    if "REFTICKETID" in data:
      REFTICKETID = data['REFTICKETID']
    headers = {'Content-Type': 'Application/json'}
    payload = {'TID': TID}
    if itsm == 'sdp':
      r = requests.post("http://localhost:3890/admin/api/v2/itsm/sdp/changeResolvedStatus", headers=headers, data=json.dumps(payload))
      if r.status_code != 200:
        return r.text
      else:
        return r.text
    elif itsm == 'otrs':
      from services.ITSMServices import otrs
      output = otrs.UpdateState(REFTICKETID, 'Resolved')
      return output
    elif itsm == 'freshdesk':
      print('came inside freshdesk')
      from services.ITSMServices import FreshWorksTktMgmt as fapi
      dPayload = {"ticket_id": TID, "status": 3}
      output = fapi.FDUpdateTicket(dPayload)
      return jsonify(output)
    else:
      return jsonify({"Message": "No ITSM Integrations Found", "Status": False})
  except Exception as e:
    return jsonify({"Message": "Internal Server Error {0}".format(str(e)), "Status": False})


@itsm_api.route('/admin/api/v2/itsm/addResolution', methods=['POST'])
def addResolutionTicket():
  try:
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('select integration_name from admin_integration_meta where integration_type=\'itsm\' and status=\'Enabled\'');
    itsm = cur.fetchone()
    itsm = itsm[0]
    data = request.get_json()
    if data['TID'] == '' or data['comment'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": False})
    TID = data['TID']
    if "REFTICKETID" in data:
      REFTICKETID = data['REFTICKETID']
    comment = data['comment']
    headers = {'Content-Type': 'Application/json'}
    payload = {'TID': TID, 'comment': comment}
    if itsm == 'sdp':
      r = requests.post("http://localhost:3890/admin/api/v2/itsm/sdp/addResolution", headers=headers, data=json.dumps(payload))
      if r.status_code != 200:
        return r.text
      else:
        return r.text
    elif itsm == 'otrs':
      from services.ITSMServices import otrs
      output = otrs.AddWorklog(REFTICKETID, "Ticket Resolved Successfully by OTRS")
      return output
    elif itsm == 'freshdesk':
      print('came inside freshdesk')
      from services.ITSMServices import FreshWorksTktMgmt as fapi
      dPayload = {"ticket_id": TID, "description": comment}
      output = fapi.FDUpdateWorkLog(dPayload)
      return jsonify(output)
    else:
      return jsonify({"Message": "No ITSM Integrations Found", "Status": False})
  except Exception as e:
    return jsonify({"Message": "Internal Server Error {0}".format(str(e)), "Status": False})


#@sdp_api.route('/itsm/admin/sdp/enable', methods=['POST'])
#def enable_row_sdp():
#  try:
#    data = request.get_json()
#    if data['id'] == '':
#      return jsonify({"Message": "Invalid Arguments detected", "Status": "Failure"})
#    #DB Connection String
#    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
#    cur = conn.cursor()
#    cur.execute("""select count(*) from admin_integration_meta where integration_type='itsm' and status='{0}'""".format('Enabled'))
#    count = cur.fetchall()
#    count = count[0]
#    countid = count[0]
#    if countid >= 1:
#      return jsonify({"Message": "ITSM Integration already exist, Please disable and try again", "Status": "Error"})
#    cur.execute("""update admin_sdp set status='Enabled' where itsm_id={0} """.format(data['id']))
#    cur.execute("""update admin_integration_meta set status='Enabled' where integration_name='{0}' """.format('sdp'))
#    conn.commit()
#    return jsonify({"Message": "SDP Integration Enabled", "Status": "Succes"})
#  except Exception as e:
#    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})
#
#
#@sdp_api.route('/itsm/admin/sdp/disable', methods=['POST'])
#def disable_row_sdp():
#  try:
#    data = request.get_json()
#    #DB Connection String
#    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
#    cur = conn.cursor()
#    cur.execute("""update admin_sdp set status='Disabled' where itsm_id={0} """.format(data['id']))
#    cur.execute("""update admin_integration_meta set status='Disabled' where integration_name='sdp' """)
#    conn.commit()
#    return jsonify({"Message": "SDP Integration Disabled", "Status": "Succes"})
#  except Exception as e:
#    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})

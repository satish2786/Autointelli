#!/usr/bin/env python

import json
import psycopg2
from services.utils.decoder import decode
from flask import Blueprint, jsonify, request

sdp_api = Blueprint('sdp_api', __name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])


@sdp_api.route('/itsm/admin/sdp/add', methods=['POST'])
def add_data():
  try:
    RequestID = "xxxx-ITSM-ADD-xxxx"
    data = request.get_json()
    print(data)
    if  data['communication_type'] == '' or data['ip'] == '' or data['port'] == '' or data['technician_key'] == '' or data['priority'] == '' or data['assignment_group_manual'] == '' or data['assignment_group_automation'] == '' or data['itsm_status'] == '' or data['service_category'] == '' or data['level'] == '' or data['created_by'] == '' or data['requester'] == '' or data['requesttemplate'] == '' or data['technician'] == '' or data['itsm_wip_status'] == '' or data['itsm_res_status'] == '':
      return jsonify({"Message": "Invalid Arguments Detected", "Status": "Error"})
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""insert into admin_sdp(communication_type,ip,port,technician_key,priority,assignment_group_automation,assignment_group_manual,itsm_status,service_category,level, status, createdby, requester, requesttemplate, technician, itsm_wip_status, itsm_res_status) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','Disabled','{10}', '{11}', '{12}', '{13}', '{14}', '{15}')""".format(data['communication_type'],data['ip'],data['port'],data['technician_key'],data['priority'],data['assignment_group_automation'],data['assignment_group_manual'],data['itsm_status'],data['service_category'],data['level'],data['created_by'], data['requester'], data['requesttemplate'], data['technician'], data['itsm_wip_status'], data['itsm_res_status']))
    cur.execute("""insert into admin_integration_meta(integration_name, integration_type,status) VALUES ('{0}','{1}','Disabled') ON CONFLICT DO NOTHING""".format('sdp', 'itsm'))
    return jsonify({"JOBID": RequestID, "Status": "Success", "Message": "Details added Successfully"})
  except Exception as e:
    return jsonify({"Message": "Error Processing Request", "Status": "Error"+str(e)})


@sdp_api.route('/itsm/admin/sdp/', methods=['GET'])
def get_sdp():
  try:
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    cur = conn.cursor()
    cur.execute("""select itsm_id,communication_type,ip,port,assignment_group_automation,assignment_group_manual,itsm_status,service_category, level, requester, requesttemplate, technician, status , itsm_res_status, itsm_wip_status from admin_sdp""")
    rows = cur.fetchall()   
    itsm = {}
    for count in rows:
      itsmid = count[0]
      commn = count[1]
      ip = count[2]
      port = count[3]
      assignment_auto = count[4]
      assignment_manual = count[5]
      itsm_status = count[6]
      service_category = count[7]
      level = count[8]
      requester = count[9]
      requesttemplate = count[10]
      technician = count[11]
      status = count[12]
      itsm_res_status = count[13]
      itsm_wip_status = count[14]

      itsmvalues = {itsmid: {'TYPE': commn, 'IP': ip, 'PORT': port, 'AUTOMATION GROUP': assignment_auto, 'MANUAL GROUP': assignment_manual, 'DEFAULT OPEN STATUS': itsm_status, 'DEFAULT WIP STATUS': itsm_wip_status, 'DEFAULT RESOLVED STATUS': itsm_res_status, 'Service Category': service_category, 'Level': level, 'Status': status, 'Requester': requester, 'RequersterTemplate': requesttemplate, 'Technician': technician }}
      itsm.update(itsmvalues)

    return jsonify({"Status": "Completed", "Data": itsm})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})    


@sdp_api.route('/itsm/admin/sdp/enable', methods=['POST'])
def enable_row_sdp():
  try:
    data = request.get_json()
    if data['id'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": "Failure"})
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    cur = conn.cursor()
    cur.execute("""select count(*) from admin_integration_meta where integration_type='itsm' and status='{0}'""".format('Enabled'))
    count = cur.fetchall()
    count = count[0]
    countid = count[0]
    if countid >= 1:
      return jsonify({"Message": "ITSM Integration already exist, Please disable and try again", "Status": "Error"})
    cur.execute("""update admin_sdp set status='Enabled' where itsm_id={0} """.format(data['id']))
    cur.execute("""update admin_integration_meta set status='Enabled' where integration_name='{0}' """.format('sdp'))
    conn.commit()
    return jsonify({"Message": "SDP Integration Enabled", "Status": "Succes"})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})


@sdp_api.route('/itsm/admin/sdp/disable', methods=['POST'])
def disable_row_sdp():
  try:
    data = request.get_json()
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    cur = conn.cursor()
    cur.execute("""update admin_sdp set status='Disabled' where itsm_id={0} """.format(data['id']))
    cur.execute("""update admin_integration_meta set status='Disabled' where integration_name='sdp' """)
    conn.commit()
    return jsonify({"Message": "SDP Integration Disabled", "Status": "Succes"})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})

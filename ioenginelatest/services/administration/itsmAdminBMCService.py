#!/usr/bin/env python

import json
import psycopg2
from services.utils.decoder import decode
from flask import Blueprint, jsonify, request

bmcadmin_api = Blueprint('bmcadmin_api', __name__)


# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])

@bmcadmin_api.route('/itsm/admin/bmc/add', methods=['POST'])
def create_ticket():
  try:
    RequestID = "xxxx-ITSM-ADD-xxxx"
    data = request.get_json()
    if data['customer_name'] == '' or data['first_name'] == '' or data['last_name'] == '' or data['impact'] == '' or data['urgency'] == '' or data['source'] == '' or data['service_type'] == '' or data['communication_type'] == '' or data['ip'] == '' or data['port'] == '' or data['username'] == '' or data['password'] == '' or data['assignment_group_manual'] == '' or data['assignment_group_automation'] == '' or data['itsm_status'] == '' or data['created_by'] == '':
      return jsonify({"Message": "Invalid Arguments Detected", "Status": "Error"})
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""insert into admin_bmc(communication_type,ip,port,username,password,assignment_group_automation,assignment_group_manual,itsm_status,customer_name,createdby,status,first_name,last_name,impact,urgency,source,service_type) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','Disabled','{10}','{11}','{12}','{13}','{14}', '{15}')""".format(data['communication_type'],data['ip'],data['port'],data['username'],data['password'],data['assignment_group_automation'],data['assignment_group_manual'],data['itsm_status'],data['customer_name'],data['created_by'],data['first_name'],data['last_name'],data['impact'],data['urgency'],data['source'],data['service_type']))
    cur.execute("""insert into admin_integration_meta(integration_name, integration_type,status) VALUES ('{0}','{1}','Disabled') ON CONFLICT DO NOTHING""".format('bmc', 'itsm'))
    return jsonify({"JOBID": RequestID, "Status": True, "Message": "Details added Successfully"})
  except Exception as e:
    return jsonify({"Message": "Error Processing Request", "Status": "Error"})

@bmcadmin_api.route('/itsm/admin/bmc/', methods=['GET'])
def get_bmc():
  try:
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    cur = conn.cursor()
    cur.execute("""select itsm_id,communication_type,ip,port,username,password,assignment_group_automation,assignment_group_manual,itsm_status,status,first_name,last_name,impact,urgency,source,service_type from admin_bmc""")
    rows = cur.fetchall()   
    itsm = {}
    for count in rows:
      itsmid = count[0]
      commn = count[1]
      ip = count[2]
      port = count[3]
      username = count[4]
      password = count[5]
      assignment_auto = count[6]
      assignment_manual = count[7]
      itsm_status = count[8]
      status = count[9]
      first_name = count[10]
      last_name = count[11]
      impact = count[12]
      urgency = count[13]
      source = count[14]
      service_type = count[15]

      itsmvalues = {itsmid: {'DEFAULT IMPACT': impact, 'DEFAULT URGENCY': urgency, 'FIRST_NAME': first_name, 'LAST_NAME': last_name, 'REPORTED SOURCE': source, 'SERVICE TYPE': service_type,'TYPE': commn, 'IP': ip, 'PORT': port, 'USER': username, 'AUTOMATION GROUP': assignment_auto, 'MANUAL GROUP': assignment_manual, 'DEFAULT STATUS': itsm_status, 'Status': status}}
      itsm.update(itsmvalues)

    return jsonify({"Status": "Completed", "Data": itsm})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})    

@bmcadmin_api.route('/itsm/admin/bmc/enable', methods=['POST'])
def enable_row():
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
    cur.execute("""update admin_bmc set status='Enabled' where itsm_id={0} """.format(data['id']))
    cur.execute("""update admin_integration_meta set status='Enabled' where integration_name='{0}' """.format('bmc'))
    conn.commit()
    return jsonify({"Message": "BMC Integration Enabled", "Status": "Succes"})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})


@bmcadmin_api.route('/itsm/admin/bmc/disable', methods=['POST'])
def disable_row():
  try:
    data = request.get_json()
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    cur = conn.cursor()
    cur.execute("""update admin_bmc set status='Disabled' where itsm_id={0} """.format(data['id']))
    cur.execute("""update admin_integration_meta set status='Disabled' where integration_name='bmc' """)
    conn.commit()
    return jsonify({"Message": "BMC Integration Disabled", "Status": "Succes"})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})


@bmcadmin_api.route('/admin/api/v2/itsm/masters', methods=['GET'])
def get_ldap_masters():
  try:
    itsmdata = {'communication_type': ['http', 'https']}
    return jsonify({'Status': 'Completed', 'Data': itsmdata})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})

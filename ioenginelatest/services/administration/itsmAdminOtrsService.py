#!/usr/bin/env python
import sys
import json
import logging
import psycopg2
from services.utils.decoder import decode
from flask import Flask, jsonify, request
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])

@app.route('/itsm/admin/otrs/add', methods=['POST'])
def create_ticket():
  try:
    app.logger.info("Received Request: OK")
    RequestID = "xxxx-ITSM-ADD-xxxx"
    data = request.get_json()
    app.logger.info(str(data))
    if data['communication_type'] == '' or data['ip'] == '' or data['port'] == '' or data['username'] == '' or data['password'] == '' or data['assignment_group_manual'] == '' or data['assignment_group_automation'] == '' or data['itsm_status'] == '' or data['priority'] == '' or data['created_by'] == '' or data['customer_name'] == '' or data['itsm_wip_status'] == '' or data['itsm_res_status'] == '':
      return jsonify({"Message": "Invalid Arguments Detected", "Status": "Error"})
    app.logger.info("Data Received for OTRS Add")
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""insert into admin_otrs(communication_type,ip,port,username,password,assignment_group_automation,assignment_group_manual,itsm_status,priority,customer_name,createdby,status, itsm_wip_status, itsm_res_status) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','Disabled', '{11}', '{12}')""".format(data['communication_type'],data['ip'],data['port'],data['username'],data['password'],data['assignment_group_automation'],data['assignment_group_manual'],data['itsm_status'],data['priority'],data['customer_name'],data['created_by'], data['itsm_wip_status'], data['itsm_res_status']))
    cur.execute("""insert into admin_integration_meta(integration_name, integration_type,status) VALUES ('{0}','{1}','Disabled') ON CONFLICT DO NOTHING""".format('otrs', 'itsm'))
    return jsonify({"JOBID": RequestID, "Status": "Success", "Message": "Details added Successfully"})
  except Exception as e:
    app.logger.error("Exception Occured : " + str(e))
    return jsonify({"Message": "Error Processing Request", "Status": "Error"})

@app.route('/itsm/admin/otrs/', methods=['GET'])
def get_otrs():
  try:
    app.logger.info("Received Request : OK")
    app.logger.info("Received request for OTRS Details")
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    cur = conn.cursor()
    cur.execute("""select itsm_id,communication_type,ip,port,username,password,assignment_group_automation,assignment_group_manual,itsm_status,priority,status, itsm_wip_status, itsm_res_status from admin_otrs""")
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
      priority = count[9]
      status = count[10]
      itsm_wip_status = count[11]
      itsm_res_status = count[12]
      itsmvalues = {itsmid: {'TYPE': commn, 'IP': ip, 'PORT': port, 'USER': username, 'AUTOMATION GROUP': assignment_auto, 'MANUAL GROUP': assignment_manual, 'DEFAULT STATUS': itsm_status, 'DEFAULT PRIORITY': priority, 'Status': status, 'WIP Status': itsm_wip_status, 'RES Status': itsm_res_status}}
      itsm.update(itsmvalues)
    return jsonify({"Status": "Completed", "Data": itsm})
  except Exception as e:
    app.logger.error("Exception Occured : " + str(e))
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})    

@app.route('/itsm/admin/otrs/enable', methods=['POST'])
def enable_row():
  try:
    app.logger.info("Received Request: OK")
    data = request.get_json()
    if data['id'] == '':
      return jsonify({"Message": "Invalid Arguments detected", "Status": "Failure"})
    app.logger.info(str(data))
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    cur = conn.cursor()
    cur.execute("""select count(*) from admin_integration_meta where integration_type='itsm' and status='{0}'""".format('Enabled'))
    count = cur.fetchall()
    count = count[0]
    countid = count[0]
    if countid >= 1:
      app.logger.info("Error OTRS Integration already exist")
      return jsonify({"Message": "OTRS Integration already exist, Please disable and try again", "Status": "Error"})
    cur.execute("""update admin_otrs set status='Enabled' where itsm_id={0} """.format(data['id']))
    cur.execute("""update admin_integration_meta set status='Enabled' where integration_name='{0}' """.format('otrs'))
    conn.commit()
    return jsonify({"Message": "OTRS Integration Enabled", "Status": "Succes"})
  except Exception as e:
    app.logger.error("Exception Occured : " + str(e))
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})


@app.route('/itsm/admin/otrs/disable', methods=['POST'])
def disable_row():
  try:
    app.logger.info("Received Request: OK")
    data = request.get_json()
    app.logger.info(str(data))
    #DB Connection String
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    cur = conn.cursor()
    cur.execute("""update admin_otrs set status='Disabled' where itsm_id={0} """.format(data['id']))
    cur.execute("""update admin_integration_meta set status='Disabled' where integration_name='otrs' """)
    conn.commit()
    return jsonify({"Message": "OTRS Integration Disabled", "Status": "Succes"})
  except Exception as e:
    app.logger.error("Exception Occured : " + str(e))
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"})

if __name__ == '__main__':
    try:
      formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
      handler = TimedRotatingFileHandler('logs/itsmadmin.log', when='midnight', interval=1)
      handler.setLevel(logging.DEBUG)
      handler.setFormatter(formatter)
      app.logger.addHandler(handler)
      app.logger.setLevel(logging.DEBUG)
      app.run(host='localhost', port=5009, debug=False)
    except Exception as e:
      print("Exception occured : "+str(e))
      sys.exit()

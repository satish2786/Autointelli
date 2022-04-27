#!/usr/bin/env python

import json
import psycopg2
from services.utils.decoder import decode
from services.utils.aitime import getcurrentutcepoch
from flask import Blueprint, jsonify, request

policy_api = Blueprint('policy_api', __name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])


@policy_api.route('/admin/api/v2/policies/masters', methods=['GET'])
def get_policy_masters():
  keyData=[]
  actionData=[]
  lscriptData=[]
  rscriptData=[]
  operatorData=[]
  conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
  conn.autocommit = True
  cur = conn.cursor()
  cur.execute("SELECT componentname from rulemeta")
  rows = cur.fetchall()
  for row in rows:
    component=row[0]
    keyData.append(component)
  cur.execute("SELECT actionname from ai_policyaction_meta")
  rows = cur.fetchall()
  for row in rows:
    action=row[0]
    actionData.append(action)
  cur.execute("SELECT bot_name from ai_bot_repo where component='LOCAL SCRIPT'")
  rows = cur.fetchall()
  for row in rows:
    lscript=row[0]
    lscriptData.append(lscript)
  cur.execute("SELECT bot_name from ai_bot_repo where component='REMOTE SCRIPT'")
  rows = cur.fetchall()
  for row in rows:
    rscript=row[0]
    rscriptData.append(rscript)
  cur.execute("SELECT operator from ai_policyoperator_meta")
  rows = cur.fetchall()
  for row in rows:
    operator=row[0]
    operatorData.append(operator)
  return jsonify({'Status': 'Success', 'Key': keyData, 'Action': actionData, 'LOCAL SCRIPT': lscriptData, 'REMOTE SCRIPT': rscriptData, 'Operator': operatorData})


@policy_api.route('/admin/api/v2/policies/add', methods=['POST'])
def add_policy_details():
  try:
    data = request.get_json()
    if data['rulename'] == '' or data['condition'] == '' or data['action'] == ''  or data['actioncommand'] == ''   or data['hostname'] == ''  or data['createdby'] == '':
      return jsonify({"Message": "Invalid Arguments Detected", "Status": "Error"})

    rulename = data['rulename']
    condition = data['condition']
    action = data['action']
    actioncommand = data['actioncommand']
    actionargs = data['actionargs']
    hostname = data['hostname']
    createdby = data['createdby']
    status = 'Disabled'

    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    currentime = getcurrentutcepoch()
    cur.execute("""insert into rules (rulename, condition, action, actioncommand, actionargs, hostname, createdby, createdtime, status) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', {7}, '{8}')""".format(rulename, json.dumps(condition), action, actioncommand, actionargs, hostname, createdby, int(currentime), status))
    return jsonify({"Status": "Success", "Message": "Details added Successfully"})
  except Exception as e:
    print(str(e))
    return jsonify({"Status": "Failed", "Message": "Failed to add Policy Details, Please try again"})


@policy_api.route('/admin/api/v2/policies', methods=['GET'])
def get_policy_details():
  try:
    policydata = {}
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
   
    cur.execute("""SELECT ruleid,rulename,condition->'Condition', action, actioncommand, actionargs, hostname, createdby, status from rules""")
    rows = cur.fetchall()
    
    for data in rows:
      ruleid = data[0]
      rulename = data[1]
      condition = data[2]
      action = data[3]
      actioncommand = data[4]
      actionargs = data[5]
      hostname = data[6]
      createdby = data[7]
      status = data[8]
      policyvalues = { ruleid: { "rulename": rulename, "Condition": condition, "action": action, "actioncommand": actioncommand, "actionargs": actionargs, "hostname": hostname, "createdby": createdby, "status": status}}
      policydata.update(policyvalues)
    return jsonify({'Status': 'Completed', 'Data': policydata})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


@policy_api.route('/admin/api/v2/policies/<policyid>/enable', methods=['POST'])
def ruledisable_row(policyid):
  try:
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""update rules set status='Enabled' where ruleid={0} """.format(policyid))
    return jsonify({"Message": "Policy Enabled Successfully", "Status": "Succes"})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request" + str(e), "Status": "Error"})



@policy_api.route('/admin/api/v2/policies/<policyid>/disable', methods=['POST'])
def ruleenable_row(policyid):
  try:
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""update rules set status='Disabled' where ruleid={0} """.format(policyid))
    return jsonify({"Message": "Policy Disabled Successfully", "Status": "Succes"})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request" + str(e), "Status": "Error"})

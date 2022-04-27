#!/usr/bin/env python

import json
import psycopg2
from services.utils.decoder import decode
from flask import Blueprint, jsonify, request

arcon_api = Blueprint('arcon_api', __name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])

@arcon_api.route('/admin/api/v2/arcon/add', methods=['POST'])
def add_arcon_details():
  try:
    data = request.get_json()
    if data['communication_type'] == '' or data['arconip'] == '' or data['arconport'] == '' or data['arconuser'] == '' or data['arconpwd'] == '':
      return jsonify({"Message": "Invalid Arguments Detected", "Status": "Error"})

    commtype = data['communication_type']
    arconip = data['arconip']
    arconport = data['arconport']
    arconuser = data['arconuser']
    arconpwd = data['arconpwd']

    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""SELECT communicationtype, configip, configport from configuration where configname='ARCON'""")
    rows = cur.fetchall()
    if not rows:
      cur.execute("""insert into configuration (communicationtype, configip, configport, username, password, configname) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}','ARCON')""".format(commtype, arconip, arconport, arconuser, arconpwd))
      return jsonify({"Status": "Success", "Message": "Details added Successfully"})
    else:
      cur.execute("""UPDATE configuration set communicationtype='{0}', configip='{1}', configport='{2}', username='{3}', password='{4}' where configname='ARCON'""".format(commtype, arconip, arconport,arconuser,arconpwd))
      return jsonify({"Status": "Success", "Message": "Details added Successfully"})
  except Exception as e:
    print(str(e))
    return jsonify({"Status": "Failed", "Message": "Failed to add ARCON Details"})


@arcon_api.route('/admin/api/v2/arcon', methods=['GET'])
def get_arcon_details():
  try:
    arcondata = {}
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
   
    cur.execute("""SELECT communicationtype, configip, configport,username,password from configuration where configname='ARCON'""")
    rows = cur.fetchall()
    
    for data in rows:
      communication_type = data[0]
      arconip = data[1]
      arconport = data[2]
      arconuser = data[3]
      arconpwd = data[4]

      arconvalues = {"communication_type": communication_type, "arconip": arconip, "arconport": arconport, "arconuser": arconuser, "arconpwd": arconpwd}
      arcondata.update(arconvalues)
    return jsonify({'Status': 'Completed', 'Data': arcondata})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


@arcon_api.route('/admin/api/v2/arcon/masters', methods=['GET'])
def get_arcon_masters():
  try:
    arcondata = {'communication_type': ['http', 'https']}
    return jsonify({'Status': 'Completed', 'Data': arcondata})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


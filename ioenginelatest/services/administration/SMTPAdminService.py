#!/usr/bin/env python

import json
import psycopg2
from services.utils.decoder import decode, encode
from flask import Blueprint, jsonify, request

smtpadmin_api = Blueprint('smtpadmin_api', __name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])

@smtpadmin_api.route('/admin/api/v2/smtp/add', methods=['POST'])
def add_smtp_details():
  try:
    data = request.get_json()
    if data['communication_type'] == '' or data['smtpip'] == '' or data['smtpport'] == '':
      return jsonify({"Message": "Invalid Arguments Detected", "Status": "Error"})

    insertQuery = """insert into configuration (communicationtype, configip, configport, configname) VALUES ('{0}', '{1}', '{2}', 'SMTP')"""
    updateQuery = """UPDATE configuration set communicationtype='{0}', configip='{1}', configport='{2}' where configname='SMTP'"""
    commtype = data['communication_type']
    smtpip = data['smtpip']
    smtpport = data['smtpport']
    smtpauth = data['smtpauth']
    if smtpauth == 'YES':
      smtpuser = data['smtpuser']
      smtppass = data['smtppass']
      smtppass = encode('auto!ntell!',smtppass)
      insertQuery = """insert into configuration (communicationtype, configip, configport, configname, username, password) VALUES ('{0}', '{1}', '{2}', 'SMTP', '{3}', '{4}')"""
      updateQuery = """UPDATE configuration set communicationtype='{0}', configip='{1}', configport='{2}', username='{3}', password='{4}' where configname='SMTP'"""
      

    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""SELECT communicationtype, configip, configport from configuration where configname='SMTP'""")
    rows = cur.fetchall()
    if not rows:
      if smtpauth != 'YES':
        cur.execute(insertQuery.format(commtype, smtpip, smtpport))
        return jsonify({"Status": "Success", "Message": "Details added Successfully"})
      else:
        cur.execute(insertQuery.format(commtype, smtpip, smtpport, smtpuser, smtppass))
        return jsonify({"Status": "Success", "Message": "Details added Successfully"})
    else:
      if smtpauth != 'YES':
        cur.execute(updateQuery.format(commtype, smtpip, smtpport))
        return jsonify({"Status": "Success", "Message": "Details added Successfully"})
      else:
        cur.execute(updateQuery.format(commtype, smtpip, smtpport, smtpuser, smtppass))
        return jsonify({"Status": "Success", "Message": "Details added Successfully"})
       
  except Exception as e:
    print(str(e))
    return jsonify({"Status": "Failed", "Message": "Failed to add SMTP Details"})


@smtpadmin_api.route('/admin/api/v2/smtp', methods=['GET'])
def get_smtp_details():
  try:
    smtpdata = {}
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
   
    cur.execute("""SELECT communicationtype, configip, configport, username, password from configuration where configname='SMTP'""")
    rows = cur.fetchall()
    
    for data in rows:
      communication_type = data[0]
      smtpip = data[1]
      smtpport = data[2]
      smtpuser = data[3]
      smtppass = data[4]
      smtppass = decode('auto!ntelli!', smtppass)
      smtpvalues = {"communication_type": communication_type, "SMTP IP": smtpip, "SMTP PORT": smtpport, "Username": smtpuser, "Password":smtppass}
      smtpdata.update(smtpvalues)
    return jsonify({'Status': 'Completed', 'Data': smtpdata})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


@smtpadmin_api.route('/admin/api/v2/smtp/masters', methods=['GET'])
def get_smtp_masters():
  try:
    smtpdata = {'communication_type': ['smtp', 'smtps', 'smtptls']}
    return jsonify({'Status': 'Completed', 'Data': smtpdata})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})

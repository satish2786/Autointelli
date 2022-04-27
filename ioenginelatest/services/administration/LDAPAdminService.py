#!/usr/bin/env python

import json
import psycopg2
from services.utils.decoder import decode
from flask import Blueprint, jsonify, request

ldap_api = Blueprint('ldap_api', __name__)

# Reading the configuration file for db connection string
conn = ""
dbdata = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',dbdata['maindb']['password'])

@ldap_api.route('/admin/api/v2/ldap/add', methods=['POST'])
def add_ldap_details():
  try:
    data = request.get_json()
    if data['communication_type'] == '' or data['ldapip'] == '' or data['ldapport'] == '':
      return jsonify({"Message": "Invalid Arguments Detected", "Status": "Error"})

    commtype = data['communication_type']
    ldapip = data['ldapip']
    ldapport = data['ldapport']
    sysAcc = data['sysacc']
    sysPasswd = data['syspwd']
    baseDN = data['basedn']

    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""SELECT communicationtype, configip, configport from configuration where configname='LDAP'""")
    rows = cur.fetchall()
    if not rows:
      cur.execute("""insert into configuration (communicationtype, configip, configport, configname, username, password, extra2) VALUES ('{0}', '{1}', '{2}', 'LDAP', '{3}', '{4}', '{5}')""".format(commtype, ldapip, ldapport, sysAcc, sysPasswd, baseDN))
      return jsonify({"Status": "Success", "Message": "Details added Successfully"})
    else:
      cur.execute("""UPDATE configuration set communicationtype='{0}', configip='{1}', configport='{2}', username='{3}', password='{4}', extra2='{5}' where configname='LDAP'""".format(commtype, ldapip, ldapport, sysAcc, sysPasswd, baseDN))
      return jsonify({"Status": "Success", "Message": "Details added Successfully"})
  except Exception as e:
    print(str(e))
    return jsonify({"Status": "Failed", "Message": "Failed to add LDAP Details"})


@ldap_api.route('/admin/api/v2/ldap', methods=['GET'])
def get_ldap_details():
  try:
    ldapdata = {}
    conn = psycopg2.connect(database=dbdata['maindb']['dbname'], user=dbdata['maindb']['username'], password=maindbpassword, host=dbdata['maindb']['dbip'], port=dbdata['maindb']['dbport'])
    conn.autocommit = True
    cur = conn.cursor()
   
    cur.execute("""SELECT communicationtype, configip, configport, username, password, extra2 basedn from configuration where configname='LDAP'""")
    rows = cur.fetchall()
    
    for data in rows:
      communication_type = data[0]
      ldapip = data[1]
      ldapport = data[2]
      sysAcc = data[3]
      sysPwd = data[4]
      baseDN = data[5]

      ldapvalues = {"communication_type": communication_type, "LDAP IP": ldapip, "LDAP PORT": ldapport, "sysacc": sysAcc, "syspwd": sysPwd, "basedn": baseDN}
      ldapdata.update(ldapvalues)
    return jsonify({'Status': 'Completed', 'Data': ldapdata})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


@ldap_api.route('/admin/api/v2/ldap/masters', methods=['GET'])
def get_ldap_masters():
  try:
    ldapdata = {'communication_type': ['ldap', 'ldaps']}
    return jsonify({'Status': 'Completed', 'Data': ldapdata})
  except Exception as e:
    return jsonify({"ERROR": "Error Processing Request", "Status": "Error"+str(e)})


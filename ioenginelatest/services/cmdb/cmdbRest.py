#!/usr/bin/env python
import sys
import pika
import json
import logging
import psycopg2
from services.utils.decoder import decode, encode
from flask import Flask, jsonify, request
from logging.handlers import TimedRotatingFileHandler
from pymongo import MongoClient
import os
from services.utils import ConnMQ



# Reading the configuration file for db connection string
conn = ""
data = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',data['maindb']['password'])
UPLOAD_FOLDER = '/tmp/uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


try:
  #DB Connection String
  conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
  cur = conn.cursor()
  cur.execute('select configip,configport,dbname,username,password from configuration where configname=\'MQ\'')
  esbdata = cur.fetchall()
  esbdata = esbdata[0]
  esbip = esbdata[0]
  esbuser = esbdata[3]
  esbpass = esbdata[4]
  vhost = esbdata[2]
  esbpass = decode('123',esbpass)
  cur.execute('select configip,configport,dbname,username,password from configuration where configname=\'CMDB\'')
  mongodata = cur.fetchall()
  mongodata = mongodata[0]
except Exception as e:
  print("Exception Occured " + str(e))
  sys.exit()


@app.route('/admin/api/v2/cmdb/masters', methods=['GET'])
def cmdb_masters():
  remediate=['Y', 'N']
  creds=[]
  conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
  conn.autocommit = True
  cur = conn.cursor()
  cur.execute("select cred_name from ai_device_credentials where active_yn='Y'")
  rows = cur.fetchall()
  for row in rows:
    crednames=row[0]
    creds.append(crednames)
  return jsonify({'Status': 'Success', 'Remediate': remediate, 'Credentials': creds})


@app.route('/admin/api/v2/cmdb/insert', methods=['POST'])
def cmdb_insert():
  try:
    #Step 0 Get data from UI
    req = request.get_json()
    platform = req['platform']
    conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
    cur = conn.cursor()
    conn.autocommit=True
    cur.execute("""INSERT into ai_machine (machine_fqdn,ip_address,platform,osname,osversion,remediate,fk_cred_id,active_yn,console_port, backend_port) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', (SELECT cred_id from ai_device_credentials where cred_name='{6}' and active_yn='Y'),'Y', {7}, {8})""".format(req['hostname'], req['ipaddress'], req['platform'], req['osname'], req['osversion'], req['remediate'], req['credentials'], req['console_port'], req['backend_port']))
    print(platform.lower())
    if platform.lower() == 'linux':
      pData = {'cred_type': 'ssh', 'hostname': req['ipaddress'], 'console_port': req['console_port']}
    else:
      pData = {'cred_type': 'winrm', 'hostname': req['ipaddress'], 'console_port': req['console_port']}
    ConnMQ.send2MQ("remoting", "automationengine", "remoting", str(json.dumps(pData)))
    return jsonify({"Status": "Success", "Message": "Details Added Successfully"})
  except Exception as e:
    app.logger.error("Error : "+str(e))
    return jsonify({"Status": "Failed", "Message": "Error in adding CI"})

@app.route('/admin/api/v2/cmdb/update/username', methods=['POST'])
def cmdb_update_username():
  try:
    #Step 0 Get data from UI
    req = request.get_json()
    if req['ipaddress'] == '' or req['username'] == '':
        return jsonify({"ERROR": "Invalid Arguments Detected", "Status": "Rejected"})

    ipaddress = req['ipaddress']
    username = req['username']
    app.logger.info("Data Received for CMDB Update")
    conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
    cur = conn.cursor()
    conn.autocommit=True
    cur.execute("""UPDATE ai_cmdb set username='{0}', status='{1}' where ipaddress='{2}'""".format(username, 'New', ipaddress))
    return jsonify({"Status": "Success", "Message": "Details Updated Successfully"})
  except Exception as e:
    app.logger.error("Error : "+str(e))
    return jsonify({"Status": "Failed", "Message": "Error in adding CI"})



@app.route('/admin/api/v2/cmdb/update/credentials', methods=['POST'])
def cmdb_update_credentials():
  try:
    req = request.get_json()
    if not req['ipaddress'] or req['ipaddress'] == '' or req['cred_name'] == '' or req['operating_system'] == '':
        return jsonify({"ERROR": "Invalid Arguments Detected", "Status": "Rejected"})

    ipaddress = req['ipaddress']
    cred_name = req['cred_name']
    operating_system = req['operating_system']
    conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
    cur = conn.cursor()
    conn.autocommit=True
    cur.execute("""SELECT cred_id from ai_device_credentials where cred_name='{0}'""".format(cred_name))
    rows = cur.fetchone()
    cred_id = rows[0]
    cur.execute(""" SELECT count(*) from ai_device_discovery where ip_address='{0}'""".format(ipaddress))
    rows = cur.fetchone()
    count = rows[0]
    if count == 1:
      cur.execute("""UPDATE ai_device_discovery set ip_address='{0}', operating_system='{1}', fk_cred_id={2}, gf_yn='N' where ip_address='{0}'""".format(ipaddress, operating_system, cred_id))
    else:
      cur.execute("""INSERT into ai_device_discovery set ip_address='{0}', operating_system='{1}', 'fk_cred_id={2}, gf_yn='N' where ip_address='{0}'""".format(ipaddress, operating_system, cred_id))
    return jsonify({"Status": "Success", "Message": "Machine will be Readded for Discovery"})
  except Exception as e:
    app.logger.error("Error : "+str(e))
    return jsonify({"Status": "Failed", "Message": "Error in adding CI"})



@app.route('/admin/api/v2/cmdb/update/password', methods=['POST'])
def cmdb_update_password():
  try:
    #Step 0 Get data from UI
    req = request.get_json()
    if req['ipaddress'] == '' or req['password'] == '':
        return jsonify({"ERROR": "Invalid Arguments Detected", "Status": "Rejected"})

    ipaddress = req['ipaddress']
    password = req['password']
    password = encode('auto!ntell!',password)
    app.logger.info("Data Received for CMDB Update")
    conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
    cur = conn.cursor()
    conn.autocommit=True
    cur.execute("""UPDATE ai_cmdb set password='{0}', status='{1}' where ipaddress='{2}'""".format(password, 'New', ipaddress))
    return jsonify({"Status": "Success", "Message": "Details Updated Successfully"})
  except Exception as e:
    app.logger.error("Error : "+str(e))
    return jsonify({"Status": "Failed", "Message": "Error in adding CI"})


@app.route('/admin/api/v2/cmdb/machine/getAllData', methods=['GET'])
#@app.route('/getAllData', methods=['GET'])
def cmdb_getAllDataNew():
  try:
    conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
    cur = conn.cursor()
    conn.autocommit=True
    cur.execute("""select am.machine_fqdn, am.ip_address, am.platform, am.osname, am.osversion, am.remediate, ac.cred_name, am.machine_id, am.console_port, am.backend_port from ai_machine am left join ai_device_credentials ac on(am.fk_cred_id=ac.cred_id)""")
    rows = cur.fetchall()
    cmdbdata = {}
    for line in rows:
      fqdn = line[0]
      hostaddress = line[1]
      platform = line[2]
      osname = line[3]
      osversion = line[4]
      remediate = line[5]
      cred_name = line[6]
      machine_id = line[7]
      console_port = line[8]
      backend_port = line[9]
      cmdbvalues = {machine_id: {'machine_id': machine_id, 'Hostname': fqdn, 'Platform': platform, 'OSName': osname, 'OSVersion': osversion, 'Remediate': remediate, 'Credentials ID': cred_name, 'IPAddress': hostaddress, 'Console Port': console_port, 'Backend Port': backend_port}}
      cmdbdata.update(cmdbvalues)
    return jsonify({"Status": "Completed", "Data": cmdbdata})
  except Exception as e:
    app.logger.error("Exception Occured : " + str(e))
    return jsonify({"ERROR": "Error Processing Request", "Status": "Rejected"})


@app.route('/admin/api/v2/cmdb/automationtype', methods=['POST'])
def cmdb_host_automation_type():
  try:
    values = request.get_json()
    if values['hostname'] == '' or values['remediate'] == '':
        return jsonify({"ERROR": "Invalid Arguments Detected", "Status": "Rejected"})
  
    conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
    cur = conn.cursor() 
    conn.autocommit = True
    cur.execute("""UPDATE ai_machine set remediate='{0}' where machine_fqdn='{1}'""".format(values['remediate'], values['hostname']))
    return jsonify({"Status": "Success", "Message": "Details added Successfully"})
  except Exception as e:
    return jsonify({"Status": "Failed", "Message": "Failed to change automation type"+str(e)})    


@app.route('/admin/api/v2/cmdb/getHostUsage/<hostname>', methods=['GET'])
def cmdb_getHostResourceUsage(hostname):
  try:
    hostdata = {}
    diskdata = {}
    worker = MongoClient(mongodata[0], int(mongodata[1]))
    db = worker.ansible
    coll = db.cache.find({"data.ansible_hostname": hostname}, {"data.ansible_system": "1"})
    for data in coll:
      if data['data']['ansible_system'] == 'Linux':
        coll = db.cache.find({"data.ansible_hostname": hostname}, {"data.ansible_swaptotal_mb": "1", "data.ansible_swapfree_mb": "1", "data.ansible_memtotal_mb": "1", "data.ansible_memfree_mb": "1", "data.system_cpu": "1", "data.total_disk_used": "1", "data.ansible_mounts": "1"})
        for data in coll:
          mounts =  data['data']['ansible_mounts']
          for mount in mounts:
            partition  = mount['mount']
            if 'size_total' in mount:
              mount_total_bytes = mount['size_total']
              mount_available_bytes = mount['size_available']
              diskid = mount['uuid']
              Usage = 100 - (float(mount_available_bytes) / float(mount_total_bytes) * 100)
              diskvalues = {diskid: {'Partition': partition, 'Usage': Usage}}
              diskdata.update(diskvalues)
          swap_free = data['data']['ansible_swapfree_mb']
          swap_total = data['data']['ansible_swaptotal_mb']
          mem_free = data['data']['ansible_memfree_mb']
          mem_total = data['data']['ansible_memtotal_mb']
          cpu_usage = data['data']['system_cpu']
          total_processor = data['data']['ansible_processor_count']
          total_disk_used = data['data']['total_disk_used']
          swapused = 100 - (float(swap_free) / float(swap_total) * 100)
          memused = 100 - (float(mem_free) / float(mem_total) * 100)
          hostvalues = {hostname: {'SwapUsage' : swapused, 'MemoryUsage': memused, 'Disk Usage': total_disk_used, 'CPUUsage': cpu_usage, 'Diskdata': diskdata}}
          hostdata.update(hostvalues)
          return jsonify({"Status": "Completed", "Data": hostdata})
      elif data['data']['ansible_system'] == 'Win32NT':
        coll = db.cache.find({"data.ansible_hostname": hostname}, {"data.swapused": "1", "data.swaptotal": "1", "data.memusage": "1", "data.cpuusage": "1", "data.totaldisk": "1", "data.freedisk": "1"})
        for data in coll:
          swapused = data['data']['swapused'] 
          swaptotal = data['data']['swaptotal']
          cpuusage = data['data']['cpuusage'].replace('\r\n','')
          memusage = data['data']['memusage'].replace('\n','')
          totaldisk = data['data']['totaldisk']
          freedisk = data['data']['freedisk']
          usedisk = float(totaldisk) - float(freedisk)
          diskusage = float(usedisk)  / float(totaldisk) * 100
          diskusage = int(diskusage)
          swapusage = float(swapused) / float(swaptotal) * 100
          hostvalues = {hostname: {'SwapUsage': swapusage, 'MemoryUsage': memusage, 'Disk Usage': diskusage, 'CPUUSage': cpuusage, 'Diskdata': diskdata}}
          hostdata.update(hostvalues)
          return jsonify({"Status": "Completed", "Data": hostdata})
    return jsonify({"ERROR": "Error Processing Request", "Status": "Rejected"})
  except Exception as e:
    app.logger.error("Exception: "+ str(e))
    return jsonify({"ERROR": "Error Processing Request", "Status": "Rejected"})


@app.route('/getHostStats', methods=['GET'])
def cmdb_getHostStats():
  try:
    cmdbdata = {}
    #worker = MongoClient(data['cmdb']['dbip'],username=data['cmdb']['username'],password=mongopassword, authSource=data['cmdb']['authdb'], authMechanism='SCRAM-SHA-1')
    worker = MongoClient(mongodata[0], int(mongodata[1]))
    db = worker.ansible
    results_Linux = db.cache.find({"data.ansible_system": "Linux"})
    results_Linux = results_Linux.count()
    results_Windows = db.cache.find({"data.ansible_system": "Win32NT"})
    results_Windows = results_Windows.count()
    results_IOS = db.cache.find({"data.ansible_net_model": {"$exists":1}})
    results_IOS = results_IOS.count()
    results_Total = db.cache.find()
    results_Total = results_Total.count()
    return jsonify({"Status": "Completed", "Network": results_IOS, "Linux": results_Linux, "Windows": results_Windows, "Total": results_Total})
  except Exception as e:
    app.logger.error("Exception Occured : " + str(e))
    return jsonify({"ERROR": "Error Processing Request", "Status": "Rejected"})


@app.route('/cmdb/insertBulk', methods=['GET', 'POST'])
def cmdb_insertBulk():
  try:
    if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
    data = {}
    credentials = pika.PlainCredentials(esbuser,esbpass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=esbip,credentials=credentials,virtual_host=vhost))
    channel = connection.channel()
    app.logger.info("CONNECTED TO ESB : OK")
    RequestID = request.headers['IO-Request-ID']
    # Add JOBID into the Json and push it to the queue
    data['JOBID'] = RequestID
    data['ACTION'] = "bulkInsert"
    data['FILENAME'] = filename
    data['UPLOAD_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER']) 
    routing_key = "io.cmdb"
    channel.basic_publish(exchange='CMDB', routing_key=routing_key,body=json.dumps(data))
    connection.close()
    app.logger.info("DATA PUSHED : OK")
    app.logger.info("END API : OK")
    return jsonify({"JOBID": RequestID, "Status": "Requested"})
  except Exception as e:
    app.logger.error("Exception Occured : " + str(e))
    return jsonify({"ERROR": "Error Processing Request, Try Again", "Status": "Rejected"})


if __name__ == '__main__':
    try:
      formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
      handler = TimedRotatingFileHandler('/var/log/autointelli/cmdb.log', when='midnight', interval=1)
      handler.setLevel(logging.DEBUG)
      handler.setFormatter(formatter)
      app.logger.addHandler(handler)
      app.logger.setLevel(logging.DEBUG)
      app.run(host='0.0.0.0', port=5003, debug=False)
    except Exception as e:
      print("Exception occured : "+str(e))
      sys.exit()

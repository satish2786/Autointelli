#!/usr/bin/env python


import services.utils.ED_AES256 as aes
import re
from services.utils import ConnMQ
from services.utils.aitime import getcurrentutcepoch
import time
import sys
import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
import pika
from ast import literal_eval
import requests
import logging


FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "/var/log/autointelli/ciremoting.log"

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler():
   file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=104857600, backupCount=5)
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger

getESBQuery = """select configip,configport,dbname,username,password from configuration where configname='MQ' """
retESBResult = ConnPostgreSQL.returnSelectQueryResult(getESBQuery)

if retESBResult["result"] == "success":
  configip = retESBResult['data'][0]['configip']
  configport = retESBResult['data'][0]['configport']
  vhost = retESBResult['data'][0]['dbname']
  configusername = retESBResult['data'][0]['username']
  configpassword = retESBResult['data'][0]['password']
  configpassword = decoder.decode("auto!ntell!", configpassword)
else:
  my_logger = get_logger("Init")
  my_logger.error("Error Connecting to DB") 
  print("DB Connection Issues")
  sys.exit(1)


credentials = pika.PlainCredentials(configusername,configpassword)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=configip,credentials=credentials,virtual_host=vhost))
channel = connection.channel()

###
getESBQuery = """select communicationtype,configip,configport,username,password from configuration where configname='REMOTINGSERVER' """
retESBResult = ConnPostgreSQL.returnSelectQueryResult(getESBQuery)

if retESBResult["result"] == "success":
  guaccommtype = retESBResult['data'][0]['communicationtype']
  guacip = retESBResult['data'][0]['configip']
  guacport = retESBResult['data'][0]['configport']
  guacusername = retESBResult['data'][0]['username']
  guacpassword = retESBResult['data'][0]['password']
  guacpassword = decoder.decode("auto!ntell!", guacpassword)
else:
  my_logger = get_logger("Init")
  my_logger.error("Error Connecting to DB")
  print("DB Connection Issues")
  sys.exit(1)


def callback(ch, method, properties, body):
  try:  
    guacurl = '{0}://{1}:{2}/guacamole'.format(guaccommtype,guacip,guacport)
    guactokenurl = guacurl+'/api/tokens'
    guacconnectionsurl = guacurl +'/api/session/data/postgresql/connections'
    my_logger = get_logger('Remoting')
    my_logger.info("---------Start : CI ADD Request----------") 
    body = body.decode('utf-8')
    data = json.loads(body)
    my_logger.info(data)
    connectionType = data['cred_type']
    platform = data['platform']
    if (connectionType.lower() == 'ssh' or connectionType.lower() == 'ssh key' or connectionType.lower() == 'pam') and platform.lower()  == 'linux':
      cihostname = data['hostname']
      ciport = data['console_port']
      headers = {'content-type': 'application/json', 'Accept': 'application/json'}
      payload = {'parentIdentifier':'ROOT','name': cihostname,'protocol':'ssh','parameters':{'port': ciport,'read-only':'','swap-red-blue':'','cursor':'','color-depth':'','clipboard-encoding':'','disable-copy':'','disable-paste':'','dest-port':'','recording-exclude-output':'','recording-exclude-mouse':'','recording-include-keys':'','create-recording-path':'true','enable-sftp':'','sftp-port':'','sftp-server-alive-interval':'','sftp-disable-download':'','sftp-disable-upload':'','enable-audio':'','wol-send-packet':'','wol-wait-time':'','hostname': cihostname,'username': '','password': '','recording-path':'', 'recording-name': ''},'attributes':{'max-connections':'','max-connections-per-user':'','weight':'','failover-only':'','guacd-port':'','guacd-encryption':''}}
      tokenreq = requests.post(guactokenurl,auth=(guacusername,guacpassword),verify=False)
      if tokenreq.status_code == 200:
        tokendata = json.loads(tokenreq.text)
        authtoken = tokendata['authToken']
        params = {'token': authtoken} 
      else:
        my_logger = get_logger('Exception')
        my_logger.error("Error | CIADDFAILED | " + str(data))
        ch.basic_ack(delivery_tag = method.delivery_tag)
      addcireq = requests.post(guacconnectionsurl,headers=headers,data=json.dumps(payload), params=params)
      if addcireq.status_code == 200:
        my_logger.info("Success | CIADDITTION | " + cihostname)
        ch.basic_ack(delivery_tag = method.delivery_tag)
      else:
        my_logger = get_logger('Exception')
        my_logger.error("Error | CIADDFAILED | " + str(data))
        my_logger.error("Error | CIADDFAILED | " + str(addcireq.text))
        ch.basic_ack(delivery_tag = method.delivery_tag)
    elif (connectionType.lower() == 'winrm' or connectionType.lower() == 'pam') and platform == 'windows':
      cihostname = data['hostname']
      ciport = data['console_port']
      headers = {'content-type': 'application/json', 'Accept': 'application/json'}
      payload = {'parentIdentifier':'ROOT','name': cihostname,'protocol':'rdp','parameters':{'port': ciport,'read-only':'','swap-red-blue':'','cursor':'','color-depth':'','clipboard-encoding':'','disable-copy':'','disable-paste':'','dest-port':'','recording-exclude-output':'','recording-exclude-mouse':'','recording-include-keys':'','create-recording-path':'','enable-sftp':'','sftp-port':'','sftp-server-alive-interval':'','sftp-disable-download':'','sftp-disable-upload':'','enable-audio':'','wol-send-packet':'','wol-wait-time':'','security':'','disable-auth':'','ignore-cert':'true','gateway-port':'','server-layout':'','timezone': '','console':'','width':'','height':'','dpi':'','resize-method': 'display-update','console-audio':'','disable-audio':'','enable-audio-input':'','enable-printing':'','enable-drive':'','disable-download':'','disable-upload':'','create-drive-path':'','enable-wallpaper':'','enable-theming':'','enable-font-smoothing':'','enable-full-window-drag':'','enable-desktop-composition':'','enable-menu-animations':'','disable-bitmap-caching':'','disable-offscreen-caching':'','disable-glyph-caching':'','preconnection-id':'','hostname': cihostname, 'username':'','password': '','recording-path': '','recording-name': ''},'attributes':{'max-connections':'','max-connections-per-user':'','weight':'','failover-only':'','guacd-port':'','guacd-encryption':''}}
      tokenreq = requests.post(guactokenurl,auth=(guacusername,guacpassword),verify=False)
      if tokenreq.status_code == 200:
        tokendata = json.loads(tokenreq.text)
        authtoken = tokendata['authToken']
        params = {'token': authtoken}
      else:
        my_logger = get_logger('Auth Exception')
        my_logger.error("Error | CIADDFAILED | " + str(data))
        ch.basic_ack(delivery_tag = method.delivery_tag)
      addcireq = requests.post(guacconnectionsurl,headers=headers,data=json.dumps(payload), params=params)
      print(addcireq.text)
      if addcireq.status_code == 200:
        print(addcireq.text)
        my_logger.info("Success | CIADDITTION | " + cihostname)
        ch.basic_ack(delivery_tag = method.delivery_tag)
      else:
        my_logger = get_logger('Add Exception')
        my_logger.error("Error | CIADDFAILED | " + str(data))
        ch.basic_ack(delivery_tag = method.delivery_tag)
  except Exception as e:
    my_logger = get_logger('Exception')
    my_logger.error("Exception in the main program : " + str(e))
    ch.basic_ack(delivery_tag = method.delivery_tag)

queue_name = "remoting"
binding_key = "remoting"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

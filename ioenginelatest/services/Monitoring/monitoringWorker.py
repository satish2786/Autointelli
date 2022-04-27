#!/usr/bin/python3.6

import json
from addMonitoring import *
from sys import exit
import time
import services.utils.validator_many as vm
import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file, logit
from services.utils import ConnMQ
import sys 
import pika


logobj = create_log_file("/var/log/autointelli/vmware_monitoring.log")
if not logobj:
  print("Not Able to create logfile")
  sys.exit(1)

logit(logobj, "info", "Started Input Validation BOT")

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
  print("DB Connection Issues")
  sys.exit(1)

try:
  credentials = pika.PlainCredentials(configusername,configpassword)
  connection = pika.BlockingConnection(pika.ConnectionParameters(host=configip,credentials=credentials,virtual_host=vhost))
  channel = connection.channel()
except Exception as e:
  print("Cannot Start .... {0}".format(str(e)))
  sys.exit()

def callback(ch, method, properties, body):
  try:
    logit(logobj,"info", body)
    body = body.decode('utf-8')
    print(body)
    data = json.loads(body)
    lAttr = ["hypervisor_ip", "object_type", "object_name"]
    lMandatoryAttr =  ["hypervisor_ip", "object_type", "object_name"]
    X = vm.isPayloadValid(dPayload=data, lHeaders=lAttr, lMandatory=lMandatoryAttr)
    if not X:
      ch.basic_ack(delivery_tag = method.delivery_tag)
    else:
      name = data['object_name']
      hypervisorip = data['hypervisor_ip']
      object_type = data['object_type']
      if object_type.lower() == 'esxivm':
        result = addesxiVirtualMachine.apply_async(args=[hypervisorip,name], connect_timeout=3)
        ch.basic_ack(delivery_tag = method.delivery_tag)
      elif object_type.lower() == 'esxihost':
        result = addesxiHost.apply_async(args=[hypervisorip,name], connect_timeout=3)
        ch.basic_ack(delivery_tag = method.delivery_tag)
      elif object_type.lower() == 'cluster':
        result = addesxiCluster.apply_async(args=[hypervisorip,name], connect_timeout=3)
        ch.basic_ack(delivery_tag = method.delivery_tag)
      elif object_type.lower() == 'datastore':
        result = addesxiDatastore.apply_async(args=[hypervisorip,name], connect_timeout=3)
        ch.basic_ack(delivery_tag = method.delivery_tag)
      else:
        ch.basic_ack(delivery_tag = method.delivery_tag)
  except Exception as e:
    ch.basic_ack(delivery_tag = method.delivery_tag)

queue_name = "vmware_monitoring"
#binding_key = "automation.processevents"
channel.queue_bind(exchange='monitoring',queue=queue_name)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

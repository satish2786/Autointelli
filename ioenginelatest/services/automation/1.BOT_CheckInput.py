#!/usr/bin/env python

# Program to Validate all the required inputs from Event Management
import services.utils.validator_many as vm
import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file, logit
from services.utils import ConnMQ
import sys 
import pika


logobj = create_log_file("/var/log/autointelli/automationengine.log")
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
    logit(logobj,"info", body)
    body = body.decode('utf-8')
    data = json.loads(body)
    lAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source", "alert_id"]
    lMandatoryAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source", "alert_id"]
    X = vm.isPayloadValid(dPayload=data, lHeaders=lAttr, lMandatory=lMandatoryAttr)
    if not X:
      data['Exception'] = 'INVALIDINPUT'
      logit(logobj, "error", "Error in Arguments {0}".format(body))
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", body)
      if output['result'] == 'success':
        logit(logobj, "info", "Success sending to mq")
      else: 
        logit(logobj, "error", "Error Sending to notprocessed Q>> {0}".format(body))
    else:
      output = ConnMQ.send2MQ("checkautomation", "automationengine", "automation.check_automation", body)
      if output['result'] == 'success':
        logit(logobj, "info", "Success sending to mq")
      else:
        logit(logobj, "error", "Error Sending to checkautomation Q>> {0}".format(body))
    ch.basic_ack(delivery_tag = method.delivery_tag)


queue_name = "processevents"
binding_key = "automation.processevents"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

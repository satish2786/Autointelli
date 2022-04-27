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

logit(logobj, "info", "Started Check Automation BOT")

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


credentials = pika.PlainCredentials(configusername,configpassword)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=configip,credentials=credentials,virtual_host=vhost))
channel = connection.channel()

def callback(ch, method, properties, body):
    logit(logobj,"info", body)
    body = body.decode('utf-8')
    data = json.loads(body)
    
    getESBQuery = """select automated from ai_automation_type"""
    retESBResult = ConnPostgreSQL.returnSelectQueryResult(getESBQuery)

    if retESBResult["result"] == "success":
      automation_yn = retESBResult['data'][0]['automated']  

    if automation_yn == 'Y':
      data['automation_yn'] = 'Y'
    else:
      data['automation_yn'] = 'N'
      data['Exception'] = 'NONAUTOMATION'
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", str(data))
    
    output = ConnMQ.send2MQ("createautomationid", "automationengine", "automation.create_auto_id", str(data))
    if output['result'] == 'success':
      logit(logobj, "info", "Success sending to mq")
    else: 
      logit(logobj, "error", "Error Sending to createautomationid Q:{0}".format(body))
    ch.basic_ack(delivery_tag = method.delivery_tag)


queue_name = "checkautomation"
binding_key = "automation.check_automation"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

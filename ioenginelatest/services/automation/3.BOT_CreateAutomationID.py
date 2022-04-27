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
from services.utils.aitime import getcurrentutcepoch
from ast import literal_eval


logobj = create_log_file("/var/log/autointelli/automationengine.log")
if not logobj:
  print("Not Able to create logfile")
  sys.exit(1)

logit(logobj, "info", "Started Create Automation ID BOT")

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
    data = literal_eval(body)
    alert_id = data['alert_id']
    currentepoch = getcurrentutcepoch()
    getESBQuery = """INSERT into ai_automation_executions(fk_alert_id, execution_status, starttime) VALUES ({0}, '{1}', {2}) RETURNING pk_execution_id""".format(int(alert_id), 'New', int(currentepoch))
    retESBResult = ConnPostgreSQL.returnSelectQueryResultWithCommit(getESBQuery)
    if retESBResult["result"] == "success":
      data['pk_execution_id'] = retESBResult['data'][0]['pk_execution_id']
      output = ConnMQ.send2MQ("createticket", "automationengine", "automation.create_ticket_id", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Success sending to createticket Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
      else: 
        logit(logobj, "error", "Error Sending to createticket Q :{0}".format(body))
    else:
      data['Exception'] = 'CAIDFAILED'
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Success sending to NotProcessed Queue")
        ch.basic_ack(delivery_tag = method.delivery_tag)
      else:
        logit(logobj, "error", "Error Sending to notprocessed Q :{0}".format(body))


queue_name = "createautomationid"
binding_key = "automation.create_auto_id"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

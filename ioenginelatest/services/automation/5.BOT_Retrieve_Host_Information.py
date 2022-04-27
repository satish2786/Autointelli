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

logit(logobj, "info", "Started Get Host Information BOT")

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

#Connect MQ
try:
  credentials = pika.PlainCredentials(configusername,configpassword)
  connection = pika.BlockingConnection(pika.ConnectionParameters(host=configip,credentials=credentials,virtual_host=vhost))
  channel = connection.channel()
except Exception as e:
  print("MQ Connection Issues")
  sys.exit(1)

def callback(ch, method, properties, body):
    logit(logobj,"info", body)
    body = body.decode('utf-8')
    data = literal_eval(body)
    ci_name = data['ci_name']
    pk_execution_id = data['pk_execution_id']
  
    currentepoch = getcurrentutcepoch()
    setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 2, int(currentepoch), 'HOST Exist', 'GREEN')
    setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 2, int(currentepoch), 'HOST Not Exist', 'RED')
    #retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)

    getHostQuery = """SELECT platform, osname, osversion, remediate from ai_machine where lower(machine_fqdn)='{0}'""".format(ci_name.lower())
    setHostQueryResult = ConnPostgreSQL.returnSelectQueryResult(getHostQuery)
    if setHostQueryResult['result'] == 'success':
      ci_platform = setHostQueryResult['data'][0]['platform']
      ci_osname = setHostQueryResult['data'][0]['osname']
      ci_version = setHostQueryResult['data'][0]['osversion']
      ci_remediate = setHostQueryResult['data'][0]['remediate']
      data['ci_platform'] = ci_platform    
      data['ci_osname'] = ci_osname       
      data['ci_version'] = ci_version    
      data['ci_remediate'] = ci_remediate
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      output = ConnMQ.send2MQ("updateticket", "automationengine", "automation.update_ticket", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Success sending to updateticket Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
      else:
        logit(logobj, "error", "Error Sending to updateticket Q:{0}".format(body))
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
    else:
      data['Exception'] = 'NILHOST'
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Success sending to notprocessed Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
      else:
        logit(logobj, "error", "Error Sending to notprocessed Q:{0}".format(body))
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return

queue_name = "gethostinformation"
binding_key = "automation.check_host_status"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

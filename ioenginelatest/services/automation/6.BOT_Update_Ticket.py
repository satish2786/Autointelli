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
import requests
from services.utils.ConnWebSocket import pushToWebSocket
from services.utils import utils as ut


logobj = create_log_file("/var/log/autointelli/automationengine.log")
if not logobj:
  print("Not Able to create logfile")
  sys.exit(1)

logit(logobj, "info", "Started Update Ticket BOT")

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
    data['ticket_update_yn'] = 'N'
    pk_execution_id = data['pk_execution_id']
    ticket_id = data['ticket_id']
    alert_id = data['alert_id']
    currentepoch = getcurrentutcepoch()
    setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 3, int(currentepoch), 'Update Ticket and Worklog', 'GREEN')
    setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 3, int(currentepoch), 'Not able to update ticket due to network connectivity', 'RED')
    update_ticket_payload = {'TID': ticket_id}
    headers  = {'Content-Type': 'application/json'}
    update_ticket_request = requests.post("http://localhost:3890/admin/api/v2/itsm/changeWIPStatus", data=json.dumps(update_ticket_payload), headers=headers)
    if update_ticket_request.status_code == 200:
      #print(update_ticket_request.text)
      logit(logobj, "info", "Changed Status to WIP for ticket {0}".format(ticket_id))
      data['ticket_update_yn'] = 'Y'
    else:
      logit(logobj, "error", "Couldnt update ticket to WIP {0}".format(ticket_id))
    update_worklog_payload = {"TID" : ticket_id , "description": "This Ticket is Managed by Autointelli BOT, Moving Ticket to Work in Progress"}      
    update_worklog_request = requests.post("http://localhost:3890/admin/api/v2/itsm/updateWorklog", data=json.dumps(update_worklog_payload), headers=headers)
    if update_worklog_request.status_code == 200:
      jsonData = {'alertid': ut.int2Alert(alert_id), 'status_details': { 'status': 'In Progress' }}
      #print(jsonData)
      module, infotype, action = 'alert', 'json', 'update'
      dRet = pushToWebSocket(pModule=module, pInfoType=infotype, pData=jsonData, pAction=action)
      #print(update_worklog_request.text)
      data['ticket_update_yn'] = 'Y'
      logit(logobj, "info", "Added worklog to ticket {0}".format(ticket_id))
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
    else:
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
      logit(logobj, "error", "Couldnt Update Worklog to ticket {0}".format(ticket_id))
    output = ConnMQ.send2MQ("getrulesandbots", "automationengine", "automation.getrulesandbots", str(data)) 
    if output['result'] == 'success':
        logit(logobj, "info", "Success sending to getrulesandbots Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
    else:
        logit(logobj, "error", "Error Sending to getrulesandbots Q:{0}".format(body))
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
    

queue_name = "updateticket"
binding_key = "automation.update_ticket"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()


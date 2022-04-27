#!/usr/bin/env python

# Program to Validate all the required inputs from Event Management

import sys
import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file, logit
from services.utils import ConnMQ
import pika
from services.utils.aitime import getcurrentutcepoch
from ast import literal_eval
import requests
from services.utils.ConnWebSocket import pushToWebSocket
from services.utils import utils as ut
import services.utils.validator_many as vm


logobj = create_log_file("/var/log/autointelli/automationengine.log")
if not logobj:
  print("Not Able to create logfile")
  sys.exit(1)

logit(logobj, "info", "Started Create Ticket BOT")

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
    summary = data['description']
    notes  = data['notes']
    group = 'automation'
    pk_execution_id = data['pk_execution_id']
    alert_id = data['alert_id']
   
    createTicketPayload =  {'subject': summary, 'description': notes, 'group': group}
    headers = {'Content-Type' : 'Application/json'}
    try:
      ticRequest = requests.post("http://localhost:3890/admin/api/v2/itsm/createTicket", data=json.dumps(createTicketPayload), headers=headers)
    except Exception as e:
      print(str(e))
      data['Exception'] = 'CTFAILED'
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Success sending to notprocessed Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
      else:
        logit(logobj, "error", "Error Sending to notprocessed Q:{0}".format(body))
      return
    ticRequestOutput = json.loads(ticRequest.text)
    print(ticRequestOutput)
    if ticRequestOutput['Status']:
      ticket_id = ticRequestOutput['TID']
      data['ticket_id'] = ticket_id
      currentepoch = getcurrentutcepoch()
      insertTicketQuery = """insert into ai_ticket_details (fk_alert_id, ticket_no, ticket_status, created_date) VALUES ({0}, '{1}', 'Open', {2})""".format(alert_id, ticket_id, currentepoch)
      insertTicketResult = ConnPostgreSQL.returnInsertResult(insertTicketQuery)
      setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 1, int(currentepoch), 'Ticket Created', 'GREEN')
      
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      module, infotype, action = 'alert', 'json', 'update'
      jsonData = {'alertid': ut.int2Alert(alert_id), 'ticket_details': {'ticketid': ticket_id}}
      #print(jsonData)
      dRet = pushToWebSocket(pModule=module, pInfoType=infotype, pData=jsonData, pAction=action)
      if retESBResult["result"] == "success":
        output = ConnMQ.send2MQ("gethostinformation", "automationengine", "automation.check_host_status", str(data))
        if output['result'] == 'success':
          logit(logobj, "info", "Success sending to gethostinformation Q")
          ch.basic_ack(delivery_tag = method.delivery_tag)
          return
        else:
          logit(logobj, "error", "Error Sending to gethostinformation Q:{0}".format(body))
      else:
        data['Exception'] = 'CTFAILED'
        output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", str(data))
        if output['result'] == 'success':
          logit(logobj, "info", "Success sending to notprocessed Q")
          ch.basic_ack(delivery_tag = method.delivery_tag)
          return
        else:
          logit(logobj, "error", "Error Sending to notprocessed Q:{0}".format(body))
    else:
      currentepoch = getcurrentutcepoch()
      setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 1, int(currentepoch), 'Ticket Creation Failed', 'RED')
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
      data['Exception'] = 'CTFAILED'
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Success sending to notprocessed Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
      else:
        logit(logobj, "error", "Error Sending to gethostinformation Q:{0}".format(body))


queue_name = "createticket"
binding_key = "automation.create_ticket_id"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

# Program to Validate all the required inputs from Event Management
import services.utils.validator_many as vm
import os
import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file, logit
import sys
import pika
from services.utils.aitime import getcurrentutcepoch
from ast import literal_eval
import requests


logobj = create_log_file("/var/log/autointelli/automationengine.log")
if not logobj:
  print("Not Able to create logfile")
  sys.exit(1)

logit(logobj, "info", "Started Move Ticket BOT")

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
    pk_execution_id = data['pk_execution_id']
    ticket_id = data['ticket_id']
    ticket_group = data['ticket_group']

    move_ticket_payload = {'TID': ticket_id, 'group': ticket_group}
    headers  = {'Content-Type': 'Application/json'}
    resolve_ticket_request = requests.post("http://localhost:3890/admin/api/v2/itsm/moveTicket", data=json.dumps(move_ticket_payload), headers=headers)
    if resolve_ticket_request.status_code == 200:
      currentepoch = getcurrentutcepoch()
      setExecQuery_GREEN = """INSERT INTO ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 6, int(currentepoch), 'Moved ticket to Respective group', 'GREEN')
      setExeccResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      logit(logobj, "info", "Ticket Moved to the Respective Group:{0}".format(ticket_id))
    else:
      logit(logobj, "error", "Couldn't Move Ticket to Respective Group:{0}".format(ticket_id))
    ch.basic_ack(delivery_tag = method.delivery_tag)


queue_name = "moveticket"
binding_key = "automation.move_ticket"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

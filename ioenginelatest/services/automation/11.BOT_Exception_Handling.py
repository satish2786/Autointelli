#!/usr/bin/env python

# Program to Validate all the required inputs from Event Management
import services.utils.validator_many as vm
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file, logit
from services.utils import ConnMQ
import sys
import pika
from ast import literal_eval

logobj = create_log_file("/var/log/autointelli/automationengine.log")
if not logobj:
  print("Not Able to create logfile")
  sys.exit(1)

logit(logobj, "info", "Started Exception handling BOT")

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
    if not 'Exception' in data:
      ch.basic_ack(delivery_tag = method.delivery_tag)
      return 
    exception = data['Exception']
    if exception == 'CTFAILED':
      ch.basic_ack(delivery_tag = method.delivery_tag)
      return 
    elif exception == 'CAIDFAILED':
      ch.basic_ack(delivery_tag = method.delivery_tag)
      return 
    elif exception == 'INVALIDINPUT':
      ch.basic_ack(delivery_tag = method.delivery_tag)
      return
    elif exception == 'NONAUTOMATION':
      data['ticket_group'] = 'manual'
      output = ConnMQ.send2MQ("moveticket", "automationengine", "automation.move_ticket", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Sent to moveticket Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
      else:
        logit(logobj, "error", "not able to sent to moveticket Q")
    elif exception == 'RULEEXECFAILED':
      data['ticket_group'] = 'manual'
      output = ConnMQ.send2MQ("moveticket", "automationengine", "automation.move_ticket", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Sent to moveticket Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
      else:
        logit(logobj, "error", "not able to sent to moveticket Q") 
    elif exception == 'BOTEXECFAILED':
      data['ticket_group'] = 'manual'
      output = ConnMQ.send2MQ("moveticket", "automationengine", "automation.move_ticket", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Sent to moveticket Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
      else:
        logit(logobj, "error", "not able to sent to moveticket Q") 
    elif exception == 'RESOLVEFAILED':
      data['ticket_group'] = 'manual'
      output = ConnMQ.send2MQ("moveticket", "automationengine", "automation.move_ticket", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Sent to moveticket Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return
      else:
        logit(logobj, "error", "not able to sent to moveticket Q")
    elif exception =='NILHOST':
      data['ticket_group'] = 'manual'
      output = ConnMQ.send2MQ("moveticket", "automationengine", "automation.move_ticket", str(data))
      if output['result'] == 'success':
        logit(logobj, "info", "Sent to moveticket Q")
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return 
      else:
        logit(logobj, "error", "not able to sent to moveticket Q")
    else:
      print(exception) 
      ch.basic_ack(delivery_tag = method.delivery_tag)
      return
   

queue_name = "notprocessed"
binding_key = "automation.notprocessed"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

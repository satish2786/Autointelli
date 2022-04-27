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
from airules import get_rules
from services.utils.ConnWebSocket import pushToWebSocket
from services.utils import utils as ut

logobj = create_log_file("/var/log/autointelli/automationengine.log")
if not logobj:
  print("Not Able to create logfile")
  sys.exit(1)

logit(logobj, "info", "Started BOT Identification BOT")

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
    data['bot_ids'] = []
    data['rule_ids'] = []
    pk_execution_id = data['pk_execution_id']
    ticket_id = data['ticket_id']
    alert_id = data['alert_id']
    ci_name = data['ci_name']
    Remediate = data['ci_remediate']
    if Remediate == 'Y':
      Remediate = 'R'
    else:
      Remediate = 'D'
    ci_platform = data['ci_platform']
    ci_os = data['ci_osname']
    component = data['component']
    currentepoch = getcurrentutcepoch()
    setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 4, int(currentepoch), 'Virtual Engineer available to fix this issue', 'GREEN')
    setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 3, int(currentepoch), 'No Virtual Engineers available to fix this Alert', 'RED')    
    ruleids = get_rules(ci_name, int(alert_id))
    if not ruleids or ruleids == '':
      getBOTQuery = """select pk_bot_id, bot_name from ai_bot_repo where bot_type='{0}' and platform_type='{1}' and os_type='{2}' and component='{3}'""".format(Remediate, ci_platform, ci_os, component)
      retBOTResult = ConnPostgreSQL.returnSelectQueryResult(getBOTQuery)
      print(getBOTQuery)
      print(retBOTResult)
      if retBOTResult["result"] == "success":
        for ids in retBOTResult['data']:
          updatebotQuery = """update ai_automation_executions set fk_bot_id={0} where pk_execution_id={1}""".format(ids['pk_bot_id'],pk_execution_id)
          updateQueryResult = ConnPostgreSQL.returnInsertResult(updatebotQuery)
          jsonData = {'alertid': ut.int2Alert(alert_id), 'bot_details': { 'botname': ids['bot_name'] }}
          module, infotype, action = 'alert', 'json', 'update'
          dRet = pushToWebSocket(pModule=module, pInfoType=infotype, pData=jsonData, pAction=action)
          data['bot_ids'].append(ids['pk_bot_id'])
      elif retBOTResult['data'] == 'no data':
        data['bot_ids'] = []
    elif ruleids:
      data['rule_ids'] = ruleids
    else:
      retInsertResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
      ch.basic_ack(delivery_tag = method.delivery_tag)
   
    #print(data)
    output = ConnMQ.send2MQ("executeautomation", "automationengine", "automation.execute_automation", str(data))
    if output['result'] == 'success':
        logit(logobj, "info", "Success sending to executeautomation Q")
    else:
        logit(logobj, "error", "Error Sending to executeautomation Q:{0}".format(body))
    
    retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
    ch.basic_ack(delivery_tag = method.delivery_tag)

    


queue_name = "getrulesandbots"
binding_key = "automation.getrulesandbots"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()


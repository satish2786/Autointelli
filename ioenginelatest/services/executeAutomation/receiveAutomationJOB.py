import os, json, logging, sys, pika
import services.utils.decoder as decoder
from services.utils import ConnPostgreSQL
from services.utils import ConnMQ
from services.utils.aitime import getcurrentutcepoch
from ast import literal_eval
from logging.handlers import TimedRotatingFileHandler
from executeAutomationJOB import *

#Logging
FORMATTER = logging.Formatter("%(asctime)s : %(name)s : %(levelname)s : %(message)s")
LOG_FILE = "/var/log/autointelli/receiveAutomationJOB.log"


def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler
def get_file_handler():
   file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=104857600, backupCount=5)
   file_handler.setFormatter(FORMATTER)
   return file_handler
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler())
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger

# Get Messageing Q Connection Details from the DB
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
  connection = pika.BlockingConnection(pika.ConnectionParameters(heartbeat=600, host=configip,credentials=credentials,virtual_host=vhost))
  channel = connection.channel()
except Exception as e:
  print("MQ Connection Issues")
  sys.exit(1)


# RabbitMQ Callback Method
def callback(ch, method, properties, body):
  try:
    body = body.decode('utf-8')
    data = literal_eval(body)
    my_logger = get_logger('ReceiveAutomation')
    my_logger.info("---------Receive Request----------")
    my_logger.info(data)
    fk_alert_id = data['alert_id']
    status = 'open'
    created_by = 'autointelli'
    modified_by = 'autointelli' 
    insertDataQuery = """insert into ai_bot_executions(fk_alert_id, input, status, createdby, modifiedby) VALUES ({0}, '{1}', '{2}', '{3}', '{4}') returning execid""".format(fk_alert_id, json.dumps(data), status, created_by, modified_by)
    retESBResult = ConnPostgreSQL.returnSelectQueryResultWithCommit(insertDataQuery)
    if retESBResult['result'] == 'success':
      my_logger.info(retESBResult)
      exec_id = retESBResult['data'][0]['execid']
      for flow in data['sp_flow']: 
        insertFlowQuery  = """insert into ai_bot_executions_history(fk_exec_id, input, createdby, modifiedby, status) VALUES ({0}, '{1}', 'autointelli', 'autointelli', 'new') returning pk_history_id""".format(exec_id, json.dumps(flow))
        insertFlowResult = ConnPostgreSQL.returnSelectQueryResultWithCommit(insertFlowQuery)
        history_id = insertFlowResult['data'][0]['pk_history_id']
        #Now Send the Task to Celery Workers
        result = executeAutomation.apply_async(args=[flow, history_id, data], connect_timeout=3)
        while result.ready() == False:
          time.sleep(5)
        return_data = result.get() 
        return_data = json.loads(return_data)
        automationOutput = getAutomationOutput.apply_async(args=[return_data['data'], history_id], connect_timeout=3)
        while automationOutput.ready() == False:
          time.sleep(5)
        return_data = automationOutput.get()
        return_data = json.loads(return_data)
        print(return_data)
        if return_data['result'] != 'success':
          print("BOT Failed")
          input()
    else:
      my_logger.error("Error in Inserting Data")
    my_logger.info("---------End Request----------")
    ch.basic_ack(delivery_tag = method.delivery_tag)
  except Exception as e:
    print(str(e))


queue_name = "executeautomation"
binding_key = "automation.execute_automation"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue_name, callback, auto_ack=False)
channel.start_consuming()

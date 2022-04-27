import sys, os, json, logging, psycopg2
from services.utils.decoder import decode
from logging.handlers import TimedRotatingFileHandler
from celery import Celery
import requests
import re
from services.utils import ConnPostgreSQL
import celery
import time

# Reading the configuration file for db connection string
conn = ""
data = json.load(open('/etc/autointelli/autointelli.conf'))
if not os.path.isfile('/etc/autointelli/autointelli.conf'):
  print(" [x] Worker Cannot Start, Config not found")
  sys.exit(1)
dbuser = data['maindb']['username']
dbname = data['maindb']['dbname']
dbhost = data['maindb']['dbip']
dbport = data['maindb']['dbport']

# Decoding the Password
maindbpassword = decode('auto!ntell!',data['maindb']['password'])

# Adding the Logging Configurations
#Logging
FORMATTER = logging.Formatter("%(asctime)s : %(name)s : %(levelname)s : %(message)s")
LOG_FILE = "/var/log/autointelli/executeAutomationJOB.log"


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



# Get MQ Connections
conn = psycopg2.connect(database=dbname, user=dbuser, password=maindbpassword, host=dbhost, port=dbport)
conn.autocommit = True
cur = conn.cursor()
cur.execute('select configip,configport,dbname,username,password from configuration where configname=\'MQ\'')
esbdata = cur.fetchall()
esbdata = esbdata[0]
esbip = esbdata[0]
esbuser = esbdata[3]
esbpass = esbdata[4]
vhost = esbdata[2]
esbpass = decode('auto!ntell!',esbpass)


# Create the app and set the broker location (RabbitMQ)
app = Celery('executeAutomationJOB',
             broker='pyamqp://{0}:{1}@{2}/{3}'.format(esbuser, esbpass, esbip, vhost),
             backend = 'db+postgresql://{0}:{1}@{2}:{3}/{4}'.format(dbuser, maindbpassword, dbhost, dbport, dbname),
             result_persistent = True, timeout=10)


@app.task
def executeAutomation(flow, rowid, main_data):
  try:
    my_logger = get_logger('ExecuteAutomation')
    my_logger.info("---------Receive Request----------")
    URL = flow['api']
    payload = flow['payload']
    for key in payload.keys():
      matches = re.findall(r'(@@.*?@@)',payload[key])
      for match in matches:
        if match in main_data['var_extracts']:
          payload[key] = payload[key].strip().replace(match,main_data['var_extracts'][match])
        elif '@@machine@@' in match or '@@application@@' in match or '@@value@@' in match or '@@cmdline@@' in match or '@@description@@' in match or '@@extra_description@@' or '@@day_time@@' in match:
          default_key = re.search(r'@@(.*)@@',match).groups()[0]
          payload[key] = payload[key].replace(match,main_data[default_key])
      NAME =flow['name']
      my_logger.info(URL)
      my_logger.info(payload)
      headers = {'Content-Type': 'Application/json'}
      output = requests.post(URL, headers=headers, data=json.dumps(payload), verify=False)
      output = json.loads(output.text)
      my_logger.info(output)
      if output['status'] == 'success':
        # Change rowid to in Progress
        rowUpdateQuery = """update ai_bot_executions_history set status='In Progress' where pk_history_id={0}""".format(int(rowid))
        returnUpdateResult = ConnPostgreSQL.returnInsertResult(rowUpdateQuery)
        my_logger.info("Execution of Bot Initiated, Waiting for Output...")
        response = output['response']
        response_uuid = response.split('Procss started with id')[1]
        rowUpdateQuery = """update ai_bot_executions_history set processuuid='{0}' where pk_history_id={1}""".format(response_uuid,int(rowid))
        returnUpdateResult = ConnPostgreSQL.returnInsertResult(rowUpdateQuery)
        #celery.current_app.send_task('executeAutomationJOB.getAutomationOutput', args=[response_uuid, rowid])
      else:
        my_logger.error("Critical, Automation Engine is down")
        return json.dumps({'result': 'failure'})
    return json.dumps({'result': 'success', 'data': response_uuid})
  except Exception as e:
    return json.dumps({'result': 'failure' + str(e)})


@app.task
def getAutomationOutput(processuuid, rowid):
  try:
    getESBQuery = """select connectedprocessid,status from processexecutionhistory where executionid='{0}'""".format(processuuid)
    toggle = 0
    while toggle == 0:
      retESBResult = ConnPostgreSQL.returnSelectQueryResult(getESBQuery, sDB='jcentral')
      if retESBResult["result"] == "success":
        toggle = 1
        pInstanceID = retESBResult['data'][0]['connectedprocessid']
        if pInstanceID != 'undefined':
          #Update Pinstanceid in table
          updateInstanceQuery="""update ai_bot_executions_history set processinstanceid={0} where processuuid='{1}'""".format(int(pInstanceID), processuuid)
          ConnPostgreSQL.returnInsertResult(updateInstanceQuery)
        print("Process Instance ID is : "+ str(pInstanceID))
      else:
        print("Yet to Receive Output, Looping...")
      time.sleep(5)
    #Now Connect to KieServer to Retrieve the Process Output
    getProcessStatus = """select status from processinstancelog where processinstanceid={0}""".format(int(pInstanceID))
    toggle = 0
    while toggle == 0:
      getProcessResult = ConnPostgreSQL.returnSelectQueryResult(getProcessStatus, sDB='jbpm')
      if getProcessResult['result'] == 'success':
        status = getProcessResult['data'][0]['status']
        if status == 2:
          toggle = 1
        else:
          print("Waiting for Process to be completed => " + str(status))
      else:
        print("error in DB Connection")
        return json.dumps({'result': 'failure'})
      time.sleep(3)
    getESBQuery = """select value from variableinstancelog where variableid='autointelli_log' and processinstanceid={0};""".format(int(pInstanceID))
    retESBResult = ConnPostgreSQL.returnSelectQueryResult(getESBQuery, sDB='jbpm')
    execOutput = ""
    execErr = ""
    #Get Output Variables
    if retESBResult["result"] == "success":
      for output in retESBResult['data']:
        print(output['value'])
        execOutput += "\n" + output['value']
      #Insrt into bot_execution_history table
      updateHistoryQuery="""update ai_bot_executions_history set output='{0}', status='Completed' where pk_history_id='{1}'""".format(execOutput, rowid)
      output = ConnPostgreSQL.returnInsertResult(updateHistoryQuery)
      return json.dumps({'result': 'success'})

    # Checking for 
    getErrorQuery = """select value from variableinstancelog where variableid='autointelli_err' and processinstanceid={0};""".format(int(pInstanceID))
    retErrorResult = ConnPostgreSQL.returnSelectQueryResult(getErrorQuery, sDB='jbpm')
    if retErrorResult['result'] == 'success':
      for output in retErrorResult['data']:
        print(output['value'])
        execErr += "\n" + output['value']
      #Insrt into bot_execution_history table
      updateHistoryQuery="""update ai_bot_executions_history set error='{0}', status='Failed' where pk_history_id='{1}'""".format(execErr, rowid)
      output = ConnPostgreSQL.returnInsertResult(updateHistoryQuery)
      return json.dumps({'result': 'failure'})
   
    #No Execution Output
    updateHistoryQuery="""update ai_bot_executions_history set output='{0}', status='Completed' where pk_history_id='{1}'""".format('No Output Returned from the BOT', rowid)
    output = ConnPostgreSQL.returnInsertResult(updateHistoryQuery)
    return json.dumps({'result': 'success'})
  except Exception as e:
    return json.dumps({'result': 'failure', 'data': str(e)})

if __name__ == "__main__":
    argv = ['worker', '--loglevel=info', '-n aiworker@autointelli']
    app.worker_main(argv)

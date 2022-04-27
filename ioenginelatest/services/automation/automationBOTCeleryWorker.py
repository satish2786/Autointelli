import sys
sys.path.append("../")
from celery import Celery
import json
import requests
from services.utils.decoder import decode, encode
import services.utils.validator_many as vm
from services.utils import ConnPostgreSQL
from services.utils.vmDiagnostics import esxiHostCPU
from services.utils import ConnMQ
from services.utils.aitime import getcurrentutcepoch
from airules import get_rules
from ast import literal_eval
from logging.handlers import TimedRotatingFileHandler
import os
import logging
import psycopg2

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
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
handler = TimedRotatingFileHandler('/data/autointelli/autodiagnose.log', when='midnight', interval=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


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
app = Celery('automationBOTCeleryWorker',
             broker='pyamqp://{0}:{1}@{2}/{3}'.format(esbuser, esbpass, esbip, vhost),
             backend = 'db+postgresql://{0}:{1}@{2}:{3}/{4}'.format(dbuser, maindbpassword, dbhost, dbport, dbname),
             result_persistent = True)

@app.task
def autodiagnose(data=None):
  try:
    logger.info("----------Auto Diagnose Started----------")
    lAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source", "alert_id"]
    lMandatoryAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source", "alert_id"]
    X = vm.isPayloadValid(dPayload=data, lHeaders=lAttr, lMandatory=lMandatoryAttr)
    if not X:
      logger.error("Validating Inputs : [Failed]")
      data['Exception'] = 'INVALIDINPUT'
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", json.dumps(data))
      if output['result'] == 'success':
        logger.info("Send to Not Proceesed Q : [OK]")
        logger.info("----------Auto Diagnose Ended----------")
        return
      else:
        logger.error("Send to Not Proceesed Q : [Failed]")
        logger.info("----------Auto Diagnose Ended----------")
        return
    logger.info("Validating Inputs : [OK]")
    getESBQuery = """select automated from ai_automation_type"""
    retESBResult = ConnPostgreSQL.returnSelectQueryResult(getESBQuery)

    if retESBResult["result"] == "success":
      automation_yn = retESBResult['data'][0]['automated']

    if automation_yn == 'Y':
      logger.info("Automated Diagnostics : [OK]")
    else:
      logger.info("Automated Diagnostics : [NO]")
      return
    alert_id = data['alert_id']
    currentepoch = getcurrentutcepoch()
    getESBQuery = """INSERT into ai_automation_executions(fk_alert_id, execution_status, starttime) VALUES ({0}, '{1}', {2}) RETURNING pk_execution_id""".format(int(alert_id), 'New', int(currentepoch))
    retESBResult = ConnPostgreSQL.returnSelectQueryResultWithCommit(getESBQuery)
    if retESBResult["result"] == "success":    
      pk_execution_id = retESBResult['data'][0]['pk_execution_id']  
      logger.info("Automation ID : [{0}]".format(str(pk_execution_id)))
    else:
      logger.info("Automation ID : [Failed]")
      data['Exception'] = 'CAIDFAILED'
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", json.dumps(data))
      if output['result'] == 'success':
        logger.info("Send to Not Proceesed Q : [OK]")
        logger.info("----------Auto Diagnose Ended----------")
        return
      else:
        logger.error("Send to Not Proceesed Q : [Failed]")
        logger.info("----------Auto Diagnose Ended----------")
        return
    checkTicketAutomation = requests.get("http://localhost:3890/admin/api/v2/ticketAutomation")
    output = json.loads(checkTicketAutomation.text)
    if output['Status']:
      if output['automated'] == 'N':
        logger.info("Automated Ticket  : [NO]")
        setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 1, int(currentepoch), 'Ticket Automation is set to NO', 'GREEN')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      else:
        logger.info("Automated Ticket  : [YES]")
        try:
          summary = data['description']
          notes  = data['notes']
          group = 'automation'
          createTicketPayload =  {'subject': summary, 'description': notes, 'group': group}
          headers = {'Content-Type' : 'Application/json'}
          ticRequest = requests.post("http://localhost:3890/admin/api/v2/itsm/createTicket", data=json.dumps(createTicketPayload), headers=headers)
          ticRequestOutput = json.loads(ticRequest.text)
          if ticRequestOutput['Status']:
            ticket_id = ticRequestOutput['TID']
            logger.info("Ticket ID  : {0}".format(ticketid))
            currentepoch = getcurrentutcepoch()
            insertTicketQuery = """insert into ai_ticket_details (fk_alert_id, ticket_no, ticket_status, created_date) VALUES ({0}, {1}, 'Open', {2})""".format(alert_id, ticket_id, currentepoch)
            insertTicketResult = ConnPostgreSQL.returnInsertResult(insertTicketQuery)
            setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 1, int(currentepoch), 'Ticket Created', 'GREEN')
            retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
          else:
            logger.info("Ticket ID  : [Failed]")
            currentepoch = getcurrentutcepoch()
            setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 1, int(currentepoch), 'Ticket Creation Failed', 'RED')
            retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
            raise Exception('Create Ticket Failed')
        except Exception as e:
          logger.error("Create Ticket Exception : "+str(e))
          data['Exception'] = 'CTFAILED'
          logger.error("Ticket ID  : [Failed]")
          output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", json.dumps(data))
          if output['result'] == 'success':
            logger.info("Send to Not Proceesed Q : [OK]")
            logger.info("----------Auto Diagnose Ended----------")
            return
          else:
            logger.error("Send to Not Proceesed Q : [Failed]")
            logger.info("----------Auto Diagnose Ended----------")
            return
    else:
      logger.error("Automated Ticket  : [FAILED]")
    #Host Exist
    currentepoch = getcurrentutcepoch()
    setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 2, int(currentepoch), 'HOST Exist', 'GREEN')
    setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 2, int(currentepoch), 'HOST not availale in Vault', 'RED')
    ci_name = data['ci_name']
    getHostQuery = """SELECT platform, osname, osversion, remediate from ai_machine where lower(machine_fqdn)='{0}'""".format(ci_name.lower())
    setHostQueryResult = ConnPostgreSQL.returnSelectQueryResult(getHostQuery)
    if setHostQueryResult['result'] == 'success':
      logger.info("Host Exist  : [OK]")
      ci_platform = setHostQueryResult['data'][0]['platform']
      ci_osname = setHostQueryResult['data'][0]['osname']
      ci_version = setHostQueryResult['data'][0]['osversion']
      ci_remediate = setHostQueryResult['data'][0]['remediate']
      component = data['component']
      data['ci_platform'] = ci_platform
      data['ci_osname'] = ci_osname
      data['ci_version'] = ci_version
      data['ci_remediate'] = ci_remediate
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
    else:
      logger.error("Host Exist  : [Failed]")
      data['Exception'] = 'NILHOST'
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
      output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", json.dumps(data))
      if output['result'] == 'success':
        logger.info("Send to Not Proceesed Q : [OK]")
        logger.info("----------Auto Diagnose Ended----------")
        return
      else:
        logger.error("Send to Not Proceesed Q : [Failed]")
        logger.info("----------Auto Diagnose Ended----------")
        return
    # Check Rules or BOTS
    currentepoch = getcurrentutcepoch()
    setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 3, int(currentepoch), 'Virtual Engineer available to fix this issue', 'GREEN')
    setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 3, int(currentepoch), 'No Virtual Engineers available to fix this Alert', 'RED') 
    ruleids = get_rules(ci_name, int(alert_id))
    if not ruleids or ruleids == '':
      logger.info("Custom Rules  : [NO]")
      retInsertResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
      getBOTQuery = """select pk_bot_id, bot_name from ai_bot_repo where bot_type='{0}' and platform_type='{1}' and os_type='{2}' and component='{3}'""".format(ci_remediate, ci_platform, ci_osname, component)
      retBOTResult = ConnPostgreSQL.returnSelectQueryResult(getBOTQuery)
      if retBOTResult["result"] == "success":
        logger.info("Bots Available  : [YES]")
        for ids in retBOTResult['data']:
          updatebotQuery = """update ai_automation_executions set fk_bot_id={0} where pk_execution_id={1}""".format(ids['pk_bot_id'],pk_execution_id)
          updateQueryResult = ConnPostgreSQL.returnInsertResult(updatebotQuery)
          data['bot_ids'].append(ids['pk_bot_id'])
          retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      elif retBOTResult['data'] == 'no data':
        logger.info("Bots Available  : [NO]")
        data['bot_ids'] = []
    elif ruleids:
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      logger.info("Custom Rules  : [YES]")
      data['rule_ids'] = ruleids
    else:
      logger.info("Bots Available  : [NO]")
      retInsertResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
    # Update Ticket
    checkTicketAutomation = requests.get("http://localhost:3890/admin/api/v2/ticketAutomation")
    output = json.loads(checkTicketAutomation.text)
    if output['Status']:
      if output['automated'] == 'N':
        logger.error("Automated Update Ticket  : [NO]")
        setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 4, int(currentepoch), 'Ticket Automation is set to NO', 'GREEN')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      else:
        logger.info("Automated Update Ticket  : [YES]")
        currentepoch = getcurrentutcepoch()
        setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 4, int(currentepoch), 'Update Ticket and Worklog', 'GREEN')
        setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 4, int(currentepoch), 'Not able to update ticket due to network connectivity', 'RED')
        update_ticket_payload = {'TID': ticket_id}
        headers  = {'Content-Type': 'application/json'}
        update_ticket_request = requests.post("http://localhost:3890/admin/api/v2/itsm/changeWIPStatus", data=json.dumps(update_ticket_payload), headers=headers)
        if update_ticket_request.status_code == 200:
          logger.info("Update Ticket  : [YES]")
          retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
        else:
          retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
    else:
      logger.error("Automated Update Ticket  : [Failed]")
      retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
    # Execute BOT
    if component == 'ESX HOST CPU':
      output = esxiHostCPU(ci_name,'root','V!CTOR1E$.') 
      if output['Status']:
        logger.error("Execute Automation  : [OK]")
        updateAutomationTable = """update ai_automation_executions set execution_status='Completed' where pk_execution_id={0}""".format(pk_execution_id)
        retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
        currentepoch = getcurrentutcepoch()
        Green_Var = encode('auto!ntell!',"Host with High CPU Usages\n"+output['Data'])
        setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Green_Var, 'GREEN')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      else:
        logger.error("Execute Automation  : [Failed]")
        updateAutomationTable = """update ai_automation_executions set execution_status='Failed' where pk_execution_id={0}""".format(pk_execution_id)
        retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
        currentepoch = getcurrentutcepoch()
        Red_Var = encode('auto!ntell!',"No Virtual Engineers Found")
        setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Red_Var, 'RED')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
    elif component == 'ESX HOST MEM':
      output = esxiHostMEM(ci_name,'root','V!CTOR1E$.')
      if output['Status']:
        logger.error("Execute Automation  : [OK]")
        updateAutomationTable = """update ai_automation_executions set execution_status='Completed' where pk_execution_id={0}""".format(pk_execution_id)
        retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
        currentepoch = getcurrentutcepoch()
        Green_Var = encode('auto!ntell!',"Host with High MEM Usages\n"+output['Data'])
        setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Green_Var, 'GREEN')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      else:
        logger.error("Execute Automation  : [Failed]")
        updateAutomationTable = """update ai_automation_executions set execution_status='Failed' where pk_execution_id={0}""".format(pk_execution_id)
        retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
        currentepoch = getcurrentutcepoch()
        Red_Var = encode('auto!ntell!',"No Virtual Engineers Found")
        setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Red_Var, 'RED')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
    elif component == 'ESX HOST NET':
      output = esxiHostNET(ci_name,'root','V!CTOR1E$.')
      if output['Status']:
        logger.error("Execute Automation  : [OK]")
        updateAutomationTable = """update ai_automation_executions set execution_status='Completed' where pk_execution_id={0}""".format(pk_execution_id)
        retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
        currentepoch = getcurrentutcepoch()
        Green_Var = encode('auto!ntell!',"Host with High NET Usages\n"+output['Data'])
        setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Green_Var, 'GREEN')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      else:
        logger.error("Execute Automation  : [Failed]")
        updateAutomationTable = """update ai_automation_executions set execution_status='Failed' where pk_execution_id={0}""".format(pk_execution_id)
        retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
        currentepoch = getcurrentutcepoch()
        Red_Var = encode('auto!ntell!',"No Virtual Engineers Found")
        setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Red_Var, 'RED')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
    else:
      pass 
    # Resolve
    checkTicketAutomation = requests.get("http://localhost:3890/admin/api/v2/ticketAutomation")
    output = json.loads(checkTicketAutomation.text)
    if output['Status']:
      if output['automated'] == 'N':
        logger.info("Automated Resolve Ticket  : [NO]")
        setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 6, int(currentepoch), 'Ticket Automation is set to NO', 'GREEN')
        retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
      else:
        logger.info("Automated Resolve Ticket  : [YES]")
        resolve_ticket_payload = {'TID': ticket_id}
        headers  = {'Content-Type': 'Application/json'}
        resolve_ticket_request = requests.post("http://localhost:3890/admin/api/v2/itsm/changeResolvedStatus", data=json.dumps(resolve_ticket_payload), headers=headers)
    else:     
      logger.error("Automated Ticket  : [NO]")
    logger.info("----------Auto Diagnose Ended----------")
  except Exception as e:
    logger.error("Main Exception : " +str(e))
    logger.info("----------Auto Diagnose Ended----------")
    return False
if __name__ == "__main__":
    argv = ['worker', '--loglevel=info', '-n automationworker@nxtgen']
    app.worker_main(argv)

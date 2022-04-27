import services.utils.validator_many as vm
import os
import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file, logit
from services.utils import ConnMQ
import sys
import pika
from services.utils.aitime import getcurrentutcepoch
from ast import literal_eval
import subprocess
import requests


logobj = create_log_file("/var/log/autointelli/automationengine.log")
if not logobj:
  print("Not Able to create logfile")
  sys.exit(1)

logit(logobj, "info", "Started Automation Execution BOT")

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
  try:
    logit(logobj,"info", body)
    body = body.decode('utf-8')
    data = literal_eval(body)
    ruleids = data['rule_ids']
    botids = data['bot_ids']
    pk_execution_id = data['pk_execution_id']
    component = data['component']
    Platform = data['ci_platform']
    ciname = data['ci_name']
    KPI = data['component_value']
    alert_id = data['alert_id']
    if ruleids:
      os.environ["ANSIBLE_VAULT_PASSWORD_FILE"] = "/usr/local/autointelli/ioengine/services/cmdb/.secrets/.vaultpassdb"
      for ruleid in ruleids:
        getRuleQuery = """SELECT action, actioncommand, actionargs from rules where ruleid={0}""".format(int(ruleid))
        retRuleResult = ConnPostgreSQL.returnSelectQueryResult(getRuleQuery)  
        if retRuleResult["result"] == "success":
          action = retRuleResult['data'][0]['action']
          actioncommand = retRuleResult['data'][0]['actioncommand']
          actionargs = retRuleResult['data'][0]['actionargs']
          execute_file = "/tmp/execute/"+str(pk_execution_id) + "_" + component
          if action == 'REMOTE SCRIPT':
            if Platform == 'Linux':
              getBOTQuery = """SELECT script, botargs, pk_bot_id from ai_bot_repo where component='REMOTE SCRIPT' and platform_type='Linux'"""
              getBOTResult =  ConnPostgreSQL.returnSelectQueryResult(getBOTQuery)
              script = getBOTResult['data'][0]['script']
              script = decoder.decode('auto!ntell!',script)
              botargs = getBOTResult['data'][0]['botargs']
              botid = getBOTResult['data'][0]['pk_bot_id']
              command = """ANSIBLE_STDOUT_CALLBACK=json ansible-playbook -i /usr/local/autointelli/ioengine/services/cmdb/inventory.py {2} -e "script_name={0}" --limit {1} """.format(actioncommand, ciname, execute_file)
              mList = [int(e) if e.isdigit() else e for e in actionargs.split(',')]
              find_string = "command: \"{{ script_name }}"
              for arguments in mList:
                argskey = arguments.replace(" ","_")
                command = command + " -e \'" + argskey + "=\"" + arguments + "\"\'"
                replace_string = find_string + " {{ "+argskey+"|quote }}"
                script = script.replace(find_string, replace_string)
                find_string = replace_string
              with open(execute_file, 'w') as fh:
                fh.write(script)
              print(command)
              process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
              output = process.communicate()
              output = output[0].decode('utf8')
              try:
                output = json.loads(output)
              except:
                output = json.loads(output[output.index('\n')+1:])
              retcode = output['plays'][0]['tasks'][0]['hosts'][ciname]['rc']
              if retcode != 0:
                updateAutomationTable = """update ai_automation_executions set execution_status='Failed' where pk_execution_id={0}""".format(pk_execution_id)
                retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
                data['Exception'] = 'RULEEXECFAILED'
                MSG = output['plays'][0]['tasks'][0]['hosts'][ciname]['msg']
                currentepoch = getcurrentutcepoch()
                Red_Var = decoder.encode('auto!ntell!',"Virtual Engineer Cannot Execute Policies, Kindly check the Policies\n"+MSG)
                setExecQuery_RED = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Red_Var, 'RED')
                retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_RED)
                output = ConnMQ.send2MQ("notprocessed", "automationengine", "automation.notprocessed", str(data))
                if output['result'] == 'success':
                    logit(logobj, "info", "Sent to Notprocessed Q")
                else:
                    logit(logobj, "error", "Error Sending to NotProcessed  Q:{0}".format(body))
                ch.basic_ack(delivery_tag = method.delivery_tag)
              else:
                updateAutomationTable = """update ai_automation_executions set execution_status='Completed' where pk_execution_id={0}""".format(pk_execution_id)
                retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
                currentepoch = getcurrentutcepoch()
                stdout = output['plays'][0]['tasks'][0]['hosts'][ciname]['stdout']
                stderr = output['plays'][0]['tasks'][0]['hosts'][ciname]['stderr']
                changed = output['plays'][0]['tasks'][0]['hosts'][ciname]['changed']
                time_taken = output['plays'][0]['tasks'][0]['hosts'][ciname]['delta']
                MSG = "stdout : " +stdout + "\nstderr : " + stderr + "\nchanged :  " + str(changed) + "\nreturn code : " + str(retcode) + "\nTime Taken : "+time_taken
                data['BOT_Comments'] = MSG
                Green_Var = decoder.encode('auto!ntell!',"Virtual Engineer Executed the User Defined Script through Policy Window\n"+MSG)
                setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Green_Var, 'GREEN')
                retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
                output = ConnMQ.send2MQ("resolveticket", "automationengine", "automation.resolve_ticket", str(data))
                if output['result'] == 'success':
                    logit(logobj, "info", "Sent to resolveticket Q")
                else:
                    logit(logobj, "error", "Error Sending to resolvetikcet  Q:{0}".format(body))
                ch.basic_ack(delivery_tag = method.delivery_tag)
          elif action == 'LOCAL SCRIPT':
            """Ansible playbook to call a local script here"""
          elif action == 'SEND SMS':
            """ SEND SMS CODE HERE"""
          elif action == 'EMAIL':
            """ ANSIBLE COMMAND to send email here"""
          else:
            logger.error("Unknown Action")
    elif botids:
      for botid in botids:
        getBOTQuery = """SELECT script, bot_language, botargs from ai_bot_repo where pk_bot_id={0}""".format(botid)
        getBOTResult =  ConnPostgreSQL.returnSelectQueryResult(getBOTQuery)
        script = getBOTResult['data'][0]['script']
        lang = getBOTResult['data'][0]['bot_language']
        script = script.replace("#@#component_value#@#",KPI)
        print(script)
        payload = {'LANG': lang, 'LANG_VERSION': '', 'SCRIPT': script, 'VARS': {'autointelli_log': '', 'target': ciname}}
        headers = {'Content-Type': 'application/json'}
        output = requests.post('http://127.0.0.1:5001/ui/api1.0/execscript',headers=headers,data=json.dumps(payload))
        stdout = json.loads(output.text)
        if stdout['status'] == "true":
           result = stdout['result']['autointelli_log']
           if result == "":
             result = "Remote Execution Success, But Received an empty STDOUT"
           data['BOT_Comments'] = "Remote Execution Successfull \r\n " + result
           updateAutomationTable = """update ai_automation_executions set execution_status='Completed' where pk_execution_id={0}""".format(pk_execution_id)
           retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
           currentepoch = getcurrentutcepoch()
           Green_Var = decoder.encode('auto!ntell!',result)
           setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Green_Var, 'GREEN')
           retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
           output = ConnMQ.send2MQ("resolveticket", "automationengine", "automation.resolve_ticket", str(data))
           ch.basic_ack(delivery_tag = method.delivery_tag)
        else:
          data['BOT_Comments'] = "Remote Execution Failed \r\n"
          updateAutomationTable = """update ai_automation_executions set execution_status='Completed' where pk_execution_id={0}""".format(pk_execution_id)
          retupdateResult = ConnPostgreSQL.returnInsertResult(updateAutomationTable)
          currentepoch = getcurrentutcepoch()
          Green_Var = decoder.encode('auto!ntell!',"Remote Execution Failed")
          setExecQuery_GREEN = """insert into ai_automation_execution_history(fk_execution_id, fk_stage_id, starttime, output, status) VALUES ({0}, {1}, {2}, '{3}', '{4}')""".format(pk_execution_id, 5, int(currentepoch), Green_Var, 'RED')
          retESBResult = ConnPostgreSQL.returnInsertResult(setExecQuery_GREEN)
          output = ConnMQ.send2MQ("resolveticket", "automationengine", "automation.resolve_ticket", str(data))
          ch.basic_ack(delivery_tag = method.delivery_tag)
  except Exception as e:
    print(str(e))


queue_name = "executeautomation"
binding_key = "automation.execute_automation"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

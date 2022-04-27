# Main Engine for Automation
# Author : anand@autointelli.com

from services.utils.decoder import decode
import json, logging, psycopg2, pika
import sys, os, time
from services.utils import ConnPostgreSQL

# Reading the configuration file for db connectionection string
connection = ""
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

# Get MQ Connections
connection = psycopg2.connect(database=dbname, user=dbuser, password=maindbpassword, host=dbhost, port=dbport)
connection.autocommit = True
cur = connection.cursor()

def get_value_rules(hostname,conds,autoid):
  try:
    key = conds['Key']
    value = conds['value']
    operator = conds['operator']
    cur.execute("""SELECT mappingname from RuleMeta where componentname='{0}'""".format(key))
    rows = cur.fetchone()
    if rows is None:
      return False
    table, column = rows[0].split(".")
    if table == 'ai_machine':
      getRuleKeys = """select {1} from ai_machine where machine_fqdn='{0}'""".format(hostname, column)
      retRuleResult = ConnPostgreSQL.returnSelectQueryResult(getRuleKeys)
      for data in retRuleResult['data']:
        if operator == 'equal':
          if (data[column]) == value:
            return True
          else:
            return False
        elif operator == 'not equals':
          if (data[column]) != value:
            return True
          else:
            return False
        elif operator == 'contains':
          if value in (data[column]):
            return True
          else:
            return False
        else:
          return False
    elif table == 'alert_data':
      cur.execute("""select {0} from alert_data where pk_alert_id={1}""".format(column, int(autoid)))
      rows = cur.fetchone()
      data = rows[0]
      if operator == 'equal':
        if data == value:
          return True
        else:
          return False
      elif operator == 'not equals':
        if data != value:
          return True
        else:
          return False
      elif operator == 'contains':
        if value in data:
          return True
        else:
          return False
      else:
        return False
  except Exception as e:
    print(str(e))
    return False


def get_rules(hostname,autoid):
  try:
    cur.execute("""SELECT condition,action,actioncommand,actionargs,ruleid from rules where hostname='{0}' and status='Enabled'""".format(hostname))
    rows = cur.fetchall()
    rules = [] 
    for row in rows:
      condition = row[0]
      action = row[1]
      actioncommand = row[2]
      actionargs = row[3]
      ruleid = row[4]
      if 'ALL' in condition['Condition']:
        final_condition = []
        #print("All Condition has to be true")
        valuations = (condition['Condition']['ALL'])
        for conds in valuations:
          returncode = get_value_rules(hostname, conds, autoid)
          if returncode:
            final_condition.append(True)
          else:
            final_condition.append(False)
        if False in final_condition:
          pass
        else:
          rules.append(ruleid)
      elif 'ANY' in condition['Condition']:
        final_condition = []
        #print("Any Condition has to be true")  
        valuations = (condition['Condition']['ANY'])
        for conds in valuations:
          returncode = get_value_rules(hostname, conds, autoid)
          if returncode:
            final_condition.append(True)
          else:
            final_condition.append(False)
        if True in final_condition:
          rules.append(ruleid)
      #print(final_condition)
    return rules
  except Exception as e:
    return False


if __name__ == "__main__":
  hostname = "AIDEV-WINMEM"
  autoid = "1"
  rules = get_rules(hostname, int(autoid))
  print(rules)

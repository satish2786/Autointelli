#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import json
from services.utils import ConnPostgreSQL as pcon
import services.utils.decoder as decoder
from services.utils import utils as ut
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import services.utils.ConnMQ as connmq
import pika
from datetime import datetime as dt
import pytz
import re
from services.EAM import reservice as res
from decimal import Decimal
import traceback

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file("/var/log/autointelli/eventreceiver.log")
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return {"result": s, "data": x}

def singleQuoteIssue(value):
    if not type(value) == type(None):
        return value.replace("'", "''").strip()
    else:
        return ""

def getNextDay(day):
    if day == "mon":
        return "tue"
    if day == "tue":
        return "wed"
    if day == "wed":
        return "thu"
    if day == "thu":
        return "fri"
    if day == "fri":
        return "sat"
    if day == "sat":
        return "sun"
    if day == "sun":
        return "mon"

# dayIndex = {'sun':}

def whichIsGreater(a, b, position):
    db = dt(1, 1, 1, int(a.split(':')[0]), int(a.split(':')[1]))
    new = dt(1, 1, 1, int(b.split(':')[0]), int(b.split(':')[1]))
    if position == "start":
        if db <= new:
            return True
        else:
            return False
    elif position == "end":
        if db >= new:
            return True
        else:
            return False

def getPattern(p):
    dbPatterns = []
    dbs = p.split('__')[0].split('_')[0]
    dbe = p.split('__')[1].split('_')[0]
    if dbs == dbe:
        dbPatterns.append(dbs)
    elif getNextDay(dbs) == dbe:
        dbPatterns.extend([dbs, dbe])
    else:
        dbPatterns.append(dbs)
        while (not getNextDay(dbs) == dbe):
            dbPatterns.append(getNextDay(dbs))
            dbs = getNextDay(dbs)
        dbPatterns.append(dbe)
    return ",".join(dbPatterns)

def s2d(s):
    try:
        return Decimal(s)
    except Exception as e:
        return s

def Validate(pDBCond, pDBvalue, pNewvalue, pColumn=""):
    # Day & time - Check if i/p lies between the day time in database
    if pColumn == "day_time":
        if pDBCond == "between":
            pDBvalue, pNewvalue = pNewvalue, pDBvalue
            db = getPattern(pNewvalue)
            new = pDBvalue.split('_')[0]
            if db == new:
                s = whichIsGreater(pDBvalue.split('_')[1], pNewvalue.split('__')[0].split('_')[1], "start")
                e = whichIsGreater(pDBvalue.split('_')[1], pNewvalue.split('__')[1].split('_')[1], "end")
                return True if s == False and e == False else False
            elif db.__contains__(new):
                if db.startswith(new):
                    s = whichIsGreater(pDBvalue.split('_')[1], pNewvalue.split('__')[0].split('_')[1], "start")
                    return True if s == False else False
                elif db.endswith(new):
                    e = whichIsGreater(pDBvalue.split('_')[1], pNewvalue.split('__')[1].split('_')[1], "end")
                    return True if e == False else False
                else:
                    return True
            else:
                return False

    # Day & time - Check for conflicts
    # if pColumn == "day_time":
    #     if pDBCond == 'between':
    #         db = getPattern(pDBvalue)
    #         new = getPattern(pNewvalue)
    #         if db == new:
    #             s = whichIsGreater(pDBvalue.split('__')[0].split('_')[1], pNewvalue.split('__')[0].split('_')[1],
    #                                "start")
    #             e = whichIsGreater(pDBvalue.split('__')[1].split('_')[1], pNewvalue.split('__')[1].split('_')[1], "end")
    #             return True if s == True and e == True else False
    #         elif db.__contains__(new):
    #             if db.startswith(new):
    #                 s = whichIsGreater(pDBvalue.split('__')[0].split('_')[1], pNewvalue.split('__')[0].split('_')[1],
    #                                    "start")
    #                 return True if s == True else False
    #             elif db.endswith(new):
    #                 e = whichIsGreater(pDBvalue.split('__')[1].split('_')[1], pNewvalue.split('__')[1].split('_')[1],
    #                                    "end")
    #                 return True if e == True else False
    #             else:
    #                 return True
    #         else:
    #             return False

    # Other
    else:
        print("{0}:{1}:{2}".format(pDBvalue, pDBCond, pNewvalue))
        out = None
        if pDBCond == 'equal to':
            out = True if s2d(pDBvalue) == s2d(pNewvalue) else False
        elif pDBCond == 'contains':
            out = True if pDBvalue.__contains__(pNewvalue) else False
        elif pDBCond == 'starts with':
            out = True if pDBvalue.startswith(pNewvalue) else False
        elif pDBCond == 'ends with':
            out = True if pDBvalue.endswith(pNewvalue) else False
        elif pDBCond == 'not equals to':
            out = True if s2d(pDBvalue) != s2d(pNewvalue) else False
        elif pDBCond == 'greater than':
            print(pDBCond, s2d(pDBvalue), s2d(pNewvalue))
            out = True if s2d(pDBvalue) > s2d(pNewvalue) else False
        elif pDBCond == 'greater than equal':
            out = True if s2d(pDBvalue) >= s2d(pNewvalue) else False
        elif pDBCond == 'less than':
            out = True if s2d(pDBvalue) < s2d(pNewvalue) else False
        elif pDBCond == 'less than equal':
            out = True if s2d(pDBvalue) <= s2d(pNewvalue) else False
        elif pDBCond == 'regex':
            try:
                db_reg = pDBvalue
                new_reg = pNewvalue
                value = pNewvalue # alert_payload[pColumn]
                ret = res.validatePEAttribInternal({'pattern': db_reg, 'sample': value})
                if ret['result'] == 'success':
                    out = True
                else:
                    out = False
            except Exception as e:
                logERROR(str(e))
                out = False
        print(out)
        return out

def filtered(idd, alert_id):
    try:
        uQuery = "update policyengine set applied_to_alert_total = applied_to_alert_total + 1 where pk_pk_id={0}".format(idd)
        uuQuery = "update alert_data set fk_sop_id=(select pk_sop_id from sop where pe_id={0}) where pk_alert_id={1}".format(
            idd, alert_id)
        print(uQuery)
        print(uuQuery)
        uRet = pcon.returnInsertResult(uQuery)
        uuRet = pcon.returnInsertResult(uuQuery)
        logINFO('kb selected id: {0} for alert: {1}'.format(idd, alert_id))
        return {'result': 'success', 'data': 'increased filtered count by 1'}
    except Exception as e:
        logERROR('kb selected id: {0} for alert: {1} failed with {2}'.format(idd, alert_id, str(e)))
        return {'result': 'failure', 'data': 'Unable to filtered count by 1 because of {0}'.format(str(e))}

def getSPFlow(pe_id):
    try:
        sQuery = "select sop_flow from sop where pe_id={0}".format(pe_id)
        dRet = pcon.returnSelectQueryResult(sQuery)
        if dRet['result'] == 'success':
            return dRet['data'][0]['sop_flow']
        else:
            return {'result': 'failure', 'data': 'no data'}
    except Exception as e:
        return {'result': 'failure', 'data': 'no data'}

def processEvent(dPayload):
    """Method: This method is used to filter the events those were mentioned in event filter management"""
    try:
        lAttr = ["priority", "msg_updated_time", "machine", "application", "value", "cmdline", "description",
                 "extra_description", "severity", "source", "event_created_time", "customer_id", "alert_id",
                 "id", "asset_number", "region", "asset_state", "version", "package", "pac_ver", "pac_ver_no",
                 "msg_created_time", "status_update", "additional_props", "modified_by"]
        lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
        if not 0 in lPayErr:

            # tts = {'+10:00': 'Australia/Sydney'} # Add other timezones as well. Issue here is multiple zones comes for 1 timezone
            # dds = {0: 'sun', 1: 'mon', 2: 'tue', 3: 'wed', 4: 'thu', 5: 'fri', 6: 'sat'}
            # dt_tz = re.match("(.*)(\+\d{2}:\d{2})", dPayload['msg_updated_time'])
            # gDT, gTZ = dt_tz.group(1), dt_tz.group(2)
            # extractDT = dt.strptime(gDT.strip(), '%Y-%m-%d %H:%M:%S.%f0')
            # extractDT.astimezone(pytz.timezone(tts[gTZ.strip()]))
            # extractDT = dt.strptime(dPayload['Msg_updated_time'].strip(), '%m-%d-%Y %H:%M:%S')
            extractDT = dt.strptime(dPayload['msg_updated_time'].strip(), '%m-%d-%Y %H:%M:%S')
            dPayload['day_time'] = extractDT.strftime('%a_%H:%M').lower()

            # Batch processing
            iBatchQuery = "insert into batches_policyengine(alert_id, pe_id, batch_payload, sp_flow) values({0}, {1}, '{2}', '{3}')"

            # sQuery = "select * from policyengine where active_yn ='Y'"
            sQuery = "select * from policyengine where active_yn='Y' and pk_pk_id in(select pe_id from sop where active_yn ='Y' and status='approved')"
            dRet = pcon.returnSelectQueryResult(sQuery)

            # If no filters are available push the data directly to next level
            if dRet['result'] == 'failure':
                pushed2FE = connmq.send2MQ(pQueue='processevents', pExchange='automationengine', pRoutingKey='automation.processevents', pData=json.dumps(dPayload))
                return {'result': 'success'}

            # If filters are available undergo eamworker
            # setMain = {'Machine', 'Application', 'Description', 'Extra_Description', 'Value', 'Cmdline'}
            setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline', 'day_time',
                       'priority', 'id', 'asset_number', 'region', 'asset_state', 'version', 'package',
                       'pac_ver', 'pac_ver_no', 'status_update', 'status', 'additional_props', 'modified_by'
                       }
            # paymap = {'machine': 'Machine', 'application': 'Application', 'description': 'Description',
            #           'extra_description': 'Extra_Description', 'value': 'Value', 'cmdline': 'Cmdline',
            #           'day_time': 'day_time'}
            for eachF in dRet['data']:
                d = {i: eachF[i] for i in eachF if eachF[i] != '' and eachF[i] is not None}
                overall = d['overall']
                idd = d['pk_pk_id']
                batch_flag, batch_payload = 'N', {}
                if 'batch_flag' in d:
                    batch_flag = d['batch_flag']
                    batch_payload = d['batch_payload']
                print(batch_flag, batch_payload)
                out = []
                #extract vars
                vars, vars2bot = {}, {}
                if eachF['vars_payload'] != '':
                    vars = {i['Key']:i for i in eachF['vars_payload']['Condition'][overall]}
                for eachK in setMain:
                    if eachK + "_cond" in d.keys() and eachK + "_value" in d.keys():
                        inp = dPayload[eachK]
                        cond = d[eachK + "_cond"]
                        value = d[eachK + "_value"]
                        if eachK.lower().strip() == 'value':
                            out.append(Validate(cond, inp, value, eachK))
                        else:
                            out.append(Validate(cond, value, inp, eachK))
                        # extract vars
                        if cond.strip() == 'regex':
                            try:
                                # vars2bot[eachK] = {}
                                if len(vars[eachK]['groups']) > 0:
                                    ret = res.validatePEAttribInternal({'pattern': value, 'sample': inp})
                                    if ret['result'] == 'success':
                                        if len(ret['data']['groups']) > 0:
                                            # tmpextract = {}
                                            for x in range(0, len(ret['data']['groups'])):
                                                vars2bot[vars[eachK]['groups'][x]] = ret['data']['groups'][x]
                                            # vars2bot[eachK] = tmpextract
                            except Exception as e:
                                pass

                if overall == 'ALL':
                    if False in out:
                        continue
                    else:
                        dPayload['policy_id'] = idd
                        dPayload['sp_flow'] = getSPFlow(idd)
                        dPayload['var_extracts'] = vars2bot
                        dPayload = {i.lower(): dPayload[i] for i in dPayload}
                        if batch_flag == 'Y':
                            iQuery = iBatchQuery.format(dPayload['alert_id'], idd, json.dumps(batch_payload).replace("'", "''"),
                                                        json.dumps(dPayload).replace("'", "''"))
                            batchRet = pcon.returnInsertResult(iQuery)
                            return {'result': 'success'}
                        else:
                            pushed2FE = connmq.send2MQ(pQueue='executeautomation', pExchange='automationengine',
                                                   pRoutingKey='automation.execute_automation', pData=json.dumps(dPayload))
                            return filtered(idd, dPayload['alert_id'])
                elif overall == 'ANY':
                    if True in out:
                        dPayload['policy_id'] = idd
                        dPayload['sp_flow'] = getSPFlow(idd)
                        dPayload['var_extracts'] = vars2bot
                        dPayload = {i.lower(): dPayload[i] for i in dPayload}
                        if batch_flag == 'Y':
                            iQuery = iBatchQuery.format(dPayload['alert_id'], idd, json.dumps(batch_payload).replace("'", "''"),
                                                        json.dumps(dPayload).replace("'", "''"))
                            batchRet = pcon.returnInsertResult(iQuery)
                            return {'result': 'success'}
                        else:
                            pushed2FE = connmq.send2MQ(pQueue='executeautomation', pExchange='automationengine',
                                                   pRoutingKey='automation.execute_automation', pData=json.dumps(dPayload))
                            return filtered(idd, dPayload['alert_id'])
                    else:
                        continue

            # No filters matching so pushing to next level
            dPayload = {i.lower(): dPayload[i] for i in dPayload}
            pushed2FE = connmq.send2MQ(pQueue='processevents', pExchange='automationengine', pRoutingKey='automation.processevents', pData=json.dumps(dPayload))
            return {'result': 'success'}

        else:
            return logAndRet("failure", "Event KB: Either attributes are missing or attribute's values are empty: {0}".format(dPayload))
    except Exception as e:
        print(traceback.format_exc())
        return logAndRet("failure", "unable to apply KB, payload:{0} with Exception: {1}".format(dPayload, str(e)))

def callback(ch, method, properties, body):
    dPayload = json.loads(body.decode('utf-8'))
    print("Incoming events: {0}".format(dPayload))
    retJSON = processEvent(dPayload)
    print(retJSON)


try:
    # Get the details of MQ
    sIP, sUserName, sPassword = "", "", ""
    sQuery = "select configip ip, username, password from configuration where configname='MQ'"
    dRet = pcon.returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        sIP = dRet["data"][0]["ip"]
        sUserName = dRet["data"][0]["username"]
        sPassword = decoder.decode("auto!ntell!", dRet["data"][0]["password"])
    else:
        logERROR("unable to fetch information from configuration table")
        CERROR("unable to fetch information from configuration table")

    # declare credentials
    credentials = pika.PlainCredentials(sUserName, sPassword)
    # open connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=sIP, credentials=credentials, virtual_host='autointelli'))
    # create channel
    channel = connection.channel()
    # select queue
    channel.queue_declare(queue='pe_events', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='EVM', queue='pe_events')
    channel.basic_consume('pe_events', callback, auto_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Worker failed. Reason:" + str(e))
    CERROR("Worker failed. Reason:" + str(e))

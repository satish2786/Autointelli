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

def Validate(pDBCond, pDBvalue, pNewvalue):
    print("{0}:{1}:{2}".format(pDBvalue, pDBCond, pNewvalue))
    out = None
    if pDBCond == 'equal to':
        out = True if pDBvalue == pNewvalue else False
    elif pDBCond == 'contains':
        out = True if pDBvalue.__contains__(pNewvalue) else False
    elif pDBCond == 'starts with':
        out = True if pDBvalue.startswith(pNewvalue) else False
    elif pDBCond == 'ends with':
        out = True if pDBvalue.endswith(pNewvalue) else False
    elif pDBCond == 'not equal to':
        out = True if pDBvalue != pNewvalue else False
    elif pDBCond == 'greater than':
        out = True if pDBvalue >= pNewvalue else False
    elif pDBCond == 'greater than equal':
        out = True if pDBvalue >= pNewvalue else False
    elif pDBCond == 'less than':
        out = True if pDBvalue <= pNewvalue else False
    elif pDBCond == 'less than equal':
        out = True if pDBvalue <= pNewvalue else False
    print(out)
    return out

def filtered(idd, alert_id):
    try:
        uQuery = "update policyengine set applied_to_alert_total = applied_to_alert_total + 1 where pk_pk_id={0}".format(idd)
        uuQuery = "update alert_data set fk_sop_id=(select pk_sop_id from sop where pe_id={0}) where pk_alert_id={1}".format(
            idd, alert_id)
        uRet = pcon.returnInsertResult(uQuery)
        uuRet = pcon.returnInsertResult(uuQuery)
        return {'result': 'success', 'data': 'increased filtered count by 1'}
    except Exception as e:
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

def processEvent(dPayload, pPolicyID):
    """Method: This method is used to filter the events those were mentioned in event filter management"""
    try:
        lAttr = ["priority", "msg_updated_time", "machine", "application", "value", "cmdline", "description",
                 "extra_description", "severity", "source", "event_created_time", "customer_id", "alert_id"]
        lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
        if not 0 in lPayErr:
            sQuery = "select * from policyengine where active_yn ='Y' and pk_pk_id={0}".format(pPolicyID)
            dRet = pcon.returnSelectQueryResult(sQuery)

            # If no filters are available push the data directly to next level
            if dRet['result'] == 'failure':
                pushed2FE = connmq.send2MQ(pQueue='processevents', pExchange='automationengine', pRoutingKey='automation.processevents', pData=json.dumps(dPayload))
                return {'result': 'success'}

            # If filters are available undergo eamworker
            # setMain = {'Machine', 'Application', 'Description', 'Extra_Description', 'Value', 'Cmdline'}
            setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline'}
            paymap = {'machine': 'Machine', 'application': 'Application', 'description': 'Description',
                      'extra_description': 'Extra_Description', 'value': 'Value', 'cmdline': 'Cmdline'}
            for eachF in dRet['data']:
                d = {i: eachF[i] for i in eachF if eachF[i] != '' or eachF[i] is not None}
                overall = d['overall']
                idd = d['pk_pk_id']
                out = []
                for eachK in setMain:
                    if eachK + "_cond" in d.keys() and eachK + "_value" in d.keys():
                        # inp = dPayload[paymap[eachK]]
                        inp = dPayload[eachK]
                        cond = d[eachK + "_cond"]
                        value = d[eachK + "_value"]
                        out.append(Validate(cond, inp, value))
                if overall == 'ALL':
                    if False in out:
                        continue
                    else:
                        dPayload['policy_id'] = idd
                        dPayload['sp_flow'] = getSPFlow(idd)
                        pushed2FE = connmq.send2MQ(pQueue='executeautomation', pExchange='automationengine',
                                                   pRoutingKey='automation.execute_automation', pData=json.dumps(dPayload))
                        return filtered(idd, dPayload['alert_id'])
                elif overall == 'ANY':
                    if True in out:
                        dPayload['policy_id'] = idd
                        dPayload['sp_flow'] = getSPFlow(idd)
                        pushed2FE = connmq.send2MQ(pQueue='executeautomation', pExchange='automationengine',
                                                   pRoutingKey='automation.execute_automation', pData=json.dumps(dPayload))
                        return filtered(idd, dPayload['alert_id'])
                    else:
                        continue

            # No filters matching so pushing to next level
            pushed2FE = connmq.send2MQ(pQueue='processevents', pExchange='automationengine', pRoutingKey='automation.processevents', pData=json.dumps(dPayload))
            return {'result': 'success'}

        else:
            return logAndRet("failure", "Payload Error")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def callback(ch, method, properties, body):
    dPayload = json.loads(body.decode('utf-8'))
    print("Reiterating open alerts with newly created SOP: {0}".format(dPayload))
    sQuery = """select 
                    priority,  
                    msg_updated_time,
                    ci_name Machine,
                    component Application,
                    value,
                    cmdline,
                    description,
                    notes extra_description,
                    severity,
                    source, 
                    TO_CHAR(TO_TIMESTAMP(event_created_time), 'DD-MM-YYYY HH24:MI') event_created_time,
                    customer_id,
                    pk_alert_id alert_id
                from 
                    alert_data 
                where 
                    fk_status_id=(select pk_ea_status_id from ea_status where lower(stat_description)='open') and fk_sop_id is null"""
    dRet = pcon.returnSelectQueryResult(sQuery)
    if dRet['result'] == 'success':
        for i in dRet['data']:
            retJSON = processEvent(i, dPayload['policyid'])
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
    channel.queue_declare(queue='newkb', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='EVM', queue='newkb')
    channel.basic_consume(callback, queue='newkb', no_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Worker failed. Reason:" + str(e))
    CERROR("Worker failed. Reason:" + str(e))

#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import json
from services.utils import ConnPostgreSQL as pcon
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import services.utils.ConnMQ as connmq
import pika
from copy import deepcopy

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

def validate(pDBCond, pDBvalue, pNewvalue):
    print("{0}:{1}:{2}".format(pDBvalue, pDBCond, pNewvalue))
    out = None
    if pDBCond == 'equal to':
        out = True if pDBvalue == pNewvalue else False
    elif pDBCond == 'not equals to':
        out = True if pDBvalue != pNewvalue else False
    elif pDBCond == 'greater than':
        out = True if pDBvalue >= pNewvalue else False
    elif pDBCond == 'greater than equal':
        out = True if pDBvalue >= pNewvalue else False
    elif pDBCond == 'less than':
        out = True if pDBvalue <= pNewvalue else False
    elif pDBCond == 'less than equal':
        out = True if pDBvalue <= pNewvalue else False
    else:
        out = False
    return out

def retBatchBool(iAlertID, iEventCount, iSeconds, condEvent):
    sQuery = """
    select 
        count(*) total 
    from 
       (select 
            event_created_time 
        from 
            event_data 
        where 
            pk_event_id in(select fk_event_id from event_alert_mapping where fk_alert_id={0}) and 
            to_timestamp(event_created_time) > (now() - interval '{1} seconds') order by pk_event_id desc) A""".format(
        iAlertID, iSeconds
    )
    dRet = pcon.returnSelectQueryResult(sQuery)
    if dRet['result'] == 'success':
        if dRet['data'][0]['total'] > 0:
            outBool = validate(condEvent, dRet['data'][0]['total'], iEventCount)
            if outBool:
                return {'result': True, 'data': dRet['data'][0]['total']}
            # if dRet['data'][0]['total'] >= iEventCount:
            #     return {'result': True, 'data': dRet['data'][0]['total']}
    return {'result': False, 'data': 0}

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

def updateFromBatch(iAlertID, batchpay):
    try:
        dQuery = "update batches_policyengine set batch_payload='{1}' where alert_id={0}".format(iAlertID, json.dumps(batchpay).replace("'", "''"))
        dRet = pcon.returnInsertResult(dQuery)
        return dRet
    except Exception as e:
        return {'result': 'failure', 'data': 'Failed to remove alert from batching'}

def deleteFromBatch(iAlertID):
    try:
        dQuery = "delete from batches_policyengine where alert_id={0}".format(iAlertID)
        dRet = pcon.returnInsertResult(dQuery)
        return dRet
    except Exception as e:
        return {'result': 'failure', 'data': 'Failed to remove alert from batching'}

def processEvent(dPayload):
    """Method: This method is used to filter the events those were mentioned in event filter management"""
    try:
        bPayload = dPayload['batch_payload']
        condition = list(bPayload['Condition'].keys())[0]
        overall, isMatching = [], False
        sp_flow_extracts = []
        forNextEvent = deepcopy(bPayload)
        for eachItem in bPayload['Condition'][condition]:
            out = retBatchBool(dPayload['alert_id'], eachItem['event_count'], eachItem['seconds'], eachItem['event_cond'])
            overall.append(out['result'])
            if out['result'] == True:
                forNextEvent['Condition'][condition].remove(eachItem)
                eachItem['current_count'] = out['data']
                sp_flow_extracts.append(eachItem)
                logINFO("remove matching ones: {0}".format(eachItem))

        if condition.lower().strip() == 'all':
            isMatching = False not in overall
        else:
            isMatching = True in overall

        if isMatching:
            # Apply the SOP to alert
            apply = filtered(dPayload['pe_id'], dPayload['alert_id'])
            logINFO('batching filter count increated')

            # Send the signal to automation
            logINFO('batching extracts: {0}'.format(sp_flow_extracts))
            dPayload['sp_flow']['var_extracts']['@@event_count@@'] = json.dumps(sp_flow_extracts)
            pushed2FE = connmq.send2MQ(pQueue='executeautomation', pExchange='automationengine',
                                       pRoutingKey='automation.execute_automation', pData=json.dumps(dPayload['sp_flow']))
            logINFO('json sent to automation {0}'.format(dPayload['sp_flow']))

            # Delete record from batching
            if forNextEvent['Condition'][condition] == []:
                delete = deleteFromBatch(dPayload['alert_id'])
                logINFO('temp batch deletion for alert {0}'.format(dPayload['alert_id']))
            else:
                update = updateFromBatch(dPayload['alert_id'], forNextEvent)
                logINFO('temp batch updation for alert {0} with {1}'.format(dPayload['alert_id'], forNextEvent))

        return {'result': 'executed'}
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def callback(ch, method, properties, body):
    dPayload = json.loads(body.decode('utf-8'))
    print("Incoming events: {0}".format(dPayload))
    logINFO("Batch: {0}".format(dPayload))
    retJSON = processEvent(dPayload)
    logINFO("Batch: {0}".format(retJSON))

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
    channel.queue_declare(queue='kb_batch_processing', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='EVM', queue='kb_batch_processing')
    channel.basic_consume(callback, queue='kb_batch_processing', no_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Worker failed. Reason:" + str(e))
    CERROR("Worker failed. Reason:" + str(e))
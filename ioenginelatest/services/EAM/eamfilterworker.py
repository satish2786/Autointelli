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

def filtered(idd, payload):
    try:
        uQuery = "update filters set total_event_filtered = total_event_filtered + 1 where pk_filter_id={0}".format(idd)
        iQuery = "insert into filtered_records_24(fk_filter_id, payload, created_on) values({0}, '{1}', now())".format(idd, json.dumps(payload).replace("'", "''"))
        uRet = pcon.returnInsertResult(uQuery)
        iRet = pcon.returnInsertResult(iQuery)
        logINFO('filtered payload {0}, filterid {1}'.format(payload, idd))
        return {'result': 'success', 'data': 'increased filtered count by 1'}
    except Exception as e:
        logERROR('filtered payload {0}, filterid {1} failed with {2}'.format(payload, idd, str(e)))
        return {'result': 'failure', 'data': 'Unable to filtered count by 1 because of {0}'.format(str(e))}


def processEvent(dPayload):
    """Method: This method is used to filter the events those were mentioned in event filter management"""
    try:
        lAttr = ["priority", "msg_updated_time", "machine", "application", "value", "cmdline", "description",
                 "extra_description", "severity", "source", "event_created_time", "customer_id",
                 "id", "asset_number", "region", "asset_state", "version", "package", "pac_ver", "pac_ver_no",
                 "msg_created_time", "status_update", "additional_props", "modified_by"]
        lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
        if not 0 in lPayErr:
            sQuery = "select * from filters where active_yn ='Y' and expiry_date>=now()"
            dRet = pcon.returnSelectQueryResult(sQuery)

            # If no filters are available push the data directly to next level
            if dRet['result'] == 'failure':
                pushed2FE = connmq.send2MQ(pQueue='filtered_events', pExchange='EVM', pRoutingKey='filtered_events', pData=json.dumps(dPayload))
                return {'result': 'success'}

            # If filters are available undergo eamworker
            # setMain = {'Machine', 'Application', 'Description', 'Extra_Description', 'Value', 'Cmdline'}
            setMain = {'machine', 'application', 'description', 'extra_description', 'value', 'cmdline'}
            # paymap = {'machine': 'Machine', 'application': 'Application', 'description': 'Description',
            #           'extra_description': 'Extra_Description', 'value': 'Value', 'cmdline': 'Cmdline'}
            for eachF in dRet['data']:
                d = {i: eachF[i] for i in eachF if eachF[i] != '' or eachF[i] is not None}
                overall = d['overall']
                idd = d['pk_filter_id']
                out = []
                for eachK in setMain:
                    if eachK + "_cond" in d.keys() and eachK + "_value" in d.keys():
                        inp = dPayload[eachK]
                        cond = d[eachK + "_cond"]
                        value = d[eachK + "_value"]
                        out.append(Validate(cond, inp, value))
                if overall == 'ALL':
                    if False in out:
                        continue
                    else:
                        return filtered(idd, dPayload)
                elif overall == 'ANY':
                    if True in out:
                        return filtered(idd, dPayload)
                    else:
                        continue

            # No filters matching so pushing to next level
            pushed2FE = connmq.send2MQ(pQueue='filtered_events', pExchange='EVM', pRoutingKey='filtered_events', pData=json.dumps(dPayload))
            return {'result': 'success'}

        else:
            return logAndRet("failure", "Event Filter: Either attributes are missing or attribute's values are empty: {0}".format(dPayload))
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

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
    channel.queue_declare(queue='incoming_events', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='EVM', queue='incoming_events')
    channel.basic_consume('incoming_events', callback, auto_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Worker failed. Reason:" + str(e))
    CERROR("Worker failed. Reason:" + str(e))

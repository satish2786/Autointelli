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
import services.utils.ConnPostgreSQL as dbconn
import services.utils.validator_many as vm

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

def processEvent(dPayload):
    """Method: This method is used to filter the events those were mentioned in event filter management"""
    try:
        if dPayload is not None:

            # Validate payload before pushing it to ESB
            # lAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source", "component_value"]
            # lMandatoryAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source"]
            lAttr = ["msg_updated_time", "machine", "application", "value", "cmdline", "description",
                     "extra_description", "severity", "source", "event_created_time",
                     "id", "asset_number", "region", "asset_state", "version", "package", "pac_ver", "pac_ver_no",
                     "msg_created_time", "status_update", "additional_props", "modified_by"]
            lMandatoryAttr = ["msg_updated_time", "machine", "application", "description", "extra_description",
                              "severity", "source",
                              "id", "asset_number", "region", "asset_state", "version", "package", "pac_ver",
                              "pac_ver_no", "msg_created_time", "status_update", "additional_props", "modified_by"]
            X = vm.isPayloadValid(dPayload=dPayload, lHeaders=lAttr, lMandatory=lMandatoryAttr)
            Y = ("dropped_event_id" in dPayload.keys())

            if X or Y:

                # Get severity mapping for severity from monitoring tool with severity defined in Autointelli Product
                sSeverity = dPayload["severity"]
                sToolName = dPayload["source"]
                sSQuery = "select upper(aiseverity) as severity, upper(mtool_name) as source from severity_mapping where lower(mtool_name)='%s' and lower(mseverity)='%s' and active_yn='Y'" % (
                sToolName.lower(), sSeverity.lower())
                dRet = dbconn.returnSelectQueryResult(sSQuery)
                if dRet["result"] == "success":
                    dPayload["severity"] = dRet["data"][0]["severity"]
                    dPayload["source"] = dRet["data"][0]["source"]
                elif dRet["result"] == "failure":
                    if dRet["data"] == "no data":
                        return logAndRet("failure",
                                         "Enable the mapping for {0} monitoring tool".format(dPayload["source"]))
                    else:
                        return logAndRet("failure", "Unable to fetch the severity mapping details for {0} moniroting tool".format(dPayload["source"]))

                # When things are good to go, Push the payload to MQ from where other services picks up
                dRet = connmq.send2MQ(pQueue='incoming_events', pExchange='EVM', pRoutingKey='incoming_events',
                                      pData=json.dumps(dPayload))
                return logAndRet("success", dRet["data"])

            else:
                return logAndRet("failure", "Either attributes are missing or attribute's values are empty: {0}".format(dPayload))

        else:
            return logAndRet("failure", "Payload received from Monitoring tool is empty")

    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def callback(ch, method, properties, body):
    dPayload = json.loads(body.decode('utf-8'))
    # print("Incoming events: {0}".format(dPayload))
    retJSON = processEvent(dPayload)

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
    channel.queue_declare(queue='datalake', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='EVM', queue='datalake')
    channel.basic_consume('datalake', callback, auto_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Worker failed. Reason:" + str(e))
    CERROR("Worker failed. Reason:" + str(e))
#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import json
import services.utils.ConnPostgreSQL as dbconn
import services.utils.ConnMQ as connmq
import services.utils.validator_many as vm
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc

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
    return json.dumps({"result": s, "data": x})

root = "/evm/api1.0"
rootINV = "/inv/api1.0"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/ui/*": {"origins": "http://localhost:port"}})

@app.route(root + "/endpoints/eventreceiver", methods = ["POST"])
def eventReceiver():
    """Method: accepts the the event from external monitoring system"""
    try:
        dPayload = request.get_json()
        dRet = connmq.send2MQ(pQueue='datalake', pExchange='EVM', pRoutingKey='datalake', pData=json.dumps(dPayload))
        return logAndRet("success", dRet["data"])
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

# @app.route(root + "/endpoints/eventreceiver1", methods = ["POST"])
def eventReceivervoid():
    """Method: accepts the the event from external monitoring system"""
    try:
        dPayload = request.get_json()

        if dPayload is not None:

            # Validate payload before pushing it to ESB
            # lAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source", "component_value"]
            # lMandatoryAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source"]
            lAttr = ["Msg_updated_time", "Machine", "Application", "Value", "Cmdline", "Description",
                     "Extra_Description", "severity", "source", "event_created_time"]
            lMandatoryAttr = ["Msg_updated_time", "Machine", "Application", "Description", "Extra_Description",
                              "severity", "source"]
            X = vm.isPayloadValid(dPayload=dPayload, lHeaders=lAttr, lMandatory=lMandatoryAttr)
            Y = ("dropped_event_id" in dPayload.keys())

            if X or Y:

                # Get severity mapping for severity from monitoring tool with severity defined in Autointelli Product
                sSeverity = dPayload["severity"]
                sToolName = dPayload["source"]
                sSQuery = "select upper(aiseverity) as severity, upper(mtool_name) as source from severity_mapping where lower(mtool_name)='%s' and lower(mseverity)='%s' and active_yn='Y'" %(sToolName.lower(), sSeverity.lower())
                dRet = dbconn.returnSelectQueryResult(sSQuery)
                if dRet["result"] == "success":
                    dPayload["severity"] = dRet["data"][0]["severity"]
                    dPayload["source"] = dRet["data"][0]["source"]
                elif dRet["result"] == "failure":
                    if dRet["data"] == "no data":
                        return logAndRet("failure", "Enable the mapping for {0} monitoring tool".format(dPayload["source"]))
                    else:
                        return logAndRet("failure", "Unable to fetch the severity mapping details of moniroting tool")

                # When things are good to go, Push the payload to MQ from where other services picks up
                dRet = connmq.send2MQ(pQueue='incoming_events', pExchange='EVM', pRoutingKey='incoming_events', pData=json.dumps(dPayload))
                return logAndRet("success", dRet["data"])

            else:
                return logAndRet("failure", "Either attributes are missing or attribute's values are empty")

        else:
            return logAndRet("failure", "Payload received from Monitoring tool is empty")

    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

@app.route(rootINV + "/inv_receiver/<location>", methods = ["POST"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def invpostreceiver(location):
    """Method: accepts the the event from external monitoring system"""
    try:
        dPayload = request.get_json()
        iQuery = "insert into inven(type, data, created_date, created_by, location) values('{0}', '{1}', now(), 'system', '{2}')".format(
            'vmware', json.dumps(dPayload), location
        )
        dRet = dbconn.returnInsertResult(iQuery)
        if dRet["result"] == "success":
            return logAndRet("success", "INVEN Scheduler executed successfully")
        else:
            return logAndRet("failure", "INVEN Scheduler execution failed")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

@app.route(rootINV + "/inv_receiver/<location>", methods = ["GET"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def invgetreceiver(location):
    """Method: accepts the the event from external monitoring system"""
    try:
        sQuery = "select data from inven where location='{0}' order by created_date desc limit 1".format(location)
        dRet = dbconn.returnSelectQueryResult(sQuery)
        if dRet["result"] == "success":
            return json.dumps(dRet["data"][0]["data"])
            #return logAndRet("success", "INVEN Scheduler executed successfully")
        else:
            return logAndRet("failure", "INVEN recent scheduler failed")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

@app.route(rootINV + "/client_vm", methods = ["POST"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getCompleteClientVMMapping():
    """Method: accepts the the event from external monitoring system"""
    try:
        body = request.get_json()
        #sQuery = "select customer_id, customer_name, vm_id, vm_name, hostname, vm_os, vnic_details, hypervisor_tech techno from hypervisor_techno_vm_mapping where active_yn='Y'"
        #sQuery = "select customer_id, vm_name from tbl_vms"
        sQuery = "select customer_id from tbl_vms where lower(trim(vm_name)) = '{0}'".format(body['vm_name'].strip().lower())
        dRet = dbconn.returnSelectQueryResult(sQuery)
        if dRet["result"] == "success":
            return json.dumps({'result': 'success', 'data': dRet['data'][0]['customer_id']})
            #return logAndRet("success", "INVEN Scheduler executed successfully")
        else:
            return json.dumps({'result': 'success', 'data': 'Anonymous'})
            #return logAndRet("failure", "Failed fetching client virtual machine mapping details")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5006, debug=True)
        CORS(app)
    except Exception as e:
        CERROR("Exception: {0}".format(str(e)))
        logERROR("Exception: {0}".format(str(e)))
#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as pconn
from services.utils import validator_many as vmany
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc
from datetime import datetime
from datetime import timedelta
import pytz
import requests as req

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file('/var/log/autointelli/anomaly2event.log')
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

lam_api_key_missing = lam_api_key_missing()
lam_api_key_invalid = lam_api_key_invalid()

url = ""
fConf = json.load(open('/etc/autointelli/autointelli.conf', 'r'))
if 'a2e' in list(fConf.keys()):
    url = fConf['a2e']['api']
else:
    url = "localhost:5006"

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def anomaly2event(dPayload):
    try:
        if vmany.isPayloadValid(dPayload, lHeaders=["ci_name", "component", "description", "notes", "severity"], lMandatory=["ci_name", "component", "description", "notes", "severity"]):
            newPayload = {}
            newPayload["ci_name"] = dPayload["ci_name"]
            newPayload["component"] = dPayload["component"]
            newPayload["description"] = dPayload["description"]
            newPayload["notes"] = dPayload["notes"]
            newPayload["severity"] = dPayload["severity"]
            newPayload["event_created_time"] = str(int(datetime.now().timestamp()))
            newPayload["source"] = "anomaly"
            newPayload["component_value"] = dPayload["component"]
            sQuery = "select customer_id, customer_name, vm_name, vm_id from vcloud_object_inventory where vm_vcenter_ref in(select object_ref from vcenter_object_inventory where object_type ='esxivm' and object_name='{0}')".format(
                dPayload["ci_name"]
            )
            ret = pconn.returnSelectQueryResult(sQuery)
            #NxtGen Mgmt
            if "customer_id" in ret["data"][0]:
                newPayload["customerid"] = ret["data"][0]["customer_id"]
            else:
                newPayload["customerid"] = "NxtGen Mgmt"
            print(url)
            print(newPayload)
            r = req.post(url=url, headers={"Content-Type": "application/json"}, data=json.dumps(newPayload))
            if r.status_code == 200 or r.status_code == 201:
                logINFO("Event Created")
                return json.dumps({"result": "success"})
            else:
                logINFO("Event Creation Failed")
                return json.dumps({"result": "failure"})

            # if ret["result"] == "success":

            # else:
            #     return logAndRet("failure", "Anomaly2Event: {0}".format(ret["data"]))
    except Exception as e:
        return logAndRet("failure", "Anomaly2Event: {0}".format(str(e)))









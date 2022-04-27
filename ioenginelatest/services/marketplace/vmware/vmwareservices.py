#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as conn
import services.utils.validator_many as val
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc
from werkzeug.utils import secure_filename
import os
from services.utils import ED_AES256 as aes
from subprocess import check_output
import services.utils.ConnMQ as connmq

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

lam_api_key_missing = lam_api_key_missing()
lam_api_key_invalid = lam_api_key_invalid()

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def addvCenter(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if val.isPayloadValid(dPayload, ['vendor', 'machine_id'], ['vendor', 'machine_id']):
                    iQuery = "insert into marketplace(vendor, machine_id, active_yn) values('{0}', {1}, 'Y')".format(dPayload['vendor'], dPayload['machine_id'])
                    dRet = conn.returnInsertResult(iQuery)
                    if dRet['result'] == 'success':
                        return json.dumps({'result': 'success', 'data': 'vCenter mapped successfully'})
                    else:
                        return json.dumps({'result': 'failure', 'data': dRet['data']})
                else:
                    return json.dumps({"result": "failure", "data": "Key or Value is missing"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getvCenterDetails(vendor):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select m.machine_id, am.machine_fqdn, am.ip_address, m.payload_retcode, m.payload_stdout, m.payload_stderr from marketplace m inner join ai_machine am on(m.machine_id=am.machine_id) where m.active_yn='Y' and lower(m.vendor)=lower('{0}')".format(
                    vendor
                )
                dRet = conn.returnSelectQueryResultAs2DList(sQuery)
                if dRet['result'] == 'success':
                    return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'no data'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getCredentials(machine_id):
    try:
        jobQuery = """
        select 
        	am.machine_fqdn, am.ip_address, ad.cred_type, ad.username, ad.password, am.backend_port port 
        from 
        	ai_machine am inner join ai_device_credentials ad on(am.fk_cred_id=ad.cred_id) 
        where 
        	am.machine_id in(select machine_id from marketplace where lower(vendor)='vmware') and am.machine_id={0} and am.active_yn='Y'""".format(
            machine_id
        )
        jobRet = conn.returnSelectQueryResult(jobQuery)
        if jobRet['result'] == 'success':
            cred_type = jobRet['data'][0]['cred_type'].lower()
            payload = {}
            if cred_type == 'https':
                password = aes.decrypt(jobRet['data'][0]['password'].encode(), '@ut0!ntell!'.encode()).decode('utf-8')
                return jobRet['data'][0]['ip_address'], jobRet['data'][0]['username'], password
            elif cred_type == 'pam':
                return jobRet['data'][0]['ip_address'], jobRet['data'][0]['username'], jobRet['data'][0]['password']
            else:
                return "", "", ""
        else:
            return "", "", ""
    except Exception as e:
        return "", "", ""

def getGrid():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select input_payload, rawout, retcode, stdout, stderr, to_char(created_date, 'DD-MM-YYYY HH24:MI:SS') created_date, created_by from vmware_result order by created_date desc"
                dRet = conn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def createVirtualMachine(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
#                 dPayload = {
# 	"vendor": "VMWare",
# 	"action": "create",
# 	"machine_id": 27,
# 	"datacenter": "SFL-DC",
# 	"cluster": "Production-Cluster",
# 	"template": "Oracle_Linux_8.2",
# 	"datastore": "IBMV7KG2-VMWARE-LUN04",
# 	"network": "SFL-VM-Network",
# 	"hostname": "test1",
# 	"ip_address": "192.168.1.1",
# 	"netmask": "255.255.255.0",
# 	"gateway": "192.168.1.10",
# 	"domain": "d1"
# }
                lAttr = ["vendor", "action", "machine_id", "datacenter", "cluster", "template", "datastore",
                            "network", "hostname", "ip_address", "netmask", "gateway", "domain", "request_by"]
                lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
                if not 0 in lPayErr:

                    reqBy = dPayload['request_by']
                    del dPayload['request_by']
                    iQuery = "insert into vmware_result(input_payload, created_date, created_by) values('{0}', now(), '{1}') RETURNING pk_r_id".format(
                        json.dumps(dPayload), reqBy
                    )
                    dRet = conn.returnSelectQueryResultWithCommit(iQuery)
                    if dRet['result'] == 'success':

                        dPayload['trans_id'] = dRet['data'][0]['pk_r_id']
                        pushed2FE = connmq.send2MQ(pQueue='vmwareprovision', pExchange='marketplace',
                                                   pRoutingKey='vmwareprovision',
                                                   pData=json.dumps(dPayload))
                        return json.dumps({'result': 'success', 'data': 'Request submitted for VM creation'})
                    else:
                        return json.dumps({'result': 'success', 'data': 'Unable to accept request. Try after sometime.'})

                else:
                    logERROR("Either attributes are missing or attribute's values are empty: {0}".format(dPayload))
                    return json.dumps({'result': 'failure', 'data': 'Invalid payload'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing








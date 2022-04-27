#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as conn
import requests as req
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc

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

def getTriageList(alert_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinalResult = {}
                sQuery = "select triage_name from ai_triage_master where active_yn='Y' order by pk_triage_id"
                dRet = conn.returnSelectQueryResultAsList(sQuery)
                sMachQuery = """
SELECT 
	m.ip_address, m.machine_fqdn, m.platform, m.osname, m.osversion, c.cred_type, c.username, c.password, m.console_port as port 
from 
	ai_machine m left join ai_device_credentials c on(m.fk_cred_id = c.cred_id) 
where 
	trim(lower(m.machine_fqdn)) = (select trim(lower(ci_name)) from alert_data where concat('AL',lpad(cast(pk_alert_id as text),13,'0')) = '%s')""" % alert_id
                dRetMachine = conn.returnSelectQueryResult(sMachQuery)
                if dRet['result'] == 'success' and dRetMachine['result'] == 'success':
                    dFinalResult['result'] = 'success'
                    dFinalResult['triage'] = dRet['data']
                    dFinalResult['machine'] = dRetMachine['data']
                    logINFO("Fetching triage list")
                    return json.dumps(dFinalResult)
                else:
                    logERROR("Failed to fetch the triage list: {0}".format(dRet["data"]))
                    return json.dumps({'result': 'failure', 'data': 'Add CI to HDDM to display Triage list'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTriageList1(alert_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinalResult = {}
                sQuery = "select triage_name from ai_triage_master where active_yn='Y' order by pk_triage_id"
                dRet = conn.returnSelectQueryResultAsList(sQuery)
                sMachQuery = """
SELECT 
	m.ip_address, m.machine_fqdn, m.platform, m.osname, m.osversion, (CASE WHEN c.cred_type = 'WINRM' THEN 'RDP' ELSE c.cred_type END) as cred_type, c.username, c.password, (CASE WHEN c.port = '5985' THEN '3389' ELSE c.port END) as port 
from 
	ai_machine m left join ai_device_credentials c on(m.fk_cred_id = c.cred_id) 
where 
	trim(lower(m.machine_fqdn)) = (select trim(lower(ci_name)) from alert_data where concat('AL',lpad(cast(pk_alert_id as text),13,'0')) = '%s')""" % alert_id
                dRetMachine = conn.returnSelectQueryResult(sMachQuery)
                if dRet['result'] == 'success' and dRetMachine['result'] == 'success':
                    dFinalResult['result'] = 'success'
                    dFinalResult['triage'] = dRet['data']
                    dFinalResult['machine'] = dRetMachine['data']
                    logINFO("Fetching triage list")
                    return json.dumps(dFinalResult)
                else:
                    logERROR("Failed to fetch the triage list: {0}".format(dRet["data"]))
                    return json.dumps({'result': 'failure', 'data': 'Failed to fetch the triage list'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTriageCIRemoteMetaData(ci_name):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinalResult = {}
                #sQuery = "select triage_name from ai_triage_master where active_yn='Y' order by pk_triage_id"
                #dRet = conn.returnSelectQueryResultAsList(sQuery)
                sMachQuery = """
SELECT 
	m.ip_address, m.machine_fqdn, m.platform, m.osname, m.osversion, (CASE WHEN c.cred_type = 'WINRM' THEN 'RDP' ELSE c.cred_type END) as cred_type, c.username, c.password, (CASE WHEN c.port = '5985' THEN '3389' ELSE c.port END) as port 
from 
	ai_machine m left join ai_device_credentials c on(m.fk_cred_id = c.cred_id) 
where 
	trim(lower(m.machine_fqdn)) = '{0}' """.format(ci_name.lower().strip())
                dRetMachine = conn.returnSelectQueryResult(sMachQuery)
                if dRetMachine['result'] == 'success':
                    dFinalResult['result'] = 'success'
                   # dFinalResult['triage'] = dRet['data']
                    dFinalResult['machine'] = dRetMachine['data']
                    logINFO("Fetching triage list")
                    return json.dumps(dFinalResult)
                else:
                    logERROR("Failed to fetch the remoting details")
                    return json.dumps({'result': 'failure', 'data': 'Failed to fetch the remoting details'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTriageDynamicForm(triage_name, alert_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinalResult = {}
                # Dynamic Form Structure
                sQuery = "select form_control_label lbl, form_control_type ctrl, form_control_order ctrl_order from ai_triage_dynamic_form where fk_triage_id=(select pk_triage_id from ai_triage_master where lower(triage_name)='%s') order by form_control_order" % triage_name.lower()
                dRet = conn.returnSelectQueryResultAs2DList(sQuery)
                if dRet['result'] == 'success':
                    dFinalResult['form'] = dRet['data']
                else:
                    logINFO("Form is not defined for triage: {0}".format(triage_name))
                    dFinalResult['form'] = 'no data'
                # Historical Data
                sQuery = "select output, to_char(created_dt, 'DD/MM/YYYY hh:mi') DateTime from ai_triage_history where concat('AL',lpad(cast(fk_alert_id as text),13,'0'))='%s' and fk_triage_id=(select pk_triage_id from ai_triage_master where lower(triage_name)= '%s') order by created_dt desc" % (alert_id, triage_name.lower())
                dRet = conn.returnSelectQueryResultAs2DList(sQuery)
                if dRet['result'] == 'success':
                    dFinalResult['history'] = dRet['data']
                else:
                    logINFO("No historical run for this alert id: {0}".format(alert_id))
                    dFinalResult['history'] = 'no data'
                # Final JSON Return
                dFinalResult['result'] = 'success'
                return json.dumps(dFinalResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def executeTriage(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                triage_name = dPayload['triage_name']
                alert_id = dPayload['alert_id']
                sQuery = "select triage_rest_call from ai_triage_master where lower(triage_name) ='%s'" % triage_name.strip().lower()
                dRet = conn.returnSelectQueryResult(sQuery)
                if dRet['result'] == 'success':
                    sURL = dRet['data'][0]['triage_rest_call']
                    dHeader = {'content-type': 'application/json'}
                    dData = dPayload['form_data'] if 'form_data' in list(dPayload.keys()) else {}
                    dData.update({'alert_id': alert_id})
                    ret = req.post(url=sURL, headers=dHeader, json=dData)
                    print(ret.text)
                    if ret.status_code == 200:
                        logINFO("Triage: {0} executed successfully, REST ret code: {1}".format(triage_name, ret.status_code))
                        return ret.text
                    else:
                        logERROR("Failed to execute triage: {0}, REST ret code: {1}".format(triage_name, ret.status_code))
                        return json.dumps({'result': 'failure', 'data': 'Failed to execute triage'})
                else:
                    logWARN("Triage {0} doesn't have REST references, construction is in progress".format(triage_name))
                    return json.dumps({'result': 'failure', 'data': 'Under Construction'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTriageHistory(pAlertID):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
	 atm.triage_name Triage, ath.output Output, to_char(ath.created_dt, 'DD/MM/YYYY hh:mi') DateTime 
from 
	ai_triage_history ath inner join ai_triage_master atm on(ath.fk_triage_id = atm.pk_triage_id) 
where 
	concat('AL',lpad(cast(fk_alert_id as text),13,'0')) = '%s' 
order by 
	pk_triage_history_id desc""" % (pAlertID)
                dRet = conn.returnSelectQueryResultAs2DList(sQuery)
                logINFO("Fetch triage hostory for alert: {0}".format(pAlertID))
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing



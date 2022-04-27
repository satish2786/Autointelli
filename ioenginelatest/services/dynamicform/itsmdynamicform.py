#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as conn
from services.administration import GenericITSMService as itsm
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

def getITSMFormDesign(itsm_name, ticket_action):
    sQuery = """
select 
	form_control_order, form_control_label, form_control_type 
from 
	itsm_dynamic_form 
where 
	lower(itsm_name) ='%s' and lower(ticket_action)='%s' and active_yn='Y' 
order by 
	form_control_order asc""" %(itsm_name, ticket_action)
    dRet = conn.returnSelectQueryResultAs2DList(sQuery)
    return json.dumps(dRet)

def getITSMMasters():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinalResult = []
                dJSON = itsm.getEnabledITSM()
                dData = json.loads(dJSON.data)
                sITSM = dData['itsm']
                sQuery = "select itsm_rest_name, itsm_rest_url, itsm_rest_method, itsm_rest_params, select_items from ai_itsm_rest_master where active_yn='Y' and lower(itsm_name)='%s'" % (sITSM)
                dRet = conn.returnSelectQueryResult(sQuery)
                if dRet['result'] == 'success':
                    dDropDowns = dRet['data']
                    for eachDD in dDropDowns:
                        sAttribute = eachDD['itsm_rest_name']
                        sColumns = eachDD['select_items']
                        sURL = eachDD['itsm_rest_url']
                        sMethod = eachDD['itsm_rest_method']
                        dData = eachDD['itsm_rest_params']
                        dParams = {'OPERATION_NAME': 'GET_ALL', 'TECHNICIAN_KEY': '0DDC1E19-ADA4-42C2-989D-0CE5D18463F6', 'format': 'json'}
                        if dData:
                            dParams['INPUT_DATA'] = str(eachDD['itsm_rest_params'])
                        if sMethod == 'POST':
                            ret = req.post(url=sURL, params=dParams)
                            if ret.status_code == 200:
                                dRespData = json.loads(ret.text)
                                lData = [i[j] for j in sColumns.split(',') for i in dRespData['operation']['details']]
                                dFinalResult.append({sAttribute: [lData[:int(len(lData) / 2)], lData[int(len(lData) / 2):]]})
                    logINFO("Fetching ITSM Master data for dropdowns")
                    return json.dumps({'result': 'success', 'data': dFinalResult})
                else:
                    return logAndRet("failure", "Unable to fetch master details from database")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getITSMMaster_SubCategory(category_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sColumns, sAttribute = 'ID,NAME', 'sub_category'
                dFinalResult = []
                sURL = 'http://192.168.1.105:8080/sdpapi/admin/subcategory/category/' + str(category_id)
                dParams = {'OPERATION_NAME': 'GET_ALL', 'TECHNICIAN_KEY': '0DDC1E19-ADA4-42C2-989D-0CE5D18463F6', 'format': 'json'}
                ret = req.post(url=sURL, params=dParams)
                if ret.status_code == 200:
                    dRespData = json.loads(ret.text)
                    if 'details' in list(dRespData['operation'].keys()):
                        lData = [i[j] for j in sColumns.split(',') for i in dRespData['operation']['details']]
                        dFinalResult.append({sAttribute: [lData[:int(len(lData) / 2)], lData[int(len(lData) / 2):]]})
                        logINFO("Fetching Sub Category for Selected Category")
                        return json.dumps({'result': 'success', 'data': dFinalResult})
                    else:
                        return logAndRet("failure", "Sub Category not found for category {0}".format(category_id))
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


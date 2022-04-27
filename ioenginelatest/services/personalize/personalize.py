#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as pconn
from services.utils import sessionkeygen
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc
from services.utils import validator_many as val

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

def getTimeZone(sKey):
    dRet = sessionkeygen.getUserDetailsBasedWithSessionKey(sKey)
    if dRet["result"] == "success":
        return dRet["data"][0]["time_zone"]
    else:
        return "no data"

def createPeronalize(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                attr = ['personalize_name', 'personalize_description', 'user_id', 'personalize_attributes']
                if val.isPayloadValid(dPayload=dPayload, lHeaders=attr, lMandatory=attr):

                    sQuery = "select * from personalize where lower(personalize_name)=lower('{0}') and active_yn='Y' and user_id={1}".format(dPayload['personalize_name'].strip(), dPayload['user_id'])
                    dRet = pconn.returnSelectQueryResult(sQuery)
                    if dRet['result'] == 'success':
                        return json.dumps({'result': 'failure', 'data': 'Choose a different name. Name already in use.'})

                    iQuery = "insert into personalize(personalize_name, personalize_description, user_id, personalize_attributes, created_date, active_yn) values('{0}', '{1}', {2}, '{3}', now(), 'Y')".format(
                        dPayload['personalize_name'], dPayload['personalize_description'],
                        dPayload['user_id'], json.dumps(dPayload['personalize_attributes'])
                    )
                    dRet = pconn.returnInsertResult(iQuery)
                    if dRet['result'] == 'success':
                        sQuery = "select personalize_name from personalize where user_id={0} and active_yn='Y'".format(dPayload['user_id'])
                        dRet = pconn.returnSelectQueryResultAsList(sQuery)
                        if dRet['result'] == 'success':
                            return json.dumps({'result': 'success', 'data': dRet['data']['personalize_name']})
                    else:
                        return json.dumps({'result': 'failure', 'data': 'Failed to create views'})
                else:
                    return logAndRet("failure", "Invalid Payload: Either attributes are missing or attribute's values are empty: {0}".format(dPayload))
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deletePeronalize(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dQuery = "update personalize set active_yn='N' where personalize_name='{0}' and user_id={1}".format(
                    dPayload['personalize_name'], dPayload['user_id']
                )
                dRet = pconn.returnInsertResult(dQuery)
                if dRet['result'] == 'success':
                    return json.dumps({'result': 'success', 'data': 'Views removed'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to remove views'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getPeronalize(user_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select personalize_name, personalize_description from personalize where user_id={0} and active_yn='Y'".format(user_id)
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                if dRet['result'] == 'success':
                    return json.dumps({'result': 'success', 'data': dRet['data']})
                else:
                    return json.dumps({'result': 'failure', 'data': 'no data'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing














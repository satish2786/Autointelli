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
import services.utils.validator_many as valid

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

def getCustomerEmailGrid(customer_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinal = {}
                sQuery = "select COALESCE(emailids_to,'') emailids_to, COALESCE(emailids_cc,'') emailids_cc, COALESCE(emailids_bcc,'') emailids_bcc from tbl_email_customer_mapping where fk_cust_id={0} and active_yn='Y'".format(
                    customer_id
                )
                dRet = pconn.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    dFinal["to"] = dRet["data"][0]["emailids_to"].split(';')
                    dFinal["cc"] = dRet["data"][0]["emailids_cc"].split(';') if dRet["data"][0]["emailids_cc"].strip() else []
                    dFinal["bcc"] = dRet["data"][0]["emailids_bcc"].split(';') if dRet["data"][0]["emailids_bcc"].strip() else []
                    return json.dumps(dFinal)
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def mapCustomerEmail(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if valid.isPayloadValid(dPayload, lHeaders=["cust_id", "to"], lMandatory=["cust_id", "to"]):
                    cust_id = dPayload["cust_id"]
                    to = ';'.join(dPayload["to"])
                    cc = ';'.join(dPayload["cc"]) if 'cc' in dPayload else ''
                    bcc = ';'.join(dPayload["bcc"]) if 'bcc' in dPayload else ''
                    iQuery = "insert into tbl_email_customer_mapping(fk_cust_id, emailids_to, emailids_cc, emailids_bcc, active_yn) values({0}, '{1}', '{2}', '{3}', 'Y')".format(
                        cust_id, to, cc, bcc
                    )
                    dRet = pconn.returnInsertResult(iQuery)
                    if dRet["result"] == "success":
                        return json.dumps({"result": "success", "data": "Email mapping success"})
                    else:
                        return json.dumps({"result": "failure", "data": "Mapping failed"})
                else:
                    return json.dumps({"result": "failure", "data": "Either payload is missing a mandatory field or contains empty values"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateCustomerEmailMap(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if valid.isPayloadValid(dPayload, lHeaders=["cust_id", "to"], lMandatory=["cust_id", "to"]):
                    cust_id = dPayload["cust_id"]
                    to = ';'.join(dPayload["to"])
                    cc = ';'.join(dPayload["cc"]) if 'cc' in dPayload else ''
                    bcc = ';'.join(dPayload["bcc"]) if 'bcc' in dPayload else ''
                    iQuery = "update tbl_email_customer_mapping set emailids_to='{0}', emailids_cc='{1}', emailids_bcc='{2}' where fk_cust_id={3}".format(
                        to, cc, bcc, cust_id
                    )
                    dRet = pconn.returnInsertResult(iQuery)
                    if dRet["result"] == "success":
                        return json.dumps({"result": "success", "data": "Email mapping success"})
                    else:
                        return json.dumps({"result": "failure", "data": "Mapping failed"})
                else:
                    return json.dumps({"result": "failure", "data": "Either payload is missing a mandatory field or contains empty values"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteCustomerEmailMap(cust_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                iQuery = "update tbl_email_customer_mapping set active_yn='N' where fk_cust_id={0}".format(cust_id)
                dRet = pconn.returnInsertResult(iQuery)
                if dRet["result"] == "success":
                    return json.dumps({"result": "success", "data": "Mapping removed"})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to remove mapping"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


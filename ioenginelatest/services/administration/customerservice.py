#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import request
import json
from services.utils.ConnPostgreSQL import returnInsertResult, returnSelectQueryResult, returnSelectQueryResultAs2DList, returnSelectQueryResultAsList
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc
from copy import deepcopy

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

def getCustomerServicesLoad():
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQueryCust = """select 
	c.cust_pk_id, c.customer_id, c.customer_name, c.technology_loc techno, fk_service_id service_id
from 
	tbl_customer c 
	left join tbl_customer_service_mapping m on(c.cust_pk_id=m.fk_customer_id)"""
                sQueryCustServ = "select cust_service_pk_id service_id, service_name from tbl_customer_services where active_yn='Y'"
                dRetC = returnSelectQueryResult(sQueryCust)
                dRetCS = returnSelectQueryResultAs2DList(sQueryCustServ)
                #sort
                if dRetC["result"] == "success" and dRetCS["result"] == "success":
                    lFinalRet = []
                    llServices = dRetCS["data"][1:]
                    for eachCust in dRetC["data"]:
                        dTmp = eachCust
                        lTmpServ = deepcopy(llServices)
                        if eachCust["service_id"] != None:
                            print(eachCust["service_id"])
                            [i.append("Y") if i[0] == eachCust["service_id"] else i.append("N") for i in lTmpServ]
                        else:
                            [i.append("N") for i in lTmpServ]
                        dTmp["services"] = lTmpServ
                        del dTmp["service_id"]
                        del lTmpServ
                        lFinalRet.append(dTmp)
                    return json.dumps({"result": "success", "data": lFinalRet})
                else:
                    return logAndRet("failure", "Unable to fetch information of Customer Service Administration")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def mapCustomerService(dPayload):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                cust_id = dPayload["customer_id"]
                serv_id = dPayload["service_id"]
                action = dPayload["action"]
                idQuery = ""
                if action.lower() == "add":
                    idQuery = "insert into tbl_customer_service_mapping(fk_customer_id, fk_service_id) values({0},{1})".format(
                        cust_id, serv_id)
                elif action.lower() == "del":
                    uQuery1 = "update tbl_vms set active_yn='N' where lower(customer_id)=(select lower(customer_id) from tbl_customer where cust_pk_id={0})".format(
                        cust_id)
                    uRet = returnInsertResult(uQuery1)
                    idQuery = "delete from tbl_customer_service_mapping where fk_customer_id={0} and fk_service_id={1}".format(
                        cust_id, serv_id)
                dRet = returnInsertResult(idQuery)

                if dRet["result"] == "success":
                    return json.dumps({"result": "success", "data": "Mapping Success"})
                else:
                    return json.dumps({"result": "failure", "data": "Mapping Failed"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getCustomer4User(user_id):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                lFinalDict = []
                sQueryC = "select c.cust_pk_id cid, c.customer_id, c.customer_name, c.technology_loc from tbl_customer c where c.active_yn='Y'"
                sQueryCID = """select 
	c.cust_pk_id cid 
from 
	tbl_customer c left join tbl_user_customer_mapping m on(c.cust_pk_id=m.fk_customer_id)
where 
	c.active_yn='Y' and m.fk_user_id={0}""".format(user_id)
                dRetC = returnSelectQueryResult(sQueryC)
                dRetCID = returnSelectQueryResultAsList(sQueryCID)
                if dRetC["result"] == "success" and (dRetCID["result"] == "success" or dRetCID["result"] == "failure"):
                    lMappedCust = []
                    if not dRetCID["result"] == "failure":
                        lMappedCust = dRetCID["data"]["cid"]
                    for eachCust in dRetC["data"]:
                        if eachCust["cid"] in lMappedCust:
                            eachCust["map"] = "Y"
                        else:
                            eachCust["map"] = "N"
                        lFinalDict.append(eachCust)
                    return json.dumps({"result": "success", "data": lFinalDict})
                else:
                    return json.dumps({"result": "failure", "data": "Failed fetching customer details"})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def mapUser2Customer(dPayload):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                user_id = dPayload["user_id"]
                customer_id = dPayload["customer_id"]
                # Delete
                dQuery = "delete from tbl_user_customer_mapping where fk_user_id={0}".format(user_id)
                dRet = returnInsertResult(dQuery)
                # Insert
                mulInsert = ",".join([str((user_id, i)) for i in customer_id])
                iQuery = "insert into tbl_user_customer_mapping(fk_user_id, fk_customer_id) values {0}".format(mulInsert)
                dRet = returnInsertResult(iQuery)
                if dRet["result"] == "success":
                    return json.dumps({"result": "success", "data": "Mapped Successfully"})
                else:
                    return json.dumps({"result": "failure", "data": "Mapping Failed"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getVM4Customer(customer_id, techno):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select vm_pk_id id, vm_id, vm_name, vm_os, vnic, active_yn from tbl_vms where lower(customer_id)=lower('{0}') and techno='{1}'".format(customer_id, techno)
                dRet = returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def enableService4VM(dPayload):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sCustomer_id = dPayload["customer_id"]
                lVMs = dPayload["vms"]
                sTech = dPayload["technology"]
                uQuery1 = "update tbl_vms set active_yn='N' where lower(customer_id)=lower('{0}') and lower(techno)=lower('{1}')".format(sCustomer_id, sTech)
                uQuery2 = "update tbl_vms set active_yn='Y' where vm_pk_id in({0})".format(",".join([str(i) for i in lVMs]))
                dRet1 = returnInsertResult(uQuery1)
                dRet2 = returnInsertResult(uQuery2)
                if dRet1["result"] == "success" and dRet2["result"] == "success":
                    return json.dumps({"result": "success", "data": "Mapped VMs"})
                else:
                    return json.dumps({"result": "success", "data": "Mapping Failed"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getCustomers():
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select (customer_name || '::' || customer_id) customer from tbl_customer where active_yn='Y' order by technology_loc"
                dRet = returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing














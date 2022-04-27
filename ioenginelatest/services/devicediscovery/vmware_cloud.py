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

def getClouds():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select pk_cloud_id cloud_id, cloud_name, cloud_fqdn_ip, cloud_type, cloud_cred from cloud_details where active_yn='Y'"
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def addCloud(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                headers = ["cloud_name", "cloud_ip_address", "cloud_type", "cloud_cred"]
                mheaders = ["cloud_name", "cloud_ip_address", "cloud_type", "cloud_cred"]
                if vmany.isPayloadValid(dPayload, lHeaders=headers, lMandatory=mheaders):
                    hname, hip, htyp, hcrd = dPayload['cloud_name'], dPayload['cloud_ip_address'], dPayload['cloud_type'], dPayload['cloud_cred']
                    sQuery = "select * from cloud_details where cloud_fqdn_ip='{0}' and active_yn='Y'".format(hip)
                    dRet = pconn.returnSelectQueryResult(sQuery)
                    if dRet["result"] == "failure":
                        iQuery = "insert into cloud_details(cloud_name, cloud_fqdn_ip, cloud_type, cloud_cred, active_yn) values('{0}', '{1}', '{2}', {3},'{4}') RETURNING pk_cloud_id".format(
                            hname, hip, htyp, hcrd, 'Y'
                        )
                        dRet = pconn.returnSelectQueryResultWithCommit(iQuery)
                        if dRet["result"] == "success":
                            return json.dumps({"result": "success", "data": "Cloud Added", "pk_cloud_id": dRet["data"][0]["pk_cloud_id"]})
                        else:
                            return json.dumps({"result": "failure", "data": "Cloud Addition Failed"})
                    else:
                        return json.dumps({"result": "failure", "data": "Cloud Already Exists"})
                else:
                    return json.dumps({"result": "failure", "data": "Invalid Payload"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def modifyCloud(cloud_id, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                headers = ["cloud_name", "cloud_ip_address", "cloud_type", "cloud_cred"]
                mheaders = ["cloud_name", "cloud_ip_address", "cloud_type", "cloud_cred"]
                if vmany.isPayloadValid(dPayload, lHeaders=headers, lMandatory=mheaders):
                    hname, hip, htyp, hcrd = dPayload['cloud_name'], dPayload['cloud_ip_address'], dPayload['cloud_type'], dPayload['cloud_cred']
                    sQuery = "select * from cloud_details where pk_cloud_id={0} and active_yn='Y'".format(cloud_id)
                    dRet = pconn.returnSelectQueryResult(sQuery)
                    if dRet["result"] == "success":
                        iQuery = "update cloud_details set cloud_name='{0}', cloud_fqdn_ip='{1}', cloud_type='{2}', cloud_cred='{3}' where pk_cloud_id={4}".format(
                            hname, hip, htyp, hcrd, cloud_id
                        )
                        dRet = pconn.returnInsertResult(iQuery)
                        if dRet["result"] == "success":
                            return json.dumps({"result": "success", "data": "Cloud Modified"})
                        else:
                            return json.dumps({"result": "failure", "data": "Cloud Modification Failed"})
                    else:
                        return json.dumps({"result": "failure", "data": "Cloud Doesn't Exists"})
                else:
                    return json.dumps({"result": "failure", "data": "Invalid Payload"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteCloud(cloud_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select * from cloud_details where pk_cloud_id={0} and active_yn='Y'".format(cloud_id)
                dRet = pconn.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                        iQuery = "update cloud_details set active_yn='N' where pk_cloud_id={0}".format(cloud_id)
                        dRet = pconn.returnInsertResult(iQuery)
                        if dRet["result"] == "success":
                            return json.dumps({"result": "success", "data": "Cloud Deleted"})
                        else:
                            return json.dumps({"result": "failure", "data": "Cloud Deletion Failed"})
                else:
                    return json.dumps({"result": "failure", "data": "Cloud Doesn't Exists"})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getvCenterDetails4Mapping(cloud_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
	h.pk_hypervisor_id hypervisor_id, h.hypervisor_name, m.mapped 
from 
	hypervisor_details h left join (select fk_vcenter_id, 'Y' mapped from cloud_vcenter_mapping where fk_cloud_id={0} and active_yn='Y') m on(h.pk_hypervisor_id=fk_vcenter_id) 
where 
	lower(h.hypervisor_type)='vmware vcenter' and h.active_yn='Y'""".format(cloud_id)
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def mapvcloudandvcenter(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                headers = ["vcloud_ids", "vcenter_ids"]
                mheaders = ["vcloud_ids", "vcenter_ids"]
                if vmany.isPayloadValid(dPayload, lHeaders=headers, lMandatory=mheaders):
                    dQuery = "update cloud_vcenter_mapping set active_yn='N' where fk_cloud_id={0}".format(dPayload["vcloud_ids"])
                    dRet = pconn.returnInsertResult(dQuery)
                    if len(dPayload['vcenter_ids']) > 0:
                        iQuery = "insert into cloud_vcenter_mapping(fk_cloud_id, fk_vcenter_id, active_yn) values{0}".format(
                            ','.join([str((dPayload['vcloud_ids'], i, 'Y')) for i in dPayload['vcenter_ids']])
                        )
                        iRet = pconn.returnInsertResult(iQuery)
                        if iRet["result"] == "success":
                            return json.dumps({"result": "success", "data": "Mapped successfully"})
                        else:
                            return json.dumps({"result": "failure", "data": "no data"})
                    else:
                        return json.dumps({"result": "success", "data": "Ummapped successfully"})
                else:
                    return json.dumps({"result": "failure", "data": "Invalid Payload"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing



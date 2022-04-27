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

def getHypervisors():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """select A.*, B.total from (select * from hypervisor_details) A
left join (select fk_hypervisor_id, count(fk_hypervisor_id) total from vcenter_object_inventory where dc_id is not null and obj_modified_on > to_date(to_char(now(), 'DD-MM-YYYY'), 'DD-MM-YYYY') group by fk_hypervisor_id) B 
on(A.pk_hypervisor_id=B.fk_hypervisor_id)"""
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def addHypervisor(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                headers = ["hypervisor_name", "hypervisor_ip_address", "hypervisor_type", "hypervisor_cred"]
                mheaders = ["hypervisor_name", "hypervisor_ip_address", "hypervisor_type", "hypervisor_cred"]
                if vmany.isPayloadValid(dPayload, lHeaders=headers, lMandatory=mheaders):
                    hname, hip, htyp, hcrd = dPayload['hypervisor_name'], dPayload['hypervisor_ip_address'], dPayload['hypervisor_type'], dPayload['hypervisor_cred']
                    sQuery = "select * from hypervisor_details where hypervisor_ip_address='{0}' and active_yn='Y'".format(hip)
                    dRet = pconn.returnSelectQueryResult(sQuery)
                    if dRet["result"] == "failure":
                        iQuery = "insert into hypervisor_details(hypervisor_name, hypervisor_ip_address, hypervisor_type, hypervisor_cred, active_yn) values('{0}', '{1}', '{2}', {3},'{4}') RETURNING pk_hypervisor_id".format(
                            hname, hip, htyp, hcrd, 'Y'
                        )
                        dRet = pconn.returnSelectQueryResultWithCommit(iQuery)
                        if dRet["result"] == "success":
                            return json.dumps({"result": "success", "data": "Hypervisor Added", "pk_hypervisor_id": dRet["data"][0]["pk_hypervisor_id"]})
                        else:
                            return json.dumps({"result": "failure", "data": "Hypervisor Addition Failed"})
                    else:
                        return json.dumps({"result": "failure", "data": "Hypervisor Already Exists"})
                else:
                    return json.dumps({"result": "failure", "data": "Invalid Payload"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def modifyHypervisor(hypervisor_id, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                headers = ["hypervisor_name", "hypervisor_ip_address", "hypervisor_type", "hypervisor_cred"]
                mheaders = ["hypervisor_name", "hypervisor_ip_address", "hypervisor_type", "hypervisor_cred"]
                if vmany.isPayloadValid(dPayload, lHeaders=headers, lMandatory=mheaders):
                    hname, hip, htyp, hcrd = dPayload['hypervisor_name'], dPayload['hypervisor_ip_address'], dPayload['hypervisor_type'], dPayload['hypervisor_cred']
                    sQuery = "select * from hypervisor_details where pk_hypervisor_id={0} and active_yn='Y'".format(hypervisor_id)
                    dRet = pconn.returnSelectQueryResult(sQuery)
                    if dRet["result"] == "success":
                        iQuery = "update hypervisor_details set hypervisor_name='{0}', hypervisor_ip_address='{1}', hypervisor_type='{2}', hypervisor_cred='{3}' where pk_hypervisor_id={4}".format(
                            hname, hip, htyp, hcrd, hypervisor_id
                        )
                        dRet = pconn.returnInsertResult(iQuery)
                        if dRet["result"] == "success":
                            return json.dumps({"result": "success", "data": "Hypervisor Modified"})
                        else:
                            return json.dumps({"result": "failure", "data": "Hypervisor Modification Failed"})
                    else:
                        return json.dumps({"result": "failure", "data": "Hypervisor Doesn't Exists"})
                else:
                    return json.dumps({"result": "failure", "data": "Invalid Payload"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteHypervisor(hypervisor_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select * from hypervisor_details where pk_hypervisor_id={0} and active_yn='Y'".format(hypervisor_id)
                dRet = pconn.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                        iQuery = "delete from hypervisor_details where pk_hypervisor_id={0}".format(hypervisor_id)
                        dRet = pconn.returnInsertResult(iQuery)
                        if dRet["result"] == "success":
                            return json.dumps({"result": "success", "data": "Hypervisor Deleted"})
                        else:
                            return json.dumps({"result": "failure", "data": "Hypervisor Deletion Failed"})
                else:
                    return json.dumps({"result": "failure", "data": "Hypervisor Doesn't Exists"})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getInventory(hypervisor_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dcQuery = "select distinct pk_object_id, object_name from vcenter_object_inventory where fk_hypervisor_id={0} and object_type='datacenter'".format(
                    hypervisor_id)
                dcRet = pconn.returnSelectQueryResult(dcQuery)
                if dcRet["result"] == "success":
                    dFinal = {}
                    for eachDC in dcRet["data"]:
                        dc_id = eachDC["pk_object_id"]
                        dc_name = eachDC["object_name"]
                        sDTQuery = """
select 
	A.object_type, A.total, B.new 
from 
	(select object_type,count(object_type) total from vcenter_object_inventory where fk_hypervisor_id={0} and dc_id={1} group by object_type) A
	left join
	(select object_type,count(object_type) new from vcenter_object_inventory where fk_hypervisor_id={2} and dc_id={3} and obj_modified_on > to_date(to_char(now(), 'DD-MM-YYYY'), 'DD-MM-YYYY') group by object_type) B 
on(lower(A.object_type)=lower(B.object_type)) order by A.object_type""".format(hypervisor_id, dc_id, hypervisor_id, dc_id)
                        sRet = pconn.returnSelectQueryResult(sDTQuery)
                        if sRet["result"] == "success":
                            dFinal[dc_name] = sRet["data"]
                        else:
                            dFinal[dc_name] = []
                    return json.dumps({"result": "success", "data": dFinal})
                else:
                    return json.dumps({"result": "failure", "data": "No inventory found."})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getInventoryNewCount(hypervisor_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sDTQuery = "select count(*) total from vcenter_object_inventory where fk_hypervisor_id={0} and dc_id is not null and obj_modified_on > to_date(to_char(now(), 'DD-MM-YYYY'), 'DD-MM-YYYY')".format(
                    hypervisor_id
                )
                dRet = pconn.returnSelectQueryResult(sDTQuery)
                if dRet["result"] == "success":
                    return json.dumps({"result": "success", "data": dRet["data"][0]["total"]})
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getSingleObjectDetails(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = ""
                if dPayload["obj_type"] == "esxivm":
                    sQuery = """
select 
	CASE WHEN obj_modified_on > to_date(to_char(now(), 'DD-MM-YYYY'), 'DD-MM-YYYY') THEN 'new' END AS state, 
	pk_object_id, 
	object_name, 
	to_char(obj_modified_on, 'DD/MM/YYYY HH24:MI:SS') last_modified_date, 
	obj_remark,
	customer_id || '::' || customer_name customer
from 
	vcenter_object_inventory left join vcloud_object_inventory on(vcenter_object_inventory.object_ref=vcloud_object_inventory.vm_vcenter_ref) 
where 
	dc_id=(select pk_object_id from vcenter_object_inventory where fk_hypervisor_id={0} and object_name='{1}') and 
	object_type='{2}'  
order by 
	obj_modified_on desc""".format(dPayload["hypervisor_id"], dPayload["dc_name"], dPayload["obj_type"])
                    sQuery = """
select 
	CASE WHEN obj_modified_on > to_date(to_char(now(), 'DD-MM-YYYY'), 'DD-MM-YYYY') THEN 'new' END AS state, 
	pk_object_id, 
	object_name, 
	to_char(obj_modified_on, 'DD/MM/YYYY HH24:MI:SS') last_modified_date, 
	obj_remark,
	customer_id
from 
	vcenter_object_inventory left join vcloud_from_vcenter on(vcenter_object_inventory.object_ref=vcloud_from_vcenter.vm_ref) 
where 
	dc_id=(select pk_object_id from vcenter_object_inventory where fk_hypervisor_id={0} and object_name='{1}') and 
	object_type='{2}'  
order by 
	obj_modified_on desc""".format(dPayload["hypervisor_id"], dPayload["dc_name"], dPayload["obj_type"])
                    sQuery = """
select 
	CASE WHEN vcenti.obj_modified_on > to_date(to_char(now(), 'DD-MM-YYYY'), 'DD-MM-YYYY') THEN 'new' END AS state, 
	vcenti.pk_object_id, 
	vcenti.object_name, 
	to_char(vcenti.obj_modified_on, 'DD/MM/YYYY HH24:MI:SS') last_modified_date, 
	vcenti.obj_remark,
	vcloi.customer_id || '::' || vcloi.customer_name customer, vcents.object_state
from 
	vcenter_object_inventory vcenti
	left join vcloud_object_inventory vcloi on(vcenti.object_ref=vcloi.vm_vcenter_ref) 
	left join vcenter_object_state vcents on(vcenti.object_ref=vcents.object_ref) 
where 
	vcenti.dc_id=(select pk_object_id from vcenter_object_inventory where fk_hypervisor_id={0} and object_name='{1}') and 
	vcenti.object_type='{2}' and 
	vcents.dc_id=(select pk_object_id from vcenter_object_inventory where fk_hypervisor_id={3} and object_name='{4}')
order by 
	vcloi.customer_id """.format(dPayload["hypervisor_id"], dPayload["dc_name"], dPayload["obj_type"], dPayload["hypervisor_id"], dPayload["dc_name"])
                    sQuery = """
select distinct * from (
select  
	CASE WHEN vcenti.obj_modified_on > to_date(to_char(now(), 'DD-MM-YYYY'), 'DD-MM-YYYY') THEN 'new' END AS state, 
	vcenti.pk_object_id, 
	vcenti.object_name, 
	to_char(vcenti.obj_modified_on, 'DD/MM/YYYY HH24:MI:SS') last_modified_date, 
	vcenti.obj_remark,
	vcloi.customer_id || '::' || vcloi.customer_name customer, vcents.object_state
from 
	vcenter_object_inventory vcenti
	left join vcloud_object_inventory vcloi on(vcenti.object_ref=vcloi.vm_vcenter_ref) 
	left join ( select * from  vcenter_object_state where dc_id=(select pk_object_id from vcenter_object_inventory where fk_hypervisor_id={0} and object_name='{1}') ) vcents on(vcenti.object_ref=vcents.object_ref) 
where 
	vcenti.dc_id=(select pk_object_id from vcenter_object_inventory where fk_hypervisor_id={2} and object_name='{3}') and 
	vcenti.object_type='{4}' 
order by 
	vcloi.customer_id ) A""".format(dPayload["hypervisor_id"], dPayload["dc_name"], dPayload["hypervisor_id"], dPayload["dc_name"], dPayload["obj_type"])
                else:
                    sQuery = """select CASE WHEN obj_modified_on > to_date(to_char(now(), 'DD-MM-YYYY'), 'DD-MM-YYYY') THEN 'new' END AS state, pk_object_id, object_name, to_char(obj_modified_on, 'DD/MM/YYYY HH24:MI:SS') last_modified_date, obj_remark from vcenter_object_inventory
                                where dc_id=(select pk_object_id from vcenter_object_inventory where fk_hypervisor_id={0} and object_name='{1}') and object_type='{2}'  order by obj_modified_on desc """.format(
                        dPayload["hypervisor_id"], dPayload["dc_name"], dPayload["obj_type"]
                    )
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getInventoryCountkvm():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sDTQuery = """select 
                (select count(*) hosts from (select distinct(h_host) from onapp_object_inventory) A), 
                (select count(*) vms from (select distinct(v_identifier) from onapp_object_inventory) A), 
                (select count(*) customers from (select distinct(c_login) from onapp_object_inventory) A)"""
                dRet = pconn.returnSelectQueryResult(sDTQuery)
                if dRet["result"] == "success":
                    return json.dumps({"result": "success", "data": dRet["data"]})
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def singleObjectKVM(typ):
    try:
        sQuery = ""
        if typ.lower() == "hosts":
            sQuery = "select h_id host_id, h_type host_type, h_host host, h_label hlabel, h_os host_os, h_osv host_os_version, count(h_id) total_vms from onapp_object_inventory where active_yn='Y' group by h_id, h_type, h_host, h_label, h_os, h_osv order by count(h_id) desc"
        elif typ.lower() == "vms":
            sQuery = "select v_power_state STATE, v_identifier VM_ID, v_label vm_name, v_operating_system VM_OS, c_login customer_id, h_host HOST, v_ip_addresses vm_IP from onapp_object_inventory where active_yn='Y' order by customer_id"
        elif typ.lower() == "customers":
            sQuery = "select c_id id, c_name customer_name, c_login customer_id, count(c_id) from onapp_object_inventory where active_yn='Y' group by c_id, c_name, c_login order by count(c_id) desc"
        dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
        if dRet["result"] == "success":
            return json.dumps(dRet)
        else:
            return json.dumps({"result": "failure", "data": "no data"})
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def getFirewallInven(hypervisor_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select int_id interface, int_name interface_name from firewall_object_inventory where fk_hypervisor_id={0} and active_yn='Y'".format(
                    hypervisor_id
                )
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getSwitchInven(hypervisor_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select int_id interface, int_name interface_name from switch_object_inventory where fk_hypervisor_id={0} and active_yn='Y'".format(
                    hypervisor_id
                )
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getLBInven(hypervisor_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select int_id interface, int_name interface_name from lb_object_inventory where fk_hypervisor_id={0} and active_yn='Y'".format(
                    hypervisor_id
                )
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getRInven(hypervisor_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select int_id interface, int_name interface_name from router_object_inventory where fk_hypervisor_id={0} and active_yn='Y'".format(
                    hypervisor_id
                )
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing











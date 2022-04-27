from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
from services.utils import ConnMaria as conn_m
from services.utils import ConnPostgreSQL as conn_p
import json
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
from flask import request
from urllib.parse import unquote

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar
logObj = create_log_file()
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

def getHostHostGroup4User(contact):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFRet, sQuery = [], ""
                sContactGroupQuery = """select contactgroup_object_id from (select o.object_id contactgroup_object_id, cg.contactgroup_id, o.name1 name, cg.alias description from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) contactgroup where contactgroup_id in(select contactgroup_id from 	nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and lower(o.name1)='{0}') contact))""".format(contact.strip().lower())
                dRet = conn_m.returnSelectQueryResult(sContactGroupQuery)
                if dRet["result"] == "success":
                    contact_group_id = dRet["data"][0]["contactgroup_object_id"]
                    sQuery = """select A.* from 
(select 
	hosts.host_object_id, hosts.host_id, hosts.name, hosts.description, hosts.display_name, hosts.address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name groupname, hostgroups.description groupdescription
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)) A
inner join
	nagios_host_contactgroups hcg on(A.host_id=hcg.host_id)
where hcg.contactgroup_object_id in(select contactgroup_object_id from (select o.object_id contactgroup_object_id, cg.contactgroup_id, o.name1 name, cg.alias description from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) contactgroup where contactgroup_id in(select contactgroup_id from 	nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and lower(o.name1)='{0}') contact)))""".format(contact.strip().lower())
                else:
                    sQuery = """select A.* from 
(select 
	hosts.host_object_id, hosts.host_id, hosts.name, hosts.description, hosts.display_name, hosts.address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name groupname, hostgroups.description groupdescription
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)) A
inner join
	nagios_host_contacts hcg on(A.host_id=hcg.host_id)
where hcg.contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and lower(o.name1)='{0}') contact)""".format(contact.strip().lower())
                dFRet = conn_m.returnSelectQueryResult(sQuery)
                if dFRet["result"] == "success":
                    dFirst, dFinal = {}, []
                    for eachI in dFRet["data"]:
                        host = {'host_object_id': eachI["host_object_id"], 'host_id': eachI["host_id"], 'host_name': eachI["name"],
                                'description': eachI["description"], 'display_name': eachI["display_name"], 'IP': eachI["address"]}
                        if eachI["groupname"] in list(dFirst.keys()):
                            dFirst[eachI["groupname"]].append(host)
                        else:
                            dFirst[eachI["groupname"]] = [host]
                    for i in dFirst:
                        l = len(dFirst[i])
                        dFinal.append({'hostgroupname': i, 'hostcount': l, 'hosts': dFirst[i]})
                    return json.dumps({"result": "success", "data": dFinal})
                else:
                    return json.dumps({"result": "failure", "data": "Failed fetching Host & Host Group details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getServiceDetails(host_object_id, filter):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinal = {}
                sFilter = "service asc" #default
                sQuery = ""
                subQuery = "(select host_object_id from nagios_hosts where lower(display_name) = lower('{0}'))".format(host_object_id)
                if filter == "status_a" or filter == "status_d":
                    if filter == "status_a":
                        sQuery = """select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={0} order by display_name) A  where A.current_state={1}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={2} order by display_name) A  where A.current_state={3}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={4} order by display_name) A  where A.current_state={5}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={6} order by display_name) A  where A.current_state={7}
                        """.format(subQuery, 2, subQuery, 1, subQuery, 0, subQuery, 3)
                    elif filter == "status_d":
                        sQuery = """select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={0} order by display_name) A  where A.current_state={1}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={2} order by display_name) A  where A.current_state={3}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={4} order by display_name) A  where A.current_state={5}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={6} order by display_name) A  where A.current_state={7}
                        """.format(subQuery, 0, subQuery, 1, subQuery, 2, subQuery, 3)
                else:
                    if filter == "service_a":
                        sFilter = " service asc"
                    elif filter == "service_d":
                        sFilter = " service desc"
                    elif filter == "since_a":
                        sFilter = " since asc"
                    elif filter == "since_d":
                        sFilter = " since desc"
                    sQuery = "select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={0} order by display_name) A order by {1}".format(subQuery, sFilter)
                dRet = conn_m.returnSelectQueryResultAs2DList(sQuery)
                ssQuery = "select count(*) total from ({0}) X".format(sQuery)
                dRetC = conn_m.returnSelectQueryResult(ssQuery)
                if dRet["result"] == "success" and dRetC["result"] == "success":
                    dFinal["result"] = "success"
                    dFinal["data"] = {"service": dRet["data"], "count": dRetC["data"][0]["total"]}
                    return json.dumps(dFinal)
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getServiceDetailsPOST(dPayload):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                host_object_id, filter = dPayload['host_object_id'], dPayload['filter']
                dFinal = {}
                sFilter = "service asc" #default
                sQuery = ""
                subQuery = "(select host_object_id from nagios_hosts where lower(display_name) = lower('{0}') limit 1)".format(host_object_id)
                if filter == "status_a" or filter == "status_d":
                    if filter == "status_a":
                        sQuery = """select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={0} order by display_name) A  where A.current_state={1}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={2} order by display_name) A  where A.current_state={3}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={4} order by display_name) A  where A.current_state={5}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={6} order by display_name) A  where A.current_state={7}
                        """.format(subQuery, 2, subQuery, 1, subQuery, 0, subQuery, 3)
                    elif filter == "status_d":
                        sQuery = """select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={0} order by display_name) A  where A.current_state={1}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={2} order by display_name) A  where A.current_state={3}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={4} order by display_name) A  where A.current_state={5}
                        union
                        select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={6} order by display_name) A  where A.current_state={7}
                        """.format(subQuery, 0, subQuery, 1, subQuery, 2, subQuery, 3)
                else:
                    if filter == "service_a":
                        sFilter = " service asc"
                    elif filter == "service_d":
                        sFilter = " service desc"
                    elif filter == "since_a":
                        sFilter = " since asc"
                    elif filter == "since_d":
                        sFilter = " since desc"
                    sQuery = "select A.service_object_id, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_check, '%d-%m-%Y %H:%i:%s') 'last change', date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_check,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) where s.host_object_id={0} order by display_name) A order by {1}".format(subQuery, sFilter)
                dRet = conn_m.returnSelectQueryResultAs2DList(sQuery)
                ssQuery = "select count(*) total from ({0}) X".format(sQuery)
                dRetC = conn_m.returnSelectQueryResult(ssQuery)
                if dRet["result"] == "success" and dRetC["result"] == "success":
                    dFinal["result"] = "success"
                    dFinal["data"] = {"service": dRet["data"], "count": dRetC["data"][0]["total"]}
                    return json.dumps(dFinal)
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getServiceDetailsOverAll(severity, filter, cust_type):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                queryies = {'ms': """select vm_name from tbl_vms where customer_id in(
select 
	c.customer_id 
from 
	tbl_customer c inner join tbl_customer_service_mapping csm on(c.cust_pk_id=csm.fk_customer_id) 
	inner join tbl_customer_services cs on(cs.cust_service_pk_id=csm.fk_service_id) 
where cs.service_name='Managed Service' and c.customer_id not in('NxtGen Mgmt vmware', 'NxtGen Mgmt kvm'))""",
                            'nms': """select vm_name from tbl_vms where customer_id != '' and customer_id is not null and customer_id not in(
select 
	c.customer_id 
from 
	tbl_customer c inner join tbl_customer_service_mapping csm on(c.cust_pk_id=csm.fk_customer_id) 
	inner join tbl_customer_services cs on(cs.cust_service_pk_id=csm.fk_service_id) 
where cs.service_name='Managed Service')""",
                            'mgmt': """select vm_name from tbl_vms where customer_id in(
select 
	c.customer_id 
from 
	tbl_customer c inner join tbl_customer_service_mapping csm on(c.cust_pk_id=csm.fk_customer_id) 
	inner join tbl_customer_services cs on(cs.cust_service_pk_id=csm.fk_service_id) 
where cs.service_name='Managed Service' and c.customer_id in('NxtGen Mgmt vmware', 'NxtGen Mgmt kvm'))""",
                            'anon': """select vm_name from tbl_vms where customer_id='' or customer_id is null	"""}
                retp = conn_p.returnSelectQueryResultAsList(queryies[cust_type])
                if retp["result"] == "failure":
                    return json.dumps(retp)

                dFinal = {}
                sFilter = " since asc"
                sQuery = ""
                # Severity
                filterErrors = ["error connecting to server", "service check timed out", "server version",
                                "soap request error", "host check timed out", "return code of 255 is out of bounds"]
                sFilterErrors = " and ".join([" lower(ss.output) not like '%{0}%' ".format(i) for i in filterErrors])
                if severity == 'critical':
                    sQuery = """select distinct A.host_name host, A.address, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select h.display_name host_name, h.address, s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) inner join nagios_hosts h on(h.host_object_id=s.host_object_id) where {2} order by host_name) A  where A.current_state={0} and A.host_name in({1})""".format(
                        2, ("'" + "','".join(retp["data"]["vm_name"]) + "'").encode('latin-1', 'ignore').decode('latin-1'), sFilterErrors
                    )
                elif severity == 'warning':
                    sQuery = """select distinct A.host_name host, A.address, A.display_name service, CASE A.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', A.output 'status_information',date_format(A.last_state_change, '%d-%m-%Y %H:%i:%s') 'since' from (select h.display_name host_name, h.address, s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) inner join nagios_hosts h on(h.host_object_id=s.host_object_id) where {2} order by host_name) A  where A.current_state={0} and A.host_name in({1})""".format(
                        1, ("'" + "','".join(retp["data"]["vm_name"]) + "'").encode('latin-1', 'ignore').decode('latin-1'), sFilterErrors
                    )
                # Filter
                if filter == "service_a":
                    sFilter = " service asc"
                elif filter == "service_d":
                    sFilter = " service desc"
                elif filter == "since_a":
                    sFilter = " since asc"
                elif filter == "since_d":
                    sFilter = " since desc"
                elif filter == "host_a":
                    sFilter = " host asc"
                elif filter == "host_d":
                    sFilter = " host desc"

                sQ = sQuery + " order by {0}".format(sFilter)
                dRet = conn_m.returnSelectQueryResultAs2DList(sQ)
                ssQuery = "select count(*) total from ({0}) X".format(sQ)
                dRetC = conn_m.returnSelectQueryResult(ssQuery)
                if dRet["result"] == "success" and dRetC["result"] == "success":
                    dFinal["result"] = "success"
                    dFinal["data"] = {"service": dRet["data"], "count": dRetC["data"][0]["total"]}
                    return json.dumps(dFinal)
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getUnknowServices():
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """select Y.hostgroup_name, Y.display_name host,  Y.address host_address, X.display_name service, X.status, X.output, X.since "since (days)" from 
(select A.*, s.host_object_id, s.display_name from 
(select service_object_id, CASE current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'status', output, DATEDIFF(now(),last_state_change) since from nagios_servicestatus where current_state=3) A inner join nagios_services s on(A.service_object_id=s.service_object_id)) X
inner join 
(select 
	hosts.host_object_id, hosts.host_id, hosts.name, hosts.description, hosts.display_name, hosts.address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hgdesc
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)) Y on (X.host_object_id=Y.host_object_id) order by 7 desc"""
                dRet = conn_m.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    dPayload = dRet["data"][1:]
                    # Create Mapping
                    dFinal, dMap = {}, {}
                    for i in dPayload: #map:
                        if dMap.keys().__contains__(i[0]):
                            dMap[i[0]].append(i[1:])
                        else:
                            dMap[i[0]] = [i[1:]]

                    for i in dMap:
                        dTmp = {}
                        for j in dMap[i]:
                            if dTmp.keys().__contains__(j[0]):
                                dTmp[j[0]].append(j[1:])
                            else:
                                dTmp[j[0]] = [["host_address", "service", "status" ,"output", "since(days)"], j[1:]]
                        dFinal[i] = dTmp

                    return json.dumps({"result": "success", "data": dFinal})

                else:
                    return logAndRet("failure", dRet["data"])
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getDashboardDetails(user_id):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQueryHostServiceCount = """
select X.hostgroup_name, X.total host_count, Y.total service_count from (
select A.hostgroup_name, count(A.hostgroup_name) total from (
select inn.* from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id)
where hcg.contactgroup_object_id in(select contactgroup_object_id from (select o.object_id contactgroup_object_id, cg.contactgroup_id, o.name1 name, cg.alias description from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) contactgroup where contactgroup_id in(select contactgroup_id from 	nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{0}') contact)))	) A
inner join nagios_hoststatus B on (A.host_object_id=B.host_object_id) group by A.hostgroup_name  ) X
inner join 
(select A.hostgroup_name, count(A.hostgroup_name) total from (
select X.* from (
select inn.hostgroup_name, inn.host_id, hcg.contactgroup_object_id, inn.host_object_id  from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id) ) X
inner join 
	(select contactgroup_object_id from (select o.object_id contactgroup_object_id, cg.contactgroup_id, o.name1 name, cg.alias description from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) contactgroup where contactgroup_id in(select contactgroup_id from 	nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{1}') contact))) Y on(X.contactgroup_object_id=Y.contactgroup_object_id) ) A
inner join (select s.host_object_id, s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) ) B 
on(A.host_object_id=B.host_object_id) group by A.hostgroup_name) Y on (lower(X.hostgroup_name)=lower(Y.hostgroup_name))""".format(user_id, user_id)

                sQueryHostServiceCount = """select X.hostgroup_name, X.total host_count, Y.total service_count from (
select A.hostgroup_name, count(A.hostgroup_name) total from (
select p.* from (select inn.*, hcg.contactgroup_object_id from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id) ) p inner join
(select m.contactgroup_object_id from(
select o.object_id contactgroup_object_id, cg.contactgroup_id from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) m inner join (
select contactgroup_id from nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{0}') contact)) n on(m.contactgroup_id=n.contactgroup_id)) q on(p.contactgroup_object_id=q.contactgroup_object_id) ) A
inner join nagios_hoststatus B on (A.host_object_id=B.host_object_id) group by A.hostgroup_name) X
inner join 
(select A.hostgroup_name, count(A.hostgroup_name) total from (
select X.* from (
select inn.hostgroup_name, inn.host_id, hcg.contactgroup_object_id, inn.host_object_id  from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id) ) X
inner join 
	(select m.contactgroup_object_id from(
select o.object_id contactgroup_object_id, cg.contactgroup_id from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) m inner join (
select contactgroup_id from nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{1}') contact)) n on(m.contactgroup_id=n.contactgroup_id)) Y on(X.contactgroup_object_id=Y.contactgroup_object_id) ) A
inner join (select s.host_object_id, s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) ) B 
on(A.host_object_id=B.host_object_id) group by A.hostgroup_name) Y on (lower(X.hostgroup_name)=lower(Y.hostgroup_name))""".format(user_id, user_id)

                sQueryHostCheck = """
                select X.* from (
select  A.hostgroup_name, CASE B.current_state WHEN 0 THEN 'UP' WHEN 1 THEN 'DOWN' WHEN 2 THEN 'UNREACHABLE' END 'current_state_desc', B.current_state, count(B.current_state) total from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
inner join nagios_hoststatus B on (A.host_object_id=B.host_object_id) group by A.hostgroup_name, B.current_state) X where X.hostgroup_name in(
select distinct hostgroup_name from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id)
where hcg.contactgroup_object_id in(select contactgroup_object_id from (select o.object_id contactgroup_object_id, cg.contactgroup_id, o.name1 name, cg.alias description from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) contactgroup where contactgroup_id in(select contactgroup_id from 	nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{0}') contact))))""".format(user_id)

                sQueryHostCheck = """select X.* from (
select  A.hostgroup_name, CASE B.current_state WHEN 0 THEN 'UP' WHEN 1 THEN 'DOWN' WHEN 2 THEN 'UNREACHABLE' END 'current_state_desc', B.current_state, count(B.current_state) total from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
inner join nagios_hoststatus B on (A.host_object_id=B.host_object_id) group by A.hostgroup_name, B.current_state) X where X.hostgroup_name in(
select X.hostgroup_name from (
select distinct hostgroup_name, hcg.contactgroup_object_id from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id) ) X
inner join 
(select m.contactgroup_object_id from(
select o.object_id contactgroup_object_id, cg.contactgroup_id from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) m inner join (
select contactgroup_id from nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{0}') contact)) n on(m.contactgroup_id=n.contactgroup_id)) Y on(X.contactgroup_object_id=Y.contactgroup_object_id))""".format(user_id)

                sQueryServiceCheck = """
                select X.* from (
select A.hostgroup_name, CASE B.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'current_state_desc', B.current_state, count(B.current_state) total from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
inner join (select s.host_object_id, s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) ) B 
on(A.host_object_id=B.host_object_id) group by A.hostgroup_name, B.current_state) X where X.hostgroup_name in(
select distinct hostgroup_name from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id)
where hcg.contactgroup_object_id in(select contactgroup_object_id from (select o.object_id contactgroup_object_id, cg.contactgroup_id, o.name1 name, cg.alias description from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) contactgroup where contactgroup_id in(select contactgroup_id from 	nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{0}') contact))))""".format(user_id)

                sQueryServiceCheck = """select X.* from (
select A.hostgroup_name, CASE B.current_state WHEN 0 THEN 'OK' WHEN 1 THEN 'WARNING' WHEN 2 THEN 'CRITICAL' WHEN 3 THEN 'UNKNOWN' END 'current_state_desc', B.current_state, count(B.current_state) total from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
inner join (select s.host_object_id, s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) ) B 
on(A.host_object_id=B.host_object_id) group by A.hostgroup_name, B.current_state) X where X.hostgroup_name in(
select X.hostgroup_name from (
select distinct hostgroup_name, hcg.contactgroup_object_id from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id) ) X
inner join 
(select m.contactgroup_object_id from(
select o.object_id contactgroup_object_id, cg.contactgroup_id from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) m inner join (
select contactgroup_id from nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{0}') contact)) n on(m.contactgroup_id=n.contactgroup_id)) Y on(X.contactgroup_object_id=Y.contactgroup_object_id))""".format(user_id)

                dRetHSTotal = conn_m.returnSelectQueryResult(sQueryHostServiceCount)
                dRetHChk = conn_m.returnSelectQueryResult(sQueryHostCheck)
                dRetSChk = conn_m.returnSelectQueryResult(sQueryServiceCheck)
                if dRetHSTotal["result"] == "success" and dRetHChk["result"] == "success" and dRetSChk["result"] == "success":
                    dHS = dRetHSTotal['data']
                    dH = dRetHChk['data']
                    dS = dRetSChk['data']
                    dHFinal, dSFinal, dHGFinal, dFinal = {}, {}, {}, []
                    for eachHG in dHS:
                        k = eachHG['hostgroup_name']
                        del eachHG['hostgroup_name']
                        dHGFinal[k] = eachHG
                    for eachH in dH:
                        if eachH['hostgroup_name'] in list(dHFinal.keys()):
                            dHFinal[eachH['hostgroup_name']].append([eachH['current_state'], eachH['current_state_desc'], eachH['total']])
                        else:
                            dHFinal[eachH['hostgroup_name']] = [[eachH['current_state'], eachH['current_state_desc'], eachH['total']]]
                    for i in dHFinal:
                        s = set([(j[0], j[1]) for j in dHFinal[i]])
                        d = {(0, 'UP'), (1, 'DOWN'), (2, 'UNREACHABLE'), (3, 'PENDING')}.difference(s)
                        #d.union(s)
                        dHFinal[i].extend([[k[0], k[1], 0]for k in d])
                        newd = dHFinal[i]
                        dHFinal[i] = [eachSer for s in ['UP', 'DOWN', 'UNREACHABLE', 'PENDING'] for eachSer in newd if eachSer[1] == s]
                    for eachS in dS:
                        if eachS['hostgroup_name'] in list(dSFinal.keys()):
                            dSFinal[eachS['hostgroup_name']].append([eachS['current_state'], eachS['current_state_desc'], eachS['total']])
                        else:
                            dSFinal[eachS['hostgroup_name']] = [[eachS['current_state'], eachS['current_state_desc'], eachS['total']]]
                    for i in dSFinal:
                        s = set([(j[0], j[1]) for j in dSFinal[i]])
                        d = {(0,'OK'), (1, 'WARNING'), (2, 'CRITICAL'), (3, 'UNKNOWN'), (4, 'PENDING')}.difference(s)
                        #d.union(s)
                        dSFinal[i].extend([[k[0], k[1], 0]for k in d])
                        newd = dSFinal[i]
                        dSFinal[i] = [eachSer for s in ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN', 'PENDING'] for eachSer in newd if eachSer[1] == s]
                    sHG = set(list(dHFinal.keys()))
                    for eachHG in sHG:
                        if eachHG in list(dHGFinal.keys()):
                            dTmp = dHGFinal[eachHG]
                            dTmp['hostgroup'] = eachHG
                            dTmp['host_checks'] = dHFinal[eachHG]
                            dTmp['service_checks'] = dSFinal[eachHG]
                            dFinal.append(dTmp)
                    return json.dumps({"result": "success", "data": dFinal})
                else:
                    return logAndRet("failure", "no data")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTypeGrid(dPayload):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sHG = dPayload['hostgroup']
                sTyp = dPayload['type']
                sID = dPayload['id']
                sQuery = ""
                sQueryHosts = """
                select A.host_name, A.host_description, A.host_display_name, A.host_address from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
inner join nagios_hoststatus B on (A.host_object_id=B.host_object_id) where B.current_state={0} and A.hostgroup_name='{1}'"""
                sQueryService = """
                select A.host_name, B.display_name service, B.output 'status_information',date_format(B.last_state_change, '%d-%m-%Y %H:%i:%s') 'since(days)' from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
inner join (select s.host_object_id, s.service_object_id, s.display_name,ss.current_state,ss.output,ss.last_state_change  from nagios_services s inner join nagios_servicestatus ss on(s.service_object_id=ss.service_object_id) ) B 
on(A.host_object_id=B.host_object_id) where B.current_state={0} and A.hostgroup_name='{1}' order by host_name desc
                """
                if sTyp == 0:
                    sQuery += sQueryHosts.format(sID, sHG)
                else:
                    sQuery += sQueryService.format(sID, sHG)
                dRet = conn_m.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def loadHostGroupDropDown(user):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select distinct X.hostgroup_name from (
select inn.hostgroup_name, inn.host_id, hcg.contactgroup_object_id from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id) ) inn 
inner join
	nagios_host_contactgroups hcg on(inn.host_id=hcg.host_id) ) X
inner join 
	(select contactgroup_object_id from (select o.object_id contactgroup_object_id, cg.contactgroup_id, o.name1 name, cg.alias description from nagios_objects o inner join nagios_contactgroups cg on(o.object_id=cg.contactgroup_object_id) where o.is_active=1) contactgroup where contactgroup_id in(select contactgroup_id from 	nagios_contactgroup_members where contact_object_id in(select contact_object_id from (select o.object_id contact_object_id, c.contact_id, o.name1 name, c.alias description, c.email_address from nagios_objects o inner join nagios_contacts c on(o.object_id=c.contact_object_id) where o.is_active=1 and o.name1='{0}') contact))) Y on(X.contactgroup_object_id=Y.contactgroup_object_id) order by X.hostgroup_name""".format(user)
                dRet = conn_m.returnSelectQueryResultAsList(sQuery)
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

def loadHostDropDown(dPayload):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select X.host_display_name from (
select A.hostgroup_name, A.host_name, A.host_description, A.host_display_name from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
where A.hostgroup_name in('{0}')) X""".format(dPayload['HostGroup'])
                dRet = conn_m.returnSelectQueryResultAsList(sQuery)
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

def unq(l2D, ind):
    try:
        tmp = []
        for i in l2D:
            i[ind] = unquote(i[ind])
            tmp.append(i)
        return tmp
    except Exception as e:
        return []

def loadHostDropDownMix(dPayload):
    "This method fetches all the users from the database"
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select distinct X.host_display_name from (
select A.hostgroup_name, A.host_name, A.host_description, A.host_display_name from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
where A.hostgroup_name in('{0}')) X""".format(dPayload['HostGroup'])
                dRet = conn_m.returnSelectQueryResultAsList(sQuery)
                if dRet["result"] == "success":
                    if (dPayload['HostGroup'].lower().__contains__('vm') and dPayload['HostGroup'].lower().__contains__('esx')) or (dPayload['HostGroup'].lower().__contains__('vm') and dPayload['HostGroup'].lower().__contains__('hddc')) or (dPayload['HostGroup'].lower().__contains__('vcenter vm')):
                        hosts = dRet["data"]["host_display_name"]
                        mixQuery = """
select 
	i.object_name vm, COALESCE(i.object_ip, '') ip, COALESCE(c.customer_name, '') cust 
from 
	vcenter_object_inventory i left join vcloud_object_inventory c on(i.object_ref=c.vm_vcenter_ref)  
where 
	lower(i.object_name) in{0}""".format(str(tuple([i.lower() for i in hosts])))
                        dMixRet = conn_p.returnSelectQueryResultAs2DList(mixQuery)
                        if dMixRet["result"] == "success":
                            dbhosts = [i[0] for i in dMixRet["data"][1:]]
                            for i in set(hosts).difference(set(dbhosts)):
                                dMixRet["data"].append([i, '', ''])
                            dMixRet['multisearch'] = 'yes'
                            r = unq(dMixRet["data"][1:], 0)
                            if r:
                                r.insert(0, dMixRet["data"][0])
                                dMixRet["data"] = r
                            return json.dumps(dMixRet)
                        else:
                            dRet['multisearch'] = 'no'
                            return json.dumps(dRet)
                            #return json.dumps({"result": "failure", "data": "no data"})
                    elif dPayload['HostGroup'].lower().__contains__('vms') and dPayload['HostGroup'].lower().__contains__('ng'):
                        hosts = dRet["data"]["host_display_name"]
                        mixQuery = """
select 
	v_label vm, COALESCE(v_local_remote_access_ip_address, '') ip, COALESCE(c_name, '') cust  
from 
	onapp_object_inventory 
where 
	v_label in{0}""".format(str(tuple([i.lower() for i in hosts])))
                        dMixRet = conn_p.returnSelectQueryResultAs2DList(mixQuery)
                        if dMixRet["result"] == "success":
                            dbhosts = [i[0] for i in dMixRet["data"][1:]]
                            for i in set(hosts).difference(set(dbhosts)):
                                dMixRet["data"].append([i, '', ''])
                            dMixRet['multisearch'] = 'yes'
                            r = unq(dMixRet["data"][1:], 0)
                            if r:
                                r.insert(0, dMixRet["data"][0])
                                dMixRet["data"] = r
                            return json.dumps(dMixRet)
                        else:
                            dRet['multisearch'] = 'no'
                            return json.dumps(dRet)
                            #return json.dumps({"result": "failure", "data": "no data"})
                    else:
                        dRet['multisearch'] = 'no'
                        return json.dumps(dRet)
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing



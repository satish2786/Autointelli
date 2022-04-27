from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
from services.utils.ConnLog import create_log_file
from services.utils import ConnPostgreSQL as pcon
import services.utils.LFColors as lfc
from services.utils import validator_many as payloadvalidator
import json
from flask import request



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

def getTemplates():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select pk_template_id template_id, template_name from mon_templates where active_yn='Y'"
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAccountBasedOnTechno(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sTemplateName = dPayload['template_name']
                sFinalQuery = ""
                sQuery = "select customer_id || '..' || customer_name account from tbl_customer where technology_loc='{0}' and active_yn='Y'"
                if sTemplateName.strip().lower() == 'VMWare_vCenter_ESXIVM'.lower():
                    sFinalQuery = sQuery.format('vmware')
                elif sTemplateName.strip().lower() == 'KVMVM'.lower():
                    sFinalQuery = sQuery.format('kvm')
                dRet = pcon.returnSelectQueryResultAs2DList(sFinalQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getObjects(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['template_name'], lMandatory=['template_name']):
                    sQuery = ""
                    if [1 if i in ['template_name', 'account_name'] else 0 for i in dPayload.keys()] == [1, 1]:
                        if dPayload['template_name'].lower() == 'VMWare_vCenter_ESXIVM'.lower():
                            sQuery = "select distinct vm_name from tbl_vms where device_type='esxivm' and techno='vmware' and lower(customer_id)=lower('{0}') order by vm_name".format(
                                dPayload['account_name']
                            )
                        elif dPayload['template_name'].lower() == 'KVMVM'.lower():
                            sQuery = "select distinct vm_name from tbl_vms where device_type='kvmvm' and techno='kvm' and lower(customer_id)=lower('{0}') order by vm_name".format(
                                dPayload['account_name']
                            )
                    else:
                        if dPayload['template_name'].lower() == 'KVMVM'.lower():
                            sQuery = "select distinct vm_name from tbl_vms where device_type='kvmvm' and techno='kvm' order by vm_name"
                        elif dPayload['template_name'].lower() == 'VMWare_vCenter_ESXIHost'.lower():
                            sQuery = "select distinct vm_name from tbl_vms where device_type='esxihost' and techno='vmware' order by vm_name"
                        elif dPayload['template_name'].lower() == 'VMWare_vCenter_ESXIDataStore'.lower():
                            sQuery = "select distinct vm_name from tbl_vms where device_type='datastore' and techno='vmware' order by vm_name"
                    dRet = pcon.returnSelectQueryResultAsList(sQuery)
                    return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def createHostGroup(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['host_group_name', 'objects', 'extra_search_info'],
                                                   lMandatory=['host_group_name', 'objects', 'extra_search_info']):
                    hostGroupName = dPayload['host_group_name']
                    hostGroupDesc = dPayload['host_group_desc']
                    objects = dPayload['objects']
                    extraJSON = dPayload['extra_search_info']

                    # Validate
                    sQuery = "select * from mon_hostgroups where lower(hostgroup_name)=lower('{0}')".format(hostGroupName)
                    sRet = pcon.returnSelectQueryResult(sQuery)
                    if sRet['result'] == 'success':
                        return json.dumps({'result': 'failure', 'data': 'Choose a different name. Already exists.'})

                    iQuery = "insert into mon_hostgroups(hostgroup_name, hostgroup_desc, extra_search_info, active_yn) values('{0}', '{1}', '{2}', 'Y') RETURNING pk_hostgroup_id".format(
                        hostGroupName, hostGroupDesc, json.dumps(extraJSON)
                    )
                    dRet = pcon.returnSelectQueryResultWithCommit(iQuery)
                    if dRet['result'] == 'success':
                        hgid = dRet['data'][0]['pk_hostgroup_id']
                        hIdQuery = "select {0} hg_id, pk_host_id host_id from mon_hosts where hostname in('{1}')".format(
                            hgid,
                            "','".join(objects)
                        )
                        hIdRet = pcon.returnSelectQueryResultAs2DList(hIdQuery)
                        if hIdRet['result'] == 'success':
                            mapQuery = "insert into mon_host_hostgroup_mapping(fk_hg_id, fk_host_id) values{0}".format(
                                str([tuple(i) for i in hIdRet['data'][1:]])[1:-1]
                            )
                            mapRet = pcon.returnInsertResult(mapQuery)
                            if mapRet['result'] == 'success':
                                return json.dumps({'result': 'success', 'data': 'HostGroup {0} added successfully'.format(hostGroupName)})
                            else:
                                # roll back
                                dQuery = "delete from mon_hostgroups where lower(hostgroup_name)=lower('{0}')".format(
                                    hostGroupName)
                                sRet = pcon.returnSelectQueryResult(dQuery)
                                if sRet['result'] == 'failure':
                                    print("Send a notification to developer on the bug with error")
                                return json.dumps({'result': 'failure', 'data': 'HostGroup {0} addition failed'.format(hostGroupName)})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'Not able to fetch host details'})
                    else:
                        return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def mapUserHostGroup(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['host_group_name', 'users'],
                                                   lMandatory=['host_group_name', 'users']):
                    hostGroupName = dPayload['host_group_name']
                    users = dPayload['users']

                    sQuery = "select pk_hostgroup_id hg_id from mon_hostgroups where lower(hostgroup_name)=lower('{0}') and active_yn='Y'".format(
                        hostGroupName
                    )
                    dRet = pcon.returnSelectQueryResult(sQuery)
                    if dRet['result'] == 'success':
                        hg_id = dRet['data'][0]['hg_id']
                        frQuery = "select pk_u_h_map_id id from mon_user_hostgroups_mapping where fk_hostgroup_id={0}".format(hg_id)
                        frRet = pcon.returnSelectQueryResultAsList(frQuery)
                        iQuery = "insert into mon_user_hostgroups_mapping(fk_hostgroup_id, user_id) values{0}".format(
                            str([tuple((hg_id, i)) for i in users])[1:-1]
                        )
                        iRet = pcon.returnInsertResult(iQuery)
                        if iRet['result'] == 'success':
                            if frRet['result'] == 'success':
                                dQuery = "delete from mon_user_hostgroups_mapping where pk_u_h_map_id in({0})".format(
                                    ",".join([str(i) for i in frRet['data']['id']])
                                )
                                ddRet = pcon.returnInsertResult(dQuery)
                                if ddRet['result'] == 'success':
                                    return json.dumps({'result': 'success', 'data': 'User and Host Group mapping success'})
                                else:
                                    # roll back
                                    dsQuery = "select pk_u_h_map_id id from mon_user_hostgroups_mapping where fk_hostgroup_id={0}".format(hg_id)
                                    dsRet = pcon.returnSelectQueryResultAsList(dsQuery)
                                    if dsRet['result'] == 'success':
                                        setA = set(dsRet['data']['id']).difference(set(frRet['data']['id']))
                                        if len(setA) > 0:
                                            dQuery = "delete from mon_user_hostgroups_mapping where pk_u_h_map_id in({0})".format(
                                                ",".join([str(i) for i in setA])
                                            )
                                            dRet = pcon.returnInsertResult(dQuery)
                                    return json.dumps({'result': 'failure', 'data': 'User mapping with Host Group failed'})
                            else:
                                return json.dumps({'result': 'success', 'data': 'User and Host Group mapping success'})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'User mapping with Host Group failed'})
                    else:
                        return json.dumps({'result': 'failure', 'data': "HostGroup {0} doesn't exists".format(hostGroupName)})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def loadHGGrid():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                hhgmQuery = """
select 
	hg.pk_hostgroup_id hg_id, hg.hostgroup_name, hg.extra_search_info, h.pk_host_id h_id, h.hostname, h.address, hg.hostgroup_desc 
from 
	mon_hostgroups hg left join mon_host_hostgroup_mapping hhgm on(hg.pk_hostgroup_id=hhgm.fk_hg_id) 
	left join mon_hosts h on(hhgm.fk_host_id=h.pk_host_id) 
where hg.active_yn='Y' 
order by 
	hg.hostgroup_name, h.hostname"""
                uhgmQuery = """
select 
	hg.pk_hostgroup_id hg_id, hg.hostgroup_name, uhgm.user_id 
from 
	mon_hostgroups hg left join mon_user_hostgroups_mapping uhgm on(uhgm.fk_hostgroup_id=hg.pk_hostgroup_id) 
where hg.active_yn='Y'  
order by 
	hg.hostgroup_name"""
                hhgmRet = pcon.returnSelectQueryResultAs2DList(hhgmQuery)
                uhgmRet = pcon.returnSelectQueryResultAs2DList(uhgmQuery)
                if hhgmRet['result'] == 'success' and uhgmRet['result'] == 'success':
                    hhgm = hhgmRet['data'][1:]
                    hhgmD = {}
                    for i in hhgm:
                        if i[0] in hhgmD.keys():
                            hhgmD[i[0]]["hosts"].append([i[3], i[4], i[5]])
                        else:
                            hhgmD[i[0]] = {
                                "hostgroup_name": i[1],
                                "search_info": i[2],
                                "hostgroup_desc": i[6],
                                "hosts": [[i[3], i[4], i[5]]],
                                "users": []
                            }
                    uhgm = uhgmRet['data'][1:]
                    for i in uhgm:
                        if i[0] in hhgmD.keys():
                            hhgmD[i[0]]["users"].append(i[2])
                    return json.dumps({'result': 'success', 'data': hhgmD})
                else:
                    return json.dumps({'result': 'failure', 'data': 'no data'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def usersUnselectedSelectedList(hg_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                allUQuery = "select distinct user_id from tbl_user_details where active_yn='Y'"
                hgUQuery = "select distinct user_id from mon_user_hostgroups_mapping where fk_hostgroup_id={0}".format(hg_id)
                allURet = pcon.returnSelectQueryResultAsList(allUQuery)
                hgURet = pcon.returnSelectQueryResultAsList(hgUQuery)
                if allURet['result'] == 'success' and hgURet['result'] == 'success':
                    setAllUsers = set(allURet['data']['user_id'])
                    setHgUsers = set(hgURet['data']['user_id'])
                    return json.dumps({
                        'result': 'success',
                        'data': {
                            'unselected': list(setAllUsers.difference(setHgUsers)),
                            'selected': list(setHgUsers)
                        }
                    })
                elif allURet['result'] == 'success' and hgURet['result'] == 'failure':
                    return json.dumps({
                        'result': 'success',
                        'data': {
                            'unselected': allURet['data']['user_id'],
                            'selected': []
                        }
                    })
                else:
                    return json.dumps({'result': 'failure', 'data': 'Unable to fetch user list'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def hostUnselectedSelectedList(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['host_group_id', 'extra_search_info'],
                                                   lMandatory=['host_group_id', 'extra_search_info']):
                    hghQuery = "select hostname from mon_hosts where pk_host_id in(select fk_host_id from mon_host_hostgroup_mapping where fk_hg_id={0})".format(
                        dPayload['host_group_id']
                    )
                    hghRet = pcon.returnSelectQueryResultAsList(hghQuery)
                    hgallRet = json.loads(getObjects(dPayload['extra_search_info']))
                    if hghRet['result'] == 'success' and hgallRet['result'] == 'success':
                        setHGH = set(hghRet['data']['hostname'])
                        setHGAll = set(hgallRet['data']['vm_name'])
                        return json.dumps({
                            'result': 'success',
                            'data': {
                                'unselected': list(setHGAll.difference(setHGH)),
                                'selected': list(setHGH)
                            }
                        })
                    elif hgallRet['result'] == 'success' and hghRet['result'] == 'failure':
                        return json.dumps({
                            'result': 'success',
                            'data': {
                                'unselected': hgallRet['data']['vm_name'],
                                'selected': []
                            }
                        })
                    else:
                        return json.dumps({'result': 'failure', 'data': 'Unable to fetch host list'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateHostGroup(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload,
                                                   lHeaders=['host_group_name', 'host_group_id', 'host_group_desc', 'objects', 'extra_search_info'],
                                                   lMandatory=['host_group_name', 'host_group_id', 'host_group_desc', 'objects', 'extra_search_info']):
                    hostGroupName = dPayload['host_group_name']
                    hostGroupDesc = dPayload['host_group_desc']
                    hostGroupID = dPayload['host_group_id']
                    objects = dPayload['objects']
                    extraJSON = dPayload['extra_search_info']

                    # take backup to rollback
                    hrefMainQuery = "select hostgroup_name, hostgroup_desc, extra_search_info from  mon_hostgroups where pk_hostgroup_id={0}".format(
                        hostGroupID)
                    hrefMainRet = pcon.returnSelectQueryResult(hrefMainQuery)

                    uQuery = "update mon_hostgroups set hostgroup_name='{0}', hostgroup_desc='{1}', extra_search_info='{2}' where pk_hostgroup_id={3}".format(
                        hostGroupName, hostGroupDesc, json.dumps(extraJSON), hostGroupID
                    )
                    dRet = pcon.returnInsertResult(uQuery)
                    if dRet['result'] == 'success':

                        # take backup to rollback
                        hrefQuery = "select pk_host_id host_id from mon_hosts where hostname in('{0}')".format(
                            "','".join(objects)
                        )
                        hrefRet = pcon.returnSelectQueryResultAsList(hrefQuery)

                        hIdQuery = "select {0} hg_id, pk_host_id host_id from mon_hosts where hostname in('{1}')".format(
                            hostGroupID,
                            "','".join(objects)
                        )
                        hIdRet = pcon.returnSelectQueryResultAs2DList(hIdQuery)
                        if hIdRet['result'] == 'success':
                            mapQuery = "insert into mon_host_hostgroup_mapping(fk_hg_id, fk_host_id) values{0}".format(
                                str([tuple(i) for i in hIdRet['data'][1:]])[1:-1]
                            )
                            mapRet = pcon.returnInsertResult(mapQuery)
                            if mapRet['result'] == 'success':
                                # delete
                                if hrefRet['result'] == 'success':
                                    dQuery = "delete from mon_host_hostgroup_mapping where fk_host_id in('{0}')".format(
                                        "','".join([str(i) for i in hrefRet['data']['host_id']])
                                    )
                                    dRet = pcon.returnInsertResult(dQuery)
                                    if dRet['result'] == 'failure':
                                        print('delete existing failed')
                                return json.dumps({'result': 'success', 'data': 'HostGroup {0} updated successfully'.format(hostGroupName)})
                            else:
                                # roll back
                                if hrefMainRet['result'] == 'success':
                                    rollQuery = "update mon_hostgroups set hostgroup_name='{0}', hostgroup_desc='{1}', extra_search_info='{2}' where pk_hostgroup_id={3}".format(
                                        hrefMainRet['data'][0]['hostgroup_name'], hrefMainRet['data'][0]['hostgroup_desc'],
                                        json.dumps(hrefMainRet['data'][0]['extra_search_info']), hostGroupID
                                    )
                                    rollRet = pcon.returnSelectQueryResultWithCommit(rollQuery)
                                    if rollRet['result'] == 'success':
                                        return json.dumps({'result': 'failure', 'data': 'HostGroup {0} updation failed'.format(hostGroupName)})
                                    else:
                                        print('rollback failed')
                                        return json.dumps({'result': 'failure', 'data': 'HostGroup {0} updation failed'.format(
                                                               hostGroupName)})
                                else:
                                    print('backup information not available to restore')
                                    return json.dumps({'result': 'failure',
                                                       'data': 'HostGroup {0} updation failed'.format(hostGroupName)})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'Not able to fetch host details'})
                    else:
                        return json.dumps({'result': 'failure', 'data': 'HostGroup {0} updation failed'.format(hostGroupName)})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteHostGroup(hg_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                # rollback queries
                hgRollQuery = "update mon_hostgroups set active_yn='Y' where pk_hostgroup_id={0}".format(hg_id)
                hghRollQuery = "insert into mon_host_hostgroup_mapping(fk_hg_id, fk_host_id) values{0}"
                hguRollQuery = "insert into mon_user_hostgroups_mapping(fk_hostgroup_id, user_id) values{0}"

                # transactional queries
                hgDelQuery = "update mon_hostgroups set active_yn='N' where pk_hostgroup_id={0}".format(hg_id)
                hghDelQuery = "delete from mon_host_hostgroup_mapping where fk_hg_id={0}".format(hg_id)
                hguDelQuery = "delete from mon_user_hostgroups_mapping where fk_hostgroup_id={0}".format(hg_id)

                # backup
                hhgBKPQuery = "select fk_host_id from mon_host_hostgroup_mapping where fk_hg_id={0}".format(hg_id)
                uhgBKPQuery = "select user_id from mon_user_hostgroups_mapping where fk_hostgroup_id={0}".format(hg_id)
                hhgBKPRet = pcon.returnSelectQueryResultAsList(hhgBKPQuery)
                uhgBKPRet = pcon.returnSelectQueryResultAsList(uhgBKPQuery)

                hg, hhg, uhg = 0, 0, 0
                hgDelRet = pcon.returnInsertResult(hgDelQuery)
                if hgDelRet['result'] == 'success':
                    hghDelRet = pcon.returnInsertResult(hghDelQuery)
                    if hghDelRet['result'] == 'success':
                        hguDelRet = pcon.returnInsertResult(hguDelQuery)
                        if hguDelRet['result'] == 'success':
                            return json.dumps({'result': 'success', 'data': 'Host Group removed successfully'})
                        else:
                            uhg = 1
                            hgRollRet = pcon.returnInsertResult(hgRollQuery)
                            if hhgBKPRet['result'] == 'success':
                                hghRollQuery = hghRollQuery.format(
                                    str([tuple(hg_id, i) for i in hhgBKPRet['data']['fk_host_id']])[1:-1]
                                )
                                hghRollRet = pcon.returnInsertResult(hghRollQuery)
                            return json.dumps({'result': 'success', 'data': 'Failed to remove Host Group'})
                    else:
                        hhg = 1
                        hgRollRet = pcon.returnInsertResult(hgRollQuery)
                        return json.dumps({'result': 'success', 'data': 'Failed to remove Host Group'})
                else:
                    hg = 1
                    return json.dumps({'result': 'success', 'data': 'Failed to remove Host Group'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getServiceCheckConfigForObject(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQueryAvail = """
select 
	hsc.pk_config_id config_id, hsc.check_type, s.pk_service_id service_id, s.service_name, hsc.threshold_warning, hsc.threshold_critical, hsc.threshold_unit, hsc.check_interval, hsc.retry_interval, hsc.max_check_attempts  
from 
	mon_host_service_config hsc left join mon_hosts h on(hsc.fk_host_id=h.pk_host_id) 
	left join mon_services s on(hsc.fk_service_id=s.pk_service_id) 
where  
    lower(h.hostname)=lower('{0}') order by hsc.check_type """.format(dPayload['host_name'])
                dAvailRet = pcon.returnSelectQueryResultAs2DList(sQueryAvail)
                sQueryNew = """
select check_type, fk_template_id template_id, pk_service_id service_id, service_name, default_threshold_warning, default_threshold_critical, default_threshold_unit, default_check_interval, default_retry_interval, default_max_check_attempts from(
select * from mon_services where fk_template_id in(
select distinct s.fk_template_id 
from  
	mon_host_service_config hsc left join mon_hosts h on(hsc.fk_host_id=h.pk_host_id) 
	inner join mon_services s on(hsc.fk_service_id=s.pk_service_id) 
where lower(h.hostname)=lower('{0}') and s.active_yn='Y')
except 
select s.* 
from  
	mon_host_service_config hsc left join mon_hosts h on(hsc.fk_host_id=h.pk_host_id) 
	inner join mon_services s on(hsc.fk_service_id=s.pk_service_id) 
where lower(h.hostname)=lower('{1}') and s.active_yn='Y') A""".format(dPayload['host_name'], dPayload['host_name'])
                dNewRet = pcon.returnSelectQueryResultAs2DList(sQueryNew)
                flagsQuery = "select email_alerts, email_alerts_yn, ticketing_yn from mon_hosts where lower(hostname)=lower('{0}')".format(dPayload['host_name'])
                flagRet = pcon.returnSelectQueryResult(flagsQuery)
                dFinal = {}
                if dAvailRet['result'] == 'success':
                    dFinal['existing'] = dAvailRet['data']
                    if dNewRet['result'] == 'success':
                        dFinal['new'] = dNewRet['data']
                    else:
                        dFinal['new'] = []
                    if flagRet['result'] == 'success':
                        dFinal['emails'] = flagRet['data'][0]['email_alerts'].split(',') if flagRet['data'][0]['email_alerts'] != None and flagRet['data'][0]['email_alerts'] != '' else []
                        dFinal['email_flag'] = flagRet['data'][0]['email_alerts_yn']
                        dFinal['ticket_flag'] = flagRet['data'][0]['ticketing_yn']
                    return json.dumps({'result': 'success', 'data': dFinal})
                else:
                    return json.dumps({'result': 'failure', 'data': 'No service checks configured for the host'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateServiceCheckConfigForObject(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['host_name', 'service_checks', 'new_service_checks'], lMandatory=['host_name', 'service_checks', 'new_service_checks']):

                    # hostid = dPayload["host_id"]
                    hostname = dPayload["host_name"]
                    serviceChecks = dPayload["service_checks"]
                    newChecks = dPayload["new_service_checks"]
                    emails = ','.join(dPayload["emails"])

                    # Info Gathering hostid and flags
                    query = "select pk_host_id host_id, email_alerts from mon_hosts where lower(hostname)=lower('{0}')".format(hostname)
                    queryRet = pcon.returnSelectQueryResult(query)
                    if queryRet['result'] == 'failure':
                        return json.dumps({'result': 'failure', 'data': 'Invalid host. Not Found'})
                    hostid = queryRet['data'][0]['host_id']
                    bkpEmails = queryRet['data'][0]['email_alerts']

                    # Backup
                    bkpQuery = """
                    select 
                    	hsc.pk_config_id config_id, hsc.check_type, s.pk_service_id service_id, s.service_name, hsc.threshold_warning, hsc.threshold_critical, hsc.threshold_unit, hsc.check_interval, hsc.retry_interval, hsc.max_check_attempts  
                    from 
                    	mon_host_service_config hsc left join mon_hosts h on(hsc.fk_host_id=h.pk_host_id) 
                    	left join mon_services s on(hsc.fk_service_id=s.pk_service_id) 
                    where  
                        lower(h.hostname)=lower('{0}') order by hsc.check_type """.format(hostname)
                    bkpRet = pcon.returnSelectQueryResultAs2DList(bkpQuery)
                    if bkpRet['result'] == 'success':

                        # Validation
                        dFail, sCnt, fCnt = [], 0, 0
                        l = [1 if len(i) == 10 else 0 for i in serviceChecks]
                        if 0 in l:
                            return json.dumps({'result': 'failure', 'data': 'Data missing in service_checks'})

                        # No Change Validation
                        # if not 0 in [1 if i in serviceChecks else 0 for i in bkpRet['data'][1:]]:
                        #     return json.dumps({'result': 'failure', 'data': 'No modifications found to update'})

                        # Transaction
                        for eachChecks in serviceChecks:
                            uQuery = "update mon_host_service_config set threshold_warning='{0}', threshold_critical='{1}', check_interval='{2}', retry_interval='{3}', max_check_attempts='{4}' where pk_config_id={5}".format(
                                eachChecks[4], eachChecks[5], eachChecks[7], eachChecks[8], eachChecks[9], eachChecks[0]
                            )
                            dRet = pcon.returnInsertResult(uQuery)
                            if dRet['result'] == 'success':
                                sCnt += 1
                            else:
                                fCnt += 1
                                break

                        for eachChecks in newChecks:
                            iQuery = """insert into mon_host_service_config(fk_host_id, fk_template_id, fk_service_id, threshold_warning, threshold_critical, threshold_unit, check_interval, retry_interval, max_check_attempts, check_type, created_by, created_on, active_yn) values({0}, {1}, {2}, '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', 'admin', now(), 'Y')""".format(
                                hostid, eachChecks[1], eachChecks[2], eachChecks[4], eachChecks[5], eachChecks[6], eachChecks[7], eachChecks[8], eachChecks[9], eachChecks[0],
                            )
                            dRet = pcon.returnInsertResult(iQuery)
                            # if dRet['result'] == 'success':
                            #     sCnt += 1
                            # else:
                            #     fCnt += 1

                        eQuery = "update mon_hosts set email_alerts='{0}' where pk_host_id={1}".format(emails, hostid)
                        eRet = pcon.returnInsertResult(eQuery)

                        # Roll Back
                        sRCnt, fRCnt = 0, 0
                        if fCnt > 0:
                            for eachChecks in bkpRet['data']:
                                uQuery = "update mon_host_service_config set threshold_warning='{0}', threshold_critical='{1}', check_interval='{2}', retry_interval='{3}', max_check_attempts='{4}' where pk_config_id={5}".format(
                                    eachChecks[4], eachChecks[5], eachChecks[7], eachChecks[8], eachChecks[9],
                                    eachChecks[0]
                                )
                                dRet = pcon.returnInsertResult(uQuery)
                                if dRet['result'] == 'success':
                                    sRCnt += 1
                                else:
                                    fRCnt += 1
                            if fRCnt > 0:
                                print("Roll Back Failed. BackUp: {0}".format(bkpRet['data']))
                            return json.dumps({'result': 'failure', 'data': 'Failed to update Service Checks'})
                        else:
                            return json.dumps({'result': 'success', 'data': 'Service Checks updated successfully for {0}'.format(hostname)})

                    else:
                        return json.dumps({'result': 'failure', 'data': 'Not a valid host: {0}'.format(hostname)})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateHostFlags(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['host_name', 'flag', 'status'], lMandatory=['host_name', 'flag', 'status']):

                    flagQuery = "update mon_hosts set {0}='{1}' where lower(hostname)=lower('{2}')".format(
                        'email_alerts_yn' if dPayload['flag'] == 'email' else 'ticketing_yn', dPayload['status'], dPayload['host_name']
                    )
                    flagRet = pcon.returnInsertResult(flagQuery)
                    if flagRet['result'] == 'success':
                        return json.dumps({'result': 'success', 'data': 'Service opted'})
                    else:
                        return json.dumps({'result': 'success', 'data': 'Failed to opt for service'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getHostGroupByUser(user_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select hostgroup_name from mon_hostgroups where pk_hostgroup_id in(select fk_hostgroup_id from mon_user_hostgroups_mapping where lower(user_id)=lower('{0}')) and active_yn='Y'".format(
                    user_id
                )
                dRet = pcon.returnSelectQueryResultAsList(sQuery)
                if dRet['result'] == 'success':
                    return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'No Host Group mapped'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getHostsByHostGroup(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['hostgroup_name'], lMandatory=['hostgroup_name']):
                    tQuery = "select extra_search_info from mon_hostgroups where lower(hostgroup_name)=lower('{0}') and active_yn='Y'".format(
                        dPayload['hostgroup_name']
                    )
                    tRet = pcon.returnSelectQueryResult(tQuery)
                    if tRet['result'] == 'success':
                        theKeys = tRet['data'][0]['extra_search_info']
                        if 'template_name' in theKeys.keys():
                            if theKeys['template_name'] == 'VMWare_vCenter_ESXIVM' or theKeys['template_name'] == 'KVMVM':
                                sQuery = """
select 
	v.vm_name, v.vm_ip, v.customer_id
from 
	mon_hosts h inner join mon_host_hostgroup_mapping hhgm on(h.pk_host_id=hhgm.fk_host_id)
	inner join mon_hostgroups hg on(hg.pk_hostgroup_id=hhgm.fk_hg_id) 
	inner join tbl_vms v on(lower(v.vm_name)=lower(h.hostname))
where 
	lower(hg.hostgroup_name) = lower('{0}')""".format(dPayload['hostgroup_name'])
                                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                                if dRet['result'] == 'success':
                                    dRet['multisearch'] = 'yes'
                                    return json.dumps(dRet)
                                else:
                                    if dRet['data'] == 'no data':
                                        return json.dumps(dRet)
                                    else:
                                        return json.dumps({'result': 'failure', 'data': 'Failed to fetch host list. Try after sometime.'})
                            else:
                                sQuery = """
                                                            select 
                                                            	h.hostname host_display_name 
                                                            from 
                                                            	mon_hosts h inner join mon_host_hostgroup_mapping hhgm on(h.pk_host_id=hhgm.fk_host_id)
                                                            	inner join mon_hostgroups hg on(hg.pk_hostgroup_id=hhgm.fk_hg_id)
                                                            where 
                                                            	lower(hg.hostgroup_name) = lower('{0}')""".format(
                                    dPayload['hostgroup_name'])
                                dRet = pcon.returnSelectQueryResultAsList(sQuery)
                                if dRet['result'] == 'success':
                                    dRet['multisearch'] = 'no'
                                    return json.dumps(dRet)
                                else:
                                    if dRet['data'] == 'no data':
                                        return json.dumps(dRet)
                                    else:
                                        return json.dumps({'result': 'failure', 'data': 'Failed to fetch host list. Try after sometime.'})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'Template not mapped for {0}'.format(dPayload['hostgroup_name'])})
                    else:
                        return json.dumps({'result': 'failure', 'data': '{0} not found'.format(dPayload['hostgroup_name'])})


                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


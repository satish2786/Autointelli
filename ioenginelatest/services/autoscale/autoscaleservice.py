from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import json
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
from flask import request
import services.utils.ConnPostgreSQL as pcon
from decimal import Decimal
from services.utils import DynamicE2XL as xl

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar
logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

location = ''
try:
    location = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['onapploc']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

dIPFQDN = {'blr-': [{'host': '10.227.45.119', 'port': 9200}, {'host': '10.227.45.120', 'port': 9200}, {'host': '10.227.45.121', 'port': 9200}],
           'amd-': [{'host': '10.210.45.119', 'port': 9200}, {'host': '10.210.45.120', 'port': 9200}, {'host': '10.210.45.121', 'port': 9200}],
           'fbd-': [{'host': '10.195.45.119', 'port': 9200}, {'host': '10.195.45.120', 'port': 9200}, {'host': '10.195.45.121', 'port': 9200}],
           'mum-': [{'host': '10.239.45.218', 'port': 9200}, {'host': '10.239.45.219', 'port': 9200}, {'host': '10.239.45.220', 'port': 9200}, {'host': '10.239.45.221', 'port': 9200}, {'host': '10.239.45.222', 'port': 9200}, {'host': '10.239.45.223', 'port': 9200}]}

dIPFQDNDownload = {'blr-': {'fqdn': 'r2d2.nxtgen.com'},
           'amd-': {'fqdn': '61.0.172.106'},
           'fbd-': {'fqdn': '117.255.216.170'},
           'mum-': {'fqdn': '103.230.37.88'}}

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def hypervisorMappingDetails():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select hypervisor_type, hypervisor_ip_address from hypervisor_details where lower(hypervisor_type) in('vmware vcenter', 'onapp kvm') and active_yn='Y'"
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                if dRet['result'] == 'success':
                    d = {}
                    for i in dRet['data'][1:]:
                        if i[0] in d.keys():
                            d[i[0]] += [i[1]]
                        else:
                            d[i[0]] = [i[1]]
                    return json.dumps({'result': 'success', 'data': d})
                else:
                    return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTenantDetails(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                h_type = dPayload['h_type']
                # h_ip = dPayload['h_ip']
                sQuery = ""
                if h_type.lower().__contains__('vmware'):
                    sQuery = "select customer_id || '..' || customer_name customer from tbl_customer where active_yn='Y' and technology_loc='vmware'"
                elif h_type.lower().__contains__('kvm'):
                    sQuery = "select customer_id || '..' || customer_name customer from tbl_customer where active_yn='Y' and technology_loc='kvm'"
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                if dRet['result'] == 'success':
                    return json.dumps(dRet)
                else:
                    return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def hypervisorVMList(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                h_type = dPayload['h_type']
                tenant = dPayload['tenant']
                sQuery = ""
                if h_type.lower() == "vmware vcenter":
                    sQuery = "select vm_name || '..' || vm_ip vm_name from tbl_vms where techno='vmware' and device_type='esxivm' and lower(customer_id)=lower('{0}')".format(tenant)
                elif h_type.lower() == 'onapp kvm':
                    sQuery = "select vm_name from tbl_vms where techno='kvm' and device_type='kvmguest' and lower(customer_id)=lower('{0}')".format(tenant)
                dRet = pcon.returnSelectQueryResultAsList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def hypervisorVMList1(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                h_type = dPayload['h_type']
                h_ip = dPayload['h_ip']
                sQuery = ""
                if h_type.lower() == "vmware vcenter":
                    sQuery = """select
                        object_name vm_name
                    from
                        vcenter_object_inventory
                    where
                        fk_hypervisor_id = (select pk_hypervisor_id from hypervisor_details where hypervisor_ip_address='{0}' and active_yn='Y' limit 1) and
                        object_type='esxivm' and
                        active_yn='Y'""".format(h_ip)
                elif h_type.lower() == 'onapp kvm':
                    sQuery = "select v_label || '..' ||v_identifier vm_name from onapp_object_inventory  where active_yn='Y'"
                dRet = pcon.returnSelectQueryResultAsList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def createAutoScale(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
             #    dPayload = {"name": "as-1",
			 # "h_type": "vmware_vcenter",
			 # "h_ip": "192.168.1.1",
             # "min_poweron": 2,
			 # "vms":["as-1", "as-2"],
			 # "poweron": {"unit": "mem", "unit condition": ">", "unit value":80},
			 # "poweroff": {"unit": "cpu", "unit condition": "<", "unit value":50}}
                chkQuery = "select * from ai_autoscale where lower(as_name) =lower('{0}') and active_yn='Y'".format(dPayload['name'])
                dchkRet = pcon.returnSelectQueryResult(chkQuery)
                if dchkRet["result"] == "failure":
                    iASQuery = "insert into ai_autoscale(as_name, h_type, h_ip, min_power_on,active_yn, realservice) values('{0}', '{1}', '{2}', {3}, 'Y', '{4}') RETURNING pk_as_id".format(
                        dPayload['name'], dPayload['h_type'], dPayload['tenant'], dPayload['min_poweron'], dPayload['realservicegroup']
                    )
                    iASRet = pcon.returnSelectQueryResultWithCommit(iASQuery)
                    if iASRet["result"] == "success":
                        iPKID = iASRet["data"][0]["pk_as_id"]
                        iASVMQuery = "insert into ai_autoscale_vm_mapping(fk_as_id, vm_name, vm_ip, active_yn) values"
                        iASVMQuery = iASVMQuery + (",".join([str((iPKID, i.split('..')[0], i.split('..')[1],'Y')) for i in dPayload["vms"]]))
                        iPON = "insert into ai_autoscale_condition(fk_as_id, action, unit, condition, unit_value, active_yn) values({0}, '{1}', '{2}', '{3}', {4}, 'Y')".format(
                            iPKID, 'poweron', dPayload['poweron']['unit'], dPayload['poweron']['unit condition'], dPayload['poweron']['unit value']
                        )
                        iPOFF = "insert into ai_autoscale_condition(fk_as_id, action, unit, condition, unit_value, active_yn) values({0}, '{1}', '{2}', '{3}', {4}, 'Y')".format(
                            iPKID, 'poweroff', dPayload['poweroff']['unit'], dPayload['poweroff']['unit condition'],
                            dPayload['poweroff']['unit value']
                        )
                        print(iASVMQuery)
                        print(iPON)
                        print(iPOFF)
                        iRetASVM = pcon.returnInsertResult(iASVMQuery)
                        iRetON = pcon.returnInsertResult(iPON)
                        iRetOFF = pcon.returnInsertResult(iPOFF)
                        if iRetASVM['result'] == 'success' and iRetON['result'] == 'success' and iRetOFF['result'] == 'success':
                            return json.dumps({'result': 'success', 'data': 'Successfully registered Auto Scale Service'})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'Failed to register new Auto Scale service'})
                    else:
                        return json.dumps({'result': 'failure', 'data': 'Failed to add new Auto Scale..'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Auto Scale already exists. Choose different name.'})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAutoScaleList():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select pk_as_id id, as_name from ai_autoscale where active_yn='Y'"
                ret = pcon.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(ret)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAutoScaleDetails(id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                d = {}
                sQuery = "select as_name, h_type, h_ip, min_power_on, realservice from ai_autoscale where pk_as_id={0}".format(id)
                sQuery1 = "select vm_name || '..' || vm_ip vm_name from ai_autoscale_vm_mapping where fk_as_id={0} and active_yn='Y'".format(id)
                sQuery2 = "select action,unit,condition,unit_value from ai_autoscale_condition where fk_as_id={0} and active_yn='Y'".format(id)
                ret = pcon.returnSelectQueryResult(sQuery)
                d["name"] = ret["data"][0]["as_name"]
                d["h_type"] = ret["data"][0]["h_type"]
                d["h_ip"] = ret["data"][0]["h_ip"]
                d["min_poweron"] = ret["data"][0]["min_power_on"]
                d["realservicegroup"] = ret["data"][0]["realservice"]
                ret1 = pcon.returnSelectQueryResultAsList(sQuery1)
                d["vms"] = ret1["data"]["vm_name"]
                ret2 = pcon.returnSelectQueryResult(sQuery2)
                for i in ret2["data"]:
                    d[i["action"]] = {"unit": i["unit"], "unit condition": i["condition"], "unit value": float(i["unit_value"])}
                return json.dumps({'result': 'success', 'data': d})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateAutoScale(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
             #    dPayload = {"name": "as-1",
			 # "h_type": "vmware_vcenter",
			 # "h_ip": "192.168.1.1",
             # "min_poweron": 2,
			 # "vms":["as-1", "as-2"],
			 # "poweron": {"unit": "mem", "unit condition": ">", "unit value":80},
			 # "poweroff": {"unit": "cpu", "unit condition": "<", "unit value":50}}
                chkQuery = "select * from ai_autoscale where lower(as_name) =lower('{0}') and active_yn='Y'".format(dPayload['name'])
                dchkRet = pcon.returnSelectQueryResult(chkQuery)
                if dchkRet["result"] == "success":
                    uASQuery = "update ai_autoscale set h_type='{0}', h_ip='{1}', min_power_on={2}, realservice='{4}' where as_name='{3}' and active_yn='Y' RETURNING pk_as_id".format(
                        dPayload['h_type'], dPayload['tenant'], dPayload['min_poweron'], dPayload['name'], dPayload['realservicegroup']
                    )
                    uASRet = pcon.returnSelectQueryResultWithCommit(uASQuery)

                    if uASRet["result"] == "success":
                        iPKID = uASRet["data"][0]["pk_as_id"]
                        dASVMQuery = "delete from ai_autoscale_vm_mapping where fk_as_id={0}".format(iPKID)
                        dASPQuery = "delete from ai_autoscale_condition where fk_as_id={0}".format(iPKID)

                        dASVMRet = pcon.returnInsertResult(dASVMQuery)
                        dASPRet = pcon.returnInsertResult(dASPQuery)

                        iASVMQuery = "insert into ai_autoscale_vm_mapping(fk_as_id, vm_name, vm_ip, active_yn) values"
                        iASVMQuery = iASVMQuery + (",".join([str((iPKID, i.split("..")[0], i.split("..")[1],'Y')) for i in dPayload["vms"]]))
                        iPON = "insert into ai_autoscale_condition(fk_as_id, action, unit, condition, unit_value, active_yn) values({0}, '{1}', '{2}', '{3}', {4}, 'Y')".format(
                            iPKID, 'poweron', dPayload['poweron']['unit'], dPayload['poweron']['unit condition'], dPayload['poweron']['unit value']
                        )
                        iPOFF = "insert into ai_autoscale_condition(fk_as_id, action, unit, condition, unit_value, active_yn) values({0}, '{1}', '{2}', '{3}', {4}, 'Y')".format(
                            iPKID, 'poweroff', dPayload['poweroff']['unit'], dPayload['poweroff']['unit condition'],
                            dPayload['poweroff']['unit value']
                        )
                        print(iASVMQuery)
                        print(iPON)
                        print(iPOFF)
                        iRetASVM = pcon.returnInsertResult(iASVMQuery)
                        iRetON = pcon.returnInsertResult(iPON)
                        iRetOFF = pcon.returnInsertResult(iPOFF)
                        if iRetASVM['result'] == 'success' and iRetON['result'] == 'success' and iRetOFF['result'] == 'success':
                            return json.dumps({'result': 'success', 'data': 'Successfully updated Auto Scale Service'})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'Failed to update Auto Scale service'})
                    else:
                        return json.dumps({'result': 'failure', 'data': 'Failed to update Auto Scale..'})
                else:
                    return json.dumps({'result': 'failure', 'data': "Auto Scale doesn't exists to edit."})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteAutoScale(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                as_name = dPayload["name"]
                chkQuery = "select * from ai_autoscale where lower(as_name) =lower('{0}') and active_yn='Y'".format(as_name)
                dchkRet = pcon.returnSelectQueryResult(chkQuery)
                if dchkRet["result"] == "success":
                    dQuery = "update ai_autoscale set active_yn='N' where lower(as_name) =lower('{0}')".format(as_name)
                    dRet = pcon.returnInsertResult(dQuery)
                    if dRet["result"] == "success":
                        return json.dumps({'result': 'success', 'data': '{0} removed successfully'.format(as_name)})
                    else:
                        return json.dumps({'result': 'failure', 'data': "Delete Operation Failed"})
                else:
                    return json.dumps({'result': 'failure', 'data': "{0} doesn't exists."})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

# Analytics functionalities

def analytics1(autoscaleName):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select vm_name, to_char(logged_dt, 'DD-MM-YY HH24:MI') datetime, ip_address, no_hours, cpu_percentage, mins_cpu_percentage_cont_80 cont from autoscale_analytics where as_name='{0}' order by datetime desc".format(
                    autoscaleName
                )
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    dFinal = {}
                    data = dRet["data"][1:]
                    for i in data:
                        if i[0] + "({0})".format(i[2]) in dFinal.keys():
                            dFinal[i[0] + "({0})".format(i[2])] += [[i[1], ("" if i[4] == None or i[4] == "" else float(i[4])) ]]
                        else:
                            dFinal[i[0] + "({0})".format(i[2])] = [[i[1], ("" if i[4] == None or i[4] == "" else float(i[4])) ]]
                    return json.dumps({'result': 'success', 'data': dFinal})
                else:
                    return json.dumps({"result": "failure", "data": "Unable to generate Analytics report 1"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def analytics2(autoscaleName):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select to_char(logged_dt, 'DD-MM-YY HH24:MI') datetime, vm_count, vm_base_count, vm_max_ceiling_count from autoscale_analytics2 where as_name='{0}' and active_yn='Y'".format(
                    autoscaleName
                )
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def analyticsXLS(autoscaleName):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sMetaQuery = "select aas.as_name, asvm.vm_name, asvm.vm_ip from ai_autoscale aas inner join ai_autoscale_vm_mapping asvm on(aas.pk_as_id=asvm.fk_as_id) where aas.active_yn ='Y' and lower(aas.as_name)=lower('{0}')".format(
                    autoscaleName
                )
                sQuery = "select to_char(logged_dt, 'DD-MM-YY HH24:MI') datetime, vm_name, ip_address, no_hours, coalesce(cpu_percentage, 0) cpu_percentage, coalesce(mins_cpu_percentage_cont_80, 0) cont from autoscale_analytics where as_name='{0}' order by datetime desc".format(
                    autoscaleName
                )
                dMeta = pcon.returnSelectQueryResultAs2DList(sMetaQuery)
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                dates = []
                d = {}
                dFinal = []
                if dMeta["result"] == "success" and dRet["result"] == "success":
                    for i in dRet["data"][1:]:
                        if i[0] in d.keys():
                            if i[1] in d[i[0]].keys():
                                pass
                            else:
                                d[i[0]].update({i[1]: {'cpu': i[4], 'cpu_cont': i[5]}})
                        else:
                            d[i[0]] = {i[1]: {'cpu': i[4], 'cpu_cont': i[5]}}
                            dates.append(i[0])
                    print(dates)
                    print(d)
                    for i in dMeta["data"][1:]:
                        tmp = []
                        tmp.extend(i[1:])
                        tmp.append('12')
                        for j in dates:
                            tmp.append(float(d[j][i[1]]['cpu']))
                            tmp.append(float(d[j][i[1]]['cpu_cont']))
                        dFinal.append(tmp)
                    lHeader = ['VM Name', 'IP Address', 'No Of Hours']
                    [lHeader.extend(y) for y in [['CPU Usage(%)', 'Minutes more than 80% (cont.)'] for x in range(0, len(dates))]]
                    dFinal.insert(0, lHeader)
                    lDates = ['', '', '']
                    [lDates.extend(y) for y in [[x, ''] for x in dates]]
                    dFinal.insert(0, lDates)
                    ret = xl.export2XLSX(dFinal, "Report1_" + autoscaleName.replace(' ', '_'))
                    return json.dumps(ret)
                else:
                    return json.dumps({"result": "failure", "data": "Unable to generate Analytics XLS report 1"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def analytics2XLS(autoscaleName):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select to_char(logged_dt, 'DD-MM-YY HH24:MI') datetime, vm_count, vm_base_count, vm_max_ceiling_count from autoscale_analytics2 where as_name='{0}' and active_yn='Y'".format(
                    autoscaleName
                )
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    ret = xl.export2XLSX(dRet["data"], "Report2_" + autoscaleName.replace(' ', '_'))
                    return json.dumps(ret)
                else:
                    return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def autoscaleAuditReport():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
	pk_audit_id "Audit ID",
	audit_logged_date "Audit Registered Date Time",
	servicename "Service Type",
	startdt "Event Start Date Time",
	enddt "Event End Date Time",
	autoscalinggroupname "Auto Scale Name",
	realservicegroupname "LB - Real Service Group Name",
	vms "Virtual Machines",
	condition "Conditions",
	usage "Current Usage",
	threshold "Threshold",
	poffdecisionflag "Power ON/OFF Decision Made(Yes/No)",
	rsresource "Real Service Group Resource",
	rsflag "Real Service Group Resource Available(Yes/No)",
	poffresource "Virtual Machines for ON/OFF",
	poffflag "Virtual Machine Power ON/OFF Decision Made(Yes/No)",
	oustandingwaitingtime "Waiting Time - Current Connection to Become 0",
	remarks "Comment",
	error "Error" 
from 
	autoscale_audit 
order by pk_audit_id desc
"""
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    ret = xl.export2XLSX(dRet["data"], "AutoScaleAuditReport_")
                    return json.dumps(ret)
                else:
                    return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing




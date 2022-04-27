from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim, vmodl
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import services.utils.ConnPostgreSQL as pcon
import services.utils.mailservice as mail
from elasticsearch import Elasticsearch
from datetime import datetime as dt
from datetime import timedelta as td
import time
import pytz
import pexpect as r
import requests
import json
import services.utils.ED_AES256 as aes
from decimal import Decimal

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
           'fbd-': [{'host': '10.195.45.119', 'port': 9200}, {'host': '10.195.45.120', 'port': 9200}, {'host': '10.195.45.121', 'port': 9200}]}

dIPFQDNDownload = {'blr-': {'fqdn': 'r2d2.nxtgen.com'},
           'amd-': {'fqdn': '61.0.172.106'},
           'fbd-': {'fqdn': '117.255.216.170'}}


def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def makeZero(n):
    try:
        n = float(n)
    except Exception as e:
        pass
    if type(n) == type(1) or type(n) == type(1.0):
        if n < 0:
            return 0
        else:
            return n
    else:
        return n

def esExec(_pindex, _pbody, _es_tz, _user_tz, _bucket, _units, dtype = 'null'):
    try:
        es = Elasticsearch(dIPFQDN[location])
        result = es.search(index=_pindex, scroll='2m', body=_pbody, size=1000)
        FinalData, ft = [], True
        items = _pbody['_source'][1:]
        sid = result['_scroll_id']
        scroll_size = len(result['hits']['hits'])
        if scroll_size <= 0:
            return {"result": "failure", "data": "no data"}
        while scroll_size > 0:
            try:
                data = es.scroll(scroll_id=sid, scroll='{0}m'.format(_bucket))
                for i in result['aggregations']['Date']['buckets']:
                    _date = _es_tz.localize(dt.strptime(i['key_as_string'], '%Y-%m-%dT%H:%M:%S.%fZ')).astimezone(
                        _user_tz).strftime('%Y-%m-%d %H:%M')
                    if dtype == "firewall":
                        tmpu = []
                        tmpu = [makeZero('%.2f' % (i[k]['value'] if not i[k]['value'] == None else 0)) for k in items]
                        tmpu[0] = tmpu[1] + tmpu[2]
                        tmpu[3] = tmpu[4] + tmpu[5]
                        FinalData.append([_date] + tmpu)
                    else:
                        FinalData.append(
                            [_date] + [makeZero('%.2f' % (i[k]['value'] if not i[k]['value'] == None else 0)) for k in
                                       items])
            except Exception as e:
                pass
            sid = data['_scroll_id']
            scroll_size = len(data['hits']['hits'])
            break

        FinalData.insert(0, ['DateTime'] + items)
        return {'result': 'success', 'data': {'plots': FinalData}}

    except Exception as e:
        print(str(e))
        return {'result': 'failure', 'data': []}

def esExecWithAgg(_pindex, _pbody, _es_tz, _user_tz, _bucket):
    try:
        es = Elasticsearch(dIPFQDN[location])
        result = es.search(index=_pindex, scroll='2m', body=_pbody, size=10000)
        FinalData, ft = [], True
        sid = result['_scroll_id']
        scroll_size = len(result['hits']['hits'])
        if scroll_size <= 0:
            return {"result": "failure", "data": "no data"}
        while scroll_size > 0:
            data = es.scroll(scroll_id=sid, scroll='{0}m'.format(_bucket))
            for i in result['hits']['hits']:
                FinalData.append(i['_source'])
            sid = data['_scroll_id']
            scroll_size = len(data['hits']['hits'])
        return {'result': 'success', 'data': FinalData}
    except Exception as e:
        print(str(e))
        return {'result': 'failure', 'data': []}

# Get Current Utilization
def perfDataLatest(lVMs, sUnit, sKaalam, sBucket):
    try:
        print("Unit level filtering is still under progress. As of now, only CPU")
        _index = "ai-vm-perf-metrics"
        _bucket = sBucket
        user_tz = pytz.timezone('Asia/Kolkata')
        es_tz = pytz.timezone('GMT')
        user_s, user_e = user_tz.localize(
            dt.strptime((dt.now() - td(minutes=5)).strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')), user_tz.localize(
            dt.strptime(dt.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M'))  # Declare I/P to particular timezone
        if sKaalam == "morning":
            user_s = user_tz.localize(dt.strptime(dt.now().strftime('%Y-%m-%d 08:00'), '%Y-%m-%d %H:%M') - td(hours=12))
            user_e = user_tz.localize(dt.strptime(dt.now().strftime('%Y-%m-%d 08:00'), '%Y-%m-%d %H:%M'))
        elif sKaalam == "evening":
            user_s = user_tz.localize(dt.strptime(dt.now().strftime('%Y-%m-%d 20:00'), '%Y-%m-%d %H:%M') - td(hours=12))
            user_e = user_tz.localize(dt.strptime(dt.now().strftime('%Y-%m-%d 20:00'), '%Y-%m-%d %H:%M'))
        gmt_s, gmt_e = user_s.astimezone(es_tz), user_e.astimezone(es_tz)
        start_datetime = gmt_s.strftime('%Y-%m-%dT%H:%MZ')
        end_datetime = gmt_e.strftime('%Y-%m-%dT%H:%MZ')

        mapper = {'ESXi VM': {'CPU': {'select': ['CPUUsage'], 'meta': ['VCPU'],
                                      'units': '%',
                                      'plotter': ['CPUUsage']}}
        }

        dTmp = {}
        for eachVM in lVMs:
            try:
                _body = {'size': 1,
                         '_source': [],
                         'query': {'bool': {'filter': []}},
                         'aggs': {
                             'Date': {'date_histogram': {'field': '@timestamp.GMT',
                                                         'fixed_interval': '{0}m'.format(_bucket)},
                                      'aggs': {}}}}
                _body['_source'] = ['@timestamp.GMT'] + mapper['ESXi VM']['CPU']['select']
                d, l = {}, []
                l.append({'bool': {'should': [{'match_phrase': {'Name': eachVM}}]}})
                d = {'bool': {'filter': l}}
                _body['query']['bool']['filter'].append(d)
                # _body['query']['bool']['filter'].append({'match_phrase_prefix': {'Name': _name}})
                # _body['query']['bool']['filter'].append(
                #     {'range': {'@timestamp.GMT': {'gte':  start_datetime, 'lte': end_datetime}}})
                _body['query']['bool']['filter'].append(
                    {'range': {'@timestamp.GMT': {'gte': start_datetime, 'lte': end_datetime}}})
                units = mapper['ESXi VM']['CPU']['units']
                plotters = mapper['ESXi VM']['CPU']['plotter']

                del _body['_source']
                del _body['aggs']
                _body['_source'] = ['@timestamp.GMT'] + mapper['ESXi VM']['CPU']['select']
                _body['aggs'] = {'Date': {'auto_date_histogram': {'field': '@timestamp.GMT',
                                                                  'buckets': 1},
                                          'aggs': {}}}
                dselect = {}
                for i in mapper['ESXi VM']['CPU']['select']:
                    dselect[i] = {'avg': {'field': i}}
                _body['aggs']['Date']['aggs'] = dselect

                _out = esExec(_index, _body, es_tz, user_tz, _bucket, units)
                print(_out)
                if _out['result'] == 'success':
                    _out['units'] = units
                    _out['plotters'] = plotters
                    dTmp[eachVM] = _out['data']['plots'][1][1]
                else:
                    dTmp[eachVM] = -1

            except Exception as e:
                print(str(e))
                continue

        return {'result': 'success', 'data': dTmp}

    except Exception as e:
        print(str(e))
        return {'result': 'failure', 'data': 'no data'}
        # return logAndRet("failure", "Exception: {0}".format(str(e)))

def perfDataLatestRawData(lVMs, sUnit, sKaalam, sBucket):
    try:
        print("Unit level filtering is still under progress. As of now, only CPU")
        _index = "ai-vm-perf-metrics"
        _bucket = sBucket
        user_tz = pytz.timezone('Asia/Kolkata')
        es_tz = pytz.timezone('GMT')
        user_s, user_e = user_tz.localize(
            dt.strptime((dt.now() - td(minutes=5)).strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')), user_tz.localize(
            dt.strptime(dt.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M'))  # Declare I/P to particular timezone
        if sKaalam == "morning":
            user_s = user_tz.localize(dt.strptime(dt.now().strftime('%Y-%m-%d 08:00'), '%Y-%m-%d %H:%M') - td(hours=12))
            user_e = user_tz.localize(dt.strptime(dt.now().strftime('%Y-%m-%d 08:00'), '%Y-%m-%d %H:%M'))
        elif sKaalam == "evening":
            user_s = user_tz.localize(dt.strptime(dt.now().strftime('%Y-%m-%d 20:00'), '%Y-%m-%d %H:%M') - td(hours=12))
            user_e = user_tz.localize(dt.strptime(dt.now().strftime('%Y-%m-%d 20:00'), '%Y-%m-%d %H:%M'))
        gmt_s, gmt_e = user_s.astimezone(es_tz), user_e.astimezone(es_tz)
        start_datetime = gmt_s.strftime('%Y-%m-%dT%H:%MZ')
        end_datetime = gmt_e.strftime('%Y-%m-%dT%H:%MZ')

        mapper = {'ESXi VM': {'CPU': {'select': ['CPUUsage'], 'meta': ['VCPU'],
                                      'units': '%',
                                      'plotter': ['CPUUsage']}}
        }

        dTmp = {}
        for eachVM in lVMs:
            try:
                _body = {'size': 1,
                         '_source': [],
                         'query': {'bool': {'filter': []}},
                         'aggs': {
                             'Date': {'date_histogram': {'field': '@timestamp.GMT',
                                                         'fixed_interval': '{0}m'.format(_bucket)},
                                      'aggs': {}}}}
                _body['_source'] = ['@timestamp.GMT'] + mapper['ESXi VM']['CPU']['select']
                d, l = {}, []
                l.append({'bool': {'should': [{'match_phrase': {'Name': eachVM}}]}})
                d = {'bool': {'filter': l}}
                _body['query']['bool']['filter'].append(d)
                # _body['query']['bool']['filter'].append({'match_phrase_prefix': {'Name': _name}})
                # _body['query']['bool']['filter'].append(
                #     {'range': {'@timestamp.GMT': {'gte':  start_datetime, 'lte': end_datetime}}})
                _body['query']['bool']['filter'].append(
                    {'range': {'@timestamp.GMT': {'gte': start_datetime, 'lte': end_datetime}}})
                units = mapper['ESXi VM']['CPU']['units']
                plotters = mapper['ESXi VM']['CPU']['plotter']

                del _body['_source']
                del _body['aggs']
                _body['_source'] = ['@timestamp.GMT'] + mapper['ESXi VM']['CPU']['select']
                _body['aggs'] = {'Date': {'date_histogram': {'field': '@timestamp.GMT',
                                                                  'fixed_interval': '1m'},
                                          'aggs': {}}}
                dselect = {}
                for i in mapper['ESXi VM']['CPU']['select']:
                    dselect[i] = {'avg': {'field': i}}
                _body['aggs']['Date']['aggs'] = dselect

                _out = esExec(_index, _body, es_tz, user_tz, _bucket, units)
                print(_out)
                if _out['result'] == 'success':
                    _out['units'] = units
                    _out['plotters'] = plotters
                    dTmp[eachVM] = _out['data']['plots']
                else:
                    dTmp[eachVM] = -1

            except Exception as e:
                print(str(e))
                continue

        return {'result': 'success', 'data': dTmp}

    except Exception as e:
        print(str(e))
        return {'result': 'failure', 'data': 'no data'}

# Bots to Start and Stop Interface
def putil(pobj, pexp, psend):
    try:
        i = pobj.expect(pexp)
        if i >= 0:
            pobj.sendline(psend)
            return 1
        else:
            return 0
    except Exception as e:
        return 0

def raise_exc(clazz, msg=""):
    raise clazz(msg)

if __name__ == "__main__":
    try:
        sQueryServiceDT = "select as_name, h_type, h_ip, min_power_on from ai_autoscale where pk_as_id in(select distinct fk_as_id from ai_autoscale_vm_mapping) and active_yn='Y'"
        serviceRet = pcon.returnSelectQueryResultAs2DList(sQueryServiceDT)
        if serviceRet["result"] == "success":
            lASList = dict([(i[0], i[1:]) for i in serviceRet["data"][1:]])
            for eachAutoScaler in lASList:
                print("Collect Stats for Auto Scale Group:{0}".format(eachAutoScaler))
                sQueryVM = "select vm_name, vm_ip from ai_autoscale_vm_mapping m inner join ai_autoscale s  on(s.pk_as_id=m.fk_as_id) where lower(s.as_name) = lower('{0}')".format(
                    eachAutoScaler
                )
                sVMdt = pcon.returnSelectQueryResultConvert2Col2Dict(sQueryVM)
                if sVMdt["result"] == "success":
                    _a2Ceiling = len(list(sVMdt["data"].keys()))
                    _a2Base = lASList[eachAutoScaler][2]
                    print("VMs those are part of Auto Scale Group:{0} are {1}".format(eachAutoScaler, ','.join(list(sVMdt["data"].keys()))))
                    out, kaalam = "", ""
                    kaalam = "evening" if int(dt.now().strftime('%H')) > 20 else "morning"
                    out = perfDataLatest(list(sVMdt["data"].keys()), 'CPU', kaalam, str(1))
                    if out["result"] == "success":
                        _a2Count = len([0 for i in out["data"] if out["data"][i] != -1])
                        _a2DT = dt.now().strftime('%Y-%m-%d') + " 08:00" if kaalam == "morning" else dt.now().strftime('%Y-%m-%d') + " 20:00"
                        iA2Query = "insert into autoscale_analytics2(as_name, vm_count, vm_base_count, vm_max_ceiling_count, logged_dt, active_yn) values('{0}', {1}, {2}, {3}, to_timestamp('{4}', 'YYYY-MM-DD HH24:MI'), 'Y')".format(
                            eachAutoScaler, _a2Count, _a2Base, _a2Ceiling, _a2DT
                        )
                        print(iA2Query)
                        dA2Ret = pcon.returnInsertResult(iA2Query)
                        if dA2Ret["result"] == "success":
                            print("Analytics 2 report generated")
                        else:
                            print("Analytics 2 report generation failed")
                        for i in out["data"]:
                            if out["data"][i] != -1:
                                outRaw = perfDataLatestRawData([i], 'CPU', kaalam, str(12*60))
                                if outRaw["result"] == "success":
                                    ll = outRaw["data"][i][1:]
                                    cpus = [k[1] for k in ll]
                                    tmpL, reset = [], 0
                                    for cpu in cpus:
                                        if cpu > 0.32:
                                            reset += 1
                                        else:
                                            tmpL.append(reset)
                                            reset = 0
                                    continuous = max(tmpL)
                                    iQuery = "insert into autoscale_analytics(as_name, vm_name, ip_address, no_hours, cpu_percentage, mins_cpu_percentage_cont_80, logged_dt, active_yn) values('{0}', '{1}', '{2}', 12, {3}, {4}, to_timestamp('{5}', 'YYYY-MM-DD HH24:MI'), 'Y')".format(
                                        eachAutoScaler, i, sVMdt["data"][i], out["data"][i], continuous, _a2DT
                                    )
                                    print(iQuery)
                                    dA1Ret = pcon.returnInsertResult(iQuery)
                                    if dA1Ret["result"] == "success":
                                        print("Analytics 1 report generated")
                                    else:
                                        print("Analytics 1 report generation failed")
                            else:
                                iQuery = "insert into autoscale_analytics(as_name, vm_name, ip_address, no_hours, logged_dt, active_yn) values('{0}', '{1}', '{2}', 12, to_timestamp('{3}', 'YYYY-MM-DD HH24:MI'), 'Y')".format(
                                    eachAutoScaler, i, sVMdt["data"][i], _a2DT
                                )
                                print(iQuery)
                                dA1Ret = pcon.returnInsertResult(iQuery)
                                if dA1Ret["result"] == "success":
                                    print("Analytics 1 report generated")
                                else:
                                    print("Analytics 1 report generation failed")

                    else:
                        print("Unable to fetch Performance Data: Error: {0}".format(out["data"]))
                else:
                    print("There are no VMs configured for {0} Auto-Scale Group to collect stats. You can add from Cloud Service --> Auto-Scale.".format(
                            eachAutoScaler))
        else:
            print("No Auto-Scale Group Configured to execute the service.")
    except Exception as e:
        pass





# Main that triggers things in Procedural Way
# if __name__ == "__main__":
#     # sQueryServiceDT = "select as_name from ai_autoscale where pk_as_id in(select distinct fk_as_id from ai_as_vm_mapping)"
#     # sQueryServiceDT = "select as_name, unit, condition, unit_value from ai_autoscale where pk_as_id in(select distinct fk_as_id from ai_as_vm_mapping) and active_yn='Y'"
#     sQueryServiceDT = "select as_name, h_type, h_ip, min_power_on from ai_autoscale where pk_as_id in(select distinct fk_as_id from ai_autoscale_vm_mapping) and active_yn='Y'"
#     # serviceRet = pcon.returnSelectQueryResultAsList(sQueryServiceDT)
#     serviceRet = pcon.returnSelectQueryResultAs2DList(sQueryServiceDT)
#     if serviceRet["result"] == "success":
#         lASList = dict([(i[0], i[1:]) for i in serviceRet["data"][1:]])
#         for eachAutoScaler in lASList: #serviceRet["data"]["as_name"]:
#             print("=" * 50)
#             print(" Auto Scale Group:{0}".format(eachAutoScaler))
#             try:
#                 sQueryVM = "select vm_name from ai_autoscale_vm_mapping m inner join ai_autoscale s  on(s.pk_as_id=m.fk_as_id) where lower(s.as_name) = lower('{0}')".format(
#                     eachAutoScaler
#                 )
#                 sVMdt = pcon.returnSelectQueryResultAsList(sQueryVM)
#                 if sVMdt["result"] == "success":
#                     print(" VMs those are part of Auto Scale Group:{0} are {1}".format(eachAutoScaler, ','.join(sVMdt["data"]["vm_name"])))
#                     sPowerQuery = """select
#                     	action, unit, condition, unit_value
#                     from
#                     	ai_autoscale_condition c
#                     where
#                     	c.active_yn='Y' and c.fk_as_id = (select pk_as_id from ai_autoscale where lower(as_name)=lower('{0}'))""".format(eachAutoScaler)
#                     sPRet = pcon.returnSelectQueryResult(sPowerQuery)
#                     if sPRet['result'] == 'success':
#                         dONOFF = {}
#                         for i in sPRet["data"]:
#                             dONOFF[i['action']] = {"unit": i["unit"], "unit condition": i["condition"], "unit value": float(i["unit_value"])}
#
#                         print(" Configuration : {0}".format(dONOFF))
#                         if lASList[eachAutoScaler][0].lower() == "vmware vcenter":
#
#                             # Fetch the Hypervisor Password from the Database
#                             credQuery = "select cred_type, username, password from ai_device_credentials where cred_id=(select hypervisor_cred from hypervisor_details where hypervisor_ip_address='{0}' and active_yn='Y' limit 1)".format(
#                                 lASList[eachAutoScaler][1]
#                             )
#                             credQuery = "select cred_type, username, password from ai_device_credentials where cred_id=(select hypervisor_cred from hypervisor_details where hypervisor_ip_address='{0}' and active_yn='Y' limit 1)".format(
#                                 "172.29.64.100"
#                             )
#                             credRet = pcon.returnSelectQueryResult(credQuery)
#                             if credRet['result'] == 'success':
#
#                                 ip = lASList[eachAutoScaler][1]
#                                 ip = "172.29.64.100"
#                                 username = credRet["data"][0]["username"]
#                                 password = aes.decrypt(credRet["data"][0]["password"].encode(), '@ut0!ntell!'.encode()).decode('utf-8')
#                                 pState = getVMPowerState(ip, (username, password), sVMdt["data"]["vm_name"])
#
#                                 out = perfDataLatest(pState['on'], dONOFF['poweron']['unit'])
#                                 if out["result"] == "success":
#
#                                     print(' Utilization for all Powered ON VMs: {0}'.format(out))
#                                     lValues = [i for i in out['data'].values() if not (i < 0)]
#                                     lOFFAvergae = sum(lValues) / len(lValues)
#                                     lAvergae = max(lValues) #sum(lValues) / len(lValues)
#
#                                     # Power ON
#                                     print("-" * 50)
#                                     print("Auto Scale - Power On service...")
#                                     if len(pState['off']) > 0:
#                                         c, v = dONOFF['poweron']['unit condition'], dONOFF['poweron']['unit value']
#                                         print(" Peak Utilization is: {0}".format(lAvergae))
#                                         print(" Threshold is: {0}".format(v))
#                                         if lAvergae > v:
#                                             pState = getVMPowerState(ip, (username, password), sVMdt["data"]["vm_name"])
#                                             print(" Found Powered Off resource: {0}".format(pState['off']))
#                                             pStatus = putPowerON(ip, (username, password), pState['off'])
#                                             if pStatus['result'] == 'success':
#                                                 print(" VM: {0} Powered ON Successfully".format(pStatus['vm']))
#                                                 print(" Enable Real Service in Array LB")
#                                                 enableRealServiceInArrayLB(pStatus['vm'])
#                                                 print(" SUCCESS:Send Email Notification for Auto Scale Power ON")
#                                                 sendEmailNewlyAdded(eachAutoScaler, pStatus['vm'], 'poweron', lAvergae,
#                                                                     ['dinesh@autointelli.com'])
#                                             elif pStatus['result'] == 'no action':
#                                                 print(" NO ACTION:Send Email Notification for Auto Scale Power ON")
#                                                 sendEmailNewlyAdded(eachAutoScaler, pStatus['vm'], 'no action',
#                                                                     lAvergae,
#                                                                     ['dinesh@autointelli.com'])
#                                             elif pStatus['result'] == 'failure':
#                                                 print(" FAILURE:Send Email Notification for Auto Scale Power ON")
#                                                 sendEmailNewlyAdded(eachAutoScaler, '', 'error', lAvergae,
#                                                                     ['dinesh@autointelli.com'], pState['data'])
#                                         else:
#                                             print(" Below threshold. No action for Auto-Scale power-on service.")
#                                     else:
#                                         print(" No Resource left to Auto-Scale ")
#                                     print("-" * 50)
#
#                                 else:
#                                     print(" Performance Data missing for {0}".format(pState['on']))
#
#                             else:
#                                 # print(" Login Pre-req is missing for the hypervisor: {0}".format(lASList[eachAutoScaler][1]))
#                                 print(" Login Pre-req is missing for the hypervisor: {0}".format("172.29.64.100"))
#
#                         elif lASList[eachAutoScaler][0].lower() == "onapp kvm":
#                             print(" VM Power ON/OFF functionality for KVM is Under Construction...")
#
#                     else:
#                         print(" Power ON & OFF features are missing for Auto Scale Group : {0}".format(eachAutoScaler))
#                 else:
#                     print(" There are no VMs configured for {0} Auto-Scale Group. You can add from Cloud Service --> Auto-Scale.".format(eachAutoScaler))
#             except Exception as e:
#                 print(" An exception occured while fetching VM details for the auto-scale group: {0}".format(eachAutoScaler))
#             print("=" * 50)
#     else:
#         print("No Auto-Scale Group Configured to execute the service.")
    # out = perfDataLatest()
    # if out['result'] == 'success':
    #     turnOFFAccounts = MatchAndSendNotif(out['data'])
    #     print(turnOFFAccounts)
    #     if turnOFFAccounts['result'] == 'success':
    #         print("Trun Off is under construction")
    #         turnOFF(turnOFFAccounts['data'])


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
import services.perfrpt.ArrayLBRS as lb

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

gLBIPService = {}
_gServiceName, _gStartDT, _gEndDT, _gAutoScalingGroupName, _gRealServiceGroupName, _gVMs, _gCondition, _gUsage, _gThreshold, _gPOFFDecisionFlag, _gRSResource, _gRSFlag, _gPOFFResource, _gPOFFFlag, _gOustandingWaitingTime, _gRemarks, _gError = \
    "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

def reset():
    _gServiceName, _gStartDT, _gEndDT, _gAutoScalingGroupName, _gRealServiceGroupName, _gVMs, _gCondition, _gUsage, _gThreshold, _gPOFFDecisionFlag, _gRSResource, _gRSFlag, _gPOFFResource, _gPOFFFlag, _gOustandingWaitingTime, _gRemarks, _gError = \
        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
def audit():
    try:
        sQuery = """insert into autoscale_audit(audit_logged_date, ServiceName, StartDT, EndDT, AutoScalingGroupName, RealServiceGroupName, VMs, Condition, 
        Usage, Threshold, POFFDecisionFlag, RSResource, RSFlag, POFFResource, POFFFlag, OustandingWaitingTime, Remarks, Error) 
        values(now(), '{0}', to_date('{1}', 'YYYY-MM-DD HH24:MI'), to_date('{2}', 'YYYY-MM-DD HH24:MI'), '{3}', '{4}', '{5}', '{6}', 
        '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}')""".format(
            _gServiceName, _gStartDT, _gEndDT, _gAutoScalingGroupName, _gRealServiceGroupName, _gVMs, _gCondition,
            _gUsage, _gThreshold, _gPOFFDecisionFlag, _gRSResource, _gRSFlag, _gPOFFResource, _gPOFFFlag, _gOustandingWaitingTime, _gRemarks, _gError
        )
        print("Audit Query: {0}".format(sQuery))
        dRet = pcon.returnInsertResult(sQuery)
        if dRet['result'] == 'success':
            print("Audit Push Success")
        else:
            print("Audit Push Failed: {0}".format(dRet['data']))
    except Exception as e:
        print("Audit Push Failed: {0}".format(str(e)))

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

# Notify
def sendEmail(pAcct, pQuota, pConsumedVolume, pPercent, pSeverity, pEmail, pRemark=""):
    sHTMLSubject = ""
    sAct = ""
    sHTML = "<table border=1>"
    if pSeverity == "warning":
        sHTMLSubject = "{1}: Warning! Current Utilization is :{0}".format(pPercent, pAcct)
        sAct = "ACTIVE"
    elif pSeverity == "critical":
        sHTMLSubject = "{1}: Critical! Current Utilization is :{0}".format(pPercent, pAcct)
        sAct = "ACTIVE"
    elif pSeverity == "unsubscribed":
        sHTMLSubject = "{0}: Suspended! Re-activate By Payments".format(pAcct)
        sAct = "INACTIVE"
    elif pSeverity == "error":
        sHTMLSubject = "{0}: Error! While Unsubscribing through BOT. Make it manual.".format(pAcct)
        sAct = "ACTIVE"
    sHTML += "<tr><td>Opted Quota</td><td>Consumed Volume</td><td>Exceeded Percent</td><td>Service Status</td></tr>"
    sHTML += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>".format(pQuota, pConsumedVolume, pPercent, sAct)
    sHTML += "</table>"
    if pSeverity == "error":
        sHTML += "<BR/><BR/><p>{0}</p>".format(pRemark)
    mail.sendmail(sSubject=sHTMLSubject, lTo=pEmail, lCC=pEmail, sBody=sHTML)

# Notify
def sendEmailNewlyAdded(sASName, sVM, sState, sConsumedPercent, pEmail, pRemark=""):
    sHTMLSubject = ""
    sAct = ""
    sHTML = "<table border=1>"
    sHTML += "<tr><td>Auto-Scale Group Name</td><td>Virtual Machine Name</td><td>Action</td><td>Reason</td></tr>"
    if sState == "poweron":
        sHTMLSubject = "Virtual Machine Powered On for AutoScale Group - {0}".format(sASName)
        sHTML += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>".format(sASName, sVM, 'Powered On', 'Consumed % is {0}'.format(sConsumedPercent))
    elif sState == "poweroff":
        sHTMLSubject = "Virtual Machine Powered Off for AutoScale Group - {0}".format(sASName)
        sHTML += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>".format(sASName, sVM, 'Powered Off', 'Consumed % is {0}'.format(sConsumedPercent))
    elif sState == "no action":
        sHTMLSubject = "Resource Full in AutoScale Group - {0}".format(sASName)
        sHTML += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>".format(sASName, sVM, 'No Action', 'Consumed % is {0}'.format(sConsumedPercent))
    elif sState == "error":
        sHTMLSubject = "Error in AutoScale Group - {0}".format(sASName)
        sHTML += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>".format(sASName, sVM, 'Error', 'Consumed % is {0}. Error {1}'.format(sConsumedPercent, pRemark))
    sHTML += "</table>"
    # if pSeverity == "error":
    #     sHTML += "<BR/><BR/><p>{0}</p>".format(pRemark)
    mail.sendmail(sSubject=sHTMLSubject, lTo=pEmail, lCC=pEmail, sBody=sHTML)

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

def getVMPowerState(vCenterIP, pAuth, lVMs):
    s = time.time()
    si = SmartConnectNoSSL(host=vCenterIP, user=pAuth[0], pwd=pAuth[1])
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    d = dict([(i.name, i.summary.runtime.powerState) for i in container.view])
    container.Destroy()
    Disconnect(si)
    print("Time Taken:{0}".format(time.time() - s))
    ps = {'on': [], 'off': [], 'sus': []}
    for vm in lVMs:
        if d[vm] == 'poweredOn':
            ps['on'] += [vm]
        elif d[vm] == 'poweredOff':
            ps['off'] += [vm]
        elif d[vm] == 'suspended':
            ps['sus'] += [vm]
    return ps
    #Session
    # sBaseURL = "https://{0}".format(vCenterIP)
    # sURL = "{0}/rest/com/vmware/cis/session".format(sBaseURL)
    # sHeader = {"Accept": "application/*+json;version=27.0"}
    # ret = requests.post(url=sURL, auth=pAuth, headers=sHeader, verify=False)
    # if ret.status_code != 200:
    #     raise Exception("Status Code: {0}, Return: {1}".format(ret.status_code, ret.content))
    #
    # authorization_key = ret.headers['x-vcloud-authorization']
    # sHeader['x-vcloud-authorization'] = authorization_key
    # return sHeader

def WaitForTasks(tasks, si):
   """
   Given the service instance si and tasks, it returns after all the
   tasks are complete
   """

   pc = si.content.propertyCollector

   taskList = [str(task) for task in tasks]

   # Create filter
   objSpecs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                                                            for task in tasks]
   propSpec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                         pathSet=[], all=True)
   filterSpec = vmodl.query.PropertyCollector.FilterSpec()
   filterSpec.objectSet = objSpecs
   filterSpec.propSet = [propSpec]
   filter = pc.CreateFilter(filterSpec, True)

   try:
      version, state = None, None

      # Loop looking for updates till the state moves to a completed state.
      while len(taskList):
         update = pc.WaitForUpdates(version)
         for filterSet in update.filterSet:
            for objSet in filterSet.objectSet:
               task = objSet.obj
               for change in objSet.changeSet:
                  if change.name == 'info':
                     state = change.val.state
                  elif change.name == 'info.state':
                     state = change.val
                  else:
                     continue

                  if not str(task) in taskList:
                     continue

                  if state == vim.TaskInfo.State.success:
                     # Remove task from taskList
                     taskList.remove(str(task))
                  elif state == vim.TaskInfo.State.error:
                     raise task.info.error
         # Move to next version
         version = update.version
   finally:
      if filter:
         filter.Destroy()

def putPowerON(vCenterIP, pAuth, lPowerOffList):
    try:
        s = time.time()
        sFinal = {}
        si = SmartConnectNoSSL(host=vCenterIP, user=pAuth[0], pwd=pAuth[1])
        content = si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        vmList = container.view
        #d = dict([(i.name, i.summary.runtime.powerState) for i in container.view])
        container.Destroy()
        tasks, vmSelected4PON, remarks = [], "", ""
        for vm in vmList:
            if vm.name in lPowerOffList and vm.summary.runtime.powerState == 'poweredOff':
                vmSelected4PON = vm.name
                tasks.append(vm.PowerOn())
                break
        if len(tasks) > 0:
            WaitForTasks(tasks, si)
            remarks = "Virtual Machine:{0} has got powered on successfully".format(vmSelected4PON)
            sFinal = {'result': 'success', 'data': remarks, 'vm': vmSelected4PON}
        else:
            remarks = "The pool is full. No furthur VMs available to Power On"
            sFinal = {'result': 'no action', 'data': remarks, 'vm': ''}
        Disconnect(si)
        print(" Time Taken to Power ON:{0}".format(time.time() - s))
        return sFinal
    except Exception as e:
        return {'result': 'failure', 'data': 'Error has occured while powering on the VM: {0}'.format(str(e))}

# sQuery = "select vm_ip from tbl_vms where lower(vm_name)=lower('{0}')".format(sVM)
#         dRet = pcon.returnSelectQueryResult(sQuery)
#         if dRet['result'] == 'failure':
#             return ""

def getOutStanding(sRealServiceName):
    ret = lb.getStats(sRealServiceName)
    if ret['result'] == 'success':
        if int(ret['data']['outstanding_request']) == 0:
            return False
        else:
            return True
    else:
        print("Error in LB: {0}".format(ret['data']))
        True

def putPowerOFF(vCenterIP, pAuth, lPowerONList, lNameIP):
    try:
        global _gRSFlag, _gPOFFResource, _gPOFFFlag, _gOustandingWaitingTime
        s = time.time()
        sFinal = {}
        si = SmartConnectNoSSL(host=vCenterIP, user=pAuth[0], pwd=pAuth[1])
        content = si.RetrieveContent()
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        vmList = container.view
        #d = dict([(i.name, i.summary.runtime.powerState) for i in container.view])
        container.Destroy()
        tasks, vmSelected4PON, remarks, cnt = [], "", "", 0
        for vm in vmList:
            if vm.name in lPowerONList and vm.summary.runtime.powerState == 'poweredOn':
                vmSelected4PON = vm.name
                print(" Disable Real Service in Array LB")
                disableRealServiceInArrayLB(vmSelected4PON)
                _gRSFlag = "Yes"
                _gPOFFResource = vmSelected4PON + ":" + lNameIP[vmSelected4PON]
                cnt = 0
                while getOutStanding(gLBIPService[lNameIP[vmSelected4PON]]):
                    print("Waiting for the Outstanding request to become zero(0).")
                    time.sleep(30)
                    cnt += 1
                    if cnt == 6:
                        cnt = -1
                        break
                if cnt != -1:
                    tasks.append(vm.PowerOff())
                break
        if len(tasks) > 0:
            WaitForTasks(tasks, si)
            _gPOFFFlag = "Yes"
            _gOustandingWaitingTime = cnt * 30
            remarks = "Virtual Machine:{0} has got powered off successfully".format(vmSelected4PON)
            sFinal = {'result': 'success', 'data': remarks, 'vm': vmSelected4PON}

        elif cnt == -1:
            _gPOFFFlag = "No"
            _gOustandingWaitingTime = cnt * 30
            remarks = "LB's Real Service:{0} Outstanding Connection is not getting reduced to zero".format(gLBIPService[lNameIP[vmSelected4PON]])
            sFinal = {'result': 'no action', 'data': remarks, 'vm': ''}
        else:
            remarks = "The pool is full. No furthur VMs available to Power Off"
            sFinal = {'result': 'no action', 'data': remarks, 'vm': ''}
        Disconnect(si)
        print(" Time Taken to Power OFF:{0}".format(time.time() - s))
        return sFinal
    except Exception as e:
        return {'result': 'failure', 'data': 'Error has occured while powering off the VM: {0}'.format(str(e))}

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
def perfDataLatest(lVMs, sUnit):
    try:
        print("Unit level filtering is still under progress. As of now, only CPU")
        _index = "ai-vm-perf-metrics"
        _bucket = '1'
        user_tz = pytz.timezone('Asia/Kolkata')
        es_tz = pytz.timezone('GMT')
        user_s, user_e = user_tz.localize(
            dt.strptime((dt.now() - td(minutes=5)).strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')), user_tz.localize(
            dt.strptime(dt.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M'))  # Declare I/P to particular timezone
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

def turnOFF(pOFF):
    try:
        print(pOFF)
        for eachAcc in pOFF:
            user_id = ""
            sQuery = "select c_id from onapp_object_inventory where lower(c_login)=lower('{0}')".format(eachAcc)
            dRet = pcon.returnSelectQueryResult(sQuery)
            if dRet['result'] == 'success':
                user_id = dRet['data'][0]['c_id']
                try:
                    sURL = "https://blrngcs.nxtgen.com/users/{0}/suspend.json".format(user_id)
                    dHeader = {'Content-Type': 'application/json'}
                    dAuth = ('soc', 'AIP@ssw0rd@123$#%')
                    print(sURL, dHeader)
                    ret = requests.post(url=sURL, auth=dAuth, headers=dHeader, verify=False)
                    print(ret.status_code)
                    if ret.status_code == 200 or ret.status_code == 201:
                        rettxt = ret.text
                        out = json.loads(rettxt)
                        if out['user']['status'] == 'suspended':
                            print("Send Successful suspend account email")
                            sendEmail(eachAcc, pOFF[eachAcc]['Quota'], pOFF[eachAcc]['Consumed Volume'],
                                      pOFF[eachAcc]['Percent Utilized'], 'unsubscribed', pOFF[eachAcc]['email'])
                            sendEmail(eachAcc + '--' + out['user']['status'], pOFF[eachAcc]['Quota'], pOFF[eachAcc]['Consumed Volume'],
                                      pOFF[eachAcc]['Percent Utilized'], 'unsubscribed', ['dinesh@autointelli.com'])
                        else:
                            sendEmail(eachAcc, pOFF[eachAcc]['Quota'], pOFF[eachAcc]['Consumed Volume'],
                                      pOFF[eachAcc]['Percent Utilized'], 'error', ['dinesh@autointelli.com'],
                                      'Failed to Suspend\nError:{0}'.format(rettxt))
                    else:
                        print("Consolidate and send a final mail")
                        sendEmail(eachAcc, pOFF[eachAcc]['Quota'], pOFF[eachAcc]['Consumed Volume'],
                                  pOFF[eachAcc]['Percent Utilized'], 'error', ['dinesh@autointelli.com'],
                                  'Failed to Suspend\nError:{0}'.format(ret.text))
                except Exception as e:
                    print("Consolidate and send a final mail: {0}".format(str(e)))
                    sendEmail(eachAcc, pOFF[eachAcc]['Quota'], pOFF[eachAcc]['Consumed Volume'],
                              pOFF[eachAcc]['Percent Utilized'], 'error', ['dinesh@autointelli.com'], str(e))
            else:
                sendEmail(eachAcc, pOFF[eachAcc]['Quota'], pOFF[eachAcc]['Consumed Volume'],
                          pOFF[eachAcc]['Percent Utilized'], 'error', ['dinesh@autointelli.com'], 'The Account is missing in Inventory')

    except Exception as e:
        print("Trun Off or Suspend of account failed")
        sendEmail('OverAll', '', '', '', 'error', ['dinesh@autointelli.com'], 'OverAll Suspension function failed')

def turnOFF1(pOFF):
    # pOFF = {'socintelli': {'int': ['14.192.16.226', '51', 'Fullerton-WAN'],
    #                     'email': ['dinesh@autointelli.com'],
    #                     'Quota': 1500.0,
    #                     'Consumed Volume': 1540.1248807907104,
    #                     'Percent Utilized': 102.67499205271402}}
    for eachInt in pOFF:
        print("Turn Off interface of ACCT: {0}".format(eachInt))
        _device = pOFF[eachInt]['int'][0]
        _int = pOFF[eachInt]['int'][1]
        _intname = pOFF[eachInt]['int'][2]
        try:
            obj = r.spawn('ssh AI-Dinesh@{0} -p 40022'.format(_device))
            print('entered into device') if putil(obj, 'password:', 'bbE9as9bFTttqSb') == 1 else raise_exc(Exception, 'Device: {0} Error: Failed while feeding password'.format(_device))
            print('config vdom') if putil(obj, ['#'], 'config vdom') == 1 else raise_exc(Exception, 'Device:{0} Error: {1}'.format(_device, 'config vdom'))
            print('edit fullerton') if putil(obj, ['#'], 'edit Fullerton') == 1 else raise_exc(Exception,'Device:{0} Error: {1}'.format(_device, 'edit Fullerton'))
            print('config interface') if putil(obj, ['#'], 'config system interface') == 1 else raise_exc(Exception, 'Device:{0} Error: {1}'.format(_device, 'config system interface'))
            print('edit interface') if putil(obj, ['#'], 'edit {0}'.format(_intname)) == 1 else raise_exc(Exception, 'Device:{0} Error: {1}'.format(_device, 'edit {0}'.format(_int)))
            print('bring down the interface') if putil(obj, ['#'], 'set status down') == 1 else raise_exc(Exception, 'Device:{0} Error: {1}'.format(_device, 'set status down'))

            print('end') if putil(obj, ['#'], 'end') == 1 else raise_exc(Exception, 'Device:{0} Error: {1}'.format(_device, 'end'))
            print('end') if putil(obj, ['#'], 'end') == 1 else raise_exc(Exception, 'Device:{0} Error: {1}'.format(_device, 'end'))
            print('exit') if putil(obj, ['#'], 'end') == 1 else raise_exc(Exception, 'Device:{0} Error: {1}'.format(_device, 'exit'))

            # ind = putil(obj, 'password:', 'bbE9as9bFTttqSb')
            # ind = putil(obj, ['#'], 'config vdom')
            # ind = putil(obj, ['#'], 'edit Fullerton')
            # ind = putil(obj, ['#'], 'config system interface')
            # ind = putil(obj, ['#'], 'edit {0}'.format(_int))
            # ind = putil(obj, ['#'], 'set status down')
            sendEmail(eachInt, pOFF[eachInt]['Quota'], pOFF[eachInt]['Consumed Volume'], pOFF[eachInt]['Percent Utilized'], 'unsubscribed', pOFF[eachInt]['email'])
        except Exception as e:
            err = 'Exception Raised while Shutting Down the interface for the client: {0}\n'.format(eachInt) + \
                  'Error Received from the Bot is: {0}'.format(str(e))
            print(err)
            # Notify Administartor to manually make the interface down
            sendEmail(eachInt, pOFF[eachInt]['Quota'], pOFF[eachInt]['Consumed Volume'], pOFF[eachInt]['Percent Utilized'], 'error', ['dinesh@autointelli.com'], err)

def turnOn():
    pass

# Decision Maker for Start and Stop Interface
def MatchAndSendNotif(pOut):
    turnOFF = {}
    sQuery = "select acct_id, quota || '::' || unit as quota from account_quota where active_yn='Y'"
    dRet = pcon.returnSelectQueryResultConvert2Col2Dict(sQuery)
    if dRet['result'] == 'success':
        acctQuota = dRet['data']
        # 'socintelli': {'int': ["14.192.16.226", "51", 'Fullerton-WAN'], 'email': ['dinesh@autointelli.com']},
        sample = {'oacct00000060': {'email': ['dinesh@autointelli.com']}}
        for eachAcct in sample:
            print("Processing... {0}".format(eachAcct))
            for eachStats in pOut:
                print("Assigned Quota is:{0}".format(acctQuota[eachAcct].split('::')[0]))
                print("Used Volume is:{0}".format(pOut[eachStats]))
                print("Notification should be sent to: {0}".format(sample[eachAcct]['email']))
                _quota = float(acctQuota[eachAcct].split('::')[0])
                _consumedVolume = float(sum([pOut[eachAcct][i] for i in pOut[eachAcct]])) #/ (1024 * 1024)
                _percent = (_consumedVolume / _quota) * 100
                print("Consumed Percent: {0}".format(_percent))
                if _percent > 70.0 and _percent <= 85.0:
                    print("Notification lies under warning")
                    sendEmail(eachAcct, _quota, _consumedVolume, _percent, 'warning', sample[eachAcct]['email'])
                elif _percent > 85.0 and _percent <= 100.0:
                    print("Notification lies under critical")
                    sendEmail(eachAcct, _quota, _consumedVolume, _percent, 'critical', sample[eachAcct]['email'])
                elif _percent > 100.0:
                    print("Notification lies under unsubscribe")
                    print("Once the interface is made to down state, a notification will be sent")
                    turnOFF[eachAcct] = sample[eachAcct]
                    turnOFF[eachAcct]['Quota'] = _quota
                    turnOFF[eachAcct]['Consumed Volume'] = _consumedVolume
                    turnOFF[eachAcct]['Percent Utilized'] = _percent
        return {'result': 'success', 'data': turnOFF}
    else:
        return {'result': 'failure', 'data': 'Account Quota Mapping is missing in R2D2 Database'}

    #             if eachStats['device'] == sample[eachAcct]['int'][0] and eachStats['interface'] == sample[eachAcct]['int'][1]:
    #                 print("Assigned Quota is:{0}".format(acctQuota[eachAcct].split('::')[0]))
    #                 print("Used Volume is:{0}".format(eachStats))
    #                 print("Notification should be sent to: {0}".format(sample[eachAcct]['email']))
    #                 _quota = float(acctQuota[eachAcct].split('::')[0])
    #                 _consumedVolume = float(eachStats['data']['plots'][1][4]) / (1024*1024)
    #                 _percent = (_consumedVolume/_quota) * 100
    #                 print("Consumed Percent: {0}".format(_percent))
    #                 if _percent > 70.0 and _percent <= 85.0:
    #                     print("Notification lies under warning")
    #                     sendEmail(eachAcct, _quota, _consumedVolume, _percent, 'warning', sample[eachAcct]['email'])
    #                 elif _percent > 85.0 and _percent <= 100.0:
    #                     print("Notification lies under critical")
    #                     sendEmail(eachAcct, _quota, _consumedVolume, _percent, 'critical', sample[eachAcct]['email'])
    #                 else:
    #                     print("Notification lies under unsubscribe")
    #                     print("Once the interface is made to down state, a notification will be sent")
    #                     # sendEmail(eachAcct, _quota, _consumedVolume, _percent, 'critical', sample[eachAcct]['email'])
    #                     turnOFF[eachAcct] = sample[eachAcct]
    #                     turnOFF[eachAcct]['Quota'] = _quota
    #                     turnOFF[eachAcct]['Consumed Volume'] = _consumedVolume
    #                     turnOFF[eachAcct]['Percent Utilized'] = _percent
    #     return turnOFF
    # else:
    #     pass

def getRealServiceNameUsingIP(pGroup):
    out = lb.getRealServiceGroupMembers(pGroup)
    if out['result'] == 'success':
        return out['data']
    else:
        return {}

def enableRealServiceInArrayLB(sVM):
    try:
        sQuery = "select vm_ip from tbl_vms where lower(vm_name)=lower('{0}')".format(sVM)
        dRet = pcon.returnSelectQueryResult(sQuery)
        if dRet['result'] == 'failure':
            return ""
        _device = "117.239.183.62"
        _realservicename = gLBIPService[dRet['data'][0]['vm_ip']]
        obj = r.spawn('ssh array@{0}'.format(_device))
        print('Login to Array LB') if putil(obj, 'password:', 'admin') == 1 else raise_exc(Exception,
                                                                                                       'Device: {0} Error: Failed while feeding password'.format(
                                                                                                           _device))
        print('Mode enable') if putil(obj, ['>'], 'enable') == 1 else raise_exc(Exception,
                                                                                     'Device:{0} Error: {1}'.format(
                                                                                         _device, 'enable'))
        print('Enter Password') if putil(obj, ['password:'], '') == 1 else raise_exc(Exception,
                                                                                           'Device:{0} Error: {1}'.format(
                                                                                               _device,
                                                                                               'Enter Password'))
        print('Enter into Global Config Mode') if putil(obj, ['#'], 'config t') == 1 else raise_exc(Exception,
                                                                                                      'Device:{0} Error: {1}'.format(
                                                                                                          _device,
                                                                                                          'Enter into Global Config mode'))
        print('Enable Real Service: {0}'.format(_realservicename)) if putil(obj, ['#'], 'slb real enable "{0}"'.format(_realservicename)) == 1 else raise_exc(Exception,
                                                                                                      'Device:{0} Error: {1}'.format(
                                                                                                          _device,
                                                                                                          'Enable Real Service {0}'.format(
                                                                                                              _realservicename)))
        print('Write the changes') if putil(obj, ['#'], 'wr mem') == 1 else raise_exc(Exception,
                                                                                                      'Device:{0} Error: {1}'.format(
                                                                                                          _device,
                                                                                                          'Commit the changes'))

        print('Exit from Global Config Mode') if putil(obj, ['#'], 'exit') == 1 else raise_exc(Exception,
                                                                     'Device:{0} Error: {1}'.format(_device, 'Exit from Global Config Mode'))
        print('Exit from Array LB Device') if putil(obj, ['#'], 'exit') == 1 else raise_exc(Exception,
                                                                     'Device:{0} Error: {1}'.format(_device, 'Exit from Array LB Device'))
    except Exception as e:
        pass

def disableRealServiceInArrayLB(sVM):
    try:
        global _gRSResource
        sQuery = "select vm_ip from tbl_vms where vm_name='{0}'".format(sVM)
        dRet = pcon.returnSelectQueryResult(sQuery)
        if dRet['result'] == 'failure':
            return ""
        _device = "117.239.183.62"
        _realservicename = gLBIPService[dRet['data'][0]['vm_ip']]
        _gRSResource = _realservicename
        obj = r.spawn('ssh array@{0}'.format(_device))
        print('Login to Array LB') if putil(obj, 'password:', 'admin') == 1 else raise_exc(Exception,
                                                                                             'Device: {0} Error: Failed while feeding password'.format(
                                                                                                 _device))
        print('Mode enable') if putil(obj, ['>'], 'enable') == 1 else raise_exc(Exception,
                                                                                'Device:{0} Error: {1}'.format(
                                                                                    _device, 'enable'))
        print('Enter Password') if putil(obj, ['password:'], '') == 1 else raise_exc(Exception,
                                                                                     'Device:{0} Error: {1}'.format(
                                                                                         _device,
                                                                                         'Enter Password'))
        print('Enter into Global Config Mode') if putil(obj, ['#'], 'config t') == 1 else raise_exc(Exception,
                                                                                       'Device:{0} Error: {1}'.format(
                                                                                           _device,
                                                                                           'Enter into Global Config mode'))
        print('Disable Real Service: {0}'.format(_realservicename)) if putil(obj, ['#'],
                                         'slb real disable "{0}"'.format(_realservicename)) == 1 else raise_exc(
            Exception,
            'Device:{0} Error: {1}'.format(
                _device,
                'Disable Real Service {0}'.format(
                    _realservicename)))
        print('Write the changes') if putil(obj, ['#'], 'wr mem') == 1 else raise_exc(Exception,
                                                                                             'Device:{0} Error: {1}'.format(
                                                                                                 _device,
                                                                                                 'Commit the changes'))

        print('Exit from Global Config Mode') if putil(obj, ['#'], 'exit') == 1 else raise_exc(Exception,
                                                                      'Device:{0} Error: {1}'.format(_device, 'Exit from Global Config Mode'))
        print('Exit from Array LB Device') if putil(obj, ['#'], 'exit') == 1 else raise_exc(Exception,
                                                                      'Device:{0} Error: {1}'.format(_device, 'Exit from Array LB Device'))
    except Exception as e:
        pass



# Main that triggers things in Procedural Way
if __name__ == "__main__":

    # sQueryServiceDT = "select as_name from ai_autoscale where pk_as_id in(select distinct fk_as_id from ai_as_vm_mapping)"
    # sQueryServiceDT = "select as_name, unit, condition, unit_value from ai_autoscale where pk_as_id in(select distinct fk_as_id from ai_as_vm_mapping) and active_yn='Y'"
    sQueryServiceDT = "select as_name, h_type, h_ip, min_power_on, realservice from ai_autoscale where pk_as_id in(select distinct fk_as_id from ai_autoscale_vm_mapping) and active_yn='Y'"
    # serviceRet = pcon.returnSelectQueryResultAsList(sQueryServiceDT)
    serviceRet = pcon.returnSelectQueryResultAs2DList(sQueryServiceDT)
    if serviceRet["result"] == "success":
        lASList = dict([(i[0], i[1:]) for i in serviceRet["data"][1:]])
        for eachAutoScaler in lASList: #serviceRet["data"]["as_name"]:
            # tmpRSGName = "SOC_SVR_GROUP"
            _gServiceName = "Auto Scale Power OFF"
            _gStartDT = dt.now().strftime('%Y-%m-%d %H:%M')
            _gRealServiceGroupName = lASList[eachAutoScaler][3]
            gLBIPService = getRealServiceNameUsingIP(_gRealServiceGroupName)
            print(gLBIPService)
            _gAutoScalingGroupName = eachAutoScaler
            print("=" * 50)
            print(" Auto Scale Group:{0}".format(eachAutoScaler))
            try:
                sQueryVM = "select vm_name,vm_ip from ai_autoscale_vm_mapping m inner join ai_autoscale s  on(s.pk_as_id=m.fk_as_id) where lower(s.as_name) = lower('{0}')".format(
                    eachAutoScaler
                )
                sVMdt = pcon.returnSelectQueryResultConvert2Col2Dict(sQueryVM)
                if sVMdt["result"] == "success":
                    _gVMs = ','.join(list(sVMdt["data"].keys()))
                    print(" VMs those are part of Auto Scale Group:{0} are {1}".format(eachAutoScaler, ','.join(list(sVMdt["data"].keys()))))
                    sPowerQuery = """select 
                    	action, unit, condition, unit_value 
                    from 
                    	ai_autoscale_condition c 
                    where 
                    	c.active_yn='Y' and c.fk_as_id = (select pk_as_id from ai_autoscale where lower(as_name)=lower('{0}') and active_yn='Y')""".format(eachAutoScaler)
                    sPRet = pcon.returnSelectQueryResult(sPowerQuery)
                    if sPRet['result'] == 'success':
                        dONOFF = {}
                        for i in sPRet["data"]:
                            dONOFF[i['action']] = {"unit": i["unit"], "unit condition": i["condition"], "unit value": float(i["unit_value"])}

                        print(" Configuration : {0}".format(dONOFF))
                        _gCondition = "Power OFF = " + ','.join(["{0}:{1}".format(i, dONOFF["poweroff"][i]) for i in dONOFF["poweroff"]])
                        if lASList[eachAutoScaler][0].lower() == "vmware vcenter":

                            # Fetch the Hypervisor Password from the Database
                            credQuery = "select cred_type, username, password from ai_device_credentials where cred_id=(select hypervisor_cred from hypervisor_details where hypervisor_ip_address='{0}' and active_yn='Y' limit 1)".format(
                                lASList[eachAutoScaler][1]
                            )
                            credQuery = "select cred_type, username, password from ai_device_credentials where cred_id=(select hypervisor_cred from hypervisor_details where hypervisor_ip_address='{0}' and active_yn='Y' limit 1)".format(
                                "172.29.64.100"
                            )
                            credRet = pcon.returnSelectQueryResult(credQuery)
                            if credRet['result'] == 'success':

                                ip = lASList[eachAutoScaler][1]
                                ip = "172.29.64.100"
                                username = credRet["data"][0]["username"]
                                password = aes.decrypt(credRet["data"][0]["password"].encode(), '@ut0!ntell!'.encode()).decode('utf-8')
                                pState = getVMPowerState(ip, (username, password), list(sVMdt["data"].keys()))

                                out = perfDataLatest(pState['on'], dONOFF['poweron']['unit'])
                                if out["result"] == "success":

                                    print(' Utilization for all Powered ON VMs: {0}'.format(out))
                                    lValues = [i for i in out['data'].values() if not (i < 0)]
                                    lOFFAvergae = sum(lValues) / len(lValues)
                                    lAvergae = max(lValues) #sum(lValues) / len(lValues)

                                    # Power ON
                                    # print("-" * 50)
                                    # print("Auto Scale - Power On service...")
                                    # if len(pState['off']) > 0:
                                    #     c, v = dONOFF['poweron']['unit condition'], dONOFF['poweron']['unit value']
                                    #     print(" Peak Utilization is: {0}".format(lAvergae))
                                    #     print(" Threshold is: {0}".format(v))
                                    #     if lAvergae > v:
                                    #         pState = getVMPowerState(ip, (username, password), sVMdt["data"]["vm_name"])
                                    #         print(" Found Powered Off resource: {0}".format(pState['off']))
                                    #         pStatus = putPowerON(ip, (username, password), pState['off'])
                                    #         if pStatus['result'] == 'success':
                                    #             print(" VM: {0} Powered ON Successfully".format(pStatus['vm']))
                                    #             print(" Enable Real Service in Array LB")
                                    #             enableRealServiceInArrayLB(pStatus['vm'])
                                    #             print(" SUCCESS:Send Email Notification for Auto Scale Power ON")
                                    #             sendEmailNewlyAdded(eachAutoScaler, pStatus['vm'], 'poweron', lAvergae,
                                    #                                 ['dinesh@autointelli.com'])
                                    #         elif pStatus['result'] == 'no action':
                                    #             print(" NO ACTION:Send Email Notification for Auto Scale Power ON")
                                    #             sendEmailNewlyAdded(eachAutoScaler, pStatus['vm'], 'no action',
                                    #                                 lAvergae,
                                    #                                 ['dinesh@autointelli.com'])
                                    #         elif pStatus['result'] == 'failure':
                                    #             print(" FAILURE:Send Email Notification for Auto Scale Power ON")
                                    #             sendEmailNewlyAdded(eachAutoScaler, '', 'error', lAvergae,
                                    #                                 ['dinesh@autointelli.com'], pState['data'])
                                    #     else:
                                    #         print(" Below threshold. No action for Auto-Scale power-on service.")
                                    # else:
                                    #     print(" No Resource left to Auto-Scale ")
                                    # print("-" * 50)

                                    # Power OFF
                                    # print("Sleep for 120 seconds to look @Power Off")
                                    # time.sleep(120)
                                    print("-" * 50)
                                    print("Auto Scale - Power Off service...")
                                    pState = getVMPowerState(ip, (username, password), list(sVMdt["data"].keys()))
                                    if len(pState['on']) > lASList[eachAutoScaler][2]:
                                        # print("Under Construction")
                                        c, v = dONOFF['poweroff']['unit condition'], dONOFF['poweroff']['unit value']
                                        print(" Average is: {0}".format(lOFFAvergae))
                                        print(" Threshold is: {0}".format(v))
                                        _gUsage = lOFFAvergae
                                        _gThreshold = v
                                        if lOFFAvergae < v:
                                            # pState = getVMPowerState(ip, (username, password), list(sVMdt["data"].keys()))
                                            _gPOFFDecisionFlag = "Yes"
                                            print(" Found Powered ON resource: {0}".format(pState['on']))
                                            pStatus = putPowerOFF(ip, (username, password), pState['on'], sVMdt["data"])
                                            if pStatus['result'] == 'success':
                                                print(" VM: {0} Powered OFF Successfully".format(pStatus['vm']))
                                                #disableRealServiceInArrayLB(pStatus['vm'])
                                                print(" SUCCESS:Send Email Notification for Auto Scale Power OFF")
                                                _gRemarks = pStatus["data"] + "VM: {0} Powered OFF Successfully".format(pStatus['vm']) + "\n"  \
                                                            "Sent Success Email Notification for Auto Scale Power OFF"
                                                sendEmailNewlyAdded(eachAutoScaler, pStatus['vm'], 'poweroff', lOFFAvergae,
                                                                    ['dinesh@autointelli.com'])
                                            elif pStatus['result'] == 'no action':
                                                print(" NO ACTION:Send Email Notification for Auto Scale Power OFF")
                                                sendEmailNewlyAdded(eachAutoScaler, pStatus['vm'], 'no action',
                                                                    lOFFAvergae,
                                                                    ['dinesh@autointelli.com'])
                                                _gRemarks = pStatus["data"] + "Sent No Action Email Notification for Auto Scale Power OFF"
                                            elif pStatus['result'] == 'failure':
                                                print(" FAILURE:Send Email Notification for Auto Scale Power OFF")
                                                sendEmailNewlyAdded(eachAutoScaler, '', 'error', lOFFAvergae,
                                                                    ['dinesh@autointelli.com'], pState['data'])
                                                _gRemarks = pStatus["data"] + "Sent Failure Email Notification for Auto Scale Power OFF"
                                        else:
                                            _gRemarks = "Below threshold. No action for Auto-Scale power-off service."
                                            print(" Below threshold. No action for Auto-Scale power-off service.")
                                    else:
                                        _gRemarks = "Minimum Power on is {0} and Power ON count is {1}. Cant perform PowerOFF action".format(lASList[eachAutoScaler][2], len(pState['on']))
                                        print(" Minimum Power on is {0} and Power ON count is {1}. Cant perform PowerOFF action".format(lASList[eachAutoScaler][2], len(pState['on'])))
                                    print("-" * 50)

                                else:
                                    _gError = "Performance Data missing for {0}".format(pState['on'])
                                    print(" Performance Data missing for {0}".format(pState['on']))

                            else:
                                # print(" Login Pre-req is missing for the hypervisor: {0}".format(lASList[eachAutoScaler][1]))
                                _gError = "Login Pre-req is missing for the hypervisor: {0}".format("172.29.64.100")
                                print(" Login Pre-req is missing for the hypervisor: {0}".format("172.29.64.100"))

                        elif lASList[eachAutoScaler][0].lower() == "onapp kvm":
                            print(" VM Power ON/OFF functionality for KVM is Under Construction...")

                    else:
                        _gRemarks = "Power ON & OFF features are missing for Auto Scale Group : {0}".format(eachAutoScaler)
                        print(" Power ON & OFF features are missing for Auto Scale Group : {0}".format(eachAutoScaler))
                else:
                    _gRemarks = "There are no VMs configured for {0} Auto-Scale Group. You can add from Cloud Service --> Auto-Scale.".format(eachAutoScaler)
                    print(" There are no VMs configured for {0} Auto-Scale Group. You can add from Cloud Service --> Auto-Scale.".format(eachAutoScaler))
            except Exception as e:
                _gError = "An exception occured while fetching VM details for the auto-scale group: {0}".format(eachAutoScaler)
                print("An exception occured while fetching VM details for the auto-scale group: {0}".format(eachAutoScaler))
            print("=" * 50)
            _gEndDT = dt.now().strftime('%Y-%m-%d %H:%M')
            audit()
            reset()
    else:
        # _gRemarks = "No Auto-Scale Group Configured to execute the service."
        print("No Auto-Scale Group Configured to execute the service.")
    # out = perfDataLatest()
    # if out['result'] == 'success':
    #     turnOFFAccounts = MatchAndSendNotif(out['data'])
    #     print(turnOFFAccounts)
    #     if turnOFFAccounts['result'] == 'success':
    #         print("Trun Off is under construction")
    #         turnOFF(turnOFFAccounts['data'])


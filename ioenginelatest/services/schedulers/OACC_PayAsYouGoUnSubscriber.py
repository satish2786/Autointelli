from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import json
from elasticsearch import Elasticsearch
from datetime import datetime as dt
import pytz
import services.utils.ConnPostgreSQL as pcon
import pexpect as r
import services.utils.mailservice as mail
import requests

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
def perfDataLatest():
    try:
        _index = "ai-ngvm-perf-metrics"
        _bucket = '1'
        user_tz = pytz.timezone('GMT')
        es_tz = pytz.timezone('GMT')
        user_s, user_e = user_tz.localize(
            dt.strptime(dt.now().strftime('%Y-%m') + '-01 00:00', '%Y-%m-%d %H:%M')), user_tz.localize(
            dt.strptime(dt.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M'))  # Declare I/P to particular timezone
        gmt_s, gmt_e = user_s.astimezone(es_tz), user_e.astimezone(es_tz)
        start_datetime = gmt_s.strftime('%Y-%m-%dT%H:%MZ')
        end_datetime = gmt_e.strftime('%Y-%m-%dT%H:%MZ')

        mapper = {'KVM VM': {'NIC': {'select': ['interface.Dynamic.bytes_recv', 'interface.Dynamic.bytes_sent'], 'meta': [],
                               'units': 'MB/s',
                               'plotter': ['Interface.Dynamic.bytes_recv', 'Interface.Dynamic.bytes_sent']}}
        }

        _body = {'size': 1,
                 '_source': [],
                 'query': {'bool': {'filter': []}},
                 'aggs': {
                     'Date': {'date_histogram': {'field': '@timestamp.GMT', 'fixed_interval': '{0}m'.format(_bucket)},
                              'aggs': {}}}}
        serviceDT = {}
        sQueryServiceDT = "select acct_id,to_char(service_start, 'YYYY-MM-DD HH24:MI') service_start, to_char(service_end, 'YYYY-MM-DD HH24:MI') service_end from account_quota where active_yn='Y'"
        serviceRet = pcon.returnSelectQueryResultAs2DList(sQueryServiceDT)
        if serviceRet["result"] == "success":
            for i in serviceRet["data"][1:]:
                serviceDT[i[0]] = {'servicestart': i[1].replace(' ', 'T') + 'Z', 'serviceend': i[2].replace(' ', 'T') + 'Z'}


        customer_vm_details = {'oacct00000060': ['Autointelli-Test']}
        retFinal = {}
        for eachOACC in customer_vm_details:
            dTmp = {}
            for eachVM in customer_vm_details[eachOACC]:
                try:
                    _body['_source'] = ['@timestamp.GMT'] + mapper['KVM VM']['NIC']['select']
                    d, l = {}, []
                    l.append({'bool': {'should': [{'match_phrase': {'Name': eachVM}}]}})
                    d = {'bool': {'filter': l}}
                    _body['query']['bool']['filter'].append(d)
                    # _body['query']['bool']['filter'].append({'match_phrase_prefix': {'Name': _name}})
                    # _body['query']['bool']['filter'].append(
                    #     {'range': {'@timestamp.GMT': {'gte':  start_datetime, 'lte': end_datetime}}})
                    _body['query']['bool']['filter'].append(
                        {'range': {'@timestamp.GMT': {'gte': serviceDT[eachOACC]['servicestart'], 'lte': serviceDT[eachOACC]['serviceend']}}})
                    units = mapper['KVM VM']['NIC']['units']
                    plotters = mapper['KVM VM']['NIC']['plotter']

                    if mapper['KVM VM']['NIC']['select'][0].lower().__contains__('.dynamic.'):
                        del _body['_source']
                        del _body['aggs']
                        _out = esExecWithAgg(_index, _body, es_tz, user_tz, _bucket)
                        if _out['result'] == 'success':
                            _lDyna = []
                            for x in mapper['KVM VM']['NIC']['select']:
                                _lDyna += ["{0}.{1}.{2}".format(x.split('.')[0], i, x.split('.')[2]) for i in
                                           _out['data'][0][x.split('.')[0]]]

                            _body['_source'] = ['@timestamp.GMT'] + _lDyna
                            _body['aggs'] = {'Date': {'auto_date_histogram': {'field': '@timestamp.GMT',
                                                                              'buckets': 1},
                                                      'aggs': {}}}
                            d = {}
                            for i in _lDyna:
                                d[i] = {'sum': {'field': i}}
                            _body['aggs']['Date']['aggs'] = d
                            _out = esExec(_index, _body, es_tz, user_tz, _bucket, units)
                            if _out['result'] == 'success':
                                _out['units'] = units
                                _out['plotters'] = _lDyna
                                dTmp[eachVM] = sum(_out['data']['plots'][1][3:])
                            else:
                                dTmp[eachVM] = 0
                        else:
                            dTmp[eachVM] = 0
                except Exception as e:
                    continue

            retFinal[eachOACC] = dTmp
        return {'result': 'success', 'data': retFinal}
        #     _body = {'size': 1,
        #              '_source': [],
        #              'query': {'bool': {'filter': []}},
        #              'aggs': {'Date': {
        #                  'auto_date_histogram': {'field': '@timestamp.GMT',
        #                                          'buckets': 1 }}}}
        #
        #     _body['_source'] = ['@timestamp.GMT'] + ["Traffic Total(speed)", "Traffic In(speed)",
        #                                              "Traffic Out(speed)", "Traffic Total(volume)",
        #                                              "Traffic In(volume)", "Traffic Out(volume)"]
        #     _body['query']['bool']['filter'] = []
        #     d, l = {}, []
        #     l.append({'bool': {'should': [{'match_phrase': {'Hostname': eachI[0]}}]}})
        #     l.append({'bool': {'should': [{'match_phrase': {'Interface': eachI[1]}}]}})
        #     d = {'bool': {'filter': l}}
        #     _body['query']['bool']['filter'].append(d)
        #
        #     _body['query']['bool']['filter'].append(
        #         {'range': {'@timestamp.GMT': {'gte': start_datetime, 'lte': end_datetime}}})
        #     units = 'Mbit/s'
        #     plotters = ['Traffic Total(speed)', 'Traffic In(speed)', 'Traffic Out(speed)']
        #     d = {}
        #     for i in ["Traffic Total(speed)", "Traffic In(speed)", "Traffic Out(speed)", "Traffic Total(volume)",
        #               "Traffic In(volume)", "Traffic Out(volume)"]:
        #         d[i] = {'sum': {'field': i}}
        #     _body['aggs']['Date']['aggs'] = d
        #     _out = esExec(interface_index, _body, es_tz, user_tz, _bucket, units, 'firewall')
        #     if _out['result'] == 'success':
        #         retFinal.append({'device': eachI[0], 'interface': eachI[1], 'data': _out['data']})
        #     else:
        #         retFinal.append({'device': eachI[0], 'interface': eachI[1], 'data': 'no data'})
        # return retFinal

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

# Main that triggers things in Procedural Way
if __name__ == "__main__":
    out = perfDataLatest()
    if out['result'] == 'success':
        turnOFFAccounts = MatchAndSendNotif(out['data'])
        print(turnOFFAccounts)
        if turnOFFAccounts['result'] == 'success':
            print("Trun Off is under construction")
            turnOFF(turnOFFAccounts['data'])




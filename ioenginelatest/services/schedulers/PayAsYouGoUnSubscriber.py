from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import json
from elasticsearch import Elasticsearch
from datetime import datetime as dt
import pytz
import services.utils.ConnPostgreSQL as pcon
import pexpect as r
import services.utils.mailservice as mail

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
        sHTMLSubject = "{0}: UnSubscribed! Re-activate By Payments".format(pAcct)
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

# Get Current Utilization
def perfDataLatest():
    try:
        interface_index = "ai-network-interface-bandwidth"
        _bucket = '1'
        user_tz = pytz.timezone('GMT')
        es_tz = pytz.timezone('GMT')
        user_s, user_e = user_tz.localize(
            dt.strptime(dt.now().strftime('%Y-%m') + '-01 00:00', '%Y-%m-%d %H:%M')), user_tz.localize(
            dt.strptime(dt.now().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M'))  # Declare I/P to particular timezone
        gmt_s, gmt_e = user_s.astimezone(es_tz), user_e.astimezone(es_tz)
        start_datetime = gmt_s.strftime('%Y-%m-%dT%H:%MZ')
        end_datetime = gmt_e.strftime('%Y-%m-%dT%H:%MZ')

        interface_details = [["14.192.16.226", "51"]]
        retFinal = []
        for eachI in interface_details:
            _body = {'size': 1,
                     '_source': [],
                     'query': {'bool': {'filter': []}},
                     'aggs': {'Date': {
                         'auto_date_histogram': {'field': '@timestamp.GMT',
                                                 'buckets': 1 }}}}

            _body['_source'] = ['@timestamp.GMT'] + ["Traffic Total(speed)", "Traffic In(speed)",
                                                     "Traffic Out(speed)", "Traffic Total(volume)",
                                                     "Traffic In(volume)", "Traffic Out(volume)"]
            _body['query']['bool']['filter'] = []
            d, l = {}, []
            l.append({'bool': {'should': [{'match_phrase': {'Hostname': eachI[0]}}]}})
            l.append({'bool': {'should': [{'match_phrase': {'Interface': eachI[1]}}]}})
            d = {'bool': {'filter': l}}
            _body['query']['bool']['filter'].append(d)

            _body['query']['bool']['filter'].append(
                {'range': {'@timestamp.GMT': {'gte': start_datetime, 'lte': end_datetime}}})
            units = 'Mbit/s'
            plotters = ['Traffic Total(speed)', 'Traffic In(speed)', 'Traffic Out(speed)']
            d = {}
            for i in ["Traffic Total(speed)", "Traffic In(speed)", "Traffic Out(speed)", "Traffic Total(volume)",
                      "Traffic In(volume)", "Traffic Out(volume)"]:
                d[i] = {'sum': {'field': i}}
            _body['aggs']['Date']['aggs'] = d
            _out = esExec(interface_index, _body, es_tz, user_tz, _bucket, units, 'firewall')
            if _out['result'] == 'success':
                retFinal.append({'device': eachI[0], 'interface': eachI[1], 'data': _out['data']})
            else:
                retFinal.append({'device': eachI[0], 'interface': eachI[1], 'data': 'no data'})
        return retFinal

    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

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
        sample = {'socintelli': {'int': ["14.192.16.226", "51", 'Fullerton-WAN'], 'email': ['dinesh@autointelli.com']}}
        for eachAcct in sample:
            print("Processing... {0}".format(eachAcct))
            for eachStats in pOut:
                if eachStats['device'] == sample[eachAcct]['int'][0] and eachStats['interface'] == sample[eachAcct]['int'][1]:
                    print("Assigned Quota is:{0}".format(acctQuota[eachAcct].split('::')[0]))
                    print("Used Volume is:{0}".format(eachStats))
                    print("Notification should be sent to: {0}".format(sample[eachAcct]['email']))
                    _quota = float(acctQuota[eachAcct].split('::')[0])
                    _consumedVolume = float(eachStats['data']['plots'][1][4]) / (1024*1024)
                    _percent = (_consumedVolume/_quota) * 100
                    print("Consumed Percent: {0}".format(_percent))
                    if _percent > 70.0 and _percent <= 85.0:
                        print("Notification lies under warning")
                        sendEmail(eachAcct, _quota, _consumedVolume, _percent, 'warning', sample[eachAcct]['email'])
                    elif _percent > 85.0 and _percent <= 100.0:
                        print("Notification lies under critical")
                        sendEmail(eachAcct, _quota, _consumedVolume, _percent, 'critical', sample[eachAcct]['email'])
                    else:
                        print("Notification lies under unsubscribe")
                        print("Once the interface is made to down state, a notification will be sent")
                        # sendEmail(eachAcct, _quota, _consumedVolume, _percent, 'critical', sample[eachAcct]['email'])
                        turnOFF[eachAcct] = sample[eachAcct]
                        turnOFF[eachAcct]['Quota'] = _quota
                        turnOFF[eachAcct]['Consumed Volume'] = _consumedVolume
                        turnOFF[eachAcct]['Percent Utilized'] = _percent
        return turnOFF
    else:
        pass

# Main that triggers things in Procedural Way
if __name__ == "__main__":
    out = perfDataLatest()
    print(out)
    turnOFFInts = MatchAndSendNotif(out)
    print(turnOFFInts)
    turnOFF(turnOFFInts)




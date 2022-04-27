import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import requests as req
import time
from elasticsearch import Elasticsearch
import pytz
from datetime import datetime as dt
import pika

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
           'amd-': {'fqdn': 'r2d22.nxtgen.com'},
           'fbd-': {'fqdn': 'r2d23.nxtgen.com'},
           'mum-': {'fqdn': 'r2d21.nxtgen.com'}}

def esExecWithAgg(_pindex, _pbody, _es_tz, _user_tz, _bucket):
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
                    FinalData.append([_date] + ['%.2f' % (i[k]['value']) if not i[k]['value'] == None else 0 for k in items])
            except Exception as e:
                pass
            sid = data['_scroll_id']
            scroll_size = len(data['hits']['hits'])
            break
        FinalData.insert(0, ['DateTime'] + items)
        return {'result': 'success', 'data': dict(zip(FinalData[0], FinalData[1]))}
    except Exception as e:
        print(str(e))
        return {'result': 'failure', 'data': []}

def getCPU(vm_id, start_datetime, end_datetime, timezone='Asia/Kolkata'):
    try:
        index = "ai-ngvm-perf-metrics"

        # DateTime Formatting
        user_tz = pytz.timezone(timezone)
        es_tz = pytz.timezone('GMT')
        user_s, user_e = user_tz.localize(dt.strptime(start_datetime, '%y-%m-%d %H:%M')), user_tz.localize(
            dt.strptime(end_datetime, '%y-%m-%d %H:%M'))  # Declare I/P to particular timezone
        gmt_s, gmt_e = user_s.astimezone(es_tz), user_e.astimezone(es_tz)
        start_datetime = gmt_s.strftime('%Y-%m-%dT%H:%MZ')
        end_datetime = gmt_e.strftime('%Y-%m-%dT%H:%MZ')

        # _bucket = math.ceil(((gmt_e.timestamp() - gmt_s.timestamp()) / 60) / 1000)

        _body = {'size': 1,
                 '_source': [],
                 'query': {'bool': {'filter': []}},
                 'aggs': {'Date': {
                     'auto_date_histogram': {'field': '@timestamp.GMT',
                                             'buckets': 1}}}}
        _body['_source'] = ['@timestamp.GMT'] + ["vmcpucount", "cpu_percent"]
        _body['query']['bool']['filter'] = []
        d, l = {}, []
        l.append({'bool': {'should': [{'match_phrase': {'vmid': vm_id}}]}})
        d = {'bool': {'filter': l}}
        _body['query']['bool']['filter'].append(d)
        _body['query']['bool']['filter'].append({'range': {'@timestamp.GMT': {'gte': start_datetime, 'lte': end_datetime}}})
        d = {}
        d['vmcpucount'] = {'avg': {'field': 'vmcpucount'}}
        d['cpu_percent'] = {'avg': {'field': 'cpu_percent'}}
        _body['aggs']['Date']['aggs'] = d
        _out = esExecWithAgg(index, _body, es_tz, user_tz, '1')
        return _out
    except Exception as e:
        return {'result': 'failure', 'data': []}

def getDisk(host, vm_id):
    # https://10.225.160.211:5693/api/plugins/kvm_disk_usage.sh/gwejkgsbsopwhy/75/90/1?token=NxtG3n
    try:
        sURL = "https://{0}:5693/api/plugins/kvm_disk_usage.sh/{1}/75/90/1?token=NxtG3n".format(host, vm_id)
        dHeader = {'Content-Type': 'application/json'}
        res = req.get(url=sURL, headers=dHeader, verify=False)
        if res.status_code == 200:
            retJS = json.loads(res.text)
            if retJS['returncode'] == 0:
                retD = dict(zip(json.loads(retJS['stdout'])['disk'][0], json.loads(retJS['stdout'])['disk'][1]))
                return {'result': 'success', 'data': retD}
            else:
                return {'result': 'failure', 'data': 'no data'}
        else:
            return {'result': 'failure', 'data': 'no data'}
    except Exception as e:
        return {'result': 'failure', 'data': 'no data'}

def processEvent(payload):
    """Method: accepts the the event from external monitoring system"""
    try:
        tech = payload['technology']
        accid = payload['accountid']
        sdate = dt.strptime(payload['startdate'], '%Y-%m-%d %H:%M').strftime('%y-%m-%d %H:%M')
        edate = dt.strptime(payload['enddate'], '%Y-%m-%d %H:%M').strftime('%y-%m-%d %H:%M')
        uid = payload['user_id']
        pid = payload['pk_id']

        sQuery = "select h_ip host, v_identifier vm_id, v_operating_system vm_os, v_ip_addresses vm_ip, v_power_state state, v_label vm_name from onapp_object_inventory where lower(trim(c_login))='{0}'".format(
            accid.strip().lower()
        )
        dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sQuery)
        if dRet['result'] == 'failure':
            return json.dumps({'result': 'failure', 'data': 'The selected customer has zero VMs'})
        else:
            vmList = dRet['data'][1:]
            finalData = []
            finalData.append(['Account ID', 'VM Name', 'OS', 'Power State', 'IP Address', 'CPU Count', 'CPU Percent', 'Disk Total (GB)', 'Disk Used (GB)', 'Disk Avail (GB)', 'Disk Used %', 'Disk Free %'])
            for eachVM in vmList:
                tmp = []
                tmp = tmp + [accid, eachVM[5], eachVM[2], eachVM[4], eachVM[3]]
                dCPU = getCPU(eachVM[1], sdate, edate)
                dDisk = getDisk(eachVM[0], eachVM[1])
                if dCPU['result'] == 'success' and dDisk['result'] == 'success':
                    resC = dCPU['data']
                    resD = dDisk['data']
                    kbtogb = 1024 * 1024
                    tmp = tmp + [resC['vmcpucount'], resC['cpu_percent']]
                    tmp = tmp + [str('%.2f' % (resD['Total']/kbtogb)), str('%.2f' % (resD['Used']/kbtogb)),
                                 str('%.2f' % (resD['Available']/kbtogb)), str('%.2f' % resD['Used Percent']),
                                 str('%.2f' % ((resD['Available']/resD['Total']) * 100))]
                    # tmp = tmp + ['{0} {1}'.format(resD['Total'], resD['Units']), '{0} {1}'.format(resD['Used'], resD['Units']),
                    #              '{0} {1}'.format(resD['Available'], resD['Units']), '{0} {1}'.format(resD['Used Percent'], resD['Units'])]
                else:
                    continue
                # if dCPU['result'] == 'success':
                #     resC = dCPU['data']
                #     tmp = tmp + [resC['vmcpucount'], resC['cpu_percent']]
                # else:
                #     tmp = tmp + ['', '']
                # if dDisk['result'] == 'success':
                #     resD = dDisk['data']
                #     tmp = tmp + ['{0} {1}'.format(resD['Total'], resD['Units']),
                #                  '{0} {1}'.format(resD['Used'], resD['Units']),
                #                  '{0} {1}'.format(resD['Available'], resD['Units']),
                #                  '{0} {1}'.format(resD['Used Percent'], resD['Units'])]
                # else:
                #     tmp = tmp + ['', '', '', '']
                finalData.append(tmp)
                del tmp

            filename = "{0}.csv".format(dt.now().strftime('%d%m%Y%H%M%S'))
            path = "/usr/share/nginx/html/downloads/" + filename
            open(path, 'w').write('\n'.join([','.join(i) for i in finalData]))

            #Update Table
            uQuery = "update report_vmsummary set status=1, link='{0}' where pk_vmsumm_rpt_id={1}".format(
                'https://{0}/downloads/{1}'.format(dIPFQDNDownload[location]['fqdn'], filename), pid
            )
            dRet = ConnPostgreSQL.returnInsertResult(uQuery)
            return {'result': 'success', 'data': 'https://{0}/downloads/{1}'.format(dIPFQDNDownload[location]['fqdn'], filename)}
    except Exception as e:
        print(str(e))
        # Update Table
        uQuery = "update report_vmsummary set status=1, link='Failed to Generate. Re-initiate.' where pk_vmsumm_rpt_id={1}".format(
            'https://{0}/downloads/{1}'.format(dIPFQDNDownload[location]['fqdn'], filename), pid
        )
        dRet = ConnPostgreSQL.returnInsertResult(uQuery)
        logERROR("Exception: {0}".format(str(e)))
        return {'result': 'failure', 'data': 'no data'}

def callback(ch, method, properties, body):
    try:
        payload = json.loads(body.decode('utf-8'))
        s = time.time()
        print(payload)
        retJson = processEvent(payload)
        print("TimeTaken: {0}".format(time.time() - s))
        logINFO("Discovery Call Back:{0}".format(retJson))
        if retJson["result"] == "success":
            print('Success')
        else:
            print('Failed')
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

try:
    # Get the details of MQ
    sIP, sUserName, sPassword = "", "", ""
    sQuery = "select configip ip, username, password from configuration where configname='MQ'"
    dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        sIP = dRet["data"][0]["ip"]
        sUserName = dRet["data"][0]["username"]
        sPassword = decoder.decode("auto!ntell!", dRet["data"][0]["password"])
    else:
        print("unable to fetch information from configuration table")
    # declare credentials
    credentials = pika.PlainCredentials(sUserName, sPassword)
    # open connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=sIP, credentials=credentials, virtual_host='autointelli'))
    # create channel
    channel = connection.channel()
    # select queue
    channel.queue_declare(queue='rptkvmvmsumm', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='rptkvmvmsumm', queue='rptkvmvmsumm')
    channel.basic_consume(callback, queue='rptkvmvmsumm', no_ack=True)
    channel.start_consuming()
    # channel.close()
except Exception as e:
    logERROR("Exception: {0}".format(str(e)))
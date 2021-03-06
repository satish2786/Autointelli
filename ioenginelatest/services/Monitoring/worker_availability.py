import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import requests
from requests.auth import HTTPBasicAuth
# from services.Monitoring import ServiceReport
import time

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def register(user_id, js):
    try:
        sQuery = "insert into availability_reports(fk_user_id, generated_time, status, meta) values({0}, now(), {1}, '{2}') RETURNING pk_avail_rpt_id".format(
            user_id, 0, js)
        dRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sQuery)
        if dRet["result"] == "success":
            return dRet["data"][0]["pk_avail_rpt_id"]
        else:
            return 0
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return 0

def getServiceReport(monitorurl, hostgroup, startepoch, endepoch, username, host):
    try:
        URL = ""  #
        if host:  #
            URL = "http://" + monitorurl + "/nagios/cgi-bin/archivejson.cgi?query=availability&availabilityobjecttype=services&hostname={3}&hostgroup={2}&starttime={0}&endtime={1}".format(
                startepoch, endepoch, hostgroup, host)  #
        else:  #
            URL = "http://" + monitorurl + "/nagios/cgi-bin/archivejson.cgi?query=availability&availabilityobjecttype=services&hostgroup={2}&starttime={0}&endtime={1}".format(
                startepoch, endepoch, hostgroup)
        Output = requests.get(URL, auth=HTTPBasicAuth(username, 'nagiosadmin'))
        print("{0}, {1}".format(Output.status_code, URL))
        Output = json.loads(Output.text)
        return Output
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def getRet4SingleHost(data, hostname, totaltime):
    try:
        Output_data = {}
        for service in data['data']['services']:
            if service['host_name'] == hostname:
                service_name = service['description']
                time_ok_percent = (service['time_ok'] / totaltime) * 100
                time_warning_percent = (service['time_warning'] / totaltime) * 100
                time_critical_percent = (service['time_critical'] / totaltime) * 100
                time_unknown_percent = (service['time_unknown'] / totaltime) * 100
                Output_data[service_name] = {}
                Output_data[service_name]['ok'] = float('%.2f' % time_ok_percent)
                Output_data[service_name]['warning'] = float('%.2f' % time_warning_percent)
                Output_data[service_name]['critical'] = float('%.2f' % time_critical_percent)
                Output_data[service_name]['unknown'] = float('%.2f' % time_unknown_percent)
                ll = [Output_data[service_name][i] for i in Output_data[service_name]]
                Output_data[service_name]['ok'] += (100 - sum(ll))
                Output_data.update()
        return (Output_data)
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def processEvent(payload):
    """Method: accepts the the event from external monitoring system"""
    try:
        print('inside processing')
        # Host Details through HostGroup
        host = "" #
        monitorurl, username, starttime, endtime, hostgroup, totaltime, comment, auto_user_id = payload['monitorurl'], payload['username'], \
                                                                                  payload['starttime'], payload['endtime'], \
                                                                                  payload['hostgroup'], payload['totaltime'], payload['comment'],  \
                                                                                  payload['auto_userid']
        if 'host' in (payload.keys()): #
            host = payload['host'] #
        # meta_json = json.dumps({
        #     'hostgroup': hostgroup,
        #     'start_date': time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(starttime)),
        #     'end_date': time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(endtime)),
        #     'comment': comment
        # })
        pk_avail_id = payload['pk_avail_id'] #register(auto_user_id, meta_json)
        if pk_avail_id != 0:
            URL = "" #
            if host: #
                URL = URL = "http://" + monitorurl + "/nagios/cgi-bin/archivejson.cgi?query=availability&availabilityobjecttype=hostgroups&hostname={3}&hostgroup={2}&starttime={0}&endtime={1}".format(
                starttime, endtime, hostgroup, host) #
            else: #
                URL = "http://" + monitorurl + "/nagios/cgi-bin/archivejson.cgi?query=availability&availabilityobjecttype=hostgroups&hostgroup={2}&starttime={0}&endtime={1}".format(
                starttime, endtime, hostgroup)
            Output = requests.get(URL, auth=HTTPBasicAuth(username, 'nagiosadmin'))
            print("{0}, {1}".format(Output.status_code, URL))
            Output = json.loads(Output.text)

            # Service 4 Host Group
            dService4HostGroup = getServiceReport(monitorurl, hostgroup, starttime, endtime, username, host) #

            # Process Host Data
            Output_data = {}
            Output_data['hostgroup'] = {}
            Output_data['Average'] = {}
            c, total_hosts = 0, len(Output['data']['hostgroup']['hosts'])
            for host in Output['data']['hostgroup']['hosts']:
                c += 1
                print("Host =>{0} of {1}".format(c, total_hosts))
                hostname = host['name']

                # Process Service Data
                Soutput = getRet4SingleHost(dService4HostGroup, hostname, totaltime)
                time_up_percent = (host['time_up'] / totaltime) * 100
                time_down_percent = (host['time_down'] / totaltime) * 100
                time_unreachable_percent = (host['time_unreachable'] / totaltime) * 100
                Output_data['hostgroup'][hostname] = {}
                Output_data['hostgroup'][hostname]['Status'] = {}
                Output_data['hostgroup'][hostname]['Services'] = Soutput
                Output_data['hostgroup'][hostname]['Status']['up'] = float('%.2f' % time_up_percent)
                Output_data['hostgroup'][hostname]['Status']['down'] = float('%.2f' % time_down_percent)
                Output_data['hostgroup'][hostname]['Status']['unreachable'] = float('%.2f' % time_unreachable_percent)
                ll = [Output_data['hostgroup'][hostname]['Status'][i] for i in
                      Output_data['hostgroup'][hostname]['Status']]
                Output_data['hostgroup'][hostname]['Status']['up'] += (100 - sum(ll))
                Output_data.update()

            # Process Host Average
            extract = []
            for host in Output_data['hostgroup']:
                extract.append((Output_data['hostgroup'][host]['Status']['up'],
                                Output_data['hostgroup'][host]['Status']['down'],
                                Output_data['hostgroup'][host]['Status']['unreachable']))
            up_avg, down_avg, unreach_avg = 0.0, 0.0, 0.0
            l = len(extract)
            for i in extract:
                # print(i[0])
                up_avg += i[0]
                down_avg += i[1]
                unreach_avg += i[2]
            avg_d = {'up': float('%.2f' % up_avg) if up_avg == 0.0 else float('%.2f' % (up_avg / l)),
                     'down': float('%.2f' % down_avg) if down_avg == 0.0 else float('%.2f' % (down_avg / l)),
                     'unreachable': float('%.2f' % unreach_avg) if unreach_avg == 0.0 else float(
                         '%.2f' % (unreach_avg / l))}
            Output_data['Average']['Host_Average'] = {}
            Output_data['Average']['Host_Average'] = avg_d
            Output_data.update()

            # Process Service Average
            extract_service = []
            for host in Output_data['hostgroup']:
                for Service in Output_data['hostgroup'][host]['Services']:
                    extract_service.append((Output_data['hostgroup'][host]['Services'][Service]['ok'],
                                            Output_data['hostgroup'][host]['Services'][Service]['warning'],
                                            Output_data['hostgroup'][host]['Services'][Service]['critical'],
                                            Output_data['hostgroup'][host]['Services'][Service]['unknown']))
            ok_avg, warning_avg, critical_avg, unknown_avg = 0.0, 0.0, 0.0, 0.0
            l = len(extract_service)
            for i in extract_service:
                # print(i[0])
                ok_avg += i[0]
                warning_avg += i[1]
                critical_avg += i[2]
                unknown_avg += i[3]
            avg_S = {'ok': float('%.2f' % ok_avg) if ok_avg == 0.0 else float('%.2f' % (ok_avg / l)),
                     'warning': float('%.2f' % warning_avg) if warning_avg == 0.0 else float(
                         '%.2f' % (warning_avg / l)),
                     'critical': float('%.2f' % critical_avg) if critical_avg == 0.0 else float(
                         '%.2f' % (critical_avg / l)),
                     'unknown': float('%.2f' % unknown_avg) if unknown_avg == 0.0 else float(
                         '%.2f' % (unknown_avg / l))}
            Output_data['Average']['Service_Average'] = {}
            Output_data['Average']['Service_Average'] = avg_S
            Output_data.update()

            #FIX
            ll = list(Output_data['hostgroup'].keys())
            for i in ll:
                if i.lower().strip() != payload['host'].lower().strip():
                    del Output_data['hostgroup'][i]

            user_id = ''
            # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1577836800))
            # to_timestamp(epoch)
            # meta_json = json.dumps({
            #     'hostgroup': hostgroup,
            #     'start_date': time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(starttime)),
            #     'end_date': time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(endtime)),
            #     'comment': comment
            # })
            data_json = json.dumps(Output_data)
            # sQuery = "insert into availability_reports(fk_user_id, meta, data, generated_time) values({0},'{1}','{2}',now())".format(
            #     1, meta_json, data_json)
            sQuery = "update availability_reports set data='{0}', status=1 where pk_avail_rpt_id={1}".format(data_json, pk_avail_id)
            sRet = ConnPostgreSQL.returnInsertResult(sQuery)
            if sRet["result"] == "success":
                return {"result": "success"}
            else:
                return {"result": "failure"}
        else:
            pass

    except Exception as e:
        print(str(e))
        logERROR("Exception: {0}".format(str(e)))

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

import pika
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
    channel.queue_declare(queue='availability', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='reports', queue='availability')
    channel.basic_consume(callback, queue='availability', no_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Exception: {0}".format(str(e)))

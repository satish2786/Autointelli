import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import requests
from requests.auth import HTTPBasicAuth
# from services.Monitoring import ServiceReport
import time
from datetime import datetime as dt

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

dIPFQDN = {'blr-': 'r2d2.nxtgen.com',
           'amd-': 'r2d22.nxtgen.com',
           'fbd-': 'r2d23.nxtgen.com',
           'mum-': 'r2d21.nxtgen.com'}

def processEvent(payload):
    """Method: accepts the the event from external monitoring system"""
    try:
        tech = payload['technology']
        accid = payload['accountid']
        sdate = dt.strptime(payload['startdate'], '%Y-%m-%d %H:%M').strftime('%y-%m-%d %H:%M')
        edate = dt.strptime(payload['enddate'], '%Y-%m-%d %H:%M').strftime('%y-%m-%d %H:%M')
        uid = payload['user_id']
        pid = payload['pk_id']

        sQuery = "select vm_name from tbl_vms where customer_id=(select customer_id from tbl_customer where lower(trim(technology_loc))='{0}' and lower(trim(customer_id))='{1}')".format(
            tech.strip().lower(), accid.strip().lower()
        )
        dRet = ConnPostgreSQL.returnSelectQueryResultAsList(sQuery)
        if dRet['result'] == 'failure':
            return json.dumps({'result': 'failure', 'data': 'The selected customer has zero VMs'})
        else:
            import paramiko as pmk
            from datetime import datetime
            remote = pmk.SSHClient()
            remote.set_missing_host_key_policy(pmk.AutoAddPolicy())
            remote.connect("10.227.45.121", username="root", password="@ut0!ntell!@234", port=22)
            stdin, stdout, stderr = remote.exec_command("""/opt/app/VMSummaryReport1.ps1 "{0}" "{1}" "{2}" """.format(
                '::'.join([x for x in dRet['data']['vm_name']]), sdate, edate), get_pty=False, timeout=60*60)
            retCode = stdout.channel.recv_exit_status()
            if retCode == 0:
                filename = "{0}.csv".format(datetime.now().strftime('%d%m%Y%H%M%S'))
                path = "/usr/share/nginx/html/downloads/" + filename
                content = stdout.readlines()
                open(path, 'w').write('\n'.join([x.strip() for x in content]))

                #Update Table
                uQuery = "update report_vmsummary set status=1, link='{0}' where pk_vmsumm_rpt_id={1}".format(
                    'https://{1}/downloads/{0}'.format(filename, dIPFQDN[location]), pid
                )
                dRet = ConnPostgreSQL.returnInsertResult(uQuery)

                return json.dumps(
                    {'result': 'success', 'data': 'https://{1}/downloads/{0}'.format(filename, dIPFQDN[location])})
            else:
                return json.dumps(
                    {'result': 'failure', 'data': 'failed to generate report. Please try after sometimes.'})
    except Exception as e:
        print(str(e))
        # Update Table
        uQuery = "update report_vmsummary set status=1, link='Failed to Generate. Re-initiate.' where pk_vmsumm_rpt_id={1}".format(
            'https://r2d2.nxtgen.com/downloads/{0}'.format(filename), pid
        )
        dRet = ConnPostgreSQL.returnInsertResult(uQuery)
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
    channel.queue_declare(queue='rptvmsumm', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='rptvmsumm', queue='rptvmsumm')
    channel.basic_consume(callback, queue='rptvmsumm', no_ack=True)
    channel.start_consuming()
    # channel.close()
except Exception as e:
    logERROR("Exception: {0}".format(str(e)))
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import json
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
from flask import request
from datetime import datetime as dt
from elasticsearch import Elasticsearch
from datetime import datetime as dt
import pytz
import math
from copy import deepcopy
import services.utils.ConnPostgreSQL as pcon
import requests as req
from services.utils import sessionkeygen
from openpyxl import Workbook
from openpyxl.styles.borders import Border, Side
from openpyxl.styles import Color, PatternFill, Font, Border, Alignment
from services.utils import ConnMQ as mq

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

def getCustomerList(tech):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select trim(customer_name) || '::' || trim(customer_id) as name from tbl_customer where technology_loc='{0}' order by customer_name".format(tech.lower().strip())
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def fetchReport(payload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                tech = payload['technology']
                accid = payload['accountid']
                sdate = dt.strptime(payload['startdate'], '%Y-%m-%d %H:%M').strftime('%y-%m-%d %H:%M')
                edate = dt.strptime(payload['enddate'], '%Y-%m-%d %H:%M').strftime('%y-%m-%d %H:%M')
                user_id = payload['user_id']

                sQuery = "select vm_name from tbl_vms where customer_id=(select customer_id from tbl_customer where lower(trim(technology_loc))='{0}' and lower(trim(customer_id))='{1}')".format(
                    tech.strip().lower(), accid.strip().lower()
                )
                dRet = pcon.returnSelectQueryResultAsList(sQuery)
                if dRet['result'] == 'failure':
                    return json.dumps({'result': 'failure', 'data': 'The selected customer has zero VMs'})

                iQuery = "insert into report_vmsummary(fk_user_id, meta, initiated_time, status, active_yn) values({0}, '{1}', now(), 0, 'Y') RETURNING pk_vmsumm_rpt_id".format(
                    user_id, ("{0}::{1}::{2}::{3}".format(tech, accid, sdate, edate))
                )
                dRet = pcon.returnSelectQueryResultWithCommit(iQuery)
                if dRet['result'] == 'success':
                    payload['pk_id'] = dRet['data'][0]['pk_vmsumm_rpt_id']
                    if tech == 'vmware':
                        mq.send2MQ('rptvmsumm', 'rptvmsumm', 'vmsumm', json.dumps(payload))
                    elif tech == 'kvm':
                        mq.send2MQ('rptkvmvmsumm', 'rptkvmvmsumm', 'kvmvmsumm', json.dumps(payload))
                    return json.dumps({'result': 'success', 'data': 'Report generation initiated'})
                else:
                    return json.dumps({'result': 'failure', 'data': "couldn't accept request. Try after sometimes."})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def loadgrid(user_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select to_char(initiated_time, 'DD-MM-YYYY HH:MI'), meta, link, status from report_vmsummary where active_yn='Y' and fk_user_id={0} order by initiated_time desc".format(user_id)
                dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
                if dRet['result'] == 'success':
                    return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'no data'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def fetchReport1(payload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                tech = payload['technology']
                accid = payload['accountid']
                sdate = dt.strptime(payload['startdate'], '%Y-%m-%d %H:%M').strftime('%y-%m-%d %H:%M')
                edate = dt.strptime(payload['enddate'], '%Y-%m-%d %H:%M').strftime('%y-%m-%d %H:%M')
                sQuery = "select vm_name from tbl_vms where customer_id=(select customer_id from tbl_customer where lower(trim(technology_loc))='{0}' and lower(trim(customer_id))='{1}')".format(
                    tech.strip().lower(), accid.strip().lower()
                )
                dRet = pcon.returnSelectQueryResultAsList(sQuery)
                if dRet['result'] == 'failure':
                    return json.dumps({'result': 'failure', 'data': 'The selected customer has zero VMs'})
                else:
                    import paramiko as pmk
                    from datetime import datetime
                    remote = pmk.SSHClient()
                    remote.set_missing_host_key_policy(pmk.AutoAddPolicy())
                    remote.connect("10.227.45.121", username="root", password="@ut0!ntell!@234", port=22)
                    stdin, stdout, stderr = remote.exec_command("""/opt/app/VMSummaryReport.ps1 "{0}" "{1}" "{2}" """.format('::'.join([x for x in dRet['data']['vm_name']]), sdate, edate), get_pty=False)
                    retCode = stdout.channel.recv_exit_status()
                    if retCode == 0:
                        filename = "{0}.csv".format(datetime.now().strftime('%d%m%Y%H%M%S'))
                        path = "/usr/share/nginx/html/downloads/" + filename
                        content = stdout.readlines()
                        open(path, 'w').write('\n'.join([x.strip() for x in content]))
                        return json.dumps({'result': 'success', 'data': 'https://r2d2.nxtgen.com/downloads/{0}'.format(filename)})
                    else:
                        return json.dumps({'result': 'failure', 'data': 'failed to generate report. Please try after sometimes.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing



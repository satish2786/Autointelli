#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import json
from services.utils import ConnPostgreSQL as conn
import services.utils.decoder as decoder
from services.utils import utils as ut
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import services.utils.ConnMQ as connmq
import pika
from datetime import datetime as dt
import pytz
import re
from services.EAM import reservice as res
from decimal import Decimal
import os
import subprocess
from services.utils import ED_AES256 as aes

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file("/var/log/autointelli/eventreceiver.log")
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return {"result": s, "data": x}

def singleQuoteIssue(value):
    if not type(value) == type(None):
        return value.replace("'", "''").strip()
    else:
        return ""

def s2d(s):
    try:
        return Decimal(s)
    except Exception as e:
        return s

def getCredentials(machine_id):
    try:
        jobQuery = """
        select 
        	am.machine_fqdn, am.ip_address, ad.cred_type, ad.username, ad.password, am.backend_port port 
        from 
        	ai_machine am inner join ai_device_credentials ad on(am.fk_cred_id=ad.cred_id) 
        where 
        	am.machine_id in(select machine_id from marketplace where lower(vendor)='vmware') and am.machine_id={0} and am.active_yn='Y'""".format(
            machine_id
        )
        jobRet = conn.returnSelectQueryResult(jobQuery)
        if jobRet['result'] == 'success':
            cred_type = jobRet['data'][0]['cred_type'].lower()
            payload = {}
            if cred_type == 'https':
                password = aes.decrypt(jobRet['data'][0]['password'].encode(), '@ut0!ntell!'.encode()).decode('utf-8')
                return jobRet['data'][0]['ip_address'], jobRet['data'][0]['username'], password
            elif cred_type == 'pam':

                from services.utils import ConnArcon as pam
                ret = pam.queryPassword(jobRet['data'][0]['ip_address'], jobRet['data'][0]['username'], 'vcenter')
                if ret['result'] == 'success':
                    return jobRet['data'][0]['ip_address'], jobRet['data'][0]['username'], ret['data']
                else:
                    return "", "", ""

            else:
                return "", "", ""
        else:
            return "", "", ""
    except Exception as e:
        return "", "", ""

def processEvent(dPayload):
    """Method: This method is used to filter the events those were mentioned in event filter management"""
    try:
        lAttr = ["vendor", "action", "machine_id", "datacenter", "cluster", "template", "datastore",
                 "network", "hostname", "ip_address", "netmask", "gateway", "domain", "trans_id"]
        lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
        if not 0 in lPayErr:
            try:
                #                 dPayload = {
                # 	"vendor": "VMWare",
                # 	"action": "create",
                # 	"machine_id": 27,
                # 	"datacenter": "SFL-DC",
                # 	"cluster": "Production-Cluster",
                # 	"template": "Oracle_Linux_8.2",
                # 	"datastore": "IBMV7KG2-VMWARE-LUN04",
                # 	"network": "SFL-VM-Network",
                # 	"hostname": "test1",
                # 	"ip_address": "192.168.1.1",
                # 	"netmask": "255.255.255.0",
                # 	"gateway": "192.168.1.10",
                # 	"domain": "d1"
                # }
                if 1 == 1:
                    retcode, stdout, stderr, rawout = "", "", "", ""
                    if dPayload['vendor'].lower() == 'vmware':
                        vCenterIP, vCenterUser, vCenterPwd = getCredentials(dPayload['machine_id'])

                        if vCenterIP != "" and vCenterUser != "" and vCenterPwd != "":
                            if dPayload['template'].lower().__contains__("linux"):
                                print("yes, it is linux distribution...")
                                os.chdir('/usr/local/autointelli/ioengine_iress/ioengine/services/marketplace/vmware')
                                sCmd = """ANSIBLE_STDOUT_CALLBACK=json ansible-playbook ProvisionMachineFromTemplateLinux.yml --extra-vars "datacenter={0} cluster={1} guest_template={2} datastore={3} network={4} guest_hostname={5} guest_ipaddress={6} guest_subnetmask={7} guest_gatewayip={8} vcenter_ipaddress={9} vcenter_username={10} vcenter_password={11} guest_username={12} guest_password={13}" """.format(
                                    dPayload['datacenter'], dPayload['cluster'], dPayload['template'],
                                    dPayload['datastore'],
                                    dPayload['network'], dPayload['hostname'], dPayload['ip_address'],
                                    dPayload['netmask'],
                                    dPayload['gateway'],
                                    vCenterIP, vCenterUser, vCenterPwd, 'root', 'Admin@123')
                                print(sCmd)
                            else:
                                os.chdir('/usr/local/autointelli/ioengine_iress/ioengine/services/marketplace/vmware')
                                sCmd = """ANSIBLE_STDOUT_CALLBACK=json ansible-playbook ProvisionMachineFromTemplateWindows.yml --extra-vars "datacenter={0} cluster={1} guest_template={2} datastore={3} network={4} guest_hostname={5} guest_ipaddress={6} guest_subnetmask={7} guest_gatewayip={8} vcenter_ipaddress={9} vcenter_username={10} vcenter_password={11} guest_username={12} guest_password={13} domain={14}" """.format(
                                    dPayload['datacenter'], dPayload['cluster'], dPayload['template'],
                                    dPayload['datastore'],
                                    dPayload['network'], dPayload['hostname'], dPayload['ip_address'],
                                    dPayload['netmask'],
                                    dPayload['gateway'],
                                    vCenterIP, vCenterUser, vCenterPwd, 'administrator', 'Admin@123',
                                    dPayload['domain'])
                                print(sCmd)

                                # sCmd = """ANSIBLE_STDOUT_CALLBACK=json ansible-playbook PushPreRequisities.yml --extra-vars "datacenter={0} guest_hostname={1} guest_ipaddress={2} vcenter_ipaddress={3} vcenter_username={4} vcenter_password={5} guest_username={6} guest_password={7}" """.format(
                                #     dPayload['datacenter'], dPayload['hostname'], dPayload['ip_address'],
                                #     vCenterIP, vCenterUser, vCenterPwd, 'administrator', 'Admin@123')
                                # print(sCmd)
                                # outP = check_output(sCmd, shell=True)
                                # print(outP)

                            outP = ""
                            try:
                                outP = subprocess.check_output(sCmd, shell=True)
                            except subprocess.CalledProcessError as e:
                                outP = e.output
                            if type(outP) == type(b''):
                                outP = outP.decode()
                            outP = outP[outP.find('{'):]
                            rawout = {"raw": outP}
                            try:
                                outP = json.loads(outP)
                                finalout = {}
                                retcode = "0"
                                finalout['duration'] = outP['plays'][0]['play']['duration']
                                finalout['stats'] = outP['stats']['localhost']
                                outs = []
                                for eP in outP['plays']:
                                    for eT in eP['tasks']:
                                        status, msg = "pass", ""
                                        if 'failed' in eT['hosts']['localhost']:
                                            if eT['hosts']['localhost']['failed']:
                                                status = "fail"
                                                msg = eT['hosts']['localhost']['msg']
                                        outs.append([eT['task']['name'], status, msg])
                                stdout = {"out": outs}
                            except Exception as e:
                                retcode = "1"
                                stderr = {"out": outP}

                        else:
                            retcode = "1"
                            stdout = "vCenter credentials missing"
                            stderr = ""
                            rawout = ""

                        iQuery = "update vmware_result set rawout='{0}', retcode='{1}', stdout='{2}', stderr='{3}' where pk_r_id={4}".format(
                            json.dumps(rawout), retcode, json.dumps(stdout), json.dumps(stderr), dPayload['trans_id']
                        )

                        dRet = conn.returnInsertResult(iQuery)

                return json.dumps({'result': 'success', 'data': 'VM provisioned successfully.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Event KB: Either attributes are missing or attribute's values are empty: {0}".format(dPayload))
    except Exception as e:
        return logAndRet("failure", "unable to apply KB, payload:{0} with Exception: {1}".format(dPayload, str(e)))

def callback(ch, method, properties, body):
    dPayload = json.loads(body.decode('utf-8'))
    print("Incoming events: {0}".format(dPayload))
    retJSON = processEvent(dPayload)
    print(retJSON)


try:
    # Get the details of MQ
    sIP, sUserName, sPassword = "", "", ""
    sQuery = "select configip ip, username, password from configuration where configname='MQ'"
    dRet = conn.returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        sIP = dRet["data"][0]["ip"]
        sUserName = dRet["data"][0]["username"]
        sPassword = decoder.decode("auto!ntell!", dRet["data"][0]["password"])
    else:
        logERROR("unable to fetch information from configuration table")
        CERROR("unable to fetch information from configuration table")

    # declare credentials
    credentials = pika.PlainCredentials(sUserName, sPassword)
    # open connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=sIP, credentials=credentials, virtual_host='autointelli'))
    # create channel
    channel = connection.channel()
    # select queue
    channel.queue_declare(queue='vmwareprovision', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='marketplace', queue='vmwareprovision')
    channel.basic_consume(callback, queue='vmwareprovision', no_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Worker failed. Reason:" + str(e))
    CERROR("Worker failed. Reason:" + str(e))

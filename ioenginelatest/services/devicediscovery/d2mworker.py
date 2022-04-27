import json
from services.utils import ConnPostgreSQL as conn
import services.utils.decoder as decoder
from services.devicediscovery import devicediscovery as dd
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import services.utils.ConnMQ as connmq

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def processEvent(dPayload):
    """Method: accepts the the event from external monitoring system"""
    try:
        # dPayload = {"data": [{"ip_address": "172.16.1.106", "operating_system": "Linux", "fk_cred_id": 1}]}
        if len(dPayload['data']) > 0:
            ip = dPayload['data'][0]['ip_address']
            os = dPayload['data'][0]['operating_system']
            cid = dPayload['data'][0]['fk_cred_id']
            backend, remote, remoteJS = 0, 0, {}
            sQuery = 'select * from ai_device_credentials where cred_id={0}'.format(cid)
            dRet = conn.returnSelectQueryResult(sQuery)
            if dRet['result'] == 'success':
                pay = dRet['data'][0]
                iFinalQuery, iMQuery = "", "insert into ai_machine(machine_fqdn, ip_address, platform, remediate, fk_cred_id, console_port, backend_port, active_yn, osname) values('{0}', '{1}', '{2}', '{3}', {4}, {5}, {6}, 'Y', '{7}')"
                if pay['cred_type'].upper() == 'WINRM':
                    backend, remote = 5985, 3389
                    iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, 'Server 2016 Standard')
                    remoteJS.update({i: pay[i] for i in ['cred_name', 'cred_type', 'username', 'password'] if i in pay})
                elif pay['cred_type'].upper() == 'HTTP':
                    backend, remote = 80, 80
                    iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, 'web')
                    remoteJS.update({i: pay[i] for i in ['cred_name', 'cred_type', 'username', 'password'] if i in pay})
                elif pay['cred_type'].upper() == 'HTTPS':
                    backend, remote = 443, 443
                    iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, 'web')
                    remoteJS.update({i: pay[i] for i in ['cred_name', 'cred_type', 'username', 'password'] if i in pay})
                elif pay['cred_type'].upper() == 'SSH':
                    backend, remote = 22, 22
                    iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, 'CentOS')
                    remoteJS.update({i: pay[i] for i in ['cred_name', 'cred_type', 'username', 'password', 'sudo_yn', 'enable_yn', 'enable_password'] if i in pay})
                elif pay['cred_type'].upper() == 'SSH KEY':
                    backend, remote = 22, 22
                    iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, 'CentOS')
                    remoteJS.update({i: pay[i] for i in ['cred_name', 'cred_type', 'username', 'sudo_yn', 'key', 'passphrase'] if i in pay})
                elif pay['cred_type'].upper() == 'SNMP':
                    backend, remote = 161, 161
                    iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, '')
                    if pay['version'] == 'v1':
                        remoteJS.update({i: pay[i] for i in ['cred_name', 'cred_type', 'version', 'community_string'] if i in pay})
                    else:
                        remoteJS.update({i: pay[i] for i in ['cred_name', 'cred_type', 'version', 'username', 'password'] if i in pay})
                elif pay['cred_type'].upper() == 'PAM':
                    if os.lower().__contains__('linux'):
                        backend, remote = 22, 22
                        iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, 'CentOS')
                    elif os.lower().__contains__('window'):
                        backend, remote = 5985, 3389  # Bug
                        iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, 'Server 2016 Standard')
                    else:
                        backend, remote = 22, 22
                        iFinalQuery += iMQuery.format(ip, ip, os, 'N', cid, remote, backend, '')
                    remoteJS.update({i: pay[i] for i in ['cred_name', 'cred_type', 'username'] if i in pay})
                remoteJS.update({'console_port': remote, 'backend_port': backend})
                remoteJS['hostname'] = ip
                remoteJS['platform'] = os
                rRet = connmq.send2MQ(pQueue='remoting', pExchange='automationengine', pRoutingKey='remoting',
                                      pData=json.dumps(remoteJS))
                print("Final JSON to remoting: {0}, {1}".format(remoteJS, rRet))
                print("Final Query: {0}".format(iFinalQuery))
                finalRet = conn.returnInsertResult(iFinalQuery)
                if finalRet['result'] == 'success':
                    iDQuery = "delete from ai_device_discovery where ip_address='{0}'".format(ip)
                    dDRet = conn.returnInsertResult(iDQuery)
                    if dDRet['result'] == 'success':
                        return {'result': 'success'}
                    else:
                        return {'result': 'failure'}
                else:
                    return {'result': 'failure'}
            else:
                return {'result': 'failure'}
        else:
            return {'result': 'failure'}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {'result': 'failure'}

def callback(ch, method, properties, body):
    payload = json.loads(body.decode('utf-8'))
    print(payload)
    retJson = processEvent(payload)
    logINFO("Discovery Call Back:{0}".format(retJson))
    if retJson["result"] == "success":
        print('Success')
    else:
        print('Failed')

import pika
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
        print("unable to fetch information from configuration table")

    # declare credentials
    credentials = pika.PlainCredentials(sUserName, sPassword)
    # open connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=sIP, credentials=credentials, virtual_host='autointelli'))
    # create channel
    channel = connection.channel()
    # select queue
    channel.queue_declare(queue='d2m', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='automationengine', queue='d2m')
    channel.basic_consume(callback, queue='d2m', no_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Exception: {0}".format(str(e)))

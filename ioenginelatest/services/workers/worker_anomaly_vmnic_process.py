from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import requests as req
import json
import time
import sys

# Console prints
lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

# Logging
logObj = None
try:
    cfgData = json.load(open('/etc/autointelli/autointelli.conf', "r"))
    logObj = create_log_file(cfgData['log']['anomaly'])
    if not logObj:
        CERROR("Not able to create logfile")
        exit(0)
except Exception as e:
    CERROR("Not able to create logfile")
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

# Global vars
sURL = "http://10.227.45.113:7272/api/V1/anomaly"
sHeader = {"Content-Type": "application/json"}

def processEvent(payload):
    """Method: accepts the the event from external monitoring system"""
    try:
        if 'NIC' in payload['esxivm']:
            for i in ['rx', 'tx']:
                an_process = {
                    "Timestamp": payload['@timestamp']['GMT'],  # "2020-07-10T11:58:07.709831Z",  # @timestamp.GMT
                    "metrics": payload['esxivm']['NIC']['Network adapter 1']['nic_{0}_percentage'.format(i)],
                # 0,  # esxivm.NIC.Network adapter 1.nic_rx_percentage value
                    "index_name": 'vmware_esxivm_metric',  # "vmware_esxivm_metric",  # index name
                    "host_key": 'esxivm.Name',  # "esxivm.Name",  #
                    "metric_name": 'esxivm.NIC.Network adapter 1.nic_{0}_percentage'.format(i),  # based on data
                    "host_name": payload['esxivm']['Name'],
                    "id": payload['_id']}
                print("Payload sent to ML function: {0}".format(json.dumps(an_process)))
                ret = req.post(url=sURL, data=json.dumps(an_process), headers=sHeader)
                if ret.status_code == 200 or ret.status_code == 201:
                    logINFO("{0} {1} {2}".format(sURL, ret.status_code, ret.content))
                    return {"result": "success"}
                else:
                    logERROR("{0} {1} {2}".format(sURL, ret.status_code, ret.content))
                    return {"result": "failure"}
        else:
            logERROR("Invalid payload to process NIC Utilization Anomlay detection")
    except Exception as e:
        logERROR("Call Anomaly API Exception: {0}".format(str(e)))

def callback(ch, method, properties, body):
    try:
        s = time.time()
        payload = json.loads(body.decode('utf-8'))
        print(payload)
        retJson = processEvent(payload)
        print("TimeTaken: {0}".format(time.time() - s))
        logINFO("Total Time: {0}".format(time.time() - s))
        if retJson["result"] == "success":
            print('Success')
        else:
            print('Failed')
    except Exception as e:
        logERROR("Call Back function: {0}".format(str(e)))


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
    channel.queue_declare(queue='esxivmMetrics', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='monitoring', queue='esxivmMetrics')
    channel.basic_consume(callback, queue='esxivmMetrics', no_ack=True)
    channel.start_consuming()
    #channel.close()
except Exception as e:
    logERROR("Worker is unable to start because of Exception: {0}".format(str(e)))
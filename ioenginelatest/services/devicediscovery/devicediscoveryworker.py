import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.devicediscovery import devicediscovery as dd
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def processEvent(payload):
    """Method: accepts the the event from external monitoring system"""
    try:
        return dd.startDiscovery(payload)
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

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
    channel.queue_declare(queue='discovery_socket', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='automation', queue='discovery_socket')
    channel.basic_consume(callback, queue='discovery_socket', no_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Exception: {0}".format(str(e)))

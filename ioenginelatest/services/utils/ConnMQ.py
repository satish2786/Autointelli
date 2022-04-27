import services.utils.ConnPostgreSQL as dbconn
import pika
import services.utils.decoder as decoder
import json
from services.utils.ConnLog import create_log_file

import services.utils.LFColors as lfc
lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def send2MQ(pQueue, pExchange, pRoutingKey, pData):
    try:
        # Get the details of MQ
        sIP, sUserName, sPassword = "", "", ""
        sQuery = "select configip ip, username, password from configuration where configname='MQ'"
        dRet = dbconn.returnSelectQueryResult(sQuery)
        if dRet["result"] == "success":
            sIP = dRet["data"][0]["ip"]
            sUserName = dRet["data"][0]["username"]
            sPassword = decoder.decode("auto!ntell!", dRet["data"][0]["password"])
        else:
            return json.dumps({"result": "failure", "data": "unable to fetch information from configuration table"})

        # Declare credentials
        cred = pika.PlainCredentials(sUserName, sPassword)
        # Create Connection
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=sIP, credentials=cred, virtual_host='autointelli'))
        # Create Channel
        channel = conn.channel()
        # decalre queue
        channel.queue_declare(queue=pQueue, durable=True)
        # publish data to the queue
        channel.basic_publish(exchange=pExchange, routing_key=pRoutingKey, body=pData)
        #print('Pushed Data to ESB')
        # close the connection
        conn.close()
        return {'result': 'success', 'data': 'Successfully pushed data to ESB'}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {'result': 'failure', 'data': str(e)}

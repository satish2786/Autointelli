#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import pika
from services.utils.ConnPostgreSQL import returnSelectQueryResultAsList

root = "/evm/api1.0"
app = Flask(__name__)

@app.route(root + "/endpoints/eventreceiver", methods = ["POST"])
def eventReceiver():
    """Method: accepts the the event from external monitoring system"""
    try:
        dPayload = request.get_json()
        if dPayload is not None:
            lAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source"]
            lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
            # check for payload is valid or not
            if not 0 in lPayErr:
                # Get the details of MQ

                # Declare credentials
                cred = pika.PlainCredentials('autointelli', 'autointelli')
                # Create Connection
                conn = pika.BlockingConnection(
                    pika.ConnectionParameters(host='192.168.1.100', credentials=cred, virtual_host='autointelli'))
                # Create Channel
                channel = conn.channel()
                # decalre queue
                channel.queue_declare(queue='incoming_events', durable=True)
                # publish data to the queue
                channel.basic_publish(exchange='EVM', routing_key='incoming_events', body=json.dumps(dPayload))
                print('[x] sent hello world')
                # close the connection
                conn.close()
                return json.dumps({"result": "success"})
            else:
                return json.dumps({"result": "failure"})
        else:
            return json.dumps({"result": "failure"})
    except Exception as e:
        return json.dumps({"result": "failure"})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5006, debug=True)
        CORS(app)
    except Exception as e:
        pass
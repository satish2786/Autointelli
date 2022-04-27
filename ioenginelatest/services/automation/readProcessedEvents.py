import sys
import pika
from automationBOTCeleryWorker import autodiagnose
import json


# --> Need this section to be changed from DB <---
configip='10.227.45.114'
configusername='autointelli'
configpassword='autointelli'
vhost='autointelli'

credentials = pika.PlainCredentials(configusername,configpassword)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=configip,credentials=credentials,virtual_host=vhost))
channel = connection.channel()

def callback(ch, method, properties, body):
  try:
    body = body.decode('utf-8')
    data = json.loads(body)
    task = autodiagnose.delay(data)
    ch.basic_ack(delivery_tag = method.delivery_tag)
  except Exception as e:
    print(str(e))
    ch.basic_ack(delivery_tag = method.delivery_tag)


queue_name = "processevents"
binding_key = "automation.processevents"
channel.queue_bind(exchange='automationengine', queue=queue_name, routing_key=binding_key)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=False)
channel.start_consuming()

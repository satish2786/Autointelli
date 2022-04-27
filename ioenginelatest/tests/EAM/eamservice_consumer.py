import requests
from datetime import datetime
import json
#http://localhost:9763/endpoints/<event_receiver_name>

URL = "http://127.0.0.1:5002/evm/api1.0/endpoints/eventreceiver"
js = {"content-type" : "application/json"}
current = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
print(current)
for i in range(1,100):
    payload = {
	"ci_name": "bkp-02",
	"component": "CPU",
	"description": "CPU utilization is high",
	"notes": "CPU utilization is Critical. Used : 96%",
	"severity": "critical",
	"event_created_time": "1527819671",
	"source": "NAGIOS"
}
    r = ""
    try:
        r = requests.post(url=URL, data=json, json=json.dumps(js))
    except Exception as e:
        print(str(e))
    if r.status_code == 200:
        print(i)
        print(payload)
        print("------------------------------")
current = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
print(current)

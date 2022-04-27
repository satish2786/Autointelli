#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import json
import requests as req
from services.utils import validator_many

api_key = "yxFPcKccNwciD71nHcY"
domain = "redingtoncloud"
password = "AHmcu#33hFd[ZRG["

def FDCreateTicket(dPayload):
    try:
        # Validate Payload
        lHeaders = ['subject', 'description', 'type']
        lMandate = ['subject', 'description', 'type']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            headers = {'Content-Type': 'application/json'}
            ticket = {
                'subject': dPayload['subject'],
                'description': dPayload['description'],
                'email': 'dinesh@autointelli.com',
                'priority': 3,
                'status': 2,
                'cc_emails': ['dinesh@autointelli.com'],

                'custom_fields': {
                    "cf_partner_name": "autointelli",
                    "start_date": "2020-02-01",
                    "end_date": "2020-02-02"
                },
                'type': dPayload['type']
            }
            r = req.post("https://" + domain + ".freshdesk.com/api/v2/tickets", auth=(api_key, password), headers=headers, data=json.dumps(ticket))
            if r.status_code == 201:
                out = r.content
                print("Ticket created successfully, the response is given below:")
                print(r.content)
                print("Location Header : ")
                print(r.headers['Location'])
                out = out.decode('utf-8')
                out = json.loads(out)
                return {"TID": out["id"], "Status": True}
            else:
                print("Failed to create ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response["errors"])
                print("x-request-id : " + r.headers['x-request-id'])
                print("Status Code : " + str(r.status_code))
                return {"Message": "Error creating ticket", "Status": False}

    except Exception as e:
        return {"result": "failure", "data": str(e)}

#Open	2
#Pending	3
#Resolved	4
#Closed	5
def FDUpdateTicket(dPayload):
    try:
        lHeaders = ['ticket_id', 'status']
        lMandate = ['ticket_id', 'status']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            headers = {'Content-Type': 'application/json'}
            ticket = {'status' : dPayload['status']}
            r = req.put("https://" + domain + ".freshdesk.com/api/v2/tickets/" + str(dPayload['ticket_id']),
                             auth=(api_key, password), headers=headers, data=json.dumps(ticket))
            if r.status_code == 200:
                print("Ticket updated successfully, the response is given below" + r.content.decode('utf-8'))
                return {"Message": "Status changed to In Progress", "Status": True}
            else:
                print("Failed to update ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response["errors"])

                print("x-request-id : " + r.headers['x-request-id'])
                print("Status Code : " + r.status_code)
                return {"Message": "Error updating ticket", "Status": True}
    except Exception as e:
        return {"result": "failure", "data": str(e)}

def FDUpdateWorkLog(dPayload):
    try:
        lHeaders = ['ticket_id', 'description']
        lMandate = ['ticket_id', 'description']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            headers = {'Content-Type': 'application/json'}
            ticket = {'description': dPayload['description']} #, 'description_text': dPayload['description']}
            r = req.put("https://" + domain + ".freshdesk.com/api/v2/tickets/" + dPayload['ticket_id'],
                        auth=(api_key, password), headers=headers, data=json.dumps(ticket))
            if r.status_code == 200:
                print("Ticket updated successfully, the response is given below" + r.content.decode('utf-8'))
                return {"Message": "WorkLog has been added", "Status": True}
            else:
                print("Failed to update ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response["errors"])

                print("x-request-id : " + r.headers['x-request-id'])
                print("Status Code : " + r.status_code)
                return {"Message": "Error adding WorkLog", "Status": True}
    except Exception as e:
        return {"result": "failure", "data": str(e)}

def FDMoveTicket(dPayload):
    try:
        lHeaders = ['ticket_id', 'group']
        lMandate = ['ticket_id', 'group']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            headers = {'Content-Type': 'application/json'}
            ticket = {'description': 'moved to common group {0}'.format(dPayload['group'])} #, 'description_text': 'moved to common group {0}'.format(dPayload['group'])}
            r = req.put("https://" + domain + ".freshdesk.com/api/v2/tickets/" + dPayload['ticket_id'],
                        auth=(api_key, password), headers=headers, data=json.dumps(ticket))
            if r.status_code == 200:
                print("Ticket updated successfully, the response is given below" + r.content.decode('utf-8'))
                return {"Message": "Moved to common group", "Status": True}
            else:
                print("Failed to update ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response["errors"])

                print("x-request-id : " + r.headers['x-request-id'])
                print("Status Code : " + r.status_code)
                return {"Message": "Failed moving to common group", "Status": True}
    except Exception as e:
        return {"result": "failure", "data": str(e)}



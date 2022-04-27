#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import json
import requests as req
from services.utils import validator_many
from services.utils import aitime
from services.utils import ConnPostgreSQL as conn

sBaseURL = "https://mycloud.nxtgen.com/api/index.php/autoticket"
username = "api"
password = "api@dmin2012"

def NxtGenCreateTicket(dPayload):
    try:
        # Validate Payload
        #lHeaders = ['account_id', 'vmid', 'type', 'subject', 'description', 'location_id', 'service_id']
        #lMandate = ['account_id', 'vmid', 'type', 'subject', 'description', 'location_id', 'service_id']
        lHeaders = ['Subject', 'Description', 'Type']
        lMandate = ['Subject', 'Description', 'Type']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            headers = {'Content-Type': 'application/json'}
            ticket = {
                'subject': dPayload['Subject'],
                'description': dPayload['Description'],
                'type': dPayload['Type'],
                'account_id': 'ACCT0010893',
                'vmid': 0,
                'location_id': 0,
                'service_id': 134
            }
            r = req.post(sBaseURL, auth=(username, password), headers=headers, data=json.dumps(ticket))
            if r.status_code == 200:
                out = r.content
                print("Ticket created successfully, the response is given below:")
                print(r.content)
                out = out.decode('utf-8')
                out = json.loads(out)
                #return {"TID": out[1]["ticket_number"], "Status": True}
                # make entry - ai_ticket_details
                sTicketID = out[1]["ticket_number"]
                iAlertID = int(dPayload['Alert_id'].strip('AL'))
                iTktID = sTicketID
                dEpoch = aitime.getcurrentutcepoch()
                sQuery = "insert into ai_ticket_details(fk_alert_id, ticket_no, ticket_status, created_date) values(%d,'%s','Open',%d)" % (
                iAlertID, iTktID, dEpoch)
                iRet = conn.returnInsertResult(sQuery)
                return json.dumps({'result': 'success', 'data': {'ticket_id': sTicketID}})
            else:
                print("Failed to create ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response)
                print("Status Code : " + str(r.status_code))
                #return {"Message": "Error creating ticket", "Status": False}
                return json.dumps({'result': 'failure', 'data': 'Failed to create ticket'})
    except Exception as e:
        return json.dumps({"result": "failure", "data": str(e)})

#Open	2
#Pending	3
#Resolved	4
#Closed	5

def NxtGenUpdateWorkLog(dPayload):
    try:
        lHeaders = ['Ticket ID', 'Description']
        lMandate = ['Ticket ID', 'Description']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            headers = {'Content-Type': 'application/json'}
            ticket = {
                'account_id': 'ACCT0010893',
                'ticket_number': dPayload['Ticket ID'],
                'ticket_state': 'open',
                'message': dPayload['Description']
            }
            r = req.post(sBaseURL + "/add_comments", auth=(username, password), headers=headers, data=json.dumps(ticket))
            if r.status_code == 200:
                print("Ticket updated successfully, the response is given below" + r.content.decode('utf-8'))
                #return {"Message": "WorkLog has been added", "Status": True}
                return json.dumps(
                    {'result': 'success', 'data': 'Worklog Added for Ticket {0}'.format(str(dPayload['Ticket ID']))})
            else:
                print("Failed to update ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response)
                print("Status Code : " + r.status_code)
                #return {"Message": "Error adding WorkLog", "Status": True}
                return json.dumps({'result': 'failure',
                                   'data': 'Failed to add worklog for Ticket {0}'.format(str(dPayload['Ticket ID']))})
    except Exception as e:
        return json.dumps({"result": "failure", "data": str(e)})

# payload = {'subject': 'Test ticket created by autointelli vendor', 'description': 'Test ticket created by autointelli vendor', 'type': 'vmware'}
# out = NxtGenCreateTicket(payload)
# ticket_id = out['TID']
# ticket_id = "CS049145"
# payload = {'ticket_id': ticket_id, 'description': 'Test ticket update by autointelli vendor'}
# up = NxtGenUpdateWorkLog(payload)
# print(up)


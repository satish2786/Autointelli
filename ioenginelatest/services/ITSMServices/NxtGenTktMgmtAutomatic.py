#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import json
import requests as req
from services.utils import validator_many
import binascii
import os

sBaseURL = "https://mycloud.nxtgen.com/api/index.php/autoticket"
username = "api"
password = "api@dmin2012"

def NxtGenCreateTicket(dPayload):
    try:
        def encode_multipart_formdata(fields):
          boundary = binascii.hexlify(os.urandom(16)).decode('ascii')
          body = (
              "".join("--%s\r\n"
                      "Content-Disposition: form-data; name=\"%s\"\r\n"
                      "\r\n"
                      "%s\r\n" % (boundary, field, value)
                      for field, value in fields.items()) +
              "--%s--\r\n" % boundary
          )
          content_type = "multipart/form-data; boundary=%s" % boundary
          return body, content_type
        # Validate Payload
        lHeaders = ['customerid', 'subject', 'description', 'type']
        lMandate = ['customerid', 'subject', 'description', 'type']
        if dPayload['customerid'].__contains__('NxtGen Mgmt'):
            dPayload['customerid'] = 'ACCT0010893'
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):

            ticket = {
                'subject': dPayload['subject'],
                'description': dPayload['description'],
                'type': dPayload['type'],
                'account_id': dPayload['customerid'],
                #'account_id': 'ACCT0010893',
                #'account_id': 'ACCT1000001',
                'vmid': 0,
                'location_id': 0,
                'service_id': 134
            }
            request_data = encode_multipart_formdata(ticket)
            print(request_data)
            headers = {'Content-Type': request_data[1]}
            r = req.post(sBaseURL, auth=(username, password), headers=headers, data=request_data[0])
            print(r.status_code)
            if r.status_code == 200:
                out = r.content
                print("Ticket created successfully, the response is given below:")
                print(r.content)
                out = out.decode('utf-8')
                out = json.loads(out)
                return {"TID": out[1]["ticket_number"], "Status": True}
            else:
                print("Failed to create ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response)
                print("Status Code : " + str(r.status_code))
                return {"Message": "Error creating ticket", "Status": False}
    except Exception as e:
        print(str(e))
        return {"Message": "Error creating ticket", "Status": False}

def NxtGenCreateTicket1(dPayload):
    try:
        # Validate Payload
        lHeaders = ['subject', 'description', 'type']
        lMandate = ['subject', 'description', 'type']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            headers = {'Content-Type': 'application/json'}
            ticket = {
                'subject': dPayload['subject'],
                'description': dPayload['description'],
                'type': dPayload['type'],
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
                return {"TID": out[1]["ticket_number"], "Status": True}
            else:
                print("Failed to create ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response)
                print("Status Code : " + str(r.status_code))
                return {"Message": "Error creating ticket", "Status": False}
    except Exception as e:
        return {"Message": "Error creating ticket", "Status": False}

#Open	2
#Pending	3
#Resolved	4
#Closed	5

def NxtGenUpdateWorkLog(dPayload):
    try:
        lHeaders = ['ticket_id', 'description']
        lMandate = ['ticket_id', 'description']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            headers = {'Content-Type': 'application/json'}
            ticket = {
                'account_id': 'ACCT0010893',
                'ticket_number': dPayload['ticket_id'],
                'ticket_state': 'open',
                'message': dPayload['description']
            }
            r = req.post(sBaseURL + "/add_comments", auth=(username, password), headers=headers, data=json.dumps(ticket))
            if r.status_code == 200:
                print("Ticket updated successfully, the response is given below" + r.content.decode('utf-8'))
                return {"Message": "WorkLog has been added", "Status": True}
            else:
                print("Failed to update ticket, errors are displayed below,")
                response = json.loads(r.content)
                print(response)
                print("Status Code : " + r.status_code)
                return {"Message": "Error adding WorkLog", "Status": True}
    except Exception as e:
        return {"Message": "Error adding WorkLog", "Status": True}


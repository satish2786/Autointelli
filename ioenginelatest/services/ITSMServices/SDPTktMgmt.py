#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import request
import json
from services.utils import ConnPostgreSQL as conn
from services.utils import sessionkeygen as sess
import requests as req
from services.utils import validator_many
import datetime
import urllib
from services.utils import aitime
from services.ITSMServices import NxtGenTktMgmt as nxtgen

def lam_api_key_missing():
    return json.dumps({"result": "failure", "data": "api-key missing"})

def lam_api_key_invalid():
    return json.dumps({"result": "failure", "data": "invalid api-key"})

lam_api_key_missing = lam_api_key_missing()
lam_api_key_invalid = lam_api_key_invalid()

def getTimeZone(sKey):
    dRet = sess.getUserDetailsBasedWithSessionKey(sKey)
    if dRet["result"] == "success":
        return dRet["data"][0]["time_zone"]
    else:
        return "no data"

def chkValidRequest(key):
    sQuery = "select * from tbl_session_keys where session_key='" + key + "' and active_yn='Y'"
    dRet = conn.returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        return True
    else:
        return False

def chkKeyExistsInHeader(key):
    try:
        tmp = request.headers["SESSIONKEY"]
        return True
    except KeyError as e:
        return False
    except Exception as e:
        return False

def fetchITSMSettings():
    # Fetch ITSM settings details
    sSettingsQuery = """
                select 
                     communication_type, ip, port, technician_key, priority, assignment_group_manual, assignment_group_automation, itsm_status, service_category, level, requester, requesttemplate, technician, itsm_wip_status, itsm_res_status 
                from 
                    admin_sdp 
                where 
                    lower(status) = 'enabled'"""
    dRet = conn.returnSelectQueryResult(sSettingsQuery)
    return dRet

def sdpCreateTicket(dPayload):
    try:
        # Validate Payload
        lHeaders = ['Requester', 'Subject', 'Description', 'Priority', 'Group', 'Technician', 'Status', 'Category', 'Sub-Category', 'Alert_id']
        lMandate = ['Requester', 'Subject', 'Description', 'Priority', 'Group', 'Technician', 'Status', 'Category', 'Sub-Category', 'Alert_id']
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            # Fetch ITSM settings details
            dRet = fetchITSMSettings()
            if dRet['result'] == 'success':
                sCommunicationType = dRet['data'][0]['communication_type']
                sIP = dRet['data'][0]['ip']
                sPort = dRet['data'][0]['port']
                sTechnicianKey = dRet['data'][0]['technician_key']
                # Call Ticket creation API
                sURL = "{0}://{1}:{2}/sdpapi/request/".format(sCommunicationType, sIP, sPort)
                dParams = {'TECHNICIAN_KEY': '%s' % (sTechnicianKey),
                           'OPERATION_NAME': 'ADD_REQUEST',
                           'format': 'json',
                           'INPUT_DATA': '{"operation": {"details": { "requester": "%s", "subject": "%s", "description": "%s", "priority": "%s", "group": "%s","technician": "%s", "status": "%s", "category": "%s", "subcategory": "%s" } } }' % (
                               dPayload['Requester'],
                               dPayload['Subject'],
                               dPayload['Description'],
                               dPayload['Priority'],
                               dPayload['Group'],
                               dPayload['Technician'],
                               dPayload['Status'],
                               dPayload['Category'],
                               dPayload['Sub-Category'])
                           }
                objRet = req.post(url=sURL, params=dParams)
                if objRet.status_code == 200:
                    dOutput = json.loads(objRet.text)
                    sTicketID = dOutput['operation']['Details']['WORKORDERID']
                    # make entry - ai_ticket_details
                    iAlertID = int(dPayload['Alert_id'].strip('AL'))
                    iTktID = int(sTicketID)
                    dEpoch = aitime.getcurrentutcepoch()
                    sQuery = "insert into ai_ticket_details(fk_alert_id, ticket_no, ticket_status, created_date) values(%d,%d,'Open',%d)" %(iAlertID, iTktID, dEpoch)
                    iRet = conn.returnInsertResult(sQuery)
                    return json.dumps({'result': 'success', 'data': {'ticket_id': sTicketID}})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to create ticket'})
            else:
                return json.dumps({'result': 'failure', 'data': 'Failed to fetch the ITSM settings details'})
        else:
            return json.dumps({'result': 'failure', 'data': 'Payload Error: Either a key is missing or Mandatory item has empty values'})
    except Exception as e:
        return json.dumps({"result": "failure", "data": str(e)})

def sdpChangeStatus(dPayload):
    try:
        # Validate Payload
        lHeaders = ["Ticket ID", "Status"]
        lMandate = ["Ticket ID", "Status"]
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            # Fetch ITSM settings details
            dRet = fetchITSMSettings()
            if dRet['result'] == 'success':
                sCommunicationType = dRet['data'][0]['communication_type']
                sIP = dRet['data'][0]['ip']
                sPort = dRet['data'][0]['port']
                sTechnicianKey = dRet['data'][0]['technician_key']
                # Call Ticket creation API
                sURL = "{0}://{1}:{2}/sdpapi/request/{3}".format(sCommunicationType, sIP, sPort, str(dPayload["Ticket ID"]))
                dParams = {'TECHNICIAN_KEY': '%s' % (sTechnicianKey),
                           'OPERATION_NAME': 'EDIT_REQUEST',
                           'format': 'json',
                           'INPUT_DATA': '{"operation": {"details": { "status": "%s" } } }' % (
                               dPayload['Status'] )
                           }
                objRet = req.post(url=sURL, params=dParams)
                if objRet.status_code == 200:
                    # make entry - ai_ticket_details
                    return json.dumps({'result': 'success', 'data': 'Status of Ticket {0} changed to {1}'.format(str(dPayload['Ticket ID']), dPayload['Status'])})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to update Ticket {0}'.format(str(dPayload['Ticket ID']))})
            else:
                return json.dumps({'result': 'failure', 'data': 'Failed to fetch the ITSM settings details'})
        else:
            return json.dumps({'result': 'failure', 'data': 'Payload Error: Either a key is missing or Mandatory item has empty values'})
    except Exception as e:
        return json.dumps({"result": "failure", "data": str(e)})

def sdpUpdateWorklog(dPayload):
    try:
        # Validate Payload
        lHeaders = ["Ticket ID", "Worklog", "Technician"]
        lMandate = ["Ticket ID", "Worklog", "Technician"]
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            # Fetch ITSM settings details
            dRet = fetchITSMSettings()
            if dRet['result'] == 'success':
                sCommunicationType = dRet['data'][0]['communication_type']
                sIP = dRet['data'][0]['ip']
                sPort = dRet['data'][0]['port']
                sTechnicianKey = dRet['data'][0]['technician_key']
                # Call Ticket creation API
                now = datetime.datetime.now()
                dtStartTime = now.strftime("%d %b %Y, %H:%M:%S")
                endtime = now + datetime.timedelta(seconds=3)
                dtEndTime = endtime.strftime("%d %b %Y, %H:%M:%S")
                sURL = "{0}://{1}:{2}/sdpapi/request/{3}/worklogs".format(sCommunicationType, sIP, sPort, str(dPayload["Ticket ID"]))
                dParams = {'TECHNICIAN_KEY': '%s' % (sTechnicianKey),
                           'OPERATION_NAME': 'ADD_WORKLOG',
                           'format': 'json',
                           'INPUT_DATA': '{"operation": {"details": { "worklogs": { "worklog": { "description": "%s","technician": "%s","starttime": "%s","endtime": "%s" } } } } }' % (
                               dPayload['Worklog'],
                               dPayload['Technician'],
                               dtStartTime,
                               dtEndTime)
                           }
                objRet = req.post(url=sURL, params=dParams)
                if objRet.status_code == 200:
                    # make entry - ai_ticket_details
                    return json.dumps({'result': 'success', 'data': 'Worklog Added for Ticket {0}'.format(str(dPayload['Ticket ID']))})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to add worklog for Ticket {0}'.format(str(dPayload['Ticket ID']))})
            else:
                return json.dumps({'result': 'failure', 'data': 'Failed to fetch the ITSM settings details'})
        else:
            return json.dumps({'result': 'failure', 'data': 'Payload Error: Either a key is missing or Mandatory item has empty values'})
    except Exception as e:
        return json.dumps({"result": "failure", "data": str(e)})

def sdpResolveTicket(dPayload):
    try:
        # Validate Payload
        lHeaders = ["Ticket ID", "Resolution Comment"]
        lMandate = ["Ticket ID", "Resolution Comment"]
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            # Fetch ITSM settings details
            dRet = fetchITSMSettings()
            if dRet['result'] == 'success':
                sCommunicationType = dRet['data'][0]['communication_type']
                sIP = dRet['data'][0]['ip']
                sPort = dRet['data'][0]['port']
                sTechnicianKey = dRet['data'][0]['technician_key']
                # Call Ticket creation API
                sURL = "{0}://{1}:{2}/sdpapi/request/{3}/resolution".format(sCommunicationType, sIP, sPort, str(dPayload["Ticket ID"]))
                dParams = {'TECHNICIAN_KEY': '%s' % (sTechnicianKey),
                           'OPERATION_NAME': 'ADD_RESOLUTION',
                           'format': 'json',
                           'INPUT_DATA': '{"operation": {"details": { "resolution": { "resolutiontext": "%s" } } } }' % (
                               dPayload['Resolution Comment'])
                           }
                dParams = urllib.parse.urlencode(dParams)
                objRet = req.post(url=sURL, params=dParams)
                if objRet.status_code == 200:
                    # make entry - ai_ticket_details
                    return json.dumps({'result': 'success', 'data': 'Resolution Added for Ticket {0}'.format(str(dPayload['Ticket ID']))})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to add Resolution for Ticket {0}'.format(str(dPayload['Ticket ID']))})
            else:
                return json.dumps({'result': 'failure', 'data': 'Failed to fetch the ITSM settings details'})
        else:
            return json.dumps({'result': 'failure', 'data': 'Payload Error: Either a key is missing or Mandatory item has empty values'})
    except Exception as e:
        return json.dumps({"result": "failure", "data": str(e)})

def sdpUpdateTicketGroup(dPayload):
    try:
        # Validate Payload
        lHeaders = ["Ticket ID", "Group", "Technician"]
        lMandate = ["Ticket ID", "Group", "Technician"]
        if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=lHeaders, lMandatory=lMandate):
            # Fetch ITSM settings details
            dRet = fetchITSMSettings()
            if dRet['result'] == 'success':
                sCommunicationType = dRet['data'][0]['communication_type']
                sIP = dRet['data'][0]['ip']
                sPort = dRet['data'][0]['port']
                sTechnicianKey = dRet['data'][0]['technician_key']
                # Call Ticket creation API
                sURL = "{0}://{1}:{2}/sdpapi/request/{3}/assign".format(sCommunicationType, sIP, sPort, str(dPayload["Ticket ID"]))
                dHeader = {'TECHNICIAN_KEY': '%s' % (sTechnicianKey), 'Content-Type': 'application/json'}
                dParams = {'INPUT_DATA': '{"request": {"group": { "name": "%s" }, "technician": { "name": %s }  } }' % (
                               dPayload['Group'],
                               dPayload['Technician'])
                           }
                objRet = req.post(url=sURL, params=dParams, headers=dHeader)
                if objRet.status_code == 200:
                    # make entry - ai_ticket_details
                    return json.dumps({'result': 'success', 'data': 'Group Changed for Ticket {0}'.format(str(dPayload['Ticket ID']))})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to change Group for Ticket {0}'.format(str(dPayload['Ticket ID']))})
            else:
                return json.dumps({'result': 'failure', 'data': 'Failed to fetch the ITSM settings details'})
        else:
            return json.dumps({'result': 'failure', 'data': 'Payload Error: Either a key is missing or Mandatory item has empty values'})
    except Exception as e:
        return json.dumps({"result": "failure", "data": str(e)})

def TicketCreation(itsm_name, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            if itsm_name.lower() == 'sdp':
                return sdpCreateTicket(dPayload)
            elif itsm_name.lower() == 'nxtgen':
                return nxtgen.NxtGenCreateTicket(dPayload)
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def ChangeStatus(itsm_name, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            if itsm_name.lower() == 'sdp':
                return sdpChangeStatus(dPayload)
            elif itsm_name.lower() == "nxtgen":
                return {"result": "failure", "data": "under construction"}
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def UpdateWorklog(itsm_name, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            if itsm_name.lower() == 'sdp':
                return sdpUpdateWorklog(dPayload)
            elif itsm_name.lower() == "nxtgen":
                return nxtgen.NxtGenUpdateWorkLog(dPayload)
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def ResolveTicket(itsm_name, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            if itsm_name.lower() == 'sdp':
                return sdpResolveTicket(dPayload)
            elif itsm_name.lower() == "nxtgen":
                return {"result": "failure", "data": "under construction"}
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def UpdateGroup(itsm_name, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            if itsm_name.lower() == 'sdp':
                return sdpUpdateTicketGroup(dPayload)
            elif itsm_name.lower() == "nxtgen":
                return {"result": "failure", "data": "under construction"}
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

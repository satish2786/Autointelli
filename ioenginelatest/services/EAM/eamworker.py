#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import json
from services.utils import ConnPostgreSQL
import services.utils.decoder as decoder
from services.utils import ConnWebSocket as ws
from services.utils import utils as ut
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
import services.utils.ConnMQ as connmq
import pika

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file("/var/log/autointelli/eventreceiver.log")
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return {"result": s, "data": x}

def singleQuoteIssue(value):
    if type(value) != type(None) and type(value) == type(""):
        return value.replace("'", "''").strip()
    else:
        return value

def bOpted4Service(pCustomerID, pVMName):
    try:
        sQuery = "select 'Y' bool from tbl_vms where lower(customer_id) = '{0}' and lower(vm_name) = '{1}' and active_yn='Y'".format(pCustomerID.lower(), pVMName.lower())
        dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
        if dRet["result"] == "success":
            if dRet["data"][0]["bool"] == "Y":
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return False


def insertDroppedNotifications(pCIName, pComp, pDesc, pNotes, pSeverity, pCreatedTime, pSource, pStatus):
    try:
        # Insert Event
        sInsertDroppedEvents = "insert into dropped_event(ci_name, component, description, notes, severity, event_created_time, source, fk_status_id, promote_yn) " \
                               "values('%s', '%s', '%s', '%s', '%s', %d, '%s', %d, '%s') RETURNING pk_dropped_event_id" % (
                                   pCIName, pComp, pDesc, pNotes, pSeverity, pCreatedTime, pSource, pStatus, 'N')
        iRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sInsertDroppedEvents)
        if iRet["result"] == "success":
            # event inserted successfully
            sEventID = iRet["data"][0]["pk_dropped_event_id"]
            return {"result": "success", "data": sEventID}
        elif iRet["result"] == "failure":
            return iRet
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def insertEvent(pCIName, pComp, pDesc, pNotes, pSeverity, pCreatedTime, pSource, pStatus, pCustomerID, pPriority, pMsgUpdateTime, pValue, pCmd):
    try:
        # Insert Event
        sInsertEvent = "insert into event_data(ci_name, component, description, notes, severity, event_created_time, source, fk_status_id, customer_id, priority, value, cmdline, msg_updated_time) " \
                       "values('%s', '%s', '%s', '%s', '%s', %d, '%s', %d, '%s', '%s', '%s', '%s', '%s') RETURNING pk_event_id" % (
                           singleQuoteIssue(pCIName), singleQuoteIssue(pComp), singleQuoteIssue(pDesc), singleQuoteIssue(pNotes), pSeverity, pCreatedTime, pSource, pStatus, pCustomerID, pPriority, singleQuoteIssue(pValue), singleQuoteIssue(pCmd), pMsgUpdateTime)
        iRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sInsertEvent)
        if iRet["result"] == "success":
            # event inserted successfully
            sEventID = iRet["data"][0]["pk_event_id"]
            return {"result": "success", "data": sEventID}
        elif iRet["result"] == "failure":
            return {"result": "failure", "data": 0}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def insertEventIRESS(pCIName, pComp, pDesc, pNotes, pSeverity, pCreatedTime, pSource, pStatus, pCustomerID, pPriority, pMsgUpdateTime, pValue, pCmd,
                     pID, pAssetNumber, pRegion, pAssetState, pVersion, pPackage, pPackVersion, pPackVersionNo, pMsgCreatedTime, pStatusUpdate,
                     pAddProps, pModifiedby):
    try:
        # Insert Event
        sInsertEvent = "insert into event_data(ci_name, component, description, notes, severity, event_created_time, source, fk_status_id, customer_id, priority, value, cmdline, msg_updated_time," \
                       "id, asset_number, region, asset_state, version, package, pac_ver, pac_ver_no, msg_created_time, status_update, additional_props, modified_by) " \
                       "values('%s', '%s', '%s', '%s', '%s', %d, '%s', %d, '%s', '%s', '%s', '%s', '%s', " \
                       "'%s','%s','%s', '%s','%s','%s', '%s','%s','%s', '%s','%s','%s') RETURNING pk_event_id" % (
                           singleQuoteIssue(pCIName), singleQuoteIssue(pComp), singleQuoteIssue(pDesc), singleQuoteIssue(pNotes), pSeverity,
                           pCreatedTime, pSource, pStatus, pCustomerID, pPriority, singleQuoteIssue(pValue), singleQuoteIssue(pCmd), pMsgUpdateTime,
                           pID, pAssetNumber, pRegion, pAssetState, pVersion, pPackage, pPackVersion, pPackVersionNo,
                           pMsgCreatedTime, pStatusUpdate,
                           json.dumps(pAddProps), pModifiedby
        )
        iRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sInsertEvent)
        if iRet["result"] == "success":
            # event inserted successfully
            sEventID = iRet["data"][0]["pk_event_id"]
            return {"result": "success", "data": sEventID}
        elif iRet["result"] == "failure":
            return {"result": "failure", "data": 0}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def insertAlert(pCIName, pComp, pDesc, pNotes, pSeverity, pCreatedTime, pSource, pStatus, pCustomerID, pPriority, pMsgUpdateTime, pValue, pCmd):
    try:
        # Insert Alert
        sInsertAlert = "insert into alert_data(ci_name, component, description, notes, severity, event_created_time, source, fk_status_id, customer_id, priority, value, cmdline, msg_updated_time) " \
                       "values('%s', '%s', '%s', '%s', '%s', %d, '%s', %d, '%s', '%s', '%s', '%s', '%s') RETURNING pk_alert_id" % (
                           singleQuoteIssue(pCIName), singleQuoteIssue(pComp), singleQuoteIssue(pDesc), singleQuoteIssue(pNotes), pSeverity, pCreatedTime, pSource, pStatus, pCustomerID, pPriority, singleQuoteIssue(pValue), singleQuoteIssue(pCmd), pMsgUpdateTime)
        sRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sInsertAlert)
        if sRet["result"] == "success":
            # Alert inserted successfully
            sAlertID = sRet["data"][0]["pk_alert_id"]
            return {"result": "success", "data": sAlertID}
        elif sRet["result"] == "failure":
            return {"result": "failure", "data": 0}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def insertAlertIRESS(pCIName, pComp, pDesc, pNotes, pSeverity, pCreatedTime, pSource, pStatus, pCustomerID, pPriority, pMsgUpdateTime, pValue, pCmd,
                     pID, pAssetNumber, pRegion, pAssetState, pVersion, pPackage, pPackVersion, pPackVersionNo,
                     pMsgCreatedTime, pStatusUpdate,
                     pAddProps, pModifiedby):
    try:
        # Insert Alert
        sInsertAlert = "insert into alert_data(ci_name, component, description, notes, severity, event_created_time, source, fk_status_id, customer_id, priority, value, cmdline, msg_updated_time," \
                       "id, asset_number, region, asset_state, version, package, pac_ver, pac_ver_no, msg_created_time, status_update, additional_props, modified_by) " \
                       "values('%s', '%s', '%s', '%s', '%s', %d, '%s', %d, '%s', '%s', '%s', '%s', '%s', " \
                       "'%s','%s','%s', '%s','%s','%s', '%s','%s','%s', '%s','%s','%s') RETURNING pk_alert_id" % (
                           singleQuoteIssue(pCIName), singleQuoteIssue(pComp), singleQuoteIssue(pDesc), singleQuoteIssue(pNotes), pSeverity,
                           pCreatedTime, pSource, pStatus, pCustomerID, pPriority, singleQuoteIssue(pValue), singleQuoteIssue(pCmd), pMsgUpdateTime,
                           pID, pAssetNumber, pRegion, pAssetState, pVersion, pPackage, pPackVersion, pPackVersionNo,
                           pMsgCreatedTime, pStatusUpdate,
                           json.dumps(pAddProps), pModifiedby
        )
        sRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sInsertAlert)
        if sRet["result"] == "success":
            # Alert inserted successfully
            sAlertID = sRet["data"][0]["pk_alert_id"]
            return {"result": "success", "data": sAlertID}
        elif sRet["result"] == "failure":
            return {"result": "failure", "data": 0}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def insertEAMapping(pEventID, pAlertID):
    try:
        # Insert into EA Mapping
        iEAMap = "insert into event_alert_mapping(fk_event_id, fk_alert_id) values(%d,%d)" % (pEventID, pAlertID)
        iRet = ConnPostgreSQL.returnInsertResult(iEAMap)
        if iRet["result"] == "success":
            return {"result": "success"}
        else:
            return {"result": "failure"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def insertDroppedEventMapping(pDroppedID, pEventID):
    try:
        # Insert Event ID for the corresponding dropped event
        iQuery = "update dropped_event set fk_event_id=" + str(pEventID) + " where pk_dropped_event_id=" + str(
            pDroppedID)
        iRet = ConnPostgreSQL.returnInsertResult(iQuery)
        if iRet["result"] == "success":
            return {"result": "success"}
        else:
            return {"result": "failure"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def chkSuppression(pCI, pComp):
    try:
        # check for any open event with same component and ci_name (suppression)
        sChkSup = "select * from alert_data where lower(ci_name) = '" + pCI.lower().strip() + "' and lower(component) = '" + pComp.lower().strip() + "' and " \
                                                                                                                                                     "fk_status_id in(select pk_ea_status_id from ea_status where stat_description in('open', 'wip', 'pending'))"
        sRetSup = ConnPostgreSQL.returnSelectQueryResult(sChkSup)
        if sRetSup["result"] == "success":
            if len(sRetSup["data"]) == 1:
                return {"result": "success", "data": sRetSup["data"][0]["pk_alert_id"]}
            else:
                return {"result": "failure", "data": "multiple data"}
        elif sRetSup["result"] == "failure":
            return sRetSup
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def chkSuppression3(pCI, pComp, pDesc):
    try:
        # check for any open event with same component and ci_name (suppression)
        # sChkSup = "select * from alert_data where lower(ci_name) = '" + pCI.lower().strip() + "' and lower(component) = '" + pComp.lower().strip() + "' and " \
        #                                                                                                                                              "fk_status_id in(select pk_ea_status_id from ea_status where stat_description in('open', 'wip', 'pending'))"
        sChkSup = "select * from alert_data where lower(ci_name) = '{0}' and lower(component) = '{1}' and lower(description)='{2}' and fk_status_id in(select pk_ea_status_id from ea_status where stat_description in('open', 'wip', 'pending'))".format(
            pCI.lower().strip(), pComp.lower().strip(), pDesc.lower().strip()
        )
        sRetSup = ConnPostgreSQL.returnSelectQueryResult(sChkSup)
        if sRetSup["result"] == "success":
            if len(sRetSup["data"]) == 1:
                return {"result": "success", "data": sRetSup["data"][0]["pk_alert_id"]}
            else:
                return {"result": "failure", "data": "multiple data"}
        elif sRetSup["result"] == "failure":
            return sRetSup
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def updateAlert(pAlertID, pSeverity):
    try:
        # "Handle Clear Event : Close Event and Alert if Severity if 'OK' & Update Alert's Severity if 'other than OK'"
        if pSeverity.lower() == "ok":
            iAlQuery = "update alert_data set fk_status_id=(select pk_ea_status_id from ea_status where active_yn='Y' and stat_description='closed'),severity='OK' where pk_alert_id = " + str(
                pAlertID)
            iEvQuery = "update event_data set fk_status_id=(select pk_ea_status_id from ea_status where active_yn='Y' and stat_description='closed') where pk_event_id in(select fk_event_id from  event_alert_mapping where fk_alert_id=" + str(
                pAlertID) + ")"
            iRetA = ConnPostgreSQL.returnInsertResult(iAlQuery)
            iRetE = ConnPostgreSQL.returnInsertResult(iEvQuery)
            if iRetA["result"] == "success" and iRetE["result"] == "success":
                return {"result": "success"}
            else:
                return {"result": "failure"}
        else:
            iAlQuery = "update alert_data set severity='" + pSeverity + "' where pk_alert_id = " + str(pAlertID)
            iRetA = ConnPostgreSQL.returnInsertResult(iAlQuery)
            if iRetA["result"] == "success":
                return {"result": "success"}
            else:
                return {"result": "failure"}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))

def chkBatchProcessing(iAlertID, eventid, pSeverity):
    try:
        sQuery = "select alert_id, pe_id, batch_payload, sp_flow from batches_policyengine where alert_id={0}".format(iAlertID)
        dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
        if dRet['result'] == 'success':
            if pSeverity.lower().strip() != "ok":
                logINFO("alert:{0}, event:{1} registered for batching".format(iAlertID, eventid))
                pushed2FE = connmq.send2MQ(pQueue='kb_batch_processing', pExchange='EVM',
                                           pRoutingKey='kb_batch_processing',
                                           pData=json.dumps(dRet['data'][0]))
            else:
                logINFO("alert:{0}, event:{1} cleared because of ok signal. removing from batching".format(iAlertID, eventid))
                dQuery = "delete from batches_policyengine where alert_id={0}".format(iAlertID)
                dRet = ConnPostgreSQL.returnInsertResult(dQuery)
    except Exception as e:
        logERROR("alert:{0}, event:{1} register for batching failed with Exception: {0}".format(iAlertID, eventid, str(e)))

def chkRegisterBatchAfterSuppression(iAlertID, eventid):
    try:
        kbQuery = "select count(*) total from alert_data where pk_alert_id={0} and fk_sop_id is not null".format(iAlertID)
        bQuery = "select count(*) total from batches_policyengine where alert_id={0}".format(iAlertID)
        kbRet = ConnPostgreSQL.returnSelectQueryResult(kbQuery)
        bRet = ConnPostgreSQL.returnSelectQueryResult(bQuery)
        if kbRet['result'] == 'success' and bRet['result'] == 'success':
            if kbRet['data'][0]['total'] <= 0 and bRet['data'][0]['total'] <= 0:
                return True
        else:
            return False
    except Exception as e:
        logERROR("alert:{0}, event:{1} register for batching failed with Exception: {0}".format(iAlertID, eventid, str(e)))
        return False

def processEvent(payload):
    """Method: accepts the the event from external monitoring system"""
    try:
        dPayload, droppedID = payload, 0
        # Remove if we find any dropped event id
        if "dropped_event_id" in dPayload.keys():
            droppedID = dPayload.pop("dropped_event_id")

        # dComponent = {'component_value': dPayload['component_value']}
        # del dPayload['component_value']

        # lAttr = ["ci_name", "component", "description", "notes", "severity", "event_created_time", "source", "customerid"] #chg
        lAttr = ["priority", "msg_updated_time", "machine", "application", "value", "cmdline", "description", "extra_description",
                 "severity", "source", "event_created_time", "customer_id",
                 "id", "asset_number", "region", "asset_state", "version", "package", "pac_ver", "pac_ver_no",
                 "msg_created_time", "status_update", "additional_props", "modified_by"]
        lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
        # lPayValuesErr = [1 if (not i.strip() == "") else 0 for i in dPayload.values()]

        # dPayload.update(dComponent)

        #Dropped Events capturing
        # if (0 in lPayValuesErr) and (not 0 in lPayErr):
        #     sStatus = 1
        #     dRet = ConnPostgreSQL.returnSelectQueryResult("select pk_ea_status_id as status_id from ea_status where stat_description='open'")
        #     if dRet["result"] == "success":
        #         sStatus = dRet["data"][0]["status_id"]
        #     sCIName = dPayload["ci_name"]
        #     sComp = dPayload["component"]
        #     sDesc = dPayload["description"]
        #     sNotes = dPayload["notes"]
        #     sSeverity = dPayload["severity"]
        #     sCreatedTime = float(dPayload["event_created_time"])
        #     sSource = dPayload["source"]
        #     dRet = insertDroppedNotifications(sCIName, sComp, sDesc, sNotes, sSeverity, sCreatedTime, sSource, sStatus)
        #     if dRet["result"] == "success":
        #         return logAndRet("success", "Dropped event created")
        #     else:
        #         return logAndRet("success", "Dropped event creation failed")
        # else:
        #     #Future development
        #     pass

        # Machine, Application, Description, Extra_Description, severity, event_created_time, source, customer_id, priority
        #
        # check for payload is valid or not
        if not 0 in lPayErr:
            sStatus = 1
            dRet = ConnPostgreSQL.returnSelectQueryResult("select pk_ea_status_id as status_id from ea_status where stat_description='open'")
            if dRet["result"] == "success":
                print(dRet["data"])
                sStatus = dRet["data"][0]["status_id"]
            sCIName = dPayload["machine"]
            sComp = dPayload["application"]
            sDesc = dPayload["description"]
            sNotes = dPayload["extra_description"]
            sSeverity = dPayload["severity"]
            sCreatedTime = float(dPayload["event_created_time"])
            sSource = dPayload["source"]
            sCustomerID = dPayload["customer_id"]
            sPriority = dPayload["priority"] # new
            sMsgUpdateTime = dPayload["msg_updated_time"] # new
            sValue = dPayload["value"] # new
            sCmd = dPayload["cmdline"] # new

            sID = dPayload["id"]
            sAssetNumber = dPayload["asset_number"]
            sRegion = dPayload["region"]
            sAssetState = dPayload["asset_state"]
            sVersion = dPayload["version"]
            sPackage = dPayload["package"]
            sPackVersion = dPayload["pac_ver"]
            sPackVersionNo = dPayload["pac_ver_no"]
            sMsgCreatedTime = dPayload["msg_created_time"]
            sStatusUpdate = dPayload["status_update"]
            sAddProps = dPayload["additional_props"]
            sModifiedby = dPayload["modified_by"]

            # check for any open event with same component and ci_name (suppression)
            iAlertSupp, bSupp = 0, False
            # dChkSupp = chkSuppression(sCIName, sComp)
            dChkSupp = chkSuppression3(sCIName, sComp, sDesc)
            if dChkSupp["result"] == "success":
                iAlertSupp = dChkSupp["data"]
                bSupp = True
            else:
                bSupp = False
            logINFO("Suppression State {0}".format(bSupp))
            if bSupp:
                # Insert event into event and map with the existing alert : Suppression
                try:
                    iEventID, iAlertID = 0, iAlertSupp
                    print(type(iAlertID))

                    # Insert Event
                    dRetInsEve = insertEventIRESS(sCIName, sComp, sDesc, sNotes, sSeverity, sCreatedTime, sSource, sStatus, sCustomerID, sPriority, sMsgUpdateTime, sValue, sCmd,
                                                  sID, sAssetNumber, sRegion, sAssetState, sVersion, sPackage,
                                                  sPackVersion, sPackVersionNo, sMsgCreatedTime, sStatusUpdate,
                                                  sAddProps, sModifiedby
                                                  ) #chg
                    if dRetInsEve["result"] == "success":
                        iEventID = dRetInsEve["data"]

                        # Insert into EA Mapping
                        dRetInsMap = insertEAMapping(iEventID, iAlertID)
                        if dRetInsMap["result"] == "success":

                            # Handle Clear Event : Close Event and Alert if Severity if 'OK' & Update Alert's Severity if 'other than OK'
                            dUpdateRet = updateAlert(iAlertID, sSeverity)
                            if dUpdateRet["result"] == "success":

                                # Push data to websocket
                                module, infotype, action = 'alert', 'json', 'update'
                                jsonData = {'alertid': ut.int2Alert(iAlertID),
                                            'event_details': {'eventid': ut.int2Event(iEventID), 'ci_name': sCIName, 'component': sComp, 'description': sDesc,
                                                              'notes': sNotes, 'severity': sSeverity, 'event_created_time': sCreatedTime,
                                                              'source': sSource, 'status': ('closed' if sSeverity.lower() == 'ok' else 'open'),
                                                              'priority': sPriority, 'msg_updated_time': sMsgUpdateTime, 'value': sValue, 'cmdline': sCmd,
                                                              'modified_by': sModifiedby, 'id': sID,
                                                              'asset_number': sAssetNumber, 'region': sRegion,
                                                              'asset_state': sAssetState, 'version': sVersion,
                                                              'package': sPackage, 'pac_ver': sPackVersion,
                                                              'pac_ver_no': sPackVersionNo,
                                                              'msg_created_time': sMsgCreatedTime,
                                                              'status_update': sStatusUpdate,
                                                              'additional_props': sAddProps
                                                              },
                                            'alert_details': {'severity': sSeverity, 'status': ('closed' if sSeverity.lower() == 'ok' else 'open')},
                                            'status_legends': {'open': (-1 if sSeverity.lower() == 'ok' else 0), 'total': 0, 'wip': 0, 'pending': 0, 'resolve': 0, 'closed': (1 if sSeverity.lower() == 'ok' else 0)}}
                                print(jsonData)
                                dRet = ws.pushToWebSocket(pModule=module, pInfoType=infotype, pData=jsonData, pAction=action)

                                # register for batch and kb anytime the event occur
                                dPayload["alert_id"] = iAlertID
                                if chkRegisterBatchAfterSuppression(iAlertID, iEventID):
                                    ret = connmq.send2MQ(pQueue='pe_events', pExchange='EVM', pRoutingKey='pe_events', pData=json.dumps(dPayload))

                                #Store mapping between dropped event and event
                                if droppedID != 0:
                                    dRet = insertDroppedEventMapping(droppedID, iEventID)
                                    if dRet["result"] == "success":
                                        return logAndRet("success", "Alert Promoted, Suppressed and mapped")
                                    else:
                                        return logAndRet("success", "Alert Promoted, Supressed and failed to map")

                                # Batch Processing
                                chkBatchProcessing(iAlertID, iEventID, sSeverity)

                                return logAndRet("success", "Suppressed: alert:{0} event:{1}".format(iAlertID, iEventID))
                except Exception as e:
                    # Roll back code
                    CERROR("Exception: {0}".format(str(e)))
                    return logAndRet("failure", "Supression failed: alert:{0} event:{1} with Exception: {2}".format(iAlertID, iEventID, str(e)))

            else:
                if sSeverity.lower() != "ok":
                    # Insert event as it is in event and alert table
                    try:
                        iEventID, iAlertID = 0, 0

                        # Insert Event
                        dRetInsEve = insertEventIRESS(sCIName, sComp, sDesc, sNotes, sSeverity, sCreatedTime, sSource, sStatus,
                                                      sCustomerID, sPriority, sMsgUpdateTime, sValue, sCmd,
                                                      sID, sAssetNumber, sRegion, sAssetState, sVersion, sPackage,
                                                      sPackVersion, sPackVersionNo, sMsgCreatedTime, sStatusUpdate,
                                                      sAddProps, sModifiedby
                                                      ) #chg
                        if dRetInsEve["result"] == "success":
                            iEventID = dRetInsEve["data"]

                            # Insert Alert
                            dRetInsAle = insertAlertIRESS(sCIName, sComp, sDesc, sNotes, sSeverity, sCreatedTime, sSource, sStatus,
                                                          sCustomerID, sPriority, sMsgUpdateTime, sValue, sCmd,
                                                          sID, sAssetNumber, sRegion, sAssetState, sVersion, sPackage,
                                                          sPackVersion, sPackVersionNo, sMsgCreatedTime, sStatusUpdate,
                                                          sAddProps, sModifiedby
                                                          ) #chg
                            if dRetInsAle["result"] == "success":
                                iAlertID = dRetInsAle["data"]

                                # Insert into EA Mapping
                                dRetInsMap = insertEAMapping(iEventID, iAlertID)
                                if dRetInsMap["result"] == "success":

                                    # Push data to websocket
                                    module, infotype, action = 'alert', 'json', 'create'
                                    jsonData = {'alert_details': {'alertid': ut.int2Alert(iAlertID), 'ci_name': sCIName,
                                                                  'component': sComp, 'description': sDesc,
                                                                  'notes': sNotes, 'severity': sSeverity,
                                                                  'event_created_time': sCreatedTime,
                                                                  'source': sSource, 'status': ('closed' if sSeverity.lower() == 'ok' else 'open'),
                                                                  'priority': sPriority, 'msg_updated_time': sMsgUpdateTime, 'value': sValue, 'cmdline': sCmd,
                                                                  'modified_by': sModifiedby, 'id': sID,
                                                                  'asset_number': sAssetNumber, 'region': sRegion,
                                                                  'asset_state': sAssetState, 'version': sVersion,
                                                                  'package': sPackage, 'pac_ver': sPackVersion,
                                                                  'pac_ver_no': sPackVersionNo,
                                                                  'msg_created_time': sMsgCreatedTime,
                                                                  'status_update': sStatusUpdate,
                                                                  'additional_props': sAddProps
                                                                  },
                                                'event_details': {'eventid': ut.int2Event(iEventID), 'ci_name': sCIName,
                                                                  'component': sComp, 'description': sDesc,
                                                                  'notes': sNotes, 'severity': sSeverity,
                                                                  'event_created_time': sCreatedTime,
                                                                  'source': sSource, 'status': ('closed' if sSeverity.lower() == 'ok' else 'open'),
                                                                  'priority': sPriority, 'msg_updated_time': sMsgUpdateTime, 'value': sValue, 'cmdline': sCmd,
                                                                  'modified_by': sModifiedby, 'id': sID, 'asset_number': sAssetNumber, 'region': sRegion,
                                                                  'asset_state': sAssetState, 'version': sVersion, 'package': sPackage, 'pac_ver': sPackVersion,
                                                                  'pac_ver_no': sPackVersionNo, 'msg_created_time': sMsgCreatedTime, 'status_update': sStatusUpdate,
                                                                  'additional_props': sAddProps
                                                                  },
                                                'status_legends': {'open': 1, 'total': 1, 'wip': 0, 'pending': 0, 'resolve': 0, 'closed': 0}}
                                    #print(jsonData)
                                    dRet = ws.pushToWebSocket(pModule=module, pInfoType=infotype, pData=jsonData, pAction=action)

                                    # Push details to Queue
                                    dPayload["alert_id"] = iAlertID
                                    # Check for service opted
                                    if 1 == 1: # bOpted4Service(sCustomerID, sCIName):
                                        ret = connmq.send2MQ(pQueue='pe_events', pExchange='EVM',
                                                             pRoutingKey='pe_events', pData=json.dumps(dPayload))
                                        # # Declare credentials
                                        # cred = pika.PlainCredentials(sUserName, sPassword)
                                        # # Create Connection
                                        # conn = pika.BlockingConnection(pika.ConnectionParameters(host=sIP, credentials=cred, virtual_host='autointelli'))
                                        # # Create Channel
                                        # channel = conn.channel()
                                        # # decalre queue
                                        # # channel.queue_declare(queue='processevents', durable=True)
                                        # channel.queue_declare(queue='pe_events', durable=True)
                                        # # publish data to the queue
                                        # # channel.basic_publish(exchange='automationengine', routing_key='automation.processevents', body=json.dumps(dPayload))
                                        # channel.basic_publish(exchange='EVM', routing_key='pe_events', body=json.dumps(dPayload))
                                        # # close the connection
                                        # conn.close()
                                        logINFO('Alert registered for KB execution: {0}'.format(dPayload))

                                    # Store mapping between dropped event and event
                                    if droppedID != 0:
                                        dRet = insertDroppedEventMapping(droppedID, iEventID)
                                        if dRet["result"] == "success":
                                            return logAndRet("success", "Alert Promoted, Created and mapped")
                                        else:
                                            return logAndRet("success", "Alert Promoted, Created and failed to map")

                                    return logAndRet("success", "New event:{0} and alert:{1} created".format(iEventID, iAlertID))
                                else:
                                    return logAndRet("failure", "New event:{0} and alert:{1} mapping failed".format(iEventID, iAlertID))
                            else:
                                return logAndRet("failure", "New alert creation failed payload: {0}".format(payload))
                        else:
                            return logAndRet("failure", "New event creation failed payload: {0}".format(payload))
                    except Exception as e:
                        # Roll Back code
                        CERROR("Exception: {0}".format(str(e)))
                        return logAndRet("failure", "New event and alert creation failed payload: {0} with Exception: {1}".format(payload, str(e)))
                else:
                    return logAndRet("failure", "Event dropped because the first event severity is OK, payload: {0}".format(payload))
        else:
            return logAndRet("failure", """Payload Error - Absent of required information. 
                                Sample Payload : {"ci_name": "bkp-02", "component": "CPU", "description": "CPU utilization is high", "notes": "CPU utilization is Critical. Used : 96%", "severity": "critical", "event_created_time": "22-03-2018 08:07:12", "source": "NAGIOS" }""")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def callback(ch, method, properties, body):
    payload = json.loads(body.decode('utf-8'))
    print(payload)
    retJson = processEvent(payload)
    print(retJson)

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
        logERROR("unable to fetch information from configuration table")
        CERROR("unable to fetch information from configuration table")

    # declare credentials
    credentials = pika.PlainCredentials(sUserName, sPassword)
    # open connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=sIP, credentials=credentials, virtual_host='autointelli'))
    # create channel
    channel = connection.channel()
    # select queue
    channel.queue_declare(queue='filtered_events', durable=True)
    # start consuming -> calls callback
    channel.queue_bind(exchange='EVM', queue='filtered_events')
    channel.basic_consume('filtered_events', callback, auto_ack=True)
    channel.start_consuming()
    channel.close()
except Exception as e:
    logERROR("Worker failed. Reason:" + str(e))
    CERROR("Worker failed. Reason:" + str(e))

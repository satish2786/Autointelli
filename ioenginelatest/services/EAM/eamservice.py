#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL
from services.utils import sessionkeygen
from copy import deepcopy
import requests as restcall
from services.utils.decoder import decode
import time
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc
from services.utils import validator_many as val
import services.utils.ConnMQ as connmq

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

lam_api_key_missing = lam_api_key_missing()
lam_api_key_invalid = lam_api_key_invalid()

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def getTimeZone(sKey):
    dRet = sessionkeygen.getUserDetailsBasedWithSessionKey(sKey)
    if dRet["result"] == "success":
        return dRet["data"][0]["time_zone"]
    else:
        return "no data"

def getAlerts(from_offset, count_limit):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sCountQuery = "select count(*) as total from alert_data"
                sPaging = "select pk_alert_id from alert_data order by pk_alert_id desc limit " + count_limit + " offset " + from_offset
                sQuery = """select
        concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity, TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name, e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time , e.source, s.stat_description as status,
        (CASE when ae.automationid is not null then concat('A',lpad(cast(ae.automationid as text),14,'0')) else null END) as automationid, ae.automationstatus,ae.start_time, ae.end_time, ae.itsmid, ae.itsmstatus
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join automationengine ae on (a.pk_alert_id = CAST( ae.alertid as BIGINT))
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sPaging + """)
order by
        a.pk_alert_id desc"""
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    #print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))#
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in ["alertid", "aci_name", "acomponent", "adescription", "anotes", "aseverity", "alert_created_time", "asource", "astatus", "automationid", "automationstatus", "start_time", "end_time", "itsmid", "itsmstatus"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'],reverse=True)
                        #print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'],reverse=True)
                    return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnStatus(pStatus, from_offset, count_limit):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sStatusCond = "1=1" if pStatus.lower() == "all" else ("fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data where " + sStatusCond
                sPaging = "select pk_alert_id from alert_data where " + sStatusCond + " order by pk_alert_id desc limit " + count_limit + " offset " + from_offset
                sQuery = """select
        concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        (CASE when ae.automationid is not null then concat('A',lpad(cast(ae.automationid as text),14,'0')) else null END) as automationid, ae.automationstatus,ae.start_time, ae.end_time, ae.itsmid, ae.itsmstatus
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join automationengine ae on (a.pk_alert_id = CAST( ae.alertid as BIGINT))
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sPaging + """)
order by
        a.pk_alert_id desc"""
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                #s.stat_description = '""" + pStatus + """'
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    #print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))#
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in ["alertid", "aci_name", "acomponent", "adescription", "anotes", "aseverity", "alert_created_time", "asource", "astatus", "automationid", "automationstatus", "start_time", "end_time", "itsmid", "itsmstatus"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'],reverse=True)
                        #print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getEvents(from_offset, count_limit):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sCountQuery = "select count(*) as total from event_data"
                sPaging = "select pk_event_id from event_data order by pk_event_id desc limit " + count_limit + " offset " + from_offset
                sQuery = """select
	concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, e.ci_name, e.component, e.description, e.notes, e.severity, TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status
from
	event_data e, alert_data a, ea_status s, event_alert_mapping ea
where
	a.fk_status_id = s.pk_ea_status_id and
	e.fk_status_id = s.pk_ea_status_id and
	a.pk_alert_id = ea.fk_alert_id and
	e.pk_event_id = ea.fk_event_id and e.pk_event_id in(""" + sPaging + """)
order by
	e.pk_event_id desc"""
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    return json.dumps({"result": "success", "data": {"event": dRet["data"], "count": dRetCnt["data"][0]["total"]}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load event details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getEventsBasedOnStatus(pStatus, from_offset, count_limit):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sStatusCond = "1=1" if pStatus.lower() == "all" else ("fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from event_data where " + sStatusCond
                sPaging = "select pk_event_id from event_data where " + sStatusCond + " order by pk_event_id desc limit " + count_limit + " offset " + from_offset
                sQuery = """select
	concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, e.ci_name, e.component, e.description, e.notes, e.severity, TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status
from
	event_data e, alert_data a, ea_status s, event_alert_mapping ea
where
	a.fk_status_id = s.pk_ea_status_id and
	e.fk_status_id = s.pk_ea_status_id and
	a.pk_alert_id = ea.fk_alert_id and
	e.pk_event_id = ea.fk_event_id and e.pk_event_id in(""" + sPaging + """)
order by
	e.pk_event_id desc"""
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    return json.dumps({"result": "success", "data": {"event": dRet["data"], "count": dRetCnt["data"][0]["total"]}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load event details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateAlertAndAssociatedEvents(alert_id, status):
    """Method: update the alert status and associated event's status."""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                # iAlertID = int(alert_id[1:])
                sAlertQuery = "update alert_data set fk_status_id=(select pk_ea_status_id from ea_status where active_yn='Y' and stat_description='" + status + "') where pk_alert_id = " + str(alert_id)
                sEventQuery = "update event_data set fk_status_id=(select pk_ea_status_id from ea_status where active_yn='Y' and stat_description='" + status + "') where pk_event_id in(select fk_event_id from  event_alert_mapping where fk_alert_id= " + str(alert_id) + ")"
                iRetA = ConnPostgreSQL.returnInsertResult(sAlertQuery)
                iRetE = ConnPostgreSQL.returnInsertResult(sEventQuery)
                if iRetA["result"] == "success" and iRetE["result"] == "success":
                    return json.dumps({"result": "success", "data": "Alert and associated Events updated"})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to update Alert and Events"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsStatusGroupBy():
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sQuery = """select ea.stat_description, coalesce(e.cnt,0) from ea_status ea left join (select fk_status_id, count(fk_status_id) cnt from alert_data group by fk_status_id) e 
 on (ea.pk_ea_status_id=e.fk_status_id)"""
                dRet = ConnPostgreSQL.returnSelectQueryResultConvert2Col2Dict(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getEventssStatusGroupBy():
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sQuery = """select ea.stat_description, coalesce(e.cnt,0) from ea_status ea left join (select fk_status_id, count(fk_status_id) cnt from event_data group by fk_status_id) e 
 on (ea.pk_ea_status_id=e.fk_status_id)"""
                dRet = ConnPostgreSQL.returnSelectQueryResultConvert2Col2Dict(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load event details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnFilter(pStatus, from_offset, count_limit, dPayload):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sFilterCond = ""
                for eachCond in dPayload.keys():
                    if eachCond == "alert_id":
                        sFilterCond += " concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) like '%" + dPayload[eachCond] + "%' and "
                    elif eachCond == "ciname":
                        sFilterCond += " lower(a.ci_name) like '%" + dPayload[eachCond].lower() + "%' and "
                    elif eachCond == "component":
                        sFilterCond += " lower(a.component) like '%" + dPayload[eachCond].lower() + "%' and "
                    elif eachCond == "datetime":
                        sFilterCond += " to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + dPayload[eachCond].split("__")[0].replace("_","/") + "', 'DD/MM/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + dPayload[eachCond].split("__")[1].replace("_","/") + "', 'DD/MM/YYYY') and ".format("at time zone 'utc' at time zone '" + sTimeZone + "'", "at time zone 'utc' at time zone '" + sTimeZone + "'")
                    elif eachCond == "status":
                        sFilterCond += " lower(s.stat_description) = '" + dPayload[eachCond].lower() + "' and "
                    elif eachCond == "autoid":
                        sFilterCond += " (CASE when ae.automationid is not null then concat('A',lpad(cast(ae.automationid as text),14,'0')) else null END) like '%" + dPayload[eachCond] + "%' and "
                    elif eachCond == "ticketid":
                        sFilterCond += " ae.itsmid = '" + dPayload[eachCond] + "' and "
                sFilterCond = sFilterCond[:-4]
                sStatusCond = "1=1" if pStatus.lower() == "all" else ("fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data where " + sStatusCond
                sPaging = "select pk_alert_id from alert_data where " + sStatusCond + " order by pk_alert_id desc limit " + count_limit + " offset " + from_offset
                sQuery = """select
        concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        (CASE when ae.automationid is not null then concat('A',lpad(cast(ae.automationid as text),14,'0')) else null END) as automationid, ae.automationstatus,ae.start_time, ae.end_time, ae.itsmid, ae.itsmstatus
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join automationengine ae on (a.pk_alert_id = CAST( ae.alertid as BIGINT))
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and """ + sFilterCond + """ and a.pk_alert_id in(""" + sPaging + """)
order by
        a.pk_alert_id desc"""
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                #s.stat_description = '""" + pStatus + """'
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    #print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))#
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in ["alertid", "aci_name", "acomponent", "adescription", "anotes", "aseverity", "alert_created_time", "asource", "astatus", "automationid", "automationstatus", "start_time", "end_time", "itsmid", "itsmstatus"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'],reverse=True)
                        #print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getEventsBasedOnFilter(pStatus, from_offset, count_limit, dPayload):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sFilterCond = ""
                for eachCond in dPayload.keys():
                    if eachCond == "event_id":
                        sFilterCond += " concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) like '%" + dPayload[
                            eachCond] + "%' and "
                    elif eachCond == "ciname":
                        sFilterCond += " lower(e.ci_name) like '%" + dPayload[eachCond].lower() + "%' and "
                    elif eachCond == "component":
                        sFilterCond += " lower(e.component) like '%" + dPayload[eachCond].lower() + "%' and "
                    elif eachCond == "datetime":
                        sFilterCond += " to_date(TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                       dPayload[eachCond].split("__")[0].replace("_",
                                                                                 "/") + "', 'DD/MM/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                       dPayload[eachCond].split("__")[1].replace("_", "/") + "', 'DD/MM/YYYY') and ".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                    elif eachCond == "status":
                        sFilterCond += " lower(s.stat_description) = '" + dPayload[eachCond].lower() + "' and "
                    elif eachCond == "source":
                        sFilterCond += " lower(e.source) like '%" + dPayload[eachCond].lower() + "%' and "
                    elif eachCond == "severity":
                        sFilterCond += " lower(e.severity) = '" + dPayload[eachCond].lower() + "' and "
                sFilterCond = sFilterCond[:-4]
                sStatusCond = "1=1" if pStatus.lower() == "all" else ("fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from event_data where " + sStatusCond
                sPaging = "select pk_event_id from event_data where " + sStatusCond + " order by pk_event_id desc limit " + count_limit + " offset " + from_offset
                sQuery = """select
	concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, e.ci_name, e.component, e.description, e.notes, e.severity, TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status
from
	event_data e, alert_data a, ea_status s, event_alert_mapping ea
where
	a.fk_status_id = s.pk_ea_status_id and
	e.fk_status_id = s.pk_ea_status_id and
	a.pk_alert_id = ea.fk_alert_id and
	e.pk_event_id = ea.fk_event_id and """ + sFilterCond + """ and e.pk_event_id in(""" + sPaging + """)
order by
	e.pk_event_id desc"""
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    return json.dumps({"result": "success", "data": {"event": dRet["data"], "count": dRetCnt["data"][0]["total"]}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load event details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnStatusFilterOrderBy1(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sFilterQuery, sSortQuery = "", ""

                #Applying Filter on colums = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += " to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                       filter_value.split("__")[0].replace("_",
                                                                                 "/") + "', 'DD/MM/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                       filter_value.split("__")[1].replace("_", "/") + "', 'DD/MM/YYYY') and ".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                elif filter_key == "autoid":
                    sFilterQuery += " (CASE when ae.automationid is not null then concat('A',lpad(cast(ae.automationid as text),14,'0')) else null END) like '%" + \
                                       filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " ae.itsmid = '" + filter_value.lower() + "' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                #Applying sorting = ASC and DESC
                adCol = column_sort[:-2]
                #adColSort = "asc" if column_sort[-1] == "a" else "desc"
                adColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    #sSortQuery += " a.pk_alert_id desc"
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        #sSortQuery += " a.pk_alert_id " + adColSort
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "autoid":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sStatusCond = "1=1" if pStatus.lower() == "all" else ("fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data where " + sStatusCond
                sPaging = "select pk_alert_id from alert_data where " + sStatusCond + " order by pk_alert_id desc limit " + count_limit + " offset " + from_offset
                #sPaging = " limit " + count_limit + " offset " + from_offset
                sQuery = """select
        concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        (CASE when ae.automationid is not null then concat('A',lpad(cast(ae.automationid as text),14,'0')) else null END) as automationid, ae.automationstatus,ae.start_time, ae.end_time, ae.itsmid, ae.itsmstatus
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join automationengine ae on (a.pk_alert_id = CAST( ae.alertid as BIGINT))
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and """ + sFilterQuery + """ and a.pk_alert_id in(""" + sPaging + """)
order by """ + sSortQuery
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                #s.stat_description = '""" + pStatus + """'
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    #print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))#
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in ["alertid", "aci_name", "acomponent", "adescription", "anotes", "aseverity", "alert_created_time", "asource", "astatus", "automationid", "automationstatus", "start_time", "end_time", "itsmid", "itsmstatus"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'],reverse=adColSort)
                        #print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                    #lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=adColSort)
                    return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getEventsBasedOnStatusFilterOrderBy1(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sFilterQuery, sSortQuery = "", ""

                # Applying Filter on colums = Basic Search
                if filter_key == "event_id":
                    sFilterQuery += " concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "alert_id":
                    sFilterQuery += " concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(e.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(e.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += " to_date(TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                    filter_value.split("__")[0].replace("_",
                                                                        "/") + "', 'DD/MM/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                    filter_value.split("__")[1].replace("_", "/") + "', 'DD/MM/YYYY') and ".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                elif filter_key == "severity":
                    sFilterQuery += " lower(e.severity) ='" + filter_value.lower() + "' and "
                elif filter_key == "source":
                    sFilterQuery += " lower(e.source) = '" + filter_value.lower() + "' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                # Applying sorting = ASC and DESC
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                if column_sort == "null":
                    sSortQuery += " e.pk_event_id desc"
                else:
                    if adCol == "event_id":
                        sSortQuery += " e.pk_event_id " + adColSort
                    elif adCol == "alert_id":
                        sSortQuery += " a.pk_alert_id " + adColSort
                    elif adCol == "ciname":
                        sSortQuery += " e.ci_name " + adColSort
                    elif adCol == "component":
                        sSortQuery += " e.component " + adColSort
                    elif adCol == "datetime":
                        sSortQuery += " TO_TIMESTAMP(e.event_created_time ) " + adColSort
                    elif adCol == "severity":
                        sSortQuery += " e.severity " + adColSort
                    elif adCol == "source":
                        sSortQuery += " e.source " + adColSort

                sStatusCond = "1=1" if pStatus.lower() == "all" else ("fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from event_data where " + sStatusCond
                sPaging = "select pk_event_id from event_data where " + sStatusCond + " order by pk_event_id desc limit " + count_limit + " offset " + from_offset
                sQuery = """select
	concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, e.ci_name, e.component, e.description, e.notes, e.severity, TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status
from
	event_data e, alert_data a, ea_status s, event_alert_mapping ea
where
	a.fk_status_id = s.pk_ea_status_id and
	e.fk_status_id = s.pk_ea_status_id and
	a.pk_alert_id = ea.fk_alert_id and
	e.pk_event_id = ea.fk_event_id and """ + sFilterQuery + """ and e.pk_event_id in(""" + sPaging + """)
order by """ + sSortQuery
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    return json.dumps({"result": "success", "data": {"event": dRet["data"], "count": dRetCnt["data"][0]["total"]}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load event details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


#-----------------------------------------------------------------------------------------------------------------------------------------------------

def getAlertsBasedOnStatusFilterOrderByDownload(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            s = time.time()
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            if filter_key == "customer_id":
                sQuery = "select count(*) total from alert_data where lower(customer_id) like lower('%{0}%')".format(filter_value)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    if dRet["data"][0]["total"] == 0:
                        return json.dumps({"result": "failure", "data": "no data"})

            try:
                sFilterQuery, sSortQuery = "", ""

                # Applying Filter on columns = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += (" to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                    filter_value.split("__")[0].replace("-",
                                                                        "/") + "', 'DD/MON/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                    filter_value.split("__")[1].replace("-", "/") + "', 'DD/MON/YYYY') and ").format(
                        "at time zone '" + sTimeZone + "'",
                        "at time zone '" + sTimeZone + "'")
                elif filter_key == "botname":
                    sFilterQuery += " lower(abr.bot_name) like '%" + \
                                    filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " atd.ticket_no = '" + filter_value.lower() + "' and "
                elif filter_key == "customer_id":
                    sFilterQuery += " lower(a.customer_id) like '%" + filter_value.lower().strip() + "%' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                # Applying sort
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                bColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "botname":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sSortQueryWOAlias = {"alertid": "a.pk_alert_id", "aci_name": "a.ci_name", "acomponent": "a.component",
                                     "automationid": "abr.bot_name", "itsmid": "atd.ticket_no"}

                # Applying Filter based on status
                sStatusCond = "1=1" if pStatus.lower() == "all" else (
                        "a.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data a where " + sStatusCond

                sPaging = " limit " + count_limit + " offset " + from_offset
                sQuery = """
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT))
                  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b order by alertid %s %s""" % (sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort, adColSort, sPaging)
                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQuery)
                lDistinctValues = dDistinctValues['data']['alertid']
                print(lDistinctValues)

                sQuery = """
select count(alertid) as total from (
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT))
                  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b ) c""" % (sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort)
                dCountAlertIDs = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                print(dCountAlertIDs)
                iTotalNumberOfAlert = dCountAlertIDs['data'][0]['total']
                print(iTotalNumberOfAlert)

                # Get Alerts because alerts gets missed out on doing query
                # sPaging = " limit " + count_limit + " offset " + from_offset
                # sQueryAlertAssociationIssue = "select alertid from (" + sQuery + ") a " #+ sPaging
                # print("First Query to DB---> " + str(float(time.time()-s)))
                # dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQueryAlertAssociationIssue)
                # print("Time Spent in DB---> " + str(float(time.time()-s)))
                # if dDistinctValues["result"] == "failure":
                #    return json.dumps(dDistinctValues)
                # lOutDV = dDistinctValues["data"]["alertid"]
                # lDistinctValues = []
                # print(sQueryAlertAssociationIssue)
                # print(lOutDV)
                # for eachID in lOutDV:
                #    if lDistinctValues.__contains__(eachID):
                #        continue
                #    else:
                #        lDistinctValues.append(eachID)
                sDistinctValuesData = ",".join([str(i) for i in lDistinctValues])
                #sDistinctValuesData = ",".join([str(i) for i in lDistinctValues][int(from_offset):(int(from_offset) + int(count_limit))])
                print(sDistinctValuesData)
                print("Python Time First Loop---> " + str(float(time.time() - s)))
                # So, the main query will be like
                sMainQuery = """
select 
        concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        COALESCE(abr.bot_name, '') as automationid, COALESCE(atd.ticket_no,'')	as itsmid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT)) 
		  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id) 
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sDistinctValuesData + """)   
order by """ + sSortQuery + """ """ + adColSort
                sMainQuery = """
select distinct a.customer_id, concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as ci_name, a.component as component, a.description as description, a.notes as notes, a.severity as severity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) at time zone 'Asia/Kolkata', 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as source, s.stat_description as status,
        COALESCE(abr.bot_name, '') as automationid, COALESCE(atd.ticket_no,'')  as itsmid
from
         ea_status s, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT))
                  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id in(""" + sDistinctValuesData + """)  
order by alertid desc"""
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'",
                                               "at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                print("Query 2 sent to DB---> " + str(float(time.time() - s)))
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sMainQuery)
                print("Response from DB for Query 2---> " + str(float(time.time() - s)))
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    from services.utils import E2XL
                    out = E2XL.export2XLSX(dRet['data'])
                    if out['result'] == 'success':
                        return json.dumps({'result': 'success', 'data': {'link': out['data']}})
                    else:
                        return json.dumps({'result': 'failure', 'data': {'link': ''}})
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    # print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))  #
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        # dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        # dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        # dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        # dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in
                                ["alertid", "aci_name", "acomponent", "adescription", "anotes", "aseverity",
                                 "alert_created_time", "asource", "astatus", "automationid", "itsmid"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'], reverse=True)
                        # print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                        # print(eachA)
                    # lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=bColSort)
                    print("Python Loop 2 time---> " + str(float(time.time() - s)))
                    # return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                    print({"result": "success", "data": {"alert": lAllAlertDesc, "count": len(lDistinctValues)}})
                    return json.dumps(
                        {"result": "success", "data": {"alert": lAllAlertDesc, "count": iTotalNumberOfAlert}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getSOPName():
    try:
        pass
    except Exception as e:
        return ""

def getPersonlizeFilterCondition(condition):
    try:
        cond, sWhere, result = "", [], ""
        if 'ALL' in condition.keys():
            cond = 'ALL'
        else:
            cond = 'ANY'
        sqlTextMapping = {'equal to': " ='{0}' ",
                          'not equal to': " !='{0}' ",
                          'contains': " like '%{0}%' ",
                          'starts with': " like '{0}%' ",
                          'ends with': " like '%{0}' ",
                          'sql like': " like '{0}' "}
        tblMapping = {'region': 'a.region', 'machine': 'a.ci_name', 'application': 'a.component', 'description': 'a.description',
                      'extra_description': 'a.notes', 'priority': 'a.priority'}

        for i in condition[cond]:
            sWhere.append(" {0} {1} ".format(tblMapping[i['Key']], sqlTextMapping[i['Operator']].format(i['Value'])))
        if cond == 'ALL':
            result = '(' + ' and '.join(sWhere) + ')'
        else:
            result = '(' + ' or '.join(sWhere) + ')'
        return result
    except Exception as e:
        return " 1=1 "

def getAlertsBasedOnStatusFilterOrderByWithPINP(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort, user, personalize):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            s = time.time()
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            if filter_key == "customer_id":
                sQuery = "select count(*) total from alert_data where lower(customer_id) like lower('%{0}%')".format(filter_value)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    if dRet["data"][0]["total"] == 0:
                        return json.dumps({"result": "failure", "data": "no data"})

            try:

                sFilterQuery, sSortQuery, sPersonalize = "", "", " 1=1 "

                # Personalize
                sQueryPersonalize = "select personalize_attributes from personalize where user_id={0} and active_yn='Y' and lower(personalize_name)=lower('{1}')".format(
                    user, personalize
                )
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQueryPersonalize)
                if dRet['result'] == 'success':
                    sPersonalize = getPersonlizeFilterCondition(dRet['data'][0]['personalize_attributes']['Condition'])

                # Applying Filter on columns = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += (" to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                    filter_value.split("__")[0].replace("-",
                                                                        "/") + "', 'DD/MON/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                    filter_value.split("__")[1].replace("-", "/") + "', 'DD/MON/YYYY') and ").format(
                        "at time zone '" + sTimeZone + "'",
                        "at time zone '" + sTimeZone + "'")
                elif filter_key == "botname":
                    sFilterQuery += " lower(abr.bot_name) like '%" + \
                                    filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " atd.ticket_no = '" + filter_value.lower() + "' and "
                elif filter_key == "customer_id":
                    sFilterQuery += " lower(a.customer_id) like '%" + filter_value.lower().strip() + "%' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                # sFilterQuery = sFilterQuery[:-4]
                sFilterQuery = sFilterQuery + sPersonalize

                # Applying sort
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                bColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "botname":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sSortQueryWOAlias = {"alertid": "a.pk_alert_id", "aci_name": "a.ci_name", "acomponent": "a.component",
                                     "automationid": "abr.bot_name", "itsmid": "atd.ticket_no"}

                # Applying Filter based on status
                sStatusCond = "1=1" if pStatus.lower() == "all" else (
                        "a.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data a where " + sStatusCond

                # PIN and UNPIN
                sNotInWhere = " a.pk_alert_id not in({0}) and "
                pinQuery = "select fk_alert_id from alert_pin_unpin where fk_user_id={0} order by created_on desc".format(user)
                pinalerts = ConnPostgreSQL.returnSelectQueryResultAsList(pinQuery)
                pinnedalerts = []
                if pinalerts['result'] == 'success':
                    pinnedalerts = pinalerts['data']['fk_alert_id']
                    sNotInWhere = sNotInWhere.format(','.join([str(i) for i in pinnedalerts]))
                    count_limit = int(count_limit) - len(pinalerts['data']['fk_alert_id'])
                    if int(from_offset) > 0:
                        from_offset = int(from_offset) - len(pinalerts['data']['fk_alert_id'])
                else:
                    sNotInWhere = " 1=1 and "


                sPaging = " limit " + str(count_limit) + " offset " + str(from_offset)
                sQuery = """
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a 
where 
        %s
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b order by alertid %s %s""" % (sNotInWhere, sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort, adColSort, sPaging)
                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQuery)
                lDistinctValues = dDistinctValues['data']['alertid'] if dDistinctValues['result'] == 'success' else []
                print(lDistinctValues)

                sQuery = """
select count(alertid) as total from (
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a 
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b ) c""" % (sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort)
                dCountAlertIDs = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                print(dCountAlertIDs)
                iTotalNumberOfAlert = dCountAlertIDs['data'][0]['total']
                print(iTotalNumberOfAlert)

                # Get Alerts because alerts gets missed out on doing query
                # sPaging = " limit " + count_limit + " offset " + from_offset
                # sQueryAlertAssociationIssue = "select alertid from (" + sQuery + ") a " #+ sPaging
                # print("First Query to DB---> " + str(float(time.time()-s)))
                # dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQueryAlertAssociationIssue)
                # print("Time Spent in DB---> " + str(float(time.time()-s)))
                # if dDistinctValues["result"] == "failure":
                #    return json.dumps(dDistinctValues)
                # lOutDV = dDistinctValues["data"]["alertid"]
                # lDistinctValues = []
                # print(sQueryAlertAssociationIssue)
                # print(lOutDV)
                # for eachID in lOutDV:
                #    if lDistinctValues.__contains__(eachID):
                #        continue
                #    else:
                #        lDistinctValues.append(eachID)
                sDistinctValuesData = ",".join([str(i) for i in pinnedalerts + lDistinctValues])
                #sDistinctValuesData = ",".join([str(i) for i in lDistinctValues][int(from_offset):(int(from_offset) + int(count_limit))])
                print(sDistinctValuesData)
                # sDistinctValuesData = pinnedalerts + sDistinctValuesData
                print("Python Time First Loop---> " + str(float(time.time() - s)))
                # So, the main query will be like
                sMainQuery = """
select 
        distinct concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, sop.sop_name sop_name, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        '' as automationid, ''	as itsmid, e.msg_updated_time, e.value, e.cmdline, 
        e.modified_by, e.id, e.asset_number, e.region, e.asset_state, e.version, e.package, e.pac_ver, e.pac_ver_no, e.msg_created_time,
        e.status_update, '' as additional_props, e.priority 
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join sop on(a.fk_sop_id=sop.pk_sop_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sDistinctValuesData + """)   
order by """ + sSortQuery + """ """ + adColSort
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'",
                                               "at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                print("Query 2 sent to DB---> " + str(float(time.time() - s)))
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sMainQuery)
                print("Response from DB for Query 2---> " + str(float(time.time() - s)))
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    # print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))  #
                        # PIN UNPIN Flag
                        if int(eachA.strip('AL')) in pinnedalerts:
                            dOneAlert['pin'] = 'Y'
                        else:
                            dOneAlert['pin'] = 'N'
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["sop_name"] = lOneAlert[0]["sop_name"]
                        # dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        # dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        # dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        # dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        dOneAlert["amodified_by"] = lOneAlert[0]["modified_by"]
                        dOneAlert["aid"] = lOneAlert[0]["id"]
                        dOneAlert["aasset_number"] = lOneAlert[0]["asset_number"]
                        dOneAlert["aregion"] = lOneAlert[0]["region"]
                        dOneAlert["aasset_state"] = lOneAlert[0]["asset_state"]
                        dOneAlert["aversion"] = lOneAlert[0]["version"]
                        dOneAlert["apackage"] = lOneAlert[0]["package"]
                        dOneAlert["apac_ver"] = lOneAlert[0]["pac_ver"]
                        dOneAlert["apac_ver_no"] = lOneAlert[0]["pac_ver_no"]
                        dOneAlert["amsg_created_time"] = lOneAlert[0]["msg_created_time"]
                        dOneAlert["astatus_update"] = lOneAlert[0]["status_update"]
                        dOneAlert["aadditional_props"] = lOneAlert[0]["additional_props"]
                        dOneAlert["apriority"] = lOneAlert[0]["priority"]

                        lTmp = [i.pop(j) for i in lOneAlert for j in
                                ["alertid", "sop_name", "aci_name", "acomponent", "adescription", "anotes", "aseverity",
                                 "alert_created_time", "asource", "astatus", "automationid", "itsmid"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'], reverse=True)
                        # print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                        # print(eachA)
                    # lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=bColSort)
                    print("Python Loop 2 time---> " + str(float(time.time() - s)))
                    # return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                    print({"result": "success", "data": {"alert": lAllAlertDesc, "count": len(lDistinctValues)}})
                    return json.dumps(
                        {"result": "success", "data": {"alert": lAllAlertDesc, "count": iTotalNumberOfAlert}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnStatusFilterOrderByWithPIN(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort, user):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            s = time.time()
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            if filter_key == "customer_id":
                sQuery = "select count(*) total from alert_data where lower(customer_id) like lower('%{0}%')".format(filter_value)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    if dRet["data"][0]["total"] == 0:
                        return json.dumps({"result": "failure", "data": "no data"})

            try:
                sFilterQuery, sSortQuery = "", ""

                # Applying Filter on columns = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += (" to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                    filter_value.split("__")[0].replace("-",
                                                                        "/") + "', 'DD/MON/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                    filter_value.split("__")[1].replace("-", "/") + "', 'DD/MON/YYYY') and ").format(
                        "at time zone '" + sTimeZone + "'",
                        "at time zone '" + sTimeZone + "'")
                elif filter_key == "botname":
                    sFilterQuery += " lower(abr.bot_name) like '%" + \
                                    filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " atd.ticket_no = '" + filter_value.lower() + "' and "
                elif filter_key == "customer_id":
                    sFilterQuery += " lower(a.customer_id) like '%" + filter_value.lower().strip() + "%' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                # Applying sort
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                bColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "botname":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sSortQueryWOAlias = {"alertid": "a.pk_alert_id", "aci_name": "a.ci_name", "acomponent": "a.component",
                                     "automationid": "abr.bot_name", "itsmid": "atd.ticket_no"}

                # Applying Filter based on status
                sStatusCond = "1=1" if pStatus.lower() == "all" else (
                        "a.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data a where " + sStatusCond

                # PIN and UNPIN
                sNotInWhere = " a.pk_alert_id not in({0}) and "
                pinQuery = "select fk_alert_id from alert_pin_unpin where fk_user_id={0} order by created_on desc".format(user)
                pinalerts = ConnPostgreSQL.returnSelectQueryResultAsList(pinQuery)
                pinnedalerts = []
                if pinalerts['result'] == 'success':
                    pinnedalerts = pinalerts['data']['fk_alert_id']
                    sNotInWhere = sNotInWhere.format(','.join([str(i) for i in pinnedalerts]))
                    count_limit = int(count_limit) - len(pinalerts['data']['fk_alert_id'])
                    if int(from_offset) > 0:
                        from_offset = int(from_offset) - len(pinalerts['data']['fk_alert_id'])
                else:
                    sNotInWhere = " 1=1 and "


                sPaging = " limit " + str(count_limit) + " offset " + str(from_offset)
                sQuery = """
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a 
where 
        %s
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b order by alertid %s %s""" % (sNotInWhere, sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort, adColSort, sPaging)
                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQuery)
                lDistinctValues = dDistinctValues['data']['alertid']
                print(lDistinctValues)

                sQuery = """
select count(alertid) as total from (
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a 
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b ) c""" % (sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort)
                dCountAlertIDs = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                print(dCountAlertIDs)
                iTotalNumberOfAlert = dCountAlertIDs['data'][0]['total']
                print(iTotalNumberOfAlert)

                # Get Alerts because alerts gets missed out on doing query
                # sPaging = " limit " + count_limit + " offset " + from_offset
                # sQueryAlertAssociationIssue = "select alertid from (" + sQuery + ") a " #+ sPaging
                # print("First Query to DB---> " + str(float(time.time()-s)))
                # dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQueryAlertAssociationIssue)
                # print("Time Spent in DB---> " + str(float(time.time()-s)))
                # if dDistinctValues["result"] == "failure":
                #    return json.dumps(dDistinctValues)
                # lOutDV = dDistinctValues["data"]["alertid"]
                # lDistinctValues = []
                # print(sQueryAlertAssociationIssue)
                # print(lOutDV)
                # for eachID in lOutDV:
                #    if lDistinctValues.__contains__(eachID):
                #        continue
                #    else:
                #        lDistinctValues.append(eachID)
                sDistinctValuesData = ",".join([str(i) for i in pinnedalerts + lDistinctValues])
                #sDistinctValuesData = ",".join([str(i) for i in lDistinctValues][int(from_offset):(int(from_offset) + int(count_limit))])
                print(sDistinctValuesData)
                # sDistinctValuesData = pinnedalerts + sDistinctValuesData
                print("Python Time First Loop---> " + str(float(time.time() - s)))
                # So, the main query will be like
                sMainQuery = """
select 
        distinct concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, sop.sop_name sop_name, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        '' as automationid, ''	as itsmid, e.msg_updated_time, e.value, e.cmdline, 
        e.modified_by, e.id, e.asset_number, e.region, e.asset_state, e.version, e.package, e.pac_ver, e.pac_ver_no, e.msg_created_time,
        e.status_update, '' as additional_props, e.priority 
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join sop on(a.fk_sop_id=sop.pk_sop_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sDistinctValuesData + """)   
order by """ + sSortQuery + """ """ + adColSort
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'",
                                               "at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                print("Query 2 sent to DB---> " + str(float(time.time() - s)))
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sMainQuery)
                print("Response from DB for Query 2---> " + str(float(time.time() - s)))
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    # print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))  #
                        # PIN UNPIN Flag
                        if int(eachA.strip('AL')) in pinnedalerts:
                            dOneAlert['pin'] = 'Y'
                        else:
                            dOneAlert['pin'] = 'N'
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["sop_name"] = lOneAlert[0]["sop_name"]
                        # dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        # dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        # dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        # dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        dOneAlert["amodified_by"] = lOneAlert[0]["modified_by"]
                        dOneAlert["aid"] = lOneAlert[0]["id"]
                        dOneAlert["aasset_number"] = lOneAlert[0]["asset_number"]
                        dOneAlert["aregion"] = lOneAlert[0]["region"]
                        dOneAlert["aasset_state"] = lOneAlert[0]["asset_state"]
                        dOneAlert["aversion"] = lOneAlert[0]["version"]
                        dOneAlert["apackage"] = lOneAlert[0]["package"]
                        dOneAlert["apac_ver"] = lOneAlert[0]["pac_ver"]
                        dOneAlert["apac_ver_no"] = lOneAlert[0]["pac_ver_no"]
                        dOneAlert["amsg_created_time"] = lOneAlert[0]["msg_created_time"]
                        dOneAlert["astatus_update"] = lOneAlert[0]["status_update"]
                        dOneAlert["aadditional_props"] = lOneAlert[0]["additional_props"]
                        dOneAlert["apriority"] = lOneAlert[0]["priority"]

                        lTmp = [i.pop(j) for i in lOneAlert for j in
                                ["alertid", "sop_name", "aci_name", "acomponent", "adescription", "anotes", "aseverity",
                                 "alert_created_time", "asource", "astatus", "automationid", "itsmid"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'], reverse=True)
                        # print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                        # print(eachA)
                    # lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=bColSort)
                    print("Python Loop 2 time---> " + str(float(time.time() - s)))
                    # return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                    print({"result": "success", "data": {"alert": lAllAlertDesc, "count": len(lDistinctValues)}})
                    return json.dumps(
                        {"result": "success", "data": {"alert": lAllAlertDesc, "count": iTotalNumberOfAlert}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnStatusFilterOrderByWithPIN1(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort, user):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            s = time.time()
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            if filter_key == "customer_id":
                sQuery = "select count(*) total from alert_data where lower(customer_id) like lower('%{0}%')".format(filter_value)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    if dRet["data"][0]["total"] == 0:
                        return json.dumps({"result": "failure", "data": "no data"})

            try:
                sFilterQuery, sSortQuery = "", ""

                # Applying Filter on columns = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += (" to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                    filter_value.split("__")[0].replace("-",
                                                                        "/") + "', 'DD/MON/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                    filter_value.split("__")[1].replace("-", "/") + "', 'DD/MON/YYYY') and ").format(
                        "at time zone '" + sTimeZone + "'",
                        "at time zone '" + sTimeZone + "'")
                elif filter_key == "botname":
                    sFilterQuery += " lower(abr.bot_name) like '%" + \
                                    filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " atd.ticket_no = '" + filter_value.lower() + "' and "
                elif filter_key == "customer_id":
                    sFilterQuery += " lower(a.customer_id) like '%" + filter_value.lower().strip() + "%' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                # Applying sort
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                bColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "botname":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sSortQueryWOAlias = {"alertid": "a.pk_alert_id", "aci_name": "a.ci_name", "acomponent": "a.component",
                                     "automationid": "abr.bot_name", "itsmid": "atd.ticket_no"}

                # Applying Filter based on status
                sStatusCond = "1=1" if pStatus.lower() == "all" else (
                        "a.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data a where " + sStatusCond

                # PIN and UNPIN
                sNotInWhere = " a.pk_alert_id not in({0}) "
                pinQuery = "select fk_alert_id from alert_pin_unpin where fk_user_id={0} order by created_on desc".format(user)
                pinalerts = ConnPostgreSQL.returnSelectQueryResultAsList(pinQuery)
                pinnedalerts = []
                if pinalerts['result'] == 'success':
                    pinnedalerts = pinalerts['data']['fk_alert_id']
                    sNotInWhere = sNotInWhere.format(','.join([str(i) for i in pinnedalerts]))
                    count_limit = int(count_limit) - len(pinalerts['data']['fk_alert_id'])
                    if int(from_offset) > 0:
                        from_offset = int(from_offset) - len(pinalerts['data']['fk_alert_id'])
                else:
                    sNotInWhere = " 1=1 "


                sPaging = " limit " + str(count_limit) + " offset " + str(from_offset)
                sQuery = """
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT))
                  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id)
where 
        %s
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b order by alertid %s %s""" % (sNotInWhere, sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort, adColSort, sPaging)
                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQuery)
                lDistinctValues = dDistinctValues['data']['alertid']
                print(lDistinctValues)

                sQuery = """
select count(alertid) as total from (
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT))
                  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b ) c""" % (sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort)
                dCountAlertIDs = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                print(dCountAlertIDs)
                iTotalNumberOfAlert = dCountAlertIDs['data'][0]['total']
                print(iTotalNumberOfAlert)

                # Get Alerts because alerts gets missed out on doing query
                # sPaging = " limit " + count_limit + " offset " + from_offset
                # sQueryAlertAssociationIssue = "select alertid from (" + sQuery + ") a " #+ sPaging
                # print("First Query to DB---> " + str(float(time.time()-s)))
                # dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQueryAlertAssociationIssue)
                # print("Time Spent in DB---> " + str(float(time.time()-s)))
                # if dDistinctValues["result"] == "failure":
                #    return json.dumps(dDistinctValues)
                # lOutDV = dDistinctValues["data"]["alertid"]
                # lDistinctValues = []
                # print(sQueryAlertAssociationIssue)
                # print(lOutDV)
                # for eachID in lOutDV:
                #    if lDistinctValues.__contains__(eachID):
                #        continue
                #    else:
                #        lDistinctValues.append(eachID)
                sDistinctValuesData = ",".join([str(i) for i in pinnedalerts + lDistinctValues])
                #sDistinctValuesData = ",".join([str(i) for i in lDistinctValues][int(from_offset):(int(from_offset) + int(count_limit))])
                print(sDistinctValuesData)
                # sDistinctValuesData = pinnedalerts + sDistinctValuesData
                print("Python Time First Loop---> " + str(float(time.time() - s)))
                # So, the main query will be like
                sMainQuery = """
select 
        distinct concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, sop.sop_name sop_name, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        COALESCE(abr.bot_name, '') as automationid, COALESCE(atd.ticket_no,'')	as itsmid, e.msg_updated_time, e.value, e.cmdline, 
        e.modified_by, e.id, e.asset_number, e.region, e.asset_state, e.version, e.package, e.pac_ver, e.pac_ver_no, e.msg_created_time,
        e.status_update, '' as additional_props 
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT)) 
		  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id) 
		  left join sop on(a.fk_sop_id=sop.pk_sop_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sDistinctValuesData + """)   
order by """ + sSortQuery + """ """ + adColSort
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'",
                                               "at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                print("Query 2 sent to DB---> " + str(float(time.time() - s)))
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sMainQuery)
                print("Response from DB for Query 2---> " + str(float(time.time() - s)))
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    # print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))  #
                        # PIN UNPIN Flag
                        if int(eachA.strip('AL')) in pinnedalerts:
                            dOneAlert['pin'] = 'Y'
                        else:
                            dOneAlert['pin'] = 'N'
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["sop_name"] = lOneAlert[0]["sop_name"]
                        # dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        # dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        # dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        # dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        dOneAlert["amodified_by"] = lOneAlert[0]["modified_by"]
                        dOneAlert["aid"] = lOneAlert[0]["id"]
                        dOneAlert["aasset_number"] = lOneAlert[0]["asset_number"]
                        dOneAlert["aregion"] = lOneAlert[0]["region"]
                        dOneAlert["aasset_state"] = lOneAlert[0]["asset_state"]
                        dOneAlert["aversion"] = lOneAlert[0]["version"]
                        dOneAlert["apackage"] = lOneAlert[0]["package"]
                        dOneAlert["apac_ver"] = lOneAlert[0]["pac_ver"]
                        dOneAlert["apac_ver_no"] = lOneAlert[0]["pac_ver_no"]
                        dOneAlert["amsg_created_time"] = lOneAlert[0]["msg_created_time"]
                        dOneAlert["astatus_update"] = lOneAlert[0]["status_update"]
                        dOneAlert["aadditional_props"] = lOneAlert[0]["additional_props"]

                        lTmp = [i.pop(j) for i in lOneAlert for j in
                                ["alertid", "sop_name", "aci_name", "acomponent", "adescription", "anotes", "aseverity",
                                 "alert_created_time", "asource", "astatus", "automationid", "itsmid"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'], reverse=True)
                        # print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                        # print(eachA)
                    # lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=bColSort)
                    print("Python Loop 2 time---> " + str(float(time.time() - s)))
                    # return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                    print({"result": "success", "data": {"alert": lAllAlertDesc, "count": len(lDistinctValues)}})
                    return json.dumps(
                        {"result": "success", "data": {"alert": lAllAlertDesc, "count": iTotalNumberOfAlert}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnStatusFilterOrderBy(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            s = time.time()
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            if filter_key == "customer_id":
                sQuery = "select count(*) total from alert_data where lower(customer_id) like lower('%{0}%')".format(filter_value)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    if dRet["data"][0]["total"] == 0:
                        return json.dumps({"result": "failure", "data": "no data"})

            try:
                sFilterQuery, sSortQuery = "", ""

                # Applying Filter on columns = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += (" to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                    filter_value.split("__")[0].replace("-",
                                                                        "/") + "', 'DD/MON/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                    filter_value.split("__")[1].replace("-", "/") + "', 'DD/MON/YYYY') and ").format(
                        "at time zone '" + sTimeZone + "'",
                        "at time zone '" + sTimeZone + "'")
                elif filter_key == "botname":
                    sFilterQuery += " lower(abr.bot_name) like '%" + \
                                    filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " atd.ticket_no = '" + filter_value.lower() + "' and "
                elif filter_key == "customer_id":
                    sFilterQuery += " lower(a.customer_id) like '%" + filter_value.lower().strip() + "%' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                # Applying sort
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                bColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "botname":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sSortQueryWOAlias = {"alertid": "a.pk_alert_id", "aci_name": "a.ci_name", "acomponent": "a.component",
                                     "automationid": "abr.bot_name", "itsmid": "atd.ticket_no"}

                # Applying Filter based on status
                sStatusCond = "1=1" if pStatus.lower() == "all" else (
                        "a.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data a where " + sStatusCond

                sPaging = " limit " + count_limit + " offset " + from_offset
                sQuery = """
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT))
                  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b order by alertid %s %s""" % (sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort, adColSort, sPaging)
                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQuery)
                lDistinctValues = dDistinctValues['data']['alertid']
                print(lDistinctValues)

                sQuery = """
select count(alertid) as total from (
select distinct(alertid) as alertid from (
select alertid from (
select
    a.pk_alert_id as alertid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT))
                  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and %s and  %s
order by %s %s) a ) b ) c""" % (sStatusCond, sFilterQuery, sSortQueryWOAlias[sSortQuery], adColSort)
                dCountAlertIDs = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                print(dCountAlertIDs)
                iTotalNumberOfAlert = dCountAlertIDs['data'][0]['total']
                print(iTotalNumberOfAlert)

                # Get Alerts because alerts gets missed out on doing query
                # sPaging = " limit " + count_limit + " offset " + from_offset
                # sQueryAlertAssociationIssue = "select alertid from (" + sQuery + ") a " #+ sPaging
                # print("First Query to DB---> " + str(float(time.time()-s)))
                # dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQueryAlertAssociationIssue)
                # print("Time Spent in DB---> " + str(float(time.time()-s)))
                # if dDistinctValues["result"] == "failure":
                #    return json.dumps(dDistinctValues)
                # lOutDV = dDistinctValues["data"]["alertid"]
                # lDistinctValues = []
                # print(sQueryAlertAssociationIssue)
                # print(lOutDV)
                # for eachID in lOutDV:
                #    if lDistinctValues.__contains__(eachID):
                #        continue
                #    else:
                #        lDistinctValues.append(eachID)
                sDistinctValuesData = ",".join([str(i) for i in lDistinctValues])
                #sDistinctValuesData = ",".join([str(i) for i in lDistinctValues][int(from_offset):(int(from_offset) + int(count_limit))])
                print(sDistinctValuesData)
                print("Python Time First Loop---> " + str(float(time.time() - s)))
                # So, the main query will be like
                sMainQuery = """
select 
        distinct concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, sop.sop_name sop_name, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        COALESCE(abr.bot_name, '') as automationid, COALESCE(atd.ticket_no,'')	as itsmid, e.msg_updated_time, e.value, e.cmdline 
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT)) 
		  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id) 
		  left join sop on(a.fk_sop_id=sop.pk_sop_id)
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sDistinctValuesData + """)   
order by """ + sSortQuery + """ """ + adColSort
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'",
                                               "at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                print("Query 2 sent to DB---> " + str(float(time.time() - s)))
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sMainQuery)
                print("Response from DB for Query 2---> " + str(float(time.time() - s)))
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    # print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))  #
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["sop_name"] = lOneAlert[0]["sop_name"]
                        # dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        # dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        # dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        # dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in
                                ["alertid", "sop_name", "aci_name", "acomponent", "adescription", "anotes", "aseverity",
                                 "alert_created_time", "asource", "astatus", "automationid", "itsmid"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'], reverse=True)
                        # print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                        # print(eachA)
                    # lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=bColSort)
                    print("Python Loop 2 time---> " + str(float(time.time() - s)))
                    # return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                    print({"result": "success", "data": {"alert": lAllAlertDesc, "count": len(lDistinctValues)}})
                    return json.dumps(
                        {"result": "success", "data": {"alert": lAllAlertDesc, "count": iTotalNumberOfAlert}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnStatusFilterOrderBySR(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sFilterQuery, sSortQuery = "", ""

                #Applying Filter on colums = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += " to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                       filter_value.split("__")[0].replace("_",
                                                                                 "/") + "', 'MM/DD/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                       filter_value.split("__")[1].replace("_", "/") + "', 'MM/DD/YYYY') and ".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                elif filter_key == "botname":
                    sFilterQuery += " lower(abr.bot_name) like '%" + \
                                       filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " atd.ticket_no = '" + filter_value.lower() + "' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                #Applying sort
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                bColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "botname":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sSortQueryWOAlias = {"alertid": "a.pk_alert_id", "aci_name": "a.ci_name", "acomponent": "a.component", "automationid": "abr.bot_name", "itsmid": "atd.ticket_no"}

                #Applying Filter based on status
                sStatusCond = "1=1" if pStatus.lower() == "all" else ("a.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data a where " + sStatusCond

                sQuery = """
select 
    a.pk_alert_id as alertid      
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT)) 
		  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id) 
where
        a.fk_status_id = s.pk_ea_status_id and 
        e.fk_status_id = s.pk_ea_status_id and 
        a.pk_alert_id = ea.fk_alert_id and 
        e.pk_event_id = ea.fk_event_id and """ + sStatusCond + """ and """ + sFilterQuery + """  
order by """ + sSortQueryWOAlias[sSortQuery] + """ """ + adColSort

                # Get Alerts because alerts gets missed out on doing query
                sPaging = " limit " + count_limit + " offset " + from_offset
                sQueryAlertAssociationIssue = "select alertid from (" + sQuery + ") a " #+ sPaging

                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQueryAlertAssociationIssue)
                if dDistinctValues["result"] == "failure":
                    return json.dumps(dDistinctValues)
                lOutDV = dDistinctValues["data"]["alertid"]
                lDistinctValues = []
                for eachID in lOutDV:
                    if lDistinctValues.__contains__(eachID):
                        continue
                    else:
                        lDistinctValues.append(eachID)
                sDistinctValuesData = ",".join([str(i) for i in lDistinctValues][int(from_offset):(int(from_offset)+int(count_limit))])

                #So, the main query will be like
                sMainQuery = """
select 
        concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        COALESCE(abr.bot_name, '') as automationid, COALESCE(atd.ticket_no,'')	as itsmid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT)) 
		  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id) 
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sDistinctValuesData + """)   
order by """ + sSortQuery + """ """ + adColSort
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                print(sMainQuery)
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sMainQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    #print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        print(eachA)
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))#
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        #dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        #dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        #dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        #dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in ["alertid", "aci_name", "acomponent", "adescription", "anotes", "aseverity", "alert_created_time", "asource", "astatus", "automationid", "itsmid"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'],reverse=True)
                        #print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                        #print(eachA)
                    #lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=bColSort)
                    #return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                    return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": len(lDistinctValues)}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnStatusFilterOrderByLatest(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sFilterQuery, sSortQuery = "", ""

                #Applying Filter on colums = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += " to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                       filter_value.split("__")[0].replace("_",
                                                                                 "/") + "', 'DD/MM/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                       filter_value.split("__")[1].replace("_", "/") + "', 'DD/MM/YYYY') and ".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                elif filter_key == "autoid":
                    sFilterQuery += " (CASE when ae.automationid is not null then concat('A',lpad(cast(ae.automationid as text),14,'0')) else null END) like '%" + \
                                       filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " ae.itsmid = '" + filter_value.lower() + "' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                #Applying sort
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                bColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "autoid":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sSortQueryWOAlias = {"alertid": "a.pk_alert_id", "aci_name": "a.ci_name", "acomponent": "a.component", "automationid": "ae.automationid", "itsmid": "ae.itsmid"}

                #Applying Filter based on status
                sStatusCond = "1=1" if pStatus.lower() == "all" else ("a.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data a where " + sStatusCond

                sQuery = """
select 
    a.pk_alert_id as alertid      
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join automationengine ae on (a.pk_alert_id = CAST( ae.alertid as BIGINT))
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and """ + sStatusCond + """ and """ + sFilterQuery + """  
order by """ + sSortQueryWOAlias[sSortQuery] + """ """ + adColSort

                # Get Alerts because alerts gets missed out on doing query
                sPaging = " limit " + count_limit + " offset " + from_offset
                sQueryAlertAssociationIssue = "select alertid from (" + sQuery + ") a " #+ sPaging

                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQueryAlertAssociationIssue)
                lOutDV = dDistinctValues["data"]["alertid"]
                lDistinctValues = []
                for eachID in lOutDV:
                    if lDistinctValues.__contains__(eachID):
                        continue
                    else:
                        lDistinctValues.append(eachID)
                sDistinctValuesData = ",".join([str(i) for i in lDistinctValues][int(from_offset):(int(from_offset)+int(count_limit))])

                #So, the main query will be like
                sMainQuery = """
select 
        concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        (CASE when ae.automationid is not null then concat('A',lpad(cast(ae.automationid as text),14,'0')) else null END) as automationid, ae.automationstatus,ae.start_time, ae.end_time, ae.itsmid, ae.itsmstatus
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join automationengine ae on (a.pk_alert_id = CAST( ae.alertid as BIGINT))
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sDistinctValuesData + """)   
order by """ + sSortQuery + """ """ + adColSort
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                print(sMainQuery)
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sMainQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    #print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        print(eachA)
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))#
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in ["alertid", "aci_name", "acomponent", "adescription", "anotes", "aseverity", "alert_created_time", "asource", "astatus", "automationid", "automationstatus", "start_time", "end_time", "itsmid", "itsmstatus"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'],reverse=True)
                        #print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                        #print(eachA)
                    #lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=bColSort)
                    #return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                    return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": len(lDistinctValues)}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getEventsBasedOnStatusFilterOrderBy(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            if filter_key == "customer_id":
                sQuery = "select count(*) total from alert_data where lower(customer_id) like lower('%{0}%')".format(filter_value)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    if dRet["data"][0]["total"] == 0:
                        return json.dumps({"result": "failure", "data": "no data"})
            try:
                sFilterQuery, sSortQuery = "", ""

                # Applying Filter on colums = Basic Search
                if filter_key == "event_id":
                    sFilterQuery += " lower(concat('EV',lpad(cast(e.pk_event_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(e.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(e.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += (" to_date(TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                    filter_value.split("__")[0].replace("-",
                                                                        "/") + "', 'DD/MON/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                    filter_value.split("__")[1].replace("-", "/") + "', 'DD/MON/YYYY') and ").format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                elif filter_key == "severity":
                    sFilterQuery += " lower(e.severity) ='" + filter_value.lower() + "' and "
                elif filter_key == "source":
                    sFilterQuery += " lower(e.source) = '" + filter_value.lower() + "' and "
                elif filter_key == "customer_id":
                    sFilterQuery += " lower(e.customer_id) = '" + filter_value.lower() + "' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                # Applying sorting = ASC and DESC
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                if column_sort == "null":
                    sSortQuery += " e.pk_event_id desc"
                else:
                    if adCol == "event_id":
                        sSortQuery += " e.pk_event_id " + adColSort
                    elif adCol == "alert_id":
                        sSortQuery += " a.pk_alert_id " + adColSort
                    elif adCol == "ciname":
                        sSortQuery += " e.ci_name " + adColSort
                    elif adCol == "component":
                        sSortQuery += " e.component " + adColSort
                    elif adCol == "datetime":
                        sSortQuery += " TO_TIMESTAMP(e.event_created_time ) " + adColSort
                    elif adCol == "severity":
                        sSortQuery += " e.severity " + adColSort
                    elif adCol == "source":
                        sSortQuery += " e.source " + adColSort

                #Get Count
                sStatusCond = "1=1" if pStatus.lower() == "all" else ("e.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from event_data e where " + sStatusCond

                sQuery = """
select 
    e.pk_event_id as EventID   
from 
	event_data e, alert_data a, ea_status s, event_alert_mapping ea 
where 
	a.fk_status_id = s.pk_ea_status_id and 
	e.fk_status_id = s.pk_ea_status_id and 
	a.pk_alert_id = ea.fk_alert_id and 
	e.pk_event_id = ea.fk_event_id and """ + sStatusCond + """ and """ + sFilterQuery + """ 
order by """ + sSortQuery

                #Count
                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQuery)

                # Get Alerts because alerts gets missed out on doing query
                sPaging = " limit " + count_limit + " offset " + from_offset
                sQueryAlertAssociationIssue = "select eventid from (" + sQuery + ") e " + sPaging

                #Main Query
                sMainQuery = """ 
select 
    concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, e.ci_name, e.component, e.description, e.notes, e.severity, TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status, e.msg_updated_time, e.value, e.cmdline 
from 
    event_data e, alert_data a, ea_status s, event_alert_mapping ea  
where 
    a.fk_status_id = s.pk_ea_status_id and 
    e.fk_status_id = s.pk_ea_status_id and 
    a.pk_alert_id = ea.fk_alert_id and 
    e.pk_event_id = ea.fk_event_id and e.pk_event_id in(""" + sQueryAlertAssociationIssue + """)  
order by """ + sSortQuery
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'")

                print(sMainQuery)
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sMainQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    #return json.dumps({"result": "success", "data": {"event": dRet["data"], "count": dRetCnt["data"][0]["total"]}})
                    return json.dumps({"result": "success", "data": {"event": dRet["data"], "count": len(dDistinctValues["data"]["eventid"])}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load event details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getDroppedEvents(from_offset, count_limit):
    """Method: Get all dropped events"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sCountQuery = "select count(*) as count from dropped_event where promote_yn='N'"
                sPaging = " limit " + count_limit + " offset " + from_offset
                sQuery = """
select 
	concat('D',lpad(cast(d.pk_dropped_event_id as text),13,'0')) as DroppedEventID, COALESCE(d.ci_name,'') as ci_name, COALESCE(d.component,'') as component, d.description, d.notes, d.severity, TO_CHAR(TO_TIMESTAMP(d.event_created_time) {0}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time , d.source, s.stat_description as status, d.promote_yn as promote_flag 
from 
	dropped_event d, ea_status s  
where 
	d.fk_status_id = s.pk_ea_status_id and d.promote_yn='N' 
order by 
    event_created_time desc """ + sPaging
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'")
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                #dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResultGroupBy(sQuery, ["ci_name", "component"])
                if dRet["result"] == "success":
                    return json.dumps({"result": "success", "data": {"dropped_events" : dRet["data"], "count": dRetCnt["data"][0]["count"]}})
                else:
                    return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def promoteDroppedEvents(dPayload):
    """Methods is used to Promote the Dropped Events
payload: {
	"affected_events": "D0000000000001,D0000000000002,D0000000000003",
	"ci_name": "bkp-02",
	"component": "Memory1",
	"description": "CPU utilization is high",
	"notes": "CPU utilization is Critical. Used : 96%",
	"severity": "critical"
} """
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                lAttr = ["affected_events", "ci_name", "component", "description", "notes", "severity"]
                lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
                lPayValuesErr = [1 if (not i.strip() == "") else 0 for i in dPayload.values()]
                if not ((0 in lPayErr) and (0 in lPayValuesErr)):
                    lAffectedDroppedEvents = dPayload["affected_events"].split(",")
                    sCIName = dPayload["ci_name"]
                    sComponent = dPayload["component"]
                    sDescription = dPayload["description"]
                    sNotes = dPayload["notes"]
                    sSeverity = dPayload["severity"]
                    sDEventsQuery = "select pk_dropped_event_id, ci_name, component, description, notes, severity, event_created_time, source from dropped_event where pk_dropped_event_id in(" + ",".join([i.strip('D').strip('0') for i in lAffectedDroppedEvents]) + ")"
                    dRet = ConnPostgreSQL.returnSelectQueryResult(sDEventsQuery)
                    if dRet["result"] == "success":
                        #configure payload to post to receiver
                        lPOSTOnReceiver, iInit = [], 0
                        for i in dRet["data"]:
                            d = {}
                            d["dropped_event_id"] = str(i["pk_dropped_event_id"])
                            d["ci_name"] = sCIName
                            d["component"] = sComponent
                            if iInit == 0:
                                d["description"] = sDescription
                                d["notes"] = sNotes
                                d["severity"] = sSeverity
                            else:
                                d["description"] = i["description"]
                                d["notes"] = i["notes"]
                                d["severity"] = i["severity"]
                            d["event_created_time"] = str(i["event_created_time"])
                            d["source"] = i["source"]
                            lPOSTOnReceiver.append(d)
                            iInit = 1
                        #POST it to receiver
                        sQuery = "select configip as ip, configport as port from configuration where configname='RECEIVER'"
                        dRetIP = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                        if dRetIP["result"] == "success":
                            sIPAddress = dRetIP["data"][0]["ip"]
                            sPort = str(dRetIP["data"][0]["port"])
                            sURL = "http://" + sIPAddress + ":" + sPort + "/evm/api1.0/endpoints/eventreceiver"
                            sHeader = {'Content-Type': 'application/json'}
                            dResult = {"success_republish": 0, "failure_republish": 0, "success_flagupdate": 0, "failure_flagupdate": 0}
                            for eachPOST in lPOSTOnReceiver:
                                retDetails = restcall.post(url=sURL, json=eachPOST, headers=sHeader)
                                if retDetails.status_code == 200:
                                    dResult["success_republish"] += 1
                                    #Update Promote Flag
                                    sPQuery = "update dropped_event set promote_yn='Y' where pk_dropped_event_id=" + str(eachPOST["dropped_event_id"])
                                    dRetPF = ConnPostgreSQL.returnInsertResult(sPQuery)
                                    if dRetPF["result"] == "success":
                                        dResult["success_flagupdate"] += 1
                                    else:
                                        dResult["failure_flagupdate"] += 1
                                else:
                                    dResult["failure_republish"] += 1
                            return json.dumps({"result": "success", "data": dResult})
                        else:
                            return json.dumps({"result": "failure", "data": "Receiver Configuration is missing in Database"})
                    else:
                        return json.dumps({"result": "failure", "data": "No such Dropped Events available to Promote"})
                else:
                    return json.dumps({"result": "failure", "data": "Either the key or value is missing in the Payload"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAutomationExecutionStageWithAlertID(sAlertID):
    """Methods is used to get the execution stage of BOT"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sQuery = """
select 
	COALESCE(cast(a.pk_alert_id as varchar),'') as alert_id, COALESCE(a.starttime,'') as starttime, COALESCE(a.endtime,'') as endtime, COALESCE(a.status,'GREY') as status, COALESCE(s.stages,'') as stages , COALESCE(a.output,'') as output 
from 
	ai_automation_stages s left join 
	(select
		a.pk_alert_id, TO_CHAR(TO_TIMESTAMP(aeh.starttime) {0}, 'DD/MM/YYYY HH24:MI:SS') starttime, TO_CHAR(TO_TIMESTAMP(aeh.endtime) {1}, 'DD/MM/YYYY HH24:MI:SS') endtime, aeh.status, ast.stages, aeh.output 
	from 
		ai_automation_execution_history aeh, ai_automation_stages ast, alert_data a left join ai_automation_executions ae on(a.pk_alert_id = ae.fk_alert_id) 
	where 
		ae.pk_execution_id = aeh.fk_execution_id and 
		aeh.fk_stage_id = ast.stageid and 
		ae.pk_execution_id = (select pk_execution_id from ai_automation_executions where concat('AL',lpad(cast(fk_alert_id as text),13,'0')) = '""" + sAlertID + """' order by pk_execution_id desc offset 0 limit 1) and 
		concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) = '""" + sAlertID + """' 
	order by 
		aeh.pk_history_id desc) a 
	on (a.stages=s.stages)
order by 
	s.stageid asc"""
                sQuery = sQuery.format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    lModifiedDicts = []
                    for eachDict in dRet["data"]:
                        if eachDict["stages"].upper() == "EXECUTE BOTS / RULES":
                            if eachDict["output"].strip() != "":
                                eachDict["output"] = decode('auto!ntell!', eachDict["output"])
                        lModifiedDicts.append(eachDict)
                    dRet["data"] = lModifiedDicts
                    return json.dumps(dRet)
                else:
                    return json.dumps({"result": "failure", "data": "Unable to fetch Automation Execution details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertsBasedOnStatusFilterOrderBy4OneAlert(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    """Method: get all the events availbale"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sFilterQuery, sSortQuery = "", ""

                #Applying Filter on colums = Basic Search
                if filter_key == "alert_id":
                    sFilterQuery += " lower(concat('AL',lpad(cast(a.pk_alert_id as text),13,'0'))) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "ciname":
                    sFilterQuery += " lower(a.ci_name) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "component":
                    sFilterQuery += " lower(a.component) like '%" + filter_value.lower() + "%' and "
                elif filter_key == "datetime":
                    sFilterQuery += " to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY'), 'DD/MM/YYYY') >= to_date('" + \
                                       filter_value.split("__")[0].replace("_",
                                                                                 "/") + "', 'MM/DD/YYYY') and to_date(TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {1}, 'DD/MM/YYYY'), 'DD/MM/YYYY') <= to_date('" + \
                                       filter_value.split("__")[1].replace("_", "/") + "', 'MM/DD/YYYY') and ".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                elif filter_key == "botname":
                    sFilterQuery += " lower(abr.bot_name) like '%" + \
                                       filter_value.lower() + "%' and "
                elif filter_key == "ticketid":
                    sFilterQuery += " atd.ticket_no = '" + filter_value.lower() + "' and "
                elif filter_key == "null":
                    sFilterQuery += " 1=1 and "
                sFilterQuery = sFilterQuery[:-4]

                #Applying sort
                adCol = column_sort[:-2]
                adColSort = "asc" if column_sort[-1] == "a" else "desc"
                bColSort = False if column_sort[-1] == "a" else True
                if column_sort == "null":
                    sSortQuery = "alertid"
                else:
                    if adCol == "alert_id":
                        sSortQuery = "alertid"
                    elif adCol == "ciname":
                        sSortQuery = "aci_name"
                    elif adCol == "component":
                        sSortQuery = "acomponent"
                    elif adCol == "datetime":
                        sSortQuery = "alertid"
                    elif adCol == "botname":
                        sSortQuery = "automationid"
                    elif adCol == "ticketid":
                        sSortQuery = "itsmid"

                sSortQueryWOAlias = {"alertid": "a.pk_alert_id", "aci_name": "a.ci_name", "acomponent": "a.component", "automationid": "abr.bot_name", "itsmid": "atd.ticket_no"}

                #Applying Filter based on status
                sStatusCond = "1=1" if pStatus.lower() == "all" else ("a.fk_status_id=(select pk_ea_status_id from ea_status where stat_description='" + pStatus + "')")
                sCountQuery = "select count(*) as total from alert_data a where " + sStatusCond

                sQuery = """
select 
    a.pk_alert_id as alertid      
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT)) 
		  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id) 
where
        a.fk_status_id = s.pk_ea_status_id and 
        e.fk_status_id = s.pk_ea_status_id and 
        a.pk_alert_id = ea.fk_alert_id and 
        e.pk_event_id = ea.fk_event_id and """ + sStatusCond + """ and """ + sFilterQuery + """  
order by """ + sSortQueryWOAlias[sSortQuery] + """ """ + adColSort

                # Get Alerts because alerts gets missed out on doing query
                sPaging = " limit " + count_limit + " offset " + from_offset
                sQueryAlertAssociationIssue = "select alertid from (" + sQuery + ") a " #+ sPaging

                dDistinctValues = ConnPostgreSQL.returnSelectQueryResultAsList(sQueryAlertAssociationIssue)
                if dDistinctValues["result"] == "failure":
                    return json.dumps(dDistinctValues)
                lOutDV = dDistinctValues["data"]["alertid"]
                lDistinctValues = []
                for eachID in lOutDV:
                    if lDistinctValues.__contains__(eachID):
                        continue
                    else:
                        lDistinctValues.append(eachID)
                sDistinctValuesData = ",".join([str(i) for i in lDistinctValues][int(from_offset):(int(from_offset)+int(count_limit))])

                #So, the main query will be like
                sMainQuery = """
select 
        concat('AL',lpad(cast(a.pk_alert_id as text),13,'0')) as AlertID, a.ci_name as aci_name, a.component as acomponent, a.description as adescription, a.notes as anotes, a.severity as aseverity,TO_CHAR(TO_TIMESTAMP(a.event_created_time ) {0}, 'DD/MM/YYYY HH24:MI:SS')  as alert_created_time, a.source as asource, s.stat_description as astatus,
        concat('EV',lpad(cast(e.pk_event_id as text),13,'0')) as EventID, e.ci_name,e.component, e.description, e.notes, e.severity,TO_CHAR(TO_TIMESTAMP(e.event_created_time ) {1}, 'DD/MM/YYYY HH24:MI:SS') as event_created_time, e.source, s.stat_description as status,
        COALESCE(abr.bot_name, '') as automationid, COALESCE(atd.ticket_no,'')	as itsmid
from
         event_data e, ea_status s, event_alert_mapping ea, alert_data a left join ai_automation_executions ae on (a.pk_alert_id = CAST( ae.fk_alert_id as BIGINT)) 
		  left join ai_bot_repo abr on (ae.fk_bot_id = abr.pk_bot_id) left join ai_ticket_details atd on (a.pk_alert_id = atd.fk_alert_id) 
where
        a.fk_status_id = s.pk_ea_status_id and
        e.fk_status_id = s.pk_ea_status_id and
        a.pk_alert_id = ea.fk_alert_id and
        e.pk_event_id = ea.fk_event_id and a.pk_alert_id in(""" + sDistinctValuesData + """)   
order by """ + sSortQuery + """ """ + adColSort
                sMainQuery = sMainQuery.format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                print(sMainQuery)
                dRetCnt = ConnPostgreSQL.returnSelectQueryResult(sCountQuery)
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sMainQuery)
                if dRet["result"] == "success" and dRetCnt["result"] == "success":
                    lModAsStr = [list(map(str, i)) for i in dRet['data']]
                    setUniqueAlert = set([i[0] for i in lModAsStr[1:]])
                    #print(setUniqueAlert)
                    lPack = [dict(zip(lModAsStr[0], i)) for i in lModAsStr[1:]]
                    lAllAlert = []
                    for eachA in setUniqueAlert:
                        print(eachA)
                        lOneAlert, dOneAlert = [], {}
                        for eachD in lPack:
                            if eachD["alertid"] == eachA:
                                lOneAlert.append(deepcopy(eachD))#
                        dOneAlert["alertid"] = eachA
                        dOneAlert["aci_name"] = lOneAlert[0]["aci_name"]
                        dOneAlert["acomponent"] = lOneAlert[0]["acomponent"]
                        dOneAlert["adescription"] = lOneAlert[0]["adescription"]
                        dOneAlert["anotes"] = lOneAlert[0]["anotes"]
                        dOneAlert["aseverity"] = lOneAlert[0]["aseverity"]
                        dOneAlert["alert_created_time"] = lOneAlert[0]["alert_created_time"]
                        dOneAlert["asource"] = lOneAlert[0]["asource"]
                        dOneAlert["astatus"] = lOneAlert[0]["astatus"]
                        dOneAlert["automationid"] = lOneAlert[0]["automationid"]
                        #dOneAlert["automationstatus"] = lOneAlert[0]["automationstatus"]
                        #dOneAlert["start_time"] = lOneAlert[0]["start_time"]
                        #dOneAlert["end_time"] = lOneAlert[0]["end_time"]
                        dOneAlert["itsmid"] = lOneAlert[0]["itsmid"]
                        #dOneAlert["itsmstatus"] = lOneAlert[0]["itsmstatus"]
                        lTmp = [i.pop(j) for i in lOneAlert for j in ["alertid", "aci_name", "acomponent", "adescription", "anotes", "aseverity", "alert_created_time", "asource", "astatus", "automationid", "itsmid"]]
                        dOneAlert["associated_events"] = sorted(lOneAlert, key=lambda k: k['eventid'],reverse=True)
                        #print(dOneAlert)
                        lAllAlert.append(dOneAlert)
                        #print(eachA)
                    #lAllAlertDesc = sorted(lAllAlert, key=lambda k: k['alertid'], reverse=True)
                    lAllAlertDesc = sorted(lAllAlert, key=lambda k: k[sSortQuery], reverse=bColSort)
                    #return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": dRetCnt["data"][0]["total"]}})
                    return json.dumps({"result": "success", "data": {"alert": lAllAlertDesc, "count": len(lDistinctValues)}})
                else:
                    return json.dumps({"result": "failure", "data": "Failed to load alert details"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def filterRetention(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if val.isPayloadValid(dPayload=dPayload, lHeaders=["created_by", "noofdays"], lMandatory=["created_by", "noofdays"]):
                    uQuery = "update filters_retention set active_yn='N' where active_yn='Y' returning pk_fret_id"
                    uRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(uQuery)
                    if uRet['result'] == 'success':
                        refID = uRet['data'][0]['pk_fret_id']
                        iQuery = "insert into filters_retention(nofdays, created_date, created_by, active_yn) values({0}, now(), '{1}', 'Y')".format(
                            dPayload['noofdays'], dPayload['created_by']
                        )
                        iRet = ConnPostgreSQL.returnInsertResult(iQuery)
                        if iRet['result'] == 'success':
                            return json.dumps({"result": "success", "data": "Retention policy changed"})
                        else:
                            logERROR("Filter retention policy creation failed. Reason:{0}".format(iRet['data']))

                            # RollBack
                            uQuery = "update filters_retention set active_yn='Y' where pk_fret_id={0}".format(refID)
                            uRet = ConnPostgreSQL.returnInsertResult(uQuery)
                            if uRet['result'] == 'failure':
                                logERROR("Filter retention rollback failed. Reason:{0}".format(uRet['data']))
                                # Critical alert has to be pushed to developer for action

                            return json.dumps({"result": "failure", "data": "Something went wrong try after sometimes."})
                    else:
                        logERROR("Filter retention updation failed. Reason:{0}".format(uRet['data']))
                        return json.dumps({"result": "failure", "data": "Something went wrong try after sometimes."})
                else:
                    return json.dumps({"result": "failure", "data": "Invalid Payload"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getfilterRetention():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select nofdays, to_char(created_date, 'DD-MM-YYYY HH24:MI') created_date, created_by from filters_retention where active_yn='Y'"
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet['result'] == 'success':
                    return json.dumps(dRet)
                else:
                    logERROR("Filter retention get information failed. Reason:{0}".format(dRet['data']))
                    return json.dumps({"result": "failure", "data": "Something went wrong try after sometimes."})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def pin_unpin(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if val.isPayloadValid(dPayload=dPayload, lHeaders=["action", "alert_id", "user_id"], lMandatory=["action", "alert_id", "user_id"]):
                    iuQuery = ""
                    if dPayload["action"] == "pin":
                        iuQuery = "insert into alert_pin_unpin(fk_alert_id, fk_user_id, created_on) values({0},{1},now())".format(
                            int(dPayload['alert_id'].strip('AL')), dPayload['user_id']
                        )
                    elif dPayload["action"] == "unpin":
                        iuQuery = "delete from alert_pin_unpin where fk_alert_id={0} and fk_user_id={1}".format(
                            int(dPayload['alert_id'].strip('AL')), dPayload['user_id']
                        )
                    else:
                        return json.dumps({"result": "failure", "data": "Invalid Action"})
                    dRet = ConnPostgreSQL.returnInsertResult(iuQuery)
                    if dRet['result'] == 'success':
                        return json.dumps({'result': 'success', 'data': 'Done!'})
                    else:
                        return json.dumps({'result': 'failure', 'data': 'Failed!'})
                else:
                    return json.dumps({"result": "failure", "data": "Invalid Payload"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def clearAlerts(alert_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                alert_id = int(alert_id.strip('AL'))
                sQuery = '''
                select 
                    msg_updated_time, customer_id, priority, ci_name Machine, component Application, value, cmdline Cmdline, description Description, 
                    notes Extra_Description, 'OK' severity, source, extract(epoch from now()) event_created_time, id, asset_number, region, asset_state, version, package, pac_ver, 
                    pac_ver_no, msg_created_time, status_update, additional_props, modified_by from event_data where pk_event_id=(select max(fk_event_id) 
                from 
                    event_alert_mapping where fk_alert_id={0})'''.format(alert_id)
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet['result'] == 'success':
                    dPayload = dRet['data'][0]
                    ret = connmq.send2MQ(pQueue='datalake', pExchange='EVM', pRoutingKey='datalake',
                                         pData=json.dumps(dPayload))
                    return json.dumps({'result': 'success', 'data': 'Alert Cleared'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed!'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

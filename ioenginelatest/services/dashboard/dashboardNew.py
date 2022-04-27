#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, request
import json
from datetime import datetime, timedelta
import pytz
from services.utils.ConnPostgreSQL import returnSelectQueryResult, returnSelectQueryResultConvert2Col2Dict, returnSelectQueryResultAsList
from services.utils import sessionkeygen
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc

#https://github.com/corydolphin/flask-cors/blob/master/examples/app_based_example.py

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

def returnQueryCondition(pCond, pColumnName, pDate=0, pTimeZone='Asia/Kolkata'):
    # Date Management
    dTZ = datetime.now().astimezone(pytz.timezone(pTimeZone))
    wToday = dTZ.strftime('%d-%b-%Y')
    wYesterday = (dTZ - timedelta(days=1)).strftime('%d-%b-%Y')
    wWeekStart = (dTZ - timedelta(days=dTZ.weekday())).strftime('%d-%b-%Y')
    wWeekEnd = ((dTZ - timedelta(days=dTZ.weekday())) + timedelta(days=6)).strftime('%d-%b-%Y')
    wMonthStart =  dTZ.today().replace(day=1).strftime('%d-%b-%Y')
    wMonthEnd = wToday
    wPreviousMonthEnd = (datetime.strptime(wMonthStart, '%d-%b-%Y') - timedelta(days=1)).strftime('%d-%b-%Y')
    wPreviousMonthStart = (datetime.strptime(wPreviousMonthEnd, '%d-%b-%Y').replace(day=1)).strftime('%d-%b-%Y')

    pCond = pCond.lower()
    sQueryCond = ""
    if pCond == "all":
        sQueryCond = "1=1"
    elif pCond == "today":
        sQueryCond = pColumnName + " >= to_date('" + wToday + "','DD-MON-YYYY')"
    elif pCond == "yesterday":
        sQueryCond = pColumnName + " >= to_date('" + wYesterday + "','DD-MON-YYYY') and " + pColumnName + " < to_date('" + wToday + "','DD-MON-YYYY')"
    elif pCond == "this_week":
        sQueryCond = pColumnName + " >= to_date('" + wWeekStart + "','DD-MON-YYYY') and " + pColumnName + " <= to_date('" + wWeekEnd + "','DD-MON-YYYY')"
    elif pCond == "this_month":
        sQueryCond = pColumnName + " >= to_date('" + wMonthStart + "','DD-MON-YYYY') and " + pColumnName + " <= to_date('" + wMonthEnd + "','DD-MON-YYYY')"
    elif pCond == "last_month":
        sQueryCond = pColumnName + " >= to_date('" + wPreviousMonthStart + "','DD-MON-YYYY') and " + pColumnName + " <= to_date('" + wPreviousMonthEnd + "','DD-MON-YYYY')"
    elif pCond == "date_range":
        sFromDate = pDate.strip().split('__')[0].replace('_','-')
        sEndDate = pDate.strip().split('__')[1].replace('_', '-')
        sQueryCond = pColumnName + " >= to_date('" + sFromDate + "','DD-MON-YYYY') and " + pColumnName + " <= to_date('" + sEndDate + "','DD-MON-YYYY')"
    return sQueryCond

##################################################################################
# Event Management Section
##################################################################################

# Header  = 5
##################################################################################
def getSuppPercent(when, date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sDropQuery = "select count(*) as dropped_count from dropped_event where " + sWhereCondition1
                sSupQuery = "select count(*) as suppression_count from event_data where " + sWhereCondition1
                rDropCount = returnSelectQueryResult(sDropQuery)
                rSupQuery = returnSelectQueryResult(sSupQuery)
                if rDropCount["result"] == "success" and rSupQuery["result"] == "success":
                    iDropCount = rDropCount["data"][0]["dropped_count"]
                    iSupCount = rSupQuery["data"][0]["suppression_count"]
                    total = iDropCount + iSupCount
                    drop = ((iDropCount/total) * 100) if total !=0 else 0
                    sup = ((iSupCount/total) * 100) if total != 0 else 0
                    retFinal = {"total": total, "suppressed_count": iSupCount, "dropped_count": iDropCount, "dropped_percent": "%.2f" %(drop), "suppressed_percent": "%.2f" %(sup)}
                    return json.dumps({"result": "success", "data": retFinal})
                else:
                    return logAndRet("failure", "no data")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

# Donuts   = 3
##################################################################################
def getTop5CI(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                dFinalDict = {}
                sQuery = "select ci_name,count(ci_name) from event_data where " + sWhereCondition1 + " group by ci_name order by count(ci_name) desc limit 5"
                retQuery = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                return json.dumps(retQuery)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTop3AlertProducingComp(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = "select component,count(component) as total from alert_data where " + sWhereCondition1 + " group by component order by total desc LIMIT 3"
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAlertBySeverity(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = "select lower(severity), count(lower(severity)) from alert_data where " + sWhereCondition1 + " and lower(severity) not in ('ok') group by lower(severity)"
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

# HeatMap   = 2
##################################################################################
def getWeeklyHeatMap():
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sQueryEve = "select to_char(to_timestamp(event_created_time) {0},'DD-MON-YY HH24') as EventDate,count(*) Cnt from event_data where to_timestamp(event_created_time) {1} > ( now() {2} - INTERVAL '30 DAY') group by EventDate".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                sQueryAle = "select to_char(to_timestamp(event_created_time) {0},'DD-MON-YY HH24') as AlertDate,count(*) Cnt from alert_data where to_timestamp(event_created_time) {1} > ( now() {2} - INTERVAL '30 DAY') group by AlertDate".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                dRetE = returnSelectQueryResult(sQueryEve)
                dRetA = returnSelectQueryResult(sQueryAle)
                if dRetE["result"] == "success" and dRetA["result"] == "success":

                    #lXAxis, lEveAxis, lAleAxis = [], [], []
                    lFinalResult = {}
                    lMainEeventHM, lMainAlertHM = [], []
                    iWeekNumber = 0
                    dTZ = datetime.now().astimezone(pytz.timezone(sTimeZone)) #newly added
                    today = dTZ
                    minus = today.weekday()
                    today = today - timedelta(days=minus)
                    iWeekNumber = today.isocalendar()[1]
                    sStartDateTime = today.strftime("%d-%b-%Y").upper()
                    sEndDateTime = ((today + timedelta(days=6)).strftime('%d-%b-%Y')).upper()
                    for i in range(0,7):
                        lXAxis, lEveAxis, lAleAxis = [], [], []
                        ftime = ((today + timedelta(days=i)).strftime('%d-%b-%y')).upper()
                        td = datetime.strptime(ftime,'%d-%b-%y')

                        for j in range(0,24):
                            sRefDate = (td + timedelta(hours=j)).strftime("%d-%b-%y %H").upper()

                            dEveGroup =  {eD['eventdate'].upper():eD["cnt"] for eD in dRetE["data"]}
                            lEveGroup = dEveGroup.keys()
                            lXAxis.append(sRefDate)
                            if sRefDate in lEveGroup:
                                lEveAxis.append(dEveGroup[sRefDate])
                                lMainEeventHM.append([i,j,dEveGroup[sRefDate]])
                            else:
                                lEveAxis.append(0)
                                lMainEeventHM.append([i, j, 0])

                            dAleGroup = {aD['alertdate'].upper(): aD["cnt"] for aD in dRetA["data"]}
                            lAleGroup = dAleGroup.keys()
                            if sRefDate in lAleGroup:
                                lAleAxis.append(dAleGroup[sRefDate])
                                lMainAlertHM.append([i,j,dAleGroup[sRefDate]])
                            else:
                                lAleAxis.append(0)
                                lMainAlertHM.append([i, j, 0])

                    lFinalResult["WeekNumber"] = "Week :" + str(iWeekNumber) + " (" + sStartDateTime + " to " + sEndDateTime + ")"
                    lFinalResult["EventCoords"] = lMainEeventHM
                    lFinalResult["AlertCoords"] = lMainAlertHM

                    return json.dumps({"result": "success", "data": lFinalResult })

                else:
                    return json.dumps({"result": "failure", "data": "no data found"})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getWeeklyHeatMapForParticularWeek(weeknumber):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sQueryEve = "select to_char(to_timestamp(event_created_time) {0},'DD-MON-YY HH24') as EventDate,count(*) Cnt from event_data where to_timestamp(event_created_time) {1} > ( now() {2} - INTERVAL '30 DAY') group by EventDate".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                sQueryAle = "select to_char(to_timestamp(event_created_time) {0},'DD-MON-YY HH24') as AlertDate,count(*) Cnt from alert_data where to_timestamp(event_created_time) {1} > ( now() {2} - INTERVAL '30 DAY') group by AlertDate".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                dRetE = returnSelectQueryResult(sQueryEve)
                dRetA = returnSelectQueryResult(sQueryAle)
                if dRetE["result"] == "success" and dRetA["result"] == "success":

                    #lXAxis, lEveAxis, lAleAxis = [], [], []
                    weeknumber = int(weeknumber)
                    lFinalResult = {}
                    lMainEeventHM, lMainAlertHM = [], []
                    iWeekNumber = 0
                    dTZ = datetime.now().astimezone(pytz.timezone(sTimeZone))  # newly added
                    today = dTZ
                    minus = today.weekday()
                    today = today - timedelta(days=minus)
                    iWeekNumber = today.isocalendar()[1]

                    if iWeekNumber == weeknumber or iWeekNumber > weeknumber:

                        iToBeIncreased = iWeekNumber - weeknumber
                        today = today - timedelta(days=(iToBeIncreased*7))
                        iWeekNumber = today.isocalendar()[1]

                        sStartDateTime = today.strftime("%d-%b-%Y").upper()
                        sEndDateTime = ((today + timedelta(days=6)).strftime('%d-%b-%Y')).upper()
                        for i in range(0, 7):
                            lXAxis, lEveAxis, lAleAxis = [], [], []
                            ftime = ((today + timedelta(days=i)).strftime('%d-%b-%y')).upper()
                            td = datetime.strptime(ftime, '%d-%b-%y')

                            for j in range(0, 24):
                                sRefDate = (td + timedelta(hours=j)).strftime("%d-%b-%y %H").upper()

                                dEveGroup = {eD['eventdate'].upper(): eD["cnt"] for eD in dRetE["data"]}
                                lEveGroup = dEveGroup.keys()
                                lXAxis.append(sRefDate)
                                if sRefDate in lEveGroup:
                                    lEveAxis.append(dEveGroup[sRefDate])
                                    lMainEeventHM.append([i, j, dEveGroup[sRefDate]])
                                else:
                                    lEveAxis.append(0)
                                    lMainEeventHM.append([i, j, 0])

                                dAleGroup = {aD['alertdate'].upper(): aD["cnt"] for aD in dRetA["data"]}
                                lAleGroup = dAleGroup.keys()
                                if sRefDate in lAleGroup:
                                    lAleAxis.append(dAleGroup[sRefDate])
                                    lMainAlertHM.append([i, j, dAleGroup[sRefDate]])
                                else:
                                    lAleAxis.append(0)
                                    lMainAlertHM.append([i, j, 0])

                        lFinalResult["WeekNumber"] = "Week :" + str(iWeekNumber) + " (" + sStartDateTime + " to " + sEndDateTime + ")"
                        lFinalResult["EventCoords"] = lMainEeventHM
                        lFinalResult["AlertCoords"] = lMainAlertHM

                        return json.dumps({"result": "success", "data": lFinalResult})
                    else:
                        return json.dumps({"result": "failure", "data": "invalid week request"})

                else:
                    return json.dumps({"result": "failure", "data": "no data found"})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

# Bar Chart   = 1
##################################################################################
def alertseveritytrendBC():
    """Method: Returns the 7 days severity trend"""
    #return json.dumps({"result": "failure", "data":"this api method is not active from the version 1.1"})
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                sDateQuery = "select alertdate as date from view_7days_severity where severity='WARNING' order by to_date(alertdate,'DD-MON-YYYY') desc"
                sWarnQuery = "select total as warning from view_7days_severity where severity='WARNING' order by to_date(alertdate,'DD-MON-YYYY') desc"
                sCriticalQuery = "select total as critical from view_7days_severity where severity='CRITICAL' order by to_date(alertdate,'DD-MON-YYYY') desc"
                retResult1 = returnSelectQueryResultAsList(sDateQuery)
                retResult2 = returnSelectQueryResultAsList(sWarnQuery)
                retResult3 = returnSelectQueryResultAsList(sCriticalQuery)
                retFinal = retResult1['data']
                retFinal.update(retResult2['data'])
                retFinal.update(retResult3['data'])
                retFinal["result"] = "success"
                return json.dumps(retFinal)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


##################################################################################
# Executive Summary
##################################################################################

# Header   = 4
##################################################################################
def getExecutiveHeaders(when, date):
    """Method: Return the main header on executive summary page"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            sWhereCondition2 = returnQueryCondition(when, "to_date(to_char(to_timestamp(created_date) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            sWhereCondition3 = returnQueryCondition(when, "to_date(to_char(to_timestamp(starttime) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            sWhereCondition4 = returnQueryCondition(when, "to_date(to_char(start_date {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            iTotEvents, iTotAlerts, iTotTickets, iTotAutomations, iTotWorkflows = 0, 0, 0, 0, 0
            dRetFinal = {}
            try:
                sEventQuery = "select count(*) as event_count from event_data where " + sWhereCondition1
                sAlertQuery = "select count(*) as alert_count from alert_data where " + sWhereCondition1
                sTicketQuery = "select count(ticket_no) as ticket_count from ai_ticket_details where ticket_no is not null and " + sWhereCondition2
                sAutoQuery = "select count(fk_bot_id) as automation_count from ai_automation_executions where " + sWhereCondition3
                sTotalWFs = "select count(*) as workflow_count from processinstancelog where " + sWhereCondition4

                dEveRS = returnSelectQueryResult(sEventQuery)
                dAleRS = returnSelectQueryResult(sAlertQuery)
                dTktRS = returnSelectQueryResult(sTicketQuery)
                dAutoRS = returnSelectQueryResult(sAutoQuery)
                dWFRS = returnSelectQueryResult(sTotalWFs, sDB="jbpm")

                iTotEvents = dEveRS["data"][0]["event_count"] if dEveRS["result"] == "success" else 0
                iTotAlerts = dAleRS["data"][0]["alert_count"] if dAleRS["result"] == "success" else 0
                iTotTickets = dTktRS["data"][0]["ticket_count"] if dTktRS["result"] == "success" else 0
                iTotAutomations = dAutoRS["data"][0]["automation_count"] if dAutoRS["result"] == "success" else 0
                iTotWorkflow = dWFRS["data"][0]["workflow_count"] if dWFRS["result"] == "success" else 0

                dRetFinal["Total_Events"] = iTotEvents
                dRetFinal["Total_Alerts"] = iTotAlerts
                dRetFinal["Total_Tickets"] = iTotTickets
                dRetFinal["Total_Automations"] = iTotAutomations
                dRetFinal["Total_Workflows"] = iTotWorkflow
                return json.dumps({"result": "success", "data": dRetFinal})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getExecutiveHeadersDyD(when, date, what):
    """Method: Return the main header on executive summary page"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            sWhereCondition2 = returnQueryCondition(when, "to_date(to_char(to_timestamp(created_date) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            sWhereCondition3 = returnQueryCondition(when, "to_date(to_char(to_timestamp(starttime) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            sWhereCondition4 = returnQueryCondition(when, "to_date(to_char(start_date {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            iTotEvents, iTotAlerts, iTotTickets, iTotAutomations, iTotWorkflows = 0, 0, 0, 0, 0
            dRetFinal = {}
            try:
                sEventQuery = "select count(*) as event_count from event_data where " + sWhereCondition1
                sAlertQuery = "select count(*) as alert_count from alert_data where " + sWhereCondition1
                sTicketQuery = "select count(ticket_no) as ticket_count from ai_ticket_details where ticket_no is not null and " + sWhereCondition2
                sAutoQuery = "select count(fk_bot_id) as automation_count from ai_automation_executions where " + sWhereCondition3
                sTotalWFs = "select count(*) as workflow_count from processinstancelog where " + sWhereCondition4

                dEveRS = returnSelectQueryResult(sEventQuery)
                dAleRS = returnSelectQueryResult(sAlertQuery)
                dTktRS = returnSelectQueryResult(sTicketQuery)
                dAutoRS = returnSelectQueryResult(sAutoQuery)
                dWFRS = returnSelectQueryResult(sTotalWFs, sDB="jbpm")

                iTotEvents = dEveRS["data"][0]["event_count"] if dEveRS["result"] == "success" else 0
                iTotAlerts = dAleRS["data"][0]["alert_count"] if dAleRS["result"] == "success" else 0
                iTotTickets = dTktRS["data"][0]["ticket_count"] if dTktRS["result"] == "success" else 0
                iTotAutomations = dAutoRS["data"][0]["automation_count"] if dAutoRS["result"] == "success" else 0
                iTotWorkflow = dWFRS["data"][0]["workflow_count"] if dWFRS["result"] == "success" else 0

                dRetFinal["Total Events"] = iTotEvents
                dRetFinal["Total Alerts"] = iTotAlerts
                dRetFinal["Total Tickets"] = iTotTickets
                dRetFinal["Total BOTs Executed"] = iTotAutomations
                dRetFinal["Total Workflows Executed"] = iTotWorkflow
                out = {}
                what = what.replace('_',' ')
                out[what] = dRetFinal[what]
                return json.dumps({"result": "success", "data": out})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


# BarChart   = 3
##################################################################################
def getAlertBySeverityBC(when,date):
    """Method: Returns the alert by severity"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = """select 
                	Main.severity, COALESCE(Child.cnt,0) as total
                from 
                	(SELECT X.*
                		FROM   (VALUES ('critical',0),
                				('warning',0),
                				('unknown',0)
                	) AS X (severity,cnt)) as Main
                	left join
                	(select lower(severity) severity, count(lower(severity)) cnt from  event_data where """ + sWhereCondition1 + """ and lower(severity) not in ('ok') group by lower(severity)) as Child
                	on 
                	Main.severity = Child.severity"""
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery, SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTicketByStatusBC(when,date):
    """Method: Returns the ticket by status"""
    return json.dumps({"result":"success", "data":"under construction"})

def getAutomationTypeBC(when,date):
    """Method: Returns the automation type like number of alert resolved as Remediation or Diagnosis"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(aae.starttime) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = """
select 
	(case 
		when z.automationtype = 'D' then 'Diagnosis'
		when z.automationtype = 'R' then 'Remediation'
	END) as automationtype, z.total from 
(select 
	Main.automationtype, COALESCE(Child.cnt,0) as total
from 
	(SELECT X.*
		FROM   (VALUES ('D',0),
				('R',0)
	) AS X (automationtype,cnt)) as Main
	left join
	(select bot_type as automationtype, count(bot_type) as cnt from ai_bot_repo abr, ai_automation_executions aae where abr.pk_bot_id = aae.fk_bot_id and """ + sWhereCondition1 + """ group by bot_type) as Child
	on 
	Main.automationtype = Child.automationtype
) z	"""
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery, SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getWorkflowByStatusBC(when,date):
    """Method: Returns the workflow by status"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(start_date {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = """select 
	(case 
		when z.status = 0 then 'Pending'
		when z.status = 1 then 'Active'
		when z.status = 2 then 'Completed'
		when z.status = 3 then 'Aborted'
		when z.status = 4 then 'Suspended'
	END) as status, z.total from 
(select 
	Main.status, COALESCE(Child.cnt,0) as total
from 
	(SELECT X.*
		FROM   (VALUES (0,0),
				(1,0),
				(2,0),
				(3,0),
				(4,0)
	) AS X (status,cnt)) as Main
	left join
	(select status,count(status) as cnt from processinstancelog where """ + sWhereCondition1 + """ group by status) as Child
	on 
	Main.status = Child.status
) z	"""
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery, SortByVal=True, sDB="jbpm")
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


# Donuts   = 6
##################################################################################
def getAlertBySeverityStatus(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = """select 
	Main.status, COALESCE(Child.cnt,0) as total
from 
	(SELECT X.*
		FROM   (VALUES ('open',0),
				('wip',0),
				('pending',0),
				('resolved',0),
				('closed',0)
	) AS X (status,cnt)) as Main
	left join
	(select lower(ea.stat_description) status, count(ea.stat_description) cnt from alert_data a, ea_status ea where """ + sWhereCondition1 + """ and a.fk_status_id=ea.pk_ea_status_id group by lower(ea.stat_description)) as Child
	on 
	Main.status = Child.status"""
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getAutomationStatus(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(starttime) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = """select 
	Main.automation_status, COALESCE(Child.cnt, 0) as total
from 
	(SELECT X.*
		FROM   (VALUES ('in progress',0),
				('completed',0),
				('closed',0),
				('failed',0)
	) AS X (automation_status,cnt)) as Main
	left join
	(select 
		lower(execution_status) as automation_status, count(lower(execution_status)) as cnt 
	from 
		ai_automation_executions where """ + sWhereCondition1 + """
	group by 
		lower(execution_status)) as Child
	on
		Main.automation_status = Child.automation_status"""
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTicketStatus(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(created_date) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = """select 
	Main.itsm_status, COALESCE(Child.cnt, 0) as total
from 
	(SELECT X.*
		FROM   (VALUES ('open',0),
				('in progress',0),
				('resolved',0)
	) AS X (itsm_status,cnt)) as Main
	left join
	(select 
		lower(ticket_status) as itsm_status, count(lower(ticket_status)) as cnt 
	from 
		ai_ticket_details 
	where """ + sWhereCondition1 + """ 
	group by 
		lower(ticket_status)) as Child
	on
		Main.itsm_status = Child.itsm_status"""
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTop5AlertProducingComp(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = "select component,count(component) as total from alert_data where " + sWhereCondition1 + " group by component order by total desc LIMIT 5"
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTop5Automation(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(aae.starttime) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = """select 
	abr.bot_name, count(abr.bot_name) as total 
from 
	ai_bot_repo abr, ai_automation_executions aae 
where 
	abr.pk_bot_id = aae.fk_bot_id and """ + sWhereCondition1 + """ 
 group by 
	abr.bot_name 
order by total desc LIMIT 5"""
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery,SortByVal=True)
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getTop5Workflow(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(start_date {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQuery = "select processinstancedescription workflow, count(processinstancedescription) cnt from  processinstancelog where " + sWhereCondition1 + " group by processinstancedescription order by cnt desc limit 5"
                retResult = returnSelectQueryResultConvert2Col2Dict(sQuery, SortByVal=True, sDB="jbpm")
                return json.dumps(retResult)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

# Waves   = 1
##################################################################################
def getSuppressionFor30Days(when,date):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            dTZ = datetime.now().astimezone(pytz.timezone(sTimeZone))
            wToday = dTZ.strftime('%d-%b-%Y')
            wYesterday = (dTZ - timedelta(days=1)).strftime('%d-%b-%Y')
            wWeekStart = (dTZ - timedelta(days=dTZ.weekday())).strftime('%d-%b-%Y')
            wWeekEnd = ((dTZ - timedelta(days=dTZ.weekday())) + timedelta(days=6)).strftime('%d-%b-%Y')
            wMonthStart = dTZ.today().replace(day=1).strftime('%d-%b-%Y')
            wMonthEnd = wToday
            wPreviousMonthEnd = (datetime.strptime(wMonthStart, '%d-%b-%Y') - timedelta(days=1)).strftime('%d-%b-%Y')
            wPreviousMonthStart = (datetime.strptime(wPreviousMonthEnd, '%d-%b-%Y').replace(day=1)).strftime('%d-%b-%Y')
            sWhereCondition1 = returnQueryCondition(when, "to_date(to_char(to_timestamp(event_created_time) {0},'DD-MON-YYYY'),'DD-MON-YYYY')".format("at time zone '" + sTimeZone + "'"), date, sTimeZone)
            try:
                sQueryEve, sQueryAle = "", ""
                if when in ["this_month", "last_month", "date_range"]:
                    sQueryEve = "select to_char(to_timestamp(event_created_time) {0},'DD-MON-YY') as EventDate,count(*) Cnt from event_data where " + sWhereCondition1 + " group by EventDate".format("at time zone '" + sTimeZone + "'")
                    sQueryAle = "select to_char(to_timestamp(event_created_time) {0},'DD-MON-YY') as AlertDate,count(*) Cnt from alert_data where " + sWhereCondition1 + " group by AlertDate".format("at time zone '" + sTimeZone + "'")
                else:
                    sQueryEve = "select to_char(to_timestamp(event_created_time) {0},'DD-MON-YY') as EventDate,count(*) Cnt from event_data where to_timestamp(event_created_time) {1} > ( now() {2} - INTERVAL '30 DAY') group by EventDate".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                    sQueryAle = "select to_char(to_timestamp(event_created_time) {0},'DD-MON-YY') as AlertDate,count(*) Cnt from alert_data where to_timestamp(event_created_time) {1} > ( now() {2} - INTERVAL '30 DAY') group by AlertDate".format("at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'", "at time zone '" + sTimeZone + "'")
                dRetE = returnSelectQueryResult(sQueryEve)
                dRetA = returnSelectQueryResult(sQueryAle)
                if dRetE["result"] == "success" and dRetA["result"] == "success":

                    lXAxis, lEveAxis, lAleAxis = [], [], []
                    sCalculatedDate, iRange = None, 30

                    #Logic for multiple date selection in Analytics page
                    if when == "this_month":
                        sCalculatedDate = datetime.strptime(wMonthEnd,'%d-%b-%Y')
                        iRange = (datetime.strptime(wMonthEnd, '%d-%b-%Y') - datetime.strptime(wMonthStart,'%d-%b-%Y')).days
                    elif when == "last_month":
                        sCalculatedDate = datetime.strptime(wPreviousMonthEnd, '%d-%b-%Y')
                        iRange = (datetime.strptime(wPreviousMonthEnd, '%d-%b-%Y') - datetime.strptime(wPreviousMonthStart,'%d-%b-%Y')).days
                    elif when == "date_range":
                        sFromDate = date.strip().split('__')[0].replace('_', '-')
                        sEndDate = date.strip().split('__')[1].replace('_', '-')
                        sCalculatedDate = datetime.strptime(sEndDate, '%d-%b-%Y')
                        iRange = (datetime.strptime(sEndDate, '%d-%b-%Y') - datetime.strptime(sFromDate, '%d-%b-%Y')).days
                    else:
                        sCalculatedDate = dTZ
                        iRange = 30

                    iRange += 1 #This is to solve substraction issue in date

                    for i in reversed(range(0,iRange)):
                        sRefDate =  ((sCalculatedDate - timedelta(days=i)).strftime('%d-%b-%y')).upper()
                        dEveGroup =  {eD['eventdate'].upper():eD["cnt"] for eD in dRetE["data"]}
                        lEveGroup = dEveGroup.keys()
                        lXAxis.append(sRefDate)
                        if sRefDate in lEveGroup:
                            lEveAxis.append(dEveGroup[sRefDate])
                        else:
                            lEveAxis.append(0)
                        dAleGroup = {aD['alertdate'].upper(): aD["cnt"] for aD in dRetA["data"]}
                        lAleGroup = dAleGroup.keys()
                        if sRefDate in lAleGroup:
                            lAleAxis.append(dAleGroup[sRefDate])
                        else:
                            lAleAxis.append(0)

                    dRetFinal = {}
                    dRetFinal["x-axis"] = lXAxis
                    dRetFinal["event"] = lEveAxis
                    dRetFinal["alert"] = lAleAxis

                    # Range more than 30 solved here
                    iInto30 = iRange / 30
                    iLoopCnt = iInto30 if int(iInto30) == iInto30 else int(iInto30) + 1
                    lFixXAxis, lFixEveAxis, lFixAleAxis = [], [], []
                    #print(lEveAxis)
                    #print(lAleAxis)
                    #print(iRange)
                    if iInto30 > 1.034:
                        for eachItem in range(0,iRange,iLoopCnt):
                            iLastIndex =(eachItem + iLoopCnt) if (eachItem + iLoopCnt) < iRange else None
                            #print(str(eachItem) + " -- " + str(iLastIndex))
                            lFixXAxis.append(lXAxis[eachItem] + "--" + (lXAxis[-1] if iLastIndex == None else lXAxis[iLastIndex-1]))
                            lFixEveAxis.append(sum(lEveAxis[eachItem:iLastIndex]))
                            lFixAleAxis.append(sum(lAleAxis[eachItem:iLastIndex]))

                        dRetFinal.clear()
                        dRetFinal["x-axis"] = lFixXAxis
                        dRetFinal["event"] = lFixEveAxis
                        dRetFinal["alert"] = lFixAleAxis

                    return json.dumps({"result": "success", "data": dRetFinal })

                else:
                    return json.dumps({"result": "failure", "data": "no data found"})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

##################################################################################
# Service Dashboard
##################################################################################
def getTreeOfMARS():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                d = {
                "name": "Autointelli",
                "children": [
                    {
                        "name": "Web",
                        "children": [
                            {
								"name": "192.168.1.102",
								"children": [
									{"name": "nginx"},
									{"name": "httpd"}
								]
							}
                        ]
                    },
                    {
                        "name": "Database",
                        "children": [
                            {
								"name": "192.168.1.102",
								"children": [
									{"name": "postgresql-9.2"},
									{"name": "mongod"}
								]
							}
                        ]
                    },
					{
                        "name": "API",
                        "children": [
                            {
								"name": "192.168.1.102",
								"children": [
									{"name": "nginx"}
								]
							}
                        ]
                    }
                ]
}
                return json.dumps({'result': 'success', 'data': d})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing



##################################################################################
# OOB
##################################################################################
def getAutomationStats():
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            retFinalDict = {}
            resTotTicOpenToday, resAlertAttended, resAlertResolved, resTotalBOT, resBotOfDay = 0, 0, 0, 0, 0
            dTZ = datetime.now().astimezone(pytz.timezone(sTimeZone))
            try:
                sDate = dTZ.strftime('%d-%b-%Y')
                sDate = '11-JUL-2018'
                sAutoQuery = "select count(*) as total from automationengine where to_date(to_char(ticketcreatedtime,'DD-MON-YYYY'),'DD-MON-YYYY') >= to_date('" + sDate + "','DD-MON-YYYY')"
                sRet = returnSelectQueryResult(sAutoQuery)
                if sRet["result"] == "success":
                    resTotTicOpenToday = sRet["data"][0]["total"]

                sAutoTypeQuery = "select automationtype,count(automationtype) as total from automationengine group by automationtype"
                sRet = returnSelectQueryResult(sAutoTypeQuery)
                #print(sRet)
                if sRet["result"] == "success":
                    if sRet["data"][0]["automationtype"] == "M":
                        resAlertAttended = sRet["data"][0]["total"]
                        resAlertResolved = sRet["data"][1]["total"]
                    else:
                        resAlertAttended = sRet["data"][1]["total"]
                        resAlertResolved = sRet["data"][0]["total"]

                sTotBotQuery = "select count(*) as Total from botrepo"
                sRet = returnSelectQueryResult(sTotBotQuery)
                #print(sRet)
                if sRet["result"] == "success":
                    resTotalBOT = sRet["data"][0]["total"]

                sBotOfDayQuery = "select botname from botrepo where botid =(select botid from (select botid,count(botid) as total from automationengine where start_time > '2018-07-11' group by botid order by total desc LIMIT 1) as A)"
                sRet = returnSelectQueryResult(sBotOfDayQuery)
                #print(sRet)
                if sRet["result"] == "success":
                    resBotOfDay = sRet["data"][0]["botname"]


                retFinalDict["Total Tickets Opened Today"] = resTotTicOpenToday
                retFinalDict["Automation Resolved Count"] = resAlertResolved
                retFinalDict["Automation Attended Count"] = resAlertAttended
                retFinalDict["Total Bots Count"] = resTotalBOT
                retFinalDict["Bot of the Day"] = resBotOfDay

                #print(retFinalDict)
                return json.dumps({"result": "success", "data": retFinalDict})

            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing



#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import json
import services.utils.ConnPostgreSQL as pconn
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.E2XL as xl
from decimal import Decimal
import locale

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file("/var/log/autointelli/eventreceiver.log")
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

dbName = "jbpm"
locale.setlocale(locale.LC_NUMERIC, 'hi_IN')

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def storeProcessInitiationDetail(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            user_id = dPayload['user_id']
            process_id = dPayload['process_id']
            sQuery = "insert into orch_process_instance_log(log_user_id, log_process_id, log_dt) values('{0}', '{1}', now())".format(
                user_id,
                process_id)
            dRet = pconn.returnInsertResult(sQuery=sQuery, sDB=dbName)
            if dRet['result'] == 'success':
                return json.dumps({'result': 'success', 'data': 'log registered'})
            else:
                return json.dumps({'result': 'failure', 'data': 'log registration failed'})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getWorkflowStatus():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sQuery = """
select 
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
	(select status,count(status) as cnt from processinstancelog group by status) as Child
	on 
	Main.status = Child.status
) z"""
            dRet = pconn.returnSelectQueryResultAs2DList(sQuery=sQuery, sDB=dbName)
            if dRet['result'] == 'success':
                return json.dumps({'result': 'success', 'data': dRet['data']})
            else:
                return json.dumps({'result': 'failure', 'data': 'no data'})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getProcessByStartDate():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sQuery = "select date, count(date) total from (select to_char(start_date, 'DD-MM-YYYY') date from processinstancelog) A group by date"
            dRet = pconn.returnSelectQueryResultAs2DList(sQuery=sQuery, sDB=dbName)
            if dRet['result'] == 'success':
                return json.dumps({'result': 'success', 'data': dRet['data']})
            else:
                return json.dumps({'result': 'failure', 'data': 'no data'})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getProcessByEndDate():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sQuery = "select date, count(date) total from (select to_char(end_date, 'DD-MM-YYYY') date from processinstancelog) A group by date"
            dRet = pconn.returnSelectQueryResultAs2DList(sQuery=sQuery, sDB=dbName)
            if dRet['result'] == 'success':
                return json.dumps({'result': 'success', 'data': dRet['data']})
            else:
                return json.dumps({'result': 'failure', 'data': 'no data'})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getProcessByRunningTime():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sQuery = """select processname, cnt, to_char(period, 'HH24:MM:SS') p from ( select processname, count(processname) cnt, avg(end_date-start_date) period from processinstancelog group by processname order by count(processname) desc) Z"""
            dRet = pconn.returnSelectQueryResultAs2DList(sQuery=sQuery, sDB=dbName)
            if dRet['result'] == 'success':
                return json.dumps({'result': 'success', 'data': dRet['data']})
            else:
                return json.dumps({'result': 'failure', 'data': 'no data'})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getWorkflowByCategory():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sQuery = "select tower_name,count(tower_name) total from ai_processmetadata group by tower_name order by tower_name"
            dRet = pconn.returnSelectQueryResultAs2DList(sQuery=sQuery, sDB="jcentral")
            if dRet['result'] == 'success':
                return json.dumps({'result': 'success', 'data': dRet['data']})
            else:
                return json.dumps({'result': 'failure', 'data': 'no data'})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def auditLog(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            username = dPayload["username"]
            startdt = dPayload["startdatetime"]
            enddt = dPayload["enddatetime"]

            sQuery = """
            select 
            	processinstanceid, processname, processinstancedescription, user_identity, to_char(start_date, 'YYYY-MM-DD HH24:MI') StartDateTime, to_char(end_date, 'YYYY-MM-DD HH24:MI') EndDateTime, (case 
		when status = 0 then 'Pending'
		when status = 1 then 'Active'
		when status = 2 then 'Completed'
		when status = 3 then 'Aborted'
		when status = 4 then 'Suspended'
	END) as status 
            from 
            	processinstancelog 
            where 
            	start_date >= to_date('{0}', 'YYYY-MM-DD HH24:MI') and 
            	end_date < to_date('{1}', 'YYYY-MM-DD HH24:MI') """.format(startdt, enddt)
            	# user_identity != 'unknown' """.format(startdt, enddt)
            if username.lower().strip() != "admin":
                sQuery += " and lower(user_identity)=lower('{0}')".format(username)
            dRet = pconn.returnSelectQueryResultAs2DList(sQuery=sQuery, sDB=dbName)
            if dRet["result"] == "success":
                ret = xl.export2XLSX(dRet["data"], "AutomationAuditLog")
                return json.dumps(ret)
            else:
                return json.dumps({"result": "failure", "data": "no data"})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def ROIDashboard():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                kieSrvQueryCat = "select count(*) total from (select distinct tower_name from ai_processmetadata) A"
                kieSrvQuery = "select processname, count(processname) NumberOfTimesExecuted from processinstancelog where status=2 group by processname order by 2 desc"
                kieWbQuery = "select workflow_id, manual_effort, cost_per_hour from ai_processmetadata"
                srvRetCat = pconn.returnSelectQueryResult(sQuery=kieSrvQueryCat, sDB="jcentral")
                srvRet = pconn.returnSelectQueryResultConvert2Col2Dict(sQuery=kieSrvQuery, sDB=dbName)
                wbRet = pconn.returnSelectQueryResultAs2DList(sQuery=kieWbQuery, sDB="jcentral")
                if wbRet["result"] == "success" and srvRet["result"] =="success":
                    sOrg = "1"
                    sTower = srvRetCat["data"][0]["total"]
                    sProcesses = len(wbRet["data"])
                    sExecutions = sum(list(srvRet["data"].values()))
                    sHoursAutomated = float(sum([i[1]for i in wbRet["data"][1:]]))
                    sExecutionHourSaved = 0
                    sROI = 0

                    srvD = srvRet["data"]
                    dRaw = {}
                    for i in wbRet["data"][1:]:
                        try:
                            dRaw[i[0]] = {"manual_effort": float(i[1]), "cost_per_hour": float(i[2]), "numberofexecutions": srvD[i[0]]}
                        except Exception as e:
                            dRaw[i[0]] = {"manual_effort": float(i[1]), "cost_per_hour": float(i[2]), "numberofexecutions": 0}
                            continue
                    for i in dRaw:
                        sExecutionHourSaved += dRaw[i]["manual_effort"] * dRaw[i]["numberofexecutions"]
                        sROI += ((dRaw[i]["manual_effort"] * dRaw[i]["numberofexecutions"]) / 60) * dRaw[i]["cost_per_hour"]
                    return json.dumps({
                        "result": "success",
                        "data": {
                            "Organization": locale.format_string("%d", float(sOrg), grouping=True),
                            "Towers": locale.format_string("%d", float(sTower), grouping=True),
                            "Processes": locale.format_string("%d", float(sProcesses), grouping=True),
                            "Executions": locale.format_string("%d", float(sExecutions), grouping=True),
                            "Hours Automated": locale.format_string("%d", float(sHoursAutomated), grouping=True),
                            "Execution Hours Automated": locale.format_string("%d", float(sExecutionHourSaved), grouping=True),
                            "ROI": locale.format_string("%d", float(sROI), grouping=True)
                        }
                    })
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return json.dumps({"result": "failure", "data": "no data"})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing








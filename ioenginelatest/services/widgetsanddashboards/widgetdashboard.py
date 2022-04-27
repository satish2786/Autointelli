#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as conn
from services.utils import sessionkeygen as sess
from services.utils import validator_many as vm
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc

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

def createDashboard(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if "dashboard_name" in dPayload:
                    sQuery = "select * from Dashboard where lower(dashboard_name) = '{0}' and active_yn='Y'".format(dPayload['dashboard_name'].lower())
                    dValid = conn.returnSelectQueryResult(sQuery)
                    if dValid["result"] == "failure":
                        iQuery = "insert into Dashboard(dashboard_name, active_yn) values('{0}', '{1}') RETURNING pk_dashboard_id".format(dPayload['dashboard_name'], 'Y')
                        dComm = conn.returnSelectQueryResultWithCommit(iQuery)
                        if dComm["result"] == "success":
                            logINFO("New Dashboard created {0}".format(dPayload["dashboard_name"]))
                            return json.dumps({"result": "success", "data": {"dashboard_id": dComm["data"][0]["pk_dashboard_id"]}})
                        else:
                            return logAndRet("failure", "Dashboard creation failed.")
                    else:
                        return logAndRet("failure", "Dashboard already exists. Choose a different name.")
                else:
                    return logAndRet("failure", "Dashboard details are missing.")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def mapDashboardRole(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if vm.isPayloadValid(dPayload=dPayload, lHeaders=["dashboard_name","role_name"], lMandatory=["dashboard_name","role_name"]):
                    sQuery = "select pk_dashboard_id dashboard_id from Dashboard where lower(dashboard_name) = '{0}' and active_yn='Y'".format(dPayload['dashboard_name'].lower())
                    dValid = conn.returnSelectQueryResult(sQuery)
                    if dValid["result"] == "success":
                        iDashboardID = dValid["data"][0]["dashboard_id"]
                        sRoleQuery = "insert into Dashboard_role_mapping(fk_dashboard_id,fk_role_id) (select {0} dasboard_id,pk_role_id role_id from tbl_role where active_yn='Y' and lower(role_name) in ('{1}'))".format(iDashboardID, "','".join(dPayload["role_name"]))
                        dRDMapRet = conn.returnInsertResult(sRoleQuery)
                        if dRDMapRet["result"] == "success":
                            if dRDMapRet["data"] > 0:
                                logINFO("Dashboard Role Mapping")
                                return json.dumps({"result": "success", "data": "Mapping Success"})
                            else:
                                return logAndRet("failure", "Failed to Map Role and Dashboard")
                        else:
                            return logAndRet("failure", "Failed to Map Role and Dashboard")
                    else:
                        return logAndRet("failure", "Dashboard missing to map Roles.")
                else:
                    return logAndRet("failure", "Dashboard and Role details are missing.")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def createAndUpdateDashboard(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if vm.isPayloadValid(dPayload=dPayload, lHeaders=["dashboard_name", "role_name"], lMandatory=["dashboard_name", "role_name"]):
                    sQuery = "select pk_dashboard_id dashboard_id from Dashboard where lower(dashboard_name) = '{0}' and active_yn='Y'".format(dPayload['dashboard_name'].lower())
                    dValid = conn.returnSelectQueryResult(sQuery)
                    if dValid["result"] == "success":
                        #Update
                        iDashboardID = dValid["data"][0]["dashboard_id"]
                        uQuery = "delete from Dashboard_role_mapping where fk_dashboard_id={0}".format(iDashboardID)
                        dRet = conn.returnInsertResult(uQuery)
                        sRoleQuery = "insert into Dashboard_role_mapping(fk_dashboard_id,fk_role_id) (select {0} dasboard_id,pk_role_id role_id from tbl_role where active_yn='Y' and lower(role_name) in ('{1}'))".format(
                            iDashboardID, "','".join(dPayload["role_name"]))
                        dRDMapRet = conn.returnInsertResult(sRoleQuery)
                        if dRDMapRet["result"] == "success":
                            if dRDMapRet["data"] > 0:
                                logINFO("Map widget to Dashboard {0}".format(dPayload['dashboard_name']))
                                return logAndRet("success", "Mapping Success")
                            else:
                                return logAndRet("failure", "Failed to Map Role and Dashboard")
                        else:
                            return logAndRet("failure", "Failed to Map Role and Dashboard")
                    else:
                        #Create
                        iQuery = "insert into Dashboard(dashboard_name, active_yn) values('{0}', '{1}') RETURNING pk_dashboard_id".format(
                            dPayload['dashboard_name'], 'Y')
                        dComm = conn.returnSelectQueryResultWithCommit(iQuery)
                        if dComm["result"] == "success":
                            iDashboardID = dComm["data"][0]["pk_dashboard_id"]
                            sRoleQuery = "insert into Dashboard_role_mapping(fk_dashboard_id,fk_role_id) (select {0} dasboard_id,pk_role_id role_id from tbl_role where active_yn='Y' and lower(role_name) in ('{1}'))".format(
                                iDashboardID, "','".join(dPayload["role_name"]))
                            dRDMapRet = conn.returnInsertResult(sRoleQuery)
                            logINFO("Map widget to Dashboard {0}".format(dPayload['dashboard_name']))
                            return json.dumps({"result": "success", "data": "Dashboard created", "id": {"dashboard_id": dComm["data"][0]["pk_dashboard_id"]}})
                        else:
                            return logAndRet("failure", "Dashboard creation failed.")
                else:
                    return logAndRet("failure", "Dashboard and Role details are missing.")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteDashboard(dashboard_name):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select * from Dashboard where lower(dashboard_name) = '{0}' and active_yn='Y'".format(dashboard_name.lower())
                dValid = conn.returnSelectQueryResult(sQuery)
                if dValid["result"] == "success":
                    dQuery = "update Dashboard set active_yn='N' where lower(dashboard_name) = '{0}'".format(dashboard_name.lower())
                    dRet = conn.returnInsertResult(dQuery)
                    if dRet["result"] == "success":
                        return logAndRet("success", "Dashboard {0} removed".format(dashboard_name))
                    else:
                        return logAndRet("failure", "Failed to remove Dashboard {0}".format(dashboard_name))
                else:
                    return logAndRet("failure", "Dashboard {0} not available to delete".format(dashboard_name))
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def mapDashboardWidget(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if vm.isPayloadValid(dPayload=dPayload, lHeaders=["dashboard_name", "widgets"], lMandatory= ["dashboard_name", "widgets"]):
                    sQuery = "select pk_dashboard_id dashboard_id from Dashboard where lower(dashboard_name) = '{0}' and active_yn='Y'".format(dPayload['dashboard_name'].lower())
                    dValid = conn.returnSelectQueryResult(sQuery)
                    if dValid["result"] == "success":
                        iDashboardID = dValid["data"][0]["dashboard_id"]
                        #Remove before insert
                        dQuery = "delete from Dashboard_widget_mapping where fk_dashboard_id={0}".format(iDashboardID)
                        dRet = conn.returnInsertResult(dQuery)

                        iQueryT = "insert into Dashboard_widget_mapping(fk_dashboard_id,widget_custom_name,fk_widget_id,widget_attributes) values "
                        uQuery, iQuery = "", ""
                        dDWRet, dDURet = "", ""
                        for eachWidget in dPayload["widgets"]:
                            sQuery = "select count(*) total from Dashboard_widget_mapping where fk_dashboard_id={0} and fk_widget_id={1}".format(iDashboardID, eachWidget["widget_id"])

                            dRet = conn.returnSelectQueryResult(sQuery)
                            if dRet["result"] == "success":
                                if dRet["data"][0]["total"] > 0:
                                    uQuery += "update Dashboard_widget_mapping set widget_custom_name='{0}', widget_attributes='{1}' where fk_dashboard_id={2} and fk_widget_id={3};".format(
                                        eachWidget["widget_custom_name"], json.dumps(eachWidget["widget_attributes"]), iDashboardID, eachWidget["widget_id"]
                                    )
                                else:
                                    iQuery += "({0}, '{1}', {2}, '{3}'),".format(iDashboardID, eachWidget["widget_custom_name"], eachWidget["widget_id"], json.dumps(eachWidget["widget_attributes"]))
                            else:
                                return logAndRet("failure", "Failed to map Dashboard and Widget")
                        if iQuery != "":
                            iQuery = iQueryT + iQuery
                            dDWRet = conn.returnInsertResult(iQuery[:-1])
                        if uQuery != "":
                            dDURet = conn.returnInsertResult(uQuery)
                        iR, uR = 0, 0
                        if dDWRet:
                            if dDWRet["result"] == "success":
                                if dDWRet["data"] > 0:
                                    iR = 1
                        if dDURet:
                            if dDURet["result"] == "success":
                                if dDURet["data"] > 0:
                                    uR = 1
                        if iR == 1 or uR == 1:
                            return logAndRet("success", "Widgets mapped to Dashboard")
                        else:
                            return logAndRet("failure", "Failed to map Dashboard and Widget")
                    else:
                        return logAndRet("failure", "Dashboard missing to map Widgets.")
                else:
                    return logAndRet("failure", "Dashboard and Widget details are missing.")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getCategoryWidgetSheet():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select	
	cat.category_name, wid.pk_widget_id widget_id, wid.widget_name, wid.wwidth width, wid.wheight height, chart.chart_name, chart.attributes, plot.api_address_or_link, plot.api_method, plot.api_body, plot.api_description
from 
	WidgetCategory cat 
	left join Widget wid on(cat.pk_category_id=wid.fk_category_id) 
	left join ChartDetails chart on(wid.fk_chart_id=chart.pk_chart_id) 
	left join PlottingAPIDetails plot on(wid.fk_api_id=plot.pk_api_id)
	
where 
	cat.active_yn='Y' and
	chart.active_yn='Y' and
	plot.active_yn='Y'"""
                dRet = conn.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    dData = dRet["data"]
                    dFinal = {}
                    for eachDict in dData:
                        if eachDict["category_name"] in dFinal:
                            dFinal[eachDict["category_name"]].append(eachDict)
                        else:
                            dFinal[eachDict["category_name"]] = [eachDict]
                    return json.dumps({"result": "success", "data": dFinal})
                else:
                    return logAndRet("failure", "No Data. Add Category and then browse.")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def loadDashboardByRole(role_name):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
	d.dashboard_name, dwid.widget_custom_name, dwid.fk_widget_id widget_id, dwid.widget_attributes, plot.api_address_or_link api_url, plot.api_method, plot.api_body, chart.chart_name
from 
	Dashboard d """
                if role_name.lower() != "admin":
                    sQuery += " left join Dashboard_role_mapping drole on(d.pk_dashboard_id=drole.fk_dashboard_id)"
                sQuery += """
	left join Dashboard_widget_mapping dwid on(d.pk_dashboard_id=dwid.fk_dashboard_id) 
	left join Widget wid on(wid.pk_widget_id=dwid.fk_widget_id)
	left join PlottingAPIDetails plot on(plot.pk_api_id=wid.pk_widget_id) 
	left join ChartDetails chart on(chart.pk_chart_id=wid.fk_chart_id)
where 
	d.active_yn = 'Y'"""
                if role_name.lower() != "admin":
                    sQuery += " and drole.fk_role_id in(select pk_role_id from tbl_role where active_yn='Y' and lower(role_name) = '{0}')".format(role_name.lower())
                dRet = conn.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    dData = dRet["data"]
                    dFinal = {}
                    for eachDict in dData:
                        if eachDict["dashboard_name"] in dFinal:
                            dFinal[eachDict["dashboard_name"]].append(eachDict)
                        else:
                            dFinal[eachDict["dashboard_name"]] = [eachDict]
                    for i in list(dFinal.keys()):
                        chk4None = [j["widget_custom_name"] for j in dFinal[i]]
                        chk4NoneB = [0 if j == None else 1 for j in chk4None]
                        if not (1 in chk4NoneB):
                            dFinal[i] = "no data"
                    #for i in list(dFinal.keys()):
                    #    if len(dFinal[i]) == 1:
                    #        if dFinal[i][0]["widget_custom_name"] == None:
                    #            dFinal[i] = "no data"
                    return json.dumps({"result": "success", "data": dFinal})
                else:
                    return logAndRet("failure", "No Data. Add Widgets and then browse.")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def loadDashboardAndRoles():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinal = {}
                sQuery = """
select 
	d.dashboard_name, r.role_name
from 
	Dashboard d 
	left join Dashboard_role_mapping dr on(d.pk_dashboard_id=dr.fk_dashboard_id) 
	inner join tbl_role r on(r.pk_role_id=dr.fk_role_id) 
where 
	d.active_yn = 'Y'"""
                dRet = conn.returnSelectQueryResult(sQuery)
                for eachDict in dRet["data"]:
                    if eachDict["dashboard_name"] in dFinal:
                        dFinal[eachDict["dashboard_name"]].append(eachDict["role_name"])
                    else:
                        dFinal[eachDict["dashboard_name"]] = [eachDict["role_name"]]
                return json.dumps({'result': 'success', 'data': dFinal})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing




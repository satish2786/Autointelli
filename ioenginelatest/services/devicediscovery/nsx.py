#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as pconn
from services.utils import validator_many as vmany
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc
from datetime import datetime
from datetime import timedelta
import pytz
import requests as req

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

def generateIFrameLink(dPayload):
    #Payload Extraction
    sdate, edate, custom_date = '', '', ''
    pTimeZone = dPayload['Time Zone']
    pDateText = dPayload['date']
    pTimeZone = "Asia/Kolkata"
    pDateText = "today"

    # Date Management
    dTZ = datetime.now().astimezone(pytz.timezone(pTimeZone))
    midnight, oneminb_midnight = ' 00:00', ' 23:59'
    wToday = {'s': dTZ.strftime('%d-%m-%Y') + midnight, 'e': dTZ.strftime('%d-%m-%Y %H:%M')}
    wYesterday = {'s': (dTZ - timedelta(days=1)).strftime('%d-%m-%Y') + midnight, 'e': wToday['s']}
    wWeek = {'s': (dTZ - timedelta(days=dTZ.weekday())).strftime('%d-%m-%Y') + midnight, 'e': wToday['e']}
    wMonth = {'s': dTZ.today().replace(day=1).strftime('%d-%m-%Y') + midnight, 'e': wToday['e']}
    wPreviousMonthEnd = (datetime.strptime(wMonth['s'], '%d-%m-%Y %H:%M') - timedelta(days=1)).strftime('%d-%m-%Y %H:%M')
    wPreviousMonth = {'s': (datetime.strptime(wPreviousMonthEnd, '%d-%m-%Y %H:%M').replace(day=1)).strftime('%d-%m-%Y %H:%M'),
                           'e': datetime.strptime(wPreviousMonthEnd, '%d-%m-%Y %H:%M').strftime('%d-%m-%Y') + oneminb_midnight}
    lFilters = [wToday, wYesterday, wWeek, wMonth, wPreviousMonth]
    for i in lFilters:
        i['s'] = datetime.strptime(i['s'], '%d-%m-%Y %H:%M').astimezone(pytz.timezone('GMT')).strftime('%d.%m.%Y %H:%M')
        i['e'] = datetime.strptime(i['e'], '%d-%m-%Y %H:%M').astimezone(pytz.timezone('GMT')).strftime('%d.%m.%Y %H:%M')

    #already sent date
    if 'extra' in dPayload:
        sdate, edate = dPayload['extra']['sdate'], dPayload['extra']['edate']
        custom_date = {'s': datetime.strptime(sdate, '%d-%m-%Y %H:%M').astimezone(pytz.timezone(pTimeZone)).astimezone(
            pytz.timezone('GMT')).strftime('%d.%m.%Y %H:%M'),
                       'e': datetime.strptime(edate, '%d-%m-%Y %H:%M').astimezone(pytz.timezone(pTimeZone)).astimezone(
            pytz.timezone('GMT')).strftime('%d.%m.%Y %H:%M')}

    start, end = '', ''
    if pDateText == 'today':
        start, end = wToday['s'], wToday['e']
    elif pDateText == 'yesterday':
        start, end = wYesterday['s'], wYesterday['e']
    elif pDateText == 'this_week':
        start, end = wWeek['s'], wWeek['e']
    elif pDateText == 'this_month':
        start, end = wMonth['s'], wMonth['e']
    elif pDateText == 'previous_month':
        start, end = wPreviousMonth['s'], wPreviousMonth['e']
    elif pDateText == 'custom':
        start, end = custom_date['s'], custom_date['e']

    return {'start': datetime.strptime(start, '%d.%m.%Y %H:%M').timestamp(), 'end': datetime.strptime(end, '%d.%m.%Y %H:%M').timestamp()}

def parseData(retData):
    try:
        dRetData, dRetFinalMB = {}, {}
        interval = retData["metaDto"]["interval"]
        for nic in list(retData['dataDto'].keys()):
            if retData['dataDto'][nic] != None:
                for i in retData['dataDto'][nic]:
                    datef = datetime.fromtimestamp(i['timestamp']).strftime('%d-%m-%Y')
                    in_value = ((i["in"] * 1000) / 8) * interval
                    out_value = ((i["out"] * 1000) / 8) * interval
                    print(datef, in_value, out_value)
                    if datef in list(dRetData.keys()):
                        dRetData[datef]["in"] += in_value
                        dRetData[datef]["out"] += out_value
                    else:
                        dRetData[datef] = {"in": in_value, "out": out_value}
        kb = 1024
        mb = 1024*1024
        for i in dRetData:
            dRetFinalMB[i] = {"in": "{0} {1}".format('%.2f' %(dRetData[i]["in"]/mb), ' MB'), "out": "{0} {1}".format('%.2f' %(dRetData[i]["out"]/mb), 'MB')}

        return {"result": "success", "data": dRetFinalMB}
    except Exception as e:
        return {"result": "failure", "data": "no data"}


def getEdgeDetails():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select edge_id id, edge_object_id oid, edge_name || '::' || edge_dc_name as name from  vnsx_edge_discovery where active_yn ='Y' order by edge_name"
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    return json.dumps({"result": "success", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getEdgeUsage1(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                id = dPayload["id"]
                oid = dPayload["oid"]
                name = dPayload["name"]
                timTuple = generateIFrameLink(dPayload)
                sURL = "https://172.16.64.62/api/4.0/edges/{0}/statistics/interfaces/uplink?starttime={1}&endtime={2}".format(
                    oid, int(timTuple['start']), int(timTuple['end'])
                )
                auth = ("nxtgen\\autointelli", "cIcr@joxlnA7rLG7R#ra")
                sHeader = {"Accept": "application/json"}
                r = req.get(url=sURL, auth=auth, headers=sHeader, verify=False)
                if r.status_code == 200:
                    out = json.loads(r.content.decode('utf-8').replace('true', 'True').replace('false', 'False'))
                    data = parseData(out)
                    if data["result"] == "success":
                        return json.dumps(data)
                    else:
                        return json.dumps({"result": "failure", "data": "no data"})
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getEdgeUsage(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                id = dPayload["id"]
                oid = dPayload["oid"]
                name = dPayload["name"]
                timTuple = generateIFrameLink(dPayload)
                start = datetime.fromtimestamp(int(timTuple['start']))
                end = datetime.fromtimestamp(int(timTuple['end']))
                sQuery = """
select
        b.edge_id, d.edge_name, to_char(start_date, 'DD-MON-YYYY') Date, edge_json
from
        vnsx_edge_batch b left join vnsx_edge_discovery d on(b.edge_id=d.edge_id)
where 
	b.edge_id='{0}' and 
	start_date >= to_date('{1}', 'DD-MM-YYYY') order by start_date""".format(id, start)
                dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    dFinalRet = {}
                    inn, out = 0, 0
                    for i in dRet["data"][1:]:
                        dFinalRet[i[2]] = i[3]
                        inn += float(i[3]['in'].strip('MB').strip())
                        out += float(i[3]['in'].strip('MB').strip())
                    dFinalRet["Total"] = {'in': '%.2f' %(inn) + ' MB', 'out': '%.2f' %(out) + ' MB'}
                    #dFinalRet["customer_name"] = dRet["data"][1][1]
                    return json.dumps({"result": "success", "data": dFinalRet, "Customer Name": dRet["data"][1][1], "Date Time": datetime.now().strftime('%d-%m-%Y %H:%M')})
                else:
                    return json.dumps({"result": "failure", "data": "no data"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


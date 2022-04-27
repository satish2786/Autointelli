#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import json
from services.utils import ConnPostgreSQL as pconn
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
from datetime import datetime
from datetime import timedelta
import pytz
import requests as req
from services.utils import ED_AES256 as aes

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

nsxip, nsxuser, nsxpassword = "", "", ""

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
    # pTimeZone = "Asia/Kolkata"
    # pDateText = "today"

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
        i['s'] = datetime.strptime(i['s'], '%d-%m-%Y %H:%M').astimezone(pytz.timezone(pTimeZone)).strftime('%d.%m.%Y %H:%M') #Earlier GMT
        i['e'] = datetime.strptime(i['e'], '%d-%m-%Y %H:%M').astimezone(pytz.timezone(pTimeZone)).strftime('%d.%m.%Y %H:%M') #Earlier GMT

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

#print(generateIFrameLink({"Time Zone": "Asia/Kolkata", "date": "yesterday"}))

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
                    #print(datef, in_value, out_value)
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
    try:
        sQuery = "select edge_id id, edge_object_id oid, edge_name || '::' || edge_dc_name as name from  vnsx_edge_discovery"
        dRet = pconn.returnSelectQueryResultAs2DList(sQuery)
        if dRet["result"] == "success":
            return dRet
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def getEdgeUsage(dPayload):
    try:
        id = dPayload["id"]
        oid = dPayload["oid"]
        name = dPayload["name"]
        timTuple = generateIFrameLink(dPayload)
        sURL = "https://{0}/api/4.0/edges/{1}/statistics/interfaces/uplink?starttime={2}&endtime={3}".format(
            nsxip, oid, int(timTuple['start']), int(timTuple['end'])
        )
        #auth = ("nxtgen\\autointelli", "cIcr@joxlnA7rLG7R#ra")
        auth = (nsxuser, nsxpassword)
        sHeader = {"Accept": "application/json"}
        r = req.get(url=sURL, auth=auth, headers=sHeader, verify=False)
        if r.status_code == 200:
            out = json.loads(r.content.decode('utf-8').replace('true', 'True').replace('false', 'False'))
            data = parseData(out)
            if data["result"] == "success":
                return data
            else:
                return {"result": "failure", "data": "no data"}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        return {"result": "failure", "data": "Exception: {0}"}

if __name__ == "__main__":
    # fetch VMWare NSX IP and Credentials
    sQuery = """select
    	            h.pk_hypervisor_id, h.hypervisor_name, h.hypervisor_ip_address, c.cred_type, c.username, c.password
                from
    	            hypervisor_details h inner join ai_device_credentials c on(h.hypervisor_cred=c.cred_id)
                where
    	            h.hypervisor_type='vmware nsx' and h.active_yn='Y' """
    dRet = pconn.returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        nsxip = dRet["data"][0]["hypervisor_ip_address"]
        nsxuser = dRet["data"][0]["username"]
        nsxpassword = aes.decrypt(dRet["data"][0]["password"].encode(), '@ut0!ntell!'.encode()).decode('utf-8')

        s, f = 0, 0
        startdate, enddate = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y'), (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
        iQuery = "insert into vnsx_edge_batch(edge_id, start_date, edge_json, active_yn) values('{0}', {1}, '{2}', 'Y')"
        dRet = getEdgeDetails()
        if dRet["result"] == "success":
            for i in dRet["data"][1:]:
                payload = {'id': i[0], 'oid': i[1], 'name': i[2], 'Time Zone': 'Asia/Kolkata',
                           'date': 'yesterday'}
                # payload = {'id': i[0], 'oid': i[1], 'name': i[2], 'Time Zone': 'Asia/Kolkata', 'extra':
                #     {'sdate': '',
                #      'edate': ''}}
                dSingleNSX = getEdgeUsage(payload)
                if dSingleNSX["result"] == "success":
                    # Temp Fix Code
                    for d in dSingleNSX['data']:
                        q = iQuery.format(i[0], "to_date('{0}', 'DD-MM-YYYY')".format(d), json.dumps(dSingleNSX['data'][d]))
                        print(q)
                        iRet = pconn.returnInsertResult(q)
                        print(iRet)
                        if iRet["result"] == "success":
                            print("Pushed data successfully to database: {0}".format(i[2]))
                            s += 1
                        else:
                            print("Failed, query:{0}, ret:{1}".format(q, iRet))
                            f += 1
                    # js = json.dumps(dSingleNSX['data'][startdate]) if startdate in list(dSingleNSX['data'].keys()) else ''
                    # q = iQuery.format(i[0], "to_date('{0}', 'DD-MM-YYYY')".format(startdate), js)
                    # print(q)
                    # iRet = pconn.returnInsertResult(q)
                    # print(iRet)
                    # if iRet["result"] == "success":
                    #     print("Pushed data successfully to database: {0}".format(i[2]))
                    #     s += 1
                    # else:
                    #     f += 1
                else:
                    print("Failed: Payload:{0}, ret:{1}".format(payload, dSingleNSX))
                    f += 1
        else:
            print("Failed to fetch Edge")
        print("Final Result Summar: Success: {0}, Failure: {1}".format(s, f))

    else:
        print("Unable to fetch NSX Machine and Credentails to run the batch")



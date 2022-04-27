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
    try:
        # Payload Extraction
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
        wPreviousMonthEnd = (datetime.strptime(wMonth['s'], '%d-%m-%Y %H:%M') - timedelta(days=1)).strftime(
            '%d-%m-%Y %H:%M')
        wPreviousMonth = {
            's': (datetime.strptime(wPreviousMonthEnd, '%d-%m-%Y %H:%M').replace(day=1)).strftime('%d-%m-%Y %H:%M'),
            'e': datetime.strptime(wPreviousMonthEnd, '%d-%m-%Y %H:%M').strftime('%d-%m-%Y') + oneminb_midnight}
        lFilters = [wToday, wYesterday, wWeek, wMonth, wPreviousMonth]
        for i in lFilters:
            i['s'] = datetime.strptime(i['s'], '%d-%m-%Y %H:%M').astimezone(pytz.timezone('GMT')).strftime(
                '%d.%m.%Y %H:%M')
            i['e'] = datetime.strptime(i['e'], '%d-%m-%Y %H:%M').astimezone(pytz.timezone('GMT')).strftime(
                '%d.%m.%Y %H:%M')

        # already sent date
        if 'extra' in dPayload:
            sdate, edate = dPayload['extra']['sdate'], dPayload['extra']['edate']
            custom_date = {
                's': datetime.strptime(sdate, '%d-%m-%Y %H:%M').astimezone(pytz.timezone(pTimeZone)).astimezone(
                    pytz.timezone('GMT')).strftime('%d.%m.%Y %H:%M'),
                'e': datetime.strptime(edate, '%d-%m-%Y %H:%M').astimezone(pytz.timezone(pTimeZone)).astimezone(
                    pytz.timezone('GMT')).strftime('%d.%m.%Y %H:%M')}

        start, end = '', ''
        if pDateText.lower() == 'today':
            start, end = wToday['s'], wToday['e']
        elif pDateText.lower() == 'yesterday':
            start, end = wYesterday['s'], wYesterday['e']
        elif pDateText.lower() == 'this week':
            start, end = wWeek['s'], wWeek['e']
        elif pDateText.lower() == 'this month':
            start, end = wMonth['s'], wMonth['e']
        elif pDateText.lower() == 'previous month':
            start, end = wPreviousMonth['s'], wPreviousMonth['e']
        elif pDateText.lower() == 'custom period':
            start, end = custom_date['s'], custom_date['e']

        return {'start': datetime.strptime(start, '%d.%m.%Y %H:%M').timestamp(),
                'end': datetime.strptime(end, '%d.%m.%Y %H:%M').timestamp()}
    except Exception as e:
        return {'failed': str(e)}

def getBandwidthDetails():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select band_pk_id id, band_id interfaces from util_cost_bandwidth_discovery where active_yn='Y'"
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


def pdfComplete(URL):
    try:
        r = req.get(URL, verify=False)
        l = r.text.splitlines()
        #print(l)
        final = []
        for i in l[1:]:
            j = i.split(';')
            tmp = []
            tmp.append(datetime.fromtimestamp(int(j[0])).strftime('%d-%m-%Y'))
            for k in j[1:]:
                tmp.append(float(k))
            final.append(tmp)
        #print(final)
        d = {}
        for i in final:
            if i[0] in d:
                d[i[0]]['Traffic_in_MIN'] += 0 if i[1] < 0 else i[1]
                d[i[0]]['Traffic_in_MAX'] += 0 if i[2] < 0 else i[2]
                d[i[0]]['Traffic_in_AVERAGE'] += 0 if i[3] < 0 else i[3]
                d[i[0]]['Traffic_out_MIN'] += 0 if i[4] < 0 else i[4]
                d[i[0]]['Traffic_out_MAX'] += 0 if i[5] < 0 else i[5]
                d[i[0]]['Traffic_out_AVERAGE'] += 0 if i[6] < 0 else i[6]
                d[i[0]]['Traffic_total_MIN'] += 0 if i[7] < 0 else i[7]
                d[i[0]]['Traffic_total_MAX'] += 0 if i[8] < 0 else i[8]
                d[i[0]]['Traffic_total_AVERAGE'] += 0 if i[9] < 0 else i[9]
            else:
                d[i[0]] = {'Traffic_in_MIN': 0 if i[1] < 0 else i[1], 'Traffic_in_MAX': 0 if i[2] < 0 else i[2], 'Traffic_in_AVERAGE': 0 if i[3] < 0 else i[3],
                           'Traffic_out_MIN': 0 if i[4] < 0 else i[4], 'Traffic_out_MAX': 0 if i[5] < 0 else i[5],
                           'Traffic_out_AVERAGE': 0 if i[6] < 0 else i[6], 'Traffic_total_MIN': 0 if i[7] < 0 else i[7], 'Traffic_total_MAX': 0 if i[8] < 0 else i[8],
                           'Traffic_total_AVERAGE': 0 if i[9] < 0 else i[9]}
        #print(d)
        lFinall = []
        for i in list(d.keys()):
            t = d[i]
            for xx in t:
                t[xx] = float("%.2f" % t[xx])
            t['Timestamp'] = i
            lFinall.append(t)
        #print(lFinall)
        summ, avg = {'Traffic_in_MIN': 0, 'Traffic_in_MAX': 0, 'Traffic_in_AVERAGE': 0,
                           'Traffic_out_MIN': 0, 'Traffic_out_MAX': 0,
                           'Traffic_out_AVERAGE': 0, 'Traffic_total_MIN': 0, 'Traffic_total_MAX': 0,
                           'Traffic_total_AVERAGE': 0}, {}
        avgcnt = 0
        for i in lFinall:
            avgcnt += 1
            summ['Traffic_in_MIN'] += i['Traffic_in_MIN']
            summ['Traffic_in_MAX'] += i['Traffic_in_MAX']
            summ['Traffic_in_AVERAGE'] += i['Traffic_in_AVERAGE']
            summ['Traffic_out_MIN'] += i['Traffic_out_MIN']
            summ['Traffic_out_MAX'] += i['Traffic_out_MAX']
            summ['Traffic_out_AVERAGE'] += i['Traffic_out_AVERAGE']
            summ['Traffic_total_MIN'] += i['Traffic_total_MIN']
            summ['Traffic_total_MAX'] += i['Traffic_total_MAX']
            summ['Traffic_total_AVERAGE'] += i['Traffic_total_AVERAGE']
        avg['Traffic_in_MIN'] = summ['Traffic_in_MIN']/avgcnt
        avg['Traffic_in_MAX'] = summ['Traffic_in_MAX'] / avgcnt
        avg['Traffic_in_AVERAGE'] = summ['Traffic_in_AVERAGE'] / avgcnt
        avg['Traffic_out_MIN'] = summ['Traffic_out_MIN'] / avgcnt
        avg['Traffic_out_MAX'] = summ['Traffic_out_MAX'] / avgcnt
        avg['Traffic_out_AVERAGE'] = summ['Traffic_out_AVERAGE'] / avgcnt
        avg['Traffic_total_MIN'] = summ['Traffic_total_MIN'] / avgcnt
        avg['Traffic_total_MAX'] = summ['Traffic_total_MAX'] / avgcnt
        avg['Traffic_total_AVERAGE'] = summ['Traffic_total_AVERAGE'] / avgcnt

        for xx in summ:
            summ[xx] = float("%.2f" % summ[xx])
        for xx in avg:
            avg[xx] = float("%.2f" % avg[xx])



        return {"result": "success", "data": {"grid": lFinall, "sum": summ, "avg": avg}}
    except Exception as e:
        return {"result": "success", "data": "no data"}

def getBandwidthDownload(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if vmany.isPayloadValid(dPayload, lHeaders=["Time Zone", "date", "name", "file_type", "user_id"], lMandatory=["Time Zone", "date", "name", "file_type", "user_id"]):
                    try:
                        iQuery = "insert into util_cost_bandwidth_history(band_id, inp_from, inp_to, exec_datetime, user_id, active_yn) values('{0}', to_timestamp({1}), to_timestamp({2}), now(), {3}, 'Y')"
                        tf = generateIFrameLink(dPayload)
                        if 'failed' in tf:
                            logAndRet('failure', 'Not able to extract datetime frame')
                        sURL = ""

                        url, inturl, pdfCom = "", "", ""
                        fConf = json.load(open('/etc/autointelli/autointelli.conf', 'r'))
                        if 'bandwidth' in list(fConf.keys()):
                            url = fConf['bandwidth']['url']
                            inturl = fConf['bandwidth']['inturl']
                        else:
                            url = "localhost:81"

                        if dPayload["file_type"] == "csv":
                            sURL = "{0}/autointellireports/xport/csv?host={1}&start={2}&end={3}&srv=Bandwidth_Utilization".format(
                                url, dPayload["name"], int(tf["start"]), int(tf["end"])
                            )
                        elif dPayload["file_type"] == "pdf":
                            # sURL = "{0}/autointellireports/pdf?host={1}&start={2}&end={3}&srv=Bandwidth_Utilization".format(
                            #     url, dPayload["name"], int(tf["start"]) + 19800, int(tf["end"]) + 19800
                            # )
                            sURL = "{0}/autointellireports/xport/csv?host={1}&start={2}&end={3}&srv=Bandwidth_Utilization".format(
                                inturl, dPayload["name"], int(tf["start"]), int(tf["end"])
                            )
                            pdfCom = pdfComplete(sURL)

                        q = iQuery.format(dPayload["name"], tf["start"], tf["end"], dPayload["user_id"])
                        ret = pconn.returnInsertResult(q)
                        if ret != True:
                            logINFO("Failed to store hist details for bandwidth utilization report extraction, reason:{0}".format(ret["data"]))
                        if dPayload["file_type"] == "pdf":
                            pdfHeader = {
                                "Report Time Span": "{0} to {1}".format(datetime.fromtimestamp(tf["start"] + 19800).strftime('%d-%h-%Y %H:%M'), datetime.fromtimestamp(tf["end"] + 19800).strftime('%d-%h-%Y %H:%M')),
                                "Sensor Type": "SNMP Traffic 64bit (60s Interval)",
                                "Total (Traffic Total)": "{0} MByte".format(pdfCom["data"]["sum"]["Traffic_total_AVERAGE"])
                            }
                            pdfCom["header"] = pdfHeader
                            return json.dumps(pdfCom)
                        return json.dumps({
                            "result": "success",
                            "data": sURL
                        })
                    except Exception as e:
                        logAndRet("failure", "no data")
                else:
                    return logAndRet("failure", "Payload is not valid")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getBandwidthGrid(user_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """select band_id "Interface", to_char(inp_from, 'DD-MON-YY HH24:MI') "From", to_char(inp_to, 'DD-MON-YY HH24:MI') "To", to_char(exec_datetime, 'DD-MON-YY HH24:MI') "ExecutionDateTime" from util_cost_bandwidth_history where user_id={0} and active_yn='Y' order by exec_datetime desc limit 10""".format(user_id)
                ret = pconn.returnSelectQueryResultAs2DList(sQuery)
                if ret["result"] == "success":
                    return json.dumps({"result": "success", "data": ret["data"]})
                else:
                    return json.dumps({"result": "failure", "data": ret["data"]})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing






















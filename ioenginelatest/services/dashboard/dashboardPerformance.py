#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, request
import json
from datetime import datetime, timedelta, timezone
import pytz
from services.utils import sessionkeygen
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

def getTimeZone(sKey):
    dRet = sessionkeygen.getUserDetailsBasedWithSessionKey(sKey)
    if dRet["result"] == "success":
        return dRet["data"][0]["time_zone"]
    else:
        return "no data"

def generateIFrameLink(dPayload):
    #Payload Extraction
    sdate, edate, custom_date = '', '', ''
    pTimeZone = dPayload['Time Zone']
    pHost = dPayload['host']
    pDateText = dPayload['date']

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

    import urllib
    url = ""
    fConf = json.load(open('/etc/autointelli/autointelli.conf', 'r'))
    if 'perf' in list(fConf.keys()):
        url = fConf['perf']['url']
    else:
        url = "localhost:81"
    d = {'end': end, 'start': start, 'host': pHost}
    URL = '{0}/autointellireports/graph?{1}'.format(url, urllib.parse.urlencode(d))
    return URL

def getPerformaceOfHost(dPayload):
    """Method: Returns the roles available in backend"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            sTimeZone = getTimeZone(request.headers["SESSIONKEY"])
            if sTimeZone == "no data":
                return json.dumps({"result": "failure", "data": "Failed fetching TimeZone details of logged in user"})
            try:
                URL = generateIFrameLink(dPayload)
                return json.dumps({'iframe': URL})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


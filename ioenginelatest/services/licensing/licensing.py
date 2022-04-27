#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as conn
import jwt
from datetime import datetime
import subprocess
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

def getLicenseKey():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select license_str from ai_license where active_yn='Y'"
                dRet = conn.returnSelectQueryResult(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def insertLicenseKey(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                key = dPayload['key']
                sInactiveQuery = "update ai_license set active_yn='N'"
                dRet = conn.returnInsertResult(sInactiveQuery)
                sQuery = "insert into ai_license(license_str, active_yn, created_date) values('%s','Y',now())" % key
                dRet = conn.returnInsertResult(sQuery)
                if dRet['result'] == 'success':
                    logINFO("License updated")
                    return json.dumps({'result': 'success', 'data': 'License Updated'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def checkExpiry():
    try:
        mF = False
        sQuery = "select license_str from ai_license where active_yn='Y'"
        dRet = conn.returnSelectQueryResult(sQuery)
        if dRet['result'] == 'success':
            en = dRet['data'][0]['license_str']
            de = jwt.decode(en, key='@ut0!ntell!@123!@#')
            start_date = datetime.strptime(de['start_date'], '%d/%m/%Y')
            end_date = datetime.strptime(de['end_date'], '%d/%m/%Y')
            mac_addr = de['mac_address'].lower()
            cmd = 'cat /sys/class/net/*/address'
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out, err = p.communicate()
            out = out.decode('utf-8') if type(out) == type(b'') else out
            err = err.decode('utf-8') if type(err) == type(b'') else err
            from_machine = [i.lower() for i in out.strip().splitlines()]
            if mac_addr in from_machine:
                mF = True
            else:
                mF = False
            noww = datetime.now()
            result = (noww >= start_date) and (noww <= end_date)
            if mF and result:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        return False #json.dumps({"result": "failure", "data": str(e)})

def getLicenseInformation():
    try:
        sQuery = "select license_str from ai_license where active_yn='Y'"
        dRet = conn.returnSelectQueryResult(sQuery)
        if dRet['result'] == 'success':
            en = dRet['data'][0]['license_str']
            de = jwt.decode(en, key='@ut0!ntell!@123!@#')
            start_date = datetime.strptime(de['start_date'], '%d/%m/%Y')
            end_date = datetime.strptime(de['end_date'], '%d/%m/%Y')
            mac_addr = de['mac_address'].lower()
            daysleft = (end_date-datetime.now()).days
            return json.dumps({"result": "success", "data": {'MacAddress': mac_addr, 'StartDate': start_date.strftime('%d/%m/%Y'), 'EndDate': end_date.strftime('%d/%m/%Y'), 'DaysLeft': daysleft}})
        else:
            return json.dumps({"result": "failure", "data": {'MacAddress': '', 'StartDate': '', 'EndDate': '', 'DaysLeft': ''}})
    except Exception as e:
        return json.dumps({"result": "failure", "data": {'MacAddress': '', 'StartDate': '', 'EndDate': '', 'DaysLeft': ''}})


#select user_id from tbl_user_details where pk_user_details_id=
# (select fk_user_id from tbl_session_keys where session_key='eaaaab6a1c38d78a467486a002081f8409eb9e89ddeaedab08b610b13a4b1f18a48f2d54862ae347085a0bf9fd3087486166bad10b6126dc761fa5762d730635')


# Insert/Modify License
# view license
#
# 3a:f3:3e:16:fd:f5

#import uuid
#print ("The MAC address in formatted way is : ", end="")
#print (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]))



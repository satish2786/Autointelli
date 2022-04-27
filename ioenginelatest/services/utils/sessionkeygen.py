#import secrets
from services.utils.ConnPostgreSQL import returnSelectQueryResult, returnInsertResult
import binascii
import os

def createSessionOld():
    #k = secrets.token_hex(64)
    k = binascii.hexlify(os.urandom(64))
    k = k.decode('utf-8')
    sQuery = "insert into tbl_session_keys(session_key, active_yn) values('" + k + "','Y')"
    dRet = returnInsertResult(sQuery)
    if dRet["result"] == "success":
        if dRet["data"] > 0:
            return {"result": "success", "data": k}
        else:
            return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}
    else:
        return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}

def createSession(sUserID):
    #k = secrets.token_hex(64)
    k = binascii.hexlify(os.urandom(64))
    k = k.decode('utf-8')
    sQuery = "insert into tbl_session_keys(session_key, active_yn, fk_user_id) values('" + k + "','Y'," + sUserID + ")"
    dRet = returnInsertResult(sQuery)
    if dRet["result"] == "success":
        if dRet["data"] > 0:
            return {"result": "success", "data": k}
        else:
            return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}
    else:
        return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}

def getUserDetailsBasedWithSessionKey(sKey):
    sQuery = "select COALESCE(cast(fk_user_id as varchar),'') as user_id from tbl_session_keys where session_key='" + sKey + "' and active_yn='Y'"
    dRet = returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        if not (dRet["data"][0]["user_id"] == ""):
            sUserID = dRet["data"][0]["user_id"]
            sQuery = """
            select 
            	tud.user_id, tt.time_zone 
            from 
            	tbl_user_details tud, tbl_zone tt 
            where 
            	tud.fk_time_zone_id = tt.pk_zone_id and tud.pk_user_details_id=""" + sUserID
            dRet = returnSelectQueryResult(sQuery)
            if dRet["result"] == "success":
                return dRet
            else:
                return {"result": "failure", "data": "unable to fetch user's time zone"}
        else:
            return {"result": "failure", "data": "illegal entry"}
    else:
        return {"result": "failure", "data": "unable to fetch user's timezone based on sessionkey"}

def chkSessionAvailability(key):
    sQuery = "select * from tbl_session_keys where session_key='" + key.strip() + "' and active_yn='Y'"
    dRet = returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        return {"result": "success", "data": "Yes"}
    else:
        return {"result": "failure", "data": "Session expired. Re-Login once again"}

def destroySession(key):
    sQuery = "update tbl_session_keys set active_yn='N' where session_key='" + key + "'"
    dRet = returnInsertResult(sQuery)
    if dRet["result"] == "success":
        if dRet["data"] > 0:
            return {"result": "success", "data": "logged out"}
        else:
            return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}
    else:
        return {"result": "failure", "data": "Server is busy. Cannot login now. Try after sometimes"}




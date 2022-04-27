#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, request
import json
import services.utils.ConnPostgreSQL as postconn
from services.utils import validator_many

def lam_api_key_missing():
    return json.dumps({"result": "failure", "data": "api-key missing"})

def lam_api_key_invalid():
    return json.dumps({"result": "failure", "data": "invalid api-key"})

lam_api_key_missing = lam_api_key_missing()
lam_api_key_invalid = lam_api_key_invalid()

def chkValidRequest(key):
    sQuery = "select * from tbl_session_keys where session_key='" + key + "' and active_yn='Y'"
    dRet = postconn.returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        return True
    else:
        return False

def chkKeyExistsInHeader(key):
    try:
        #print(request.headers)
        tmp = request.headers["SESSIONKEY"]
        return True
    except KeyError as e:
        return False
    except Exception as e:
        return False

def getCINameUserOverAll():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinal = {}
                sQuery1 = "select pk_user_details_id id, user_id from tbl_user_details where active_yn='Y' order by pk_user_details_id"
                sQuery2 = "select ciname_id id, ci_name from ci_name_details where active_yn ='Y' order by ciname_id"
                dRet1, dRet2 = postconn.returnSelectQueryResultAs2DList(sQuery1), postconn.returnSelectQueryResultAs2DList(sQuery2)
                if dRet1['result'] == 'success':
                    dFinal['users'] = dRet1['data']
                else:
                    dFinal['users'] = 'unable to load users'
                if dRet2['result'] == 'success':
                    dFinal['cinames'] = dRet2['data']
                else:
                    dFinal['cinames'] = 'unable to load CIs'
                return json.dumps({'result': 'success', 'data': dFinal})
            except Exception as e:
                return json.dumps({'result': 'failure', 'data': str(e)})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getCINames4User(user_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
	cin.ci_name 
from 
	ci_name_details cin 
	inner join ci_name_user_mapping cinu on(cin.ciname_id=cinu.ciname_id) 
	inner join tbl_user_details tud on(cinu.user_id=tud.pk_user_details_id) 
where 
	tud.user_id='{0}' and cin.active_yn='Y'""".format(user_id)
                dRet = postconn.returnSelectQueryResultAsList(sQuery)
                if dRet['result'] == 'success':
                    return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'no-data'})
            except Exception as e:
                return json.dumps({'result': 'failure', 'data': str(e)})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

'''
{"user": 1, 
 "cis": [1, 2, 3]}
'''
def insertCINUMap(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dPayload = request.get_json()
                if validator_many.isPayloadValid(dPayload=dPayload, lHeaders=["user", "cis"], lMandatory=["user", "cis"]):
                    userid = dPayload['user']
                    lCIs = dPayload['cis']

                    #Remove-If Previous references
                    dQuery = "delete from ci_name_user_mapping where user_id={0}".format(userid)
                    iRet = postconn.returnInsertResult(dQuery)
                    print(dQuery)

                    #Add
                    if lCIs:
                        iQuery = 'insert into ci_name_user_mapping(user_id, ciname_id) values{0}'.format(
                            ','.join( ['({0}, {1})'.format(userid, i) for i in lCIs] )
                        )
                        print(iQuery)
                        iRet = postconn.returnInsertResult(iQuery)
                        if iRet['result'] == 'success':
                            return json.dumps({'result': 'success', 'data': 'mapped successfully'})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'failed to map'})
                    else:
                        return json.dumps({'result': 'success', 'data': 'unmapped successfully'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload Error: Either a key is missing or Mandatory item has empty values'})
            except Exception as e:
                return json.dumps({'result': 'failure', 'data': str(e)})
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing



#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as conn
from services.utils import validator_many as val
from services.devicediscovery import mgrp_mongo as mong
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

def getMachineGroupDetails():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select pk_ai_machine_group_id group_id, group_name, group_description from ai_machine_grouping where active_yn='Y'"
                dRet = conn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getMachines():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select machine_id, machine_fqdn || ':' || platform machine_name from ai_machine where active_yn='Y'"
                dRet = conn.returnSelectQueryResultAs2DList(sQuery)
                return json.dumps(dRet)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def addNewGrouping(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                lH = ['group_name', 'group_description', 'machine_ids']
                lM = ['group_name', 'group_description', 'machine_ids']
                if val.isPayloadValid(dPayload=dPayload, lHeaders=lH, lMandatory=lM):
                    iQuery = "insert into ai_machine_grouping(group_name,group_description,active_yn) values('{0}','{1}','{2}') RETURNING pk_ai_machine_group_id".format(
                        dPayload['group_name'],
                        dPayload['group_description'],
                        'Y')
                    dRet = conn.returnSelectQueryResultWithCommit(iQuery)
                    if dRet['result'] == 'success':
                        iGroupID = dRet['data'][0]['pk_ai_machine_group_id']
                        lMachineRefs = dPayload['machine_ids']
                        sInsertAll = ','.join(['(' + str(iGroupID) + ',' + str(i) + ')' for i in lMachineRefs])
                        iQuery = "insert into ai_machine_group_mapping(fk_group_id, fk_machine_id) values {0}".format(sInsertAll)
                        dRet = conn.returnInsertResult(iQuery)
                        if dRet['result'] == 'success':
                            # mongo update
                            sQueryMongo = "select machine_fqdn from ai_machine where active_yn='Y' and machine_id in({0})".format(
                                ','.join([str(i) for i in lMachineRefs])
                            )
                            dRet = conn.returnSelectQueryResultAsList(sQueryMongo)
                            if dRet['result'] == 'success':
                                fqdns = dRet['data']['machine_fqdn']
                                mRet = mong.mongoAction(action='create', group_name=dPayload['group_name'], fqdn_list=fqdns)
                            logINFO("Machine Group added successfully")
                            return json.dumps({'result': 'success', 'data': 'Machine Group added successfully', 'id': iGroupID})
                        else:
                            return logAndRet("failure", "Adding Group Failed")
                    else:
                        return logAndRet("failure", "Adding Group Failed")
                else:
                    return logAndRet("failure", "Invalid Payload!")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


def getOneMachineGroupDetails(group_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dFinal = {}
                sQuery0 = "select pk_ai_machine_group_id group_id, group_name, group_description from ai_machine_grouping where active_yn='Y' and pk_ai_machine_group_id={0}".format(group_id)
                sQuery1 = """select 
                                machine_id, machine_fqdn || ':' || platform machine_name, 'no' as action  
                            from 
                                ai_machine where active_yn='Y' and machine_id not in(select fk_machine_id from ai_machine_group_mapping where fk_group_id={0})
                            union
                            select 
                                machine_id, machine_fqdn || ':' || platform machine_name, 'yes' as action  
                            from 
                                ai_machine where active_yn='Y' and machine_id in(select fk_machine_id from ai_machine_group_mapping where fk_group_id={1})""".format(group_id, group_id)
                dRet0 = conn.returnSelectQueryResult(sQuery0)
                dRet1 = conn.returnSelectQueryResultAs2DList(sQuery1)
                if dRet0['result'] == 'success':
                    dFinal.update(dRet0['data'][0])
                if dRet1['result'] == 'success':
                    dFinal['machines'] = dRet1['data']
                return json.dumps({'result': 'success', 'data': dFinal})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def modifyMachineGroup(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                lH = ['group_id', 'group_name', 'group_description', 'machine_ids']
                lM = ['group_id', 'group_name', 'group_description', 'machine_ids']
                if val.isPayloadValid(dPayload=dPayload, lHeaders=lH, lMandatory=lM):
                    iQuery0 = "update ai_machine_grouping set group_name='{0}', group_description='{1}' where pk_ai_machine_group_id={2}".format(
                        dPayload['group_name'],
                        dPayload['group_description'],
                        dPayload['group_id']
                    )
                    iQuery1 = "delete from ai_machine_group_mapping where fk_group_id={0}".format(dPayload['group_id'])
                    lMachineRefs = dPayload['machine_ids']
                    sInsertAll = ','.join(['(' + str(dPayload['group_id']) + ',' + str(i) + ')' for i in lMachineRefs])
                    iQuery2 = "insert into ai_machine_group_mapping(fk_group_id, fk_machine_id) values {0}".format(
                        sInsertAll)
                    dRet0 = conn.returnInsertResult(iQuery0)
                    dRet1 = conn.returnInsertResult(iQuery1)
                    dRet2 = conn.returnInsertResult(iQuery2)
                    if dRet0['result'] == 'success' and dRet1['result'] == 'success' and dRet2['result'] == 'success':
                        # mongo update
                        sQueryMongo = "select machine_fqdn from ai_machine where active_yn='Y' and machine_id in({0})".format(
                            ','.join([str(i) for i in lMachineRefs])
                        )
                        dRet = conn.returnSelectQueryResultAsList(sQueryMongo)
                        if dRet['result'] == 'success':
                            fqdns = dRet['data']['machine_fqdn']
                            mRet = mong.mongoAction(action='update', group_name=dPayload['group_name'], fqdn_list=fqdns)
                        logINFO("Group modified successfully")
                        return json.dumps({'result': 'success', 'data': 'Group modified successfully'})
                    else:
                        return logAndRet("failure", "Group modification failed")
                else:
                    return logAndRet("failure", "Invalid Payload!")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteGroup(group_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                iQuery = "update ai_machine_grouping set active_yn='{0}' where pk_ai_machine_group_id={1}".format('N', group_id)
                dRet = conn.returnInsertResult(iQuery)
                if dRet['result'] == 'success':
                    # mongo update
                    sQuery = "select group_name from ai_machine_grouping where active_yn='Y' and pk_ai_machine_group_id={0}".format(group_id)
                    dRet = conn.returnSelectQueryResult(sQuery)
                    if dRet['result'] == 'success':
                        mRet = mong.mongoAction(action='delete', group_name=dRet['data'][0]['group_name'])
                    return logAndRet("success", "Group deleted successfully")
                else:
                    return logAndRet("failure", "Group deletion failed")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


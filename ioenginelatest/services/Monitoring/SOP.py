from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
from services.utils.ConnLog import create_log_file
from services.utils import ConnPostgreSQL as pcon
import services.utils.LFColors as lfc
from services.utils import validator_many as payloadvalidator
import json
from flask import request
from services.utils.decoder import decode, encode
from services.Monitoring import policyengine as pe
import services.utils.ConnMQ as connmq

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar
logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def createSOP(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['sop_name', 'alert_json', 'filter', 'sp_flow', 'created_by', 'batch_policies'],
                                                   lMandatory=['sop_name', 'alert_json', 'filter', 'sp_flow', 'created_by', 'batch_policies']):
                    sSOPValidQuery = "select * from sop where lower(sop_name)=lower('{0}') and active_yn='Y'".format(dPayload['sop_name'])
                    dSOPValidRet = pcon.returnSelectQueryResult(sSOPValidQuery)
                    if dSOPValidRet['result'] == 'failure':
                        sop_name = dPayload['sop_name']
                        alert_json = dPayload['alert_json']
                        filter = dPayload['filter']
                        policy = dPayload['policyengine']
                        sp_flow = dPayload['sp_flow']
                        created_by = dPayload['created_by']
                        # Batch Processing: This feature is based on event count
                        batch = dPayload['batch_policies']
                        remarks = dPayload['comments']
                        batch_flag, batch_json = 'N', {}
                        if len(batch['Condition'][list(batch['Condition'].keys())[0]]) != 0:
                            batch_flag = 'Y'
                            batch_json = batch

                        applied = {}
                        validation = pe.createPolicyEngine(d=policy, alert_info=alert_json, batch_flag=batch_flag, batch_json=batch_json)
                        if validation['result'] == 'failure' or validation['result'] == 'conflict':
                            return json.dumps(validation)
                        pe_id = validation['info']
                        iSOPQuery = "insert into sop(sop_name, alert_info, filters, sop_flow, status, created_by, create_on, active_yn, applied, pe_id, remarks) values('{0}', '{1}', '{2}', '{3}', 'submitted', {4}, now(), '{5}', '{6}', {7}, '{8}') returning pk_sop_id".format(
                            sop_name, json.dumps(alert_json).replace("'", "''"), json.dumps(filter).replace("'", "''"), json.dumps(sp_flow).replace("'", "''"), created_by, 'Y', json.dumps(policy).replace("'", "''"), pe_id,
                            remarks
                        )
                        dSOPRet = pcon.returnSelectQueryResultWithCommit(iSOPQuery)
                        if dSOPRet['result'] == 'success':
                            # record in history table
                            iSOPHistory = "insert into sop_history(fk_sop_id, fk_user_id, user_type, sop_h_created_dt, remarks) values({0}, {1},'AUTHOR', now(), '{2}')".format(
                                dSOPRet['data'][0]['pk_sop_id'], created_by, remarks
                            )
                            dSOPHistory = pcon.returnInsertResult(iSOPHistory)
                            # pushed2FE = connmq.send2MQ(pQueue='newkb', pExchange='EVM',
                            #                            pRoutingKey='newkb',
                            #                            pData=json.dumps({'policyid': pe_id}))

                            # k = {"Machine": "ci_name", "Application": "component", "Description": "description",
                            #      "Extra Description": "notes", "Value": "value", "CMDLine": "cmdline"}
                            # m = {"Machine": "machine", "Application": "application", "Description": "description",
                            #      "Extra Description": "extra_description", "Value": "value", "CMDLine": "cmdline"}
                            # k = {"machine": "ci_name", "application": "component", "description": "description",
                            #      "extra_description": "notes", "value": "value", "cmdline": "cmdline"}
                            # m = {"machine": "machine", "application": "application", "description": "description",
                            #      "extra_description": "extra_description", "value": "value", "cmdline": "cmdline"}
                            # uQuery = "update alert_data set fk_sop_id='{0}' where ".format(sop_name)
                            # for i in filter:
                            #     uQuery += " {0}='{1}' and ".format(k[i], alert_json[m[i]])
                            # uQuery += " fk_sop_id is null"
                            # uRet = pcon.returnInsertResult(uQuery)
                            return json.dumps({'result': 'success', 'data': 'SOP added successfully.'})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'SOP addition failed.'})
                    else:
                        return json.dumps({'result': 'failure', 'data': 'SOP already exists. Choose a different name.'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getSOPHistory(sop_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = '''
select 
    sh.user_type, usr.user_id, sh.remarks, to_char(sh.sop_h_created_dt, 'DD-MM-YYYY HH24:MI:SS') datetime
from 
    sop_history sh 
    inner join sop s on(s.pk_sop_id=sh.fk_sop_id) 
    inner join tbl_user_details usr on(usr.pk_user_details_id=sh.fk_user_id)
where s.pk_sop_id={0} 
order by sop_h_created_dt desc'''.format(sop_id)
                print(sQuery)
                dRet = pcon.returnSelectQueryResult(sQuery)
                print(dRet)
                if dRet['result'] == 'success':
                    return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'no data'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getSOPList():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
#                 sQuery = """
# select
# 	s.pk_sop_id sop_id, s.sop_name, s.alert_info, s.filters, s.applied, s.sop_flow, s.status, s.created_by, to_char(s.create_on, 'DD-MM-YYYY HH24:MI') create_on, a.pk_bot_id bot_id, COALESCE(a.bot_name, '') bot_name
# from
# 	sop s left join ai_bot_repo a on(s.bot_id=a.pk_bot_id)
# where
# 	s.active_yn='Y' order by s.create_on desc"""
                sQuery = """
select 
	s.pk_sop_id sop_id, s.sop_name, s.alert_info, s.filters, s.applied, s.sop_flow, s.status, s.created_by, to_char(s.create_on, 'DD-MM-YYYY HH24:MI') create_on, a.pk_bot_id bot_id, COALESCE(a.bot_name, '') bot_name, pe.batch_flag, pe.batch_payload 
from 
	sop s left join ai_bot_repo a on(s.bot_id=a.pk_bot_id) 
	inner join policyengine pe on(s.pe_id=pe.pk_pk_id)
where 
	s.active_yn='Y' order by s.create_on desc"""

                sQuery = """
select A.*, u.user_id QA from (
select 
	s.pk_sop_id sop_id, s.sop_name, s.alert_info, s.filters, s.applied, s.sop_flow, s.status, s.created_by, to_char(s.create_on, 'DD-MM-YYYY HH24:MI') create_on, a.pk_bot_id bot_id, COALESCE(a.bot_name, '') bot_name, pe.batch_flag, pe.batch_payload, u.user_id author, s.qa_by 
from 
	sop s left join ai_bot_repo a on(s.bot_id=a.pk_bot_id) 
	inner join policyengine pe on(s.pe_id=pe.pk_pk_id) 
	inner join tbl_user_details u on(u.pk_user_details_id=s.created_by) 
where 
	s.active_yn='Y' order by s.create_on desc) A
    left join tbl_user_details u on(u.pk_user_details_id=A.qa_by)"""
                dRet = pcon.returnSelectQueryResult(sQuery)
                if dRet['result'] == 'success':
                    return json.dumps(dRet)
                else:
                    return json.dumps({'result': 'failure', 'data': 'no data'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateSOP(dSOPID, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if payloadvalidator.isPayloadValid(dPayload=dPayload, lHeaders=['sop_name', 'alert_json', 'filter', 'sp_flow', 'created_by', 'batch_policies'],
                                                   lMandatory=['sop_name', 'alert_json', 'filter', 'sp_flow', 'created_by', 'batch_policies']):
                    sSOPValidQuery = "select * from sop where pk_sop_id={0} and active_yn='Y'".format(dSOPID)
                    dSOPValidRet = pcon.returnSelectQueryResult(sSOPValidQuery)
                    if dSOPValidRet['result'] == 'success':

                        sSOPValidQueryNameChk = "select * from sop where lower(sop_name)=lower('{0}') and active_yn='Y' and pk_sop_id!={1}".format(dPayload['sop_name'], dSOPID)
                        dSOPValidRetNameChk = pcon.returnSelectQueryResult(sSOPValidQueryNameChk)
                        if dSOPValidRetNameChk['result'] == 'success':
                            return json.dumps({'result': 'failure', 'data': 'SOP name already in use. Choose a different name.'})

                        # Batch Processing: This feature is based on event count
                        batch = dPayload['batch_policies']
                        batch_flag, batch_json = 'N', {}
                        if len(batch['Condition'][list(batch['Condition'].keys())[0]]) != 0:
                            batch_flag = 'Y'
                            batch_json = batch

                        validation = pe.createPolicyEngine(d=dPayload['policyengine'], action='update', policy_id=dSOPValidRet['data'][0]['pe_id'], batch_flag=batch_flag, batch_json=batch_json)
                        if validation['result'] == 'failure' or validation['result'] == 'conflict':
                            return json.dumps(validation)
                        pe_id = validation['info']

                        uQuery = "update sop set alert_info='{0}', filters='{1}', sop_flow='{2}', modified_by={3}, modified_on=now(), applied='{5}', remarks='{6}', sop_name='{7}' where pk_sop_id={4} RETURNING pe_id, pk_sop_id".format(
                            json.dumps(dPayload['alert_json']).replace("'", "''"), json.dumps(dPayload['filter']).replace("'", "''"), json.dumps(dPayload['sp_flow']).replace("'", "''"), dPayload['created_by'], dSOPID,
                            json.dumps(dPayload['policyengine']).replace("'", "''"), dPayload['comments'].replace("'", "''"),
                            dPayload['sop_name']
                        )
                        dRet = pcon.returnSelectQueryResultWithCommit(uQuery)
                        if dRet['result'] == 'success':
                            pe_id = dRet['data'][0]['pe_id']
                            uQuery = "update policyengine set batch_payload='{0}' where pk_pk_id={1}".format(json.dumps(dPayload['batch_policies']).replace("'", "''"), pe_id)
                            dRet1 = pcon.returnInsertResult(uQuery)
                            # record in history table
                            iSOPHistory = "insert into sop_history(fk_sop_id, fk_user_id, user_type, sop_h_created_dt, remarks) values({0}, {1},'AUTHOR', now(), '{2}')".format(
                                dRet['data'][0]['pk_sop_id'], dPayload['created_by'], dPayload['comments'].replace("'", "''")
                            )
                            dSOPHistory = pcon.returnInsertResult(iSOPHistory)
                            return json.dumps({'result': 'success', 'data': 'SOP Modified'})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'Failed to modify SOP'})
                    else:
                        return json.dumps({'result': 'failure', 'data': 'Payload is not valid.'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def deleteSOP(dSOPID):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                # If any open alerts are there for sop, dont allow to delete

                peQuery = "update policyengine set active_yn='N' where pk_pk_id=(select pe_id from sop where pk_sop_id={0})".format(dSOPID)
                peRet = pcon.returnInsertResult(peQuery)
                dQuery = "update sop set active_yn='N' where pk_sop_id={0}".format(dSOPID)
                dRet = pcon.returnInsertResult(dQuery)
                if dRet['result'] == 'success':
                    return json.dumps({'result': 'success', 'data': 'Removed SOP'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Failed to remove SOP'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def createNewBOT(sBranchID, dPayload):
    """Methods: This method is used to create a new bot"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                lAttr = ["bot_type", "bot_name", "bot_description", "bot_language", "bot_script", "platform_type", "os_type", "component", "botargs"]
                lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
                lPayValuesErr = [1 if (not i.strip() == "") else 0 for i in dPayload.values()]
                if not (0 in lPayErr or 0 in lPayValuesErr):
                    sBOTType = dPayload["bot_type"]
                    sBOTName = dPayload["bot_name"]
                    sBOTDesc = dPayload["bot_description"]
                    sBOTLang = dPayload["bot_language"]
                    sScript = encode('auto!ntell!', dPayload["bot_script"])
                    sPlatform = dPayload["platform_type"]
                    sOS = dPayload["os_type"]
                    sCom = dPayload["component"]
                    sArgs = dPayload["botargs"]
                    sInsertQuery = """insert into ai_bot_repo(bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, modified_date, botargs, active_yn) 
values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', extract(epoch from now()), '%s', 'Y') RETURNING pk_bot_id""" %(sBOTType, sBOTName, sBOTDesc, sBOTLang, sScript, sPlatform, sOS, sCom, sArgs)
                    dRet = pcon.returnSelectQueryResultWithCommit(sInsertQuery)
                    if dRet["result"] == "success":
                        logINFO("New Bot created {0}".format(sBOTName))
                        uQueryBOT = "update sop set bot_id={0} where pk_sop_id={1}".format(dRet["data"][0]["pk_bot_id"], sBranchID)
                        uRet = pcon.returnInsertResult(uQueryBOT)
                        if uRet['result'] == 'success':
                            return json.dumps({"result": "success", "data": dRet["data"][0]["pk_bot_id"]})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'Failed to create BOT'})
                    else:
                        return logAndRet("failure", "Unable to create the BOT")
                else:
                    return logAndRet("failure", "Payload Error: Either key or value is missing")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def approveSOP(sop_id, dPayload):
    """Methods: This method is used to create a new bot"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                approver_id = dPayload['approver_id']
                comments = dPayload['comments']
                status = dPayload['action']
                iQuery = "update sop set status='{0}', remarks='{1}', qa_by={3}, qa_on={4} where pk_sop_id={2} RETURNING pe_id".format(
                    status, comments, sop_id, approver_id, 'now()'
                )
                dRet = pcon.returnSelectQueryResultWithCommit(iQuery)
                if dRet['result'] == 'success':
                    pe_id = dRet['data'][0]['pe_id']
                    pushed2FE = connmq.send2MQ(pQueue='newkb', pExchange='EVM',
                                               pRoutingKey='newkb',
                                               pData=json.dumps({'policyid': pe_id}))

                    # record in history table
                    iSOPHistory = "insert into sop_history(fk_sop_id, fk_user_id, user_type, sop_h_created_dt, remarks) values({0}, {1},'QA', now(), '{2}')".format(
                        sop_id, approver_id, comments
                    )
                    dSOPHistory = pcon.returnInsertResult(iSOPHistory)
                    return json.dumps({'result': 'success', 'data': 'SOP Approved. Open matching alerts would be applied with SOP.'})
                else:
                    return json.dumps({'result': 'failure', 'data': 'Unable to approve SOP'})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


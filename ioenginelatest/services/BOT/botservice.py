#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL
from services.utils.decoder import decode, encode
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

def getBOTMapping():
    """Method: This method gives the complete mapping details of folders alone :  branch id, name, type & parent id"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
	pk_tree_id as id, name, type, COALESCE(cast(fk_parent_id as varchar),'') as parent_id  
from 
	ai_bot_tree 
where 
	active_yn='Y' and type='d'"""
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    return logAndRet("failure", "Unable to fetch BOT Tree Structure")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def insertNewBOT(dPayload):
    """Method: This method is basically used to create sub branch. Sub Branch would be a folder or a file(script file - actual bot)
    Payload: {
"name": "",
"type": "",
"parent_id": ""
}"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                lAttr = ["name", "type", "parent_id"]
                lPayErr = [1 if i in lAttr else 0 for i in dPayload.keys()]
                lPayValuesErr = [1 if (not i.strip() == "") else 0 for i in dPayload.values()]
                if not ((0 in lPayErr) or (0 in lPayValuesErr)):
                    sName = dPayload["name"]
                    sType = dPayload["type"]
                    sParentID = dPayload["parent_id"]
                    sInsertQuery = "insert into ai_bot_tree(name, type, fk_parent_id, active_yn) values('" + sName + "','" + sType + "'," + sParentID + ",'Y')  RETURNING pk_tree_id"
                    dRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sInsertQuery)
                    if dRet["result"] == "success":
                        logINFO("New bot created {0}".format(sName))
                        return json.dumps({"result": "success", "data": dRet["data"][0]["pk_tree_id"]})
                    else:
                        return logAndRet("failure", "Unable to create the branch")
                else:
                    return logAndRet("failure", "Payload Error: Either Key or value is empty to proceed with the action")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def removeBOT(pBranchID):
    """Method: To delete the branch or file"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                chkQuery = "select count(*) as total from ai_bot_tree where fk_parent_id=" + pBranchID + " and active_yn='Y'"
                dRet = ConnPostgreSQL.returnSelectQueryResult(chkQuery)
                if dRet["result"] == "success":
                    if dRet["data"][0]["total"] <= 0:
                        sUpdateQuery = "update ai_bot_tree set active_yn='N' where pk_tree_id=" + pBranchID
                        dRet = ConnPostgreSQL.returnInsertResult(sUpdateQuery)
                        if dRet["result"] == "success":
                            return logAndRet("success", "Branch {0} deleted successfully.".format(pBranchID))
                        else:
                            return logAndRet("failure", "Cannot delete Branch {0}".format(pBranchID))
                    else:
                        return logAndRet("failure", "Branch {0} cannot be delete because it has one or more child".format(pBranchID))
                else:
                    return logAndRet("failure", dRet["data"])
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def renameBOT(pBranchName, pBranchID):
    """Method: To delete the branch or file"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                chkQuery = "select count(*) as total from ai_bot_tree where pk_tree_id=" + pBranchID + " and active_yn='Y'"
                dRet = ConnPostgreSQL.returnSelectQueryResult(chkQuery)
                if dRet["result"] == "success":
                    sUpdateQuery = "update ai_bot_tree set name='" + pBranchName + "' where pk_tree_id=" + pBranchID
                    dRet = ConnPostgreSQL.returnInsertResult(sUpdateQuery)
                    if dRet["result"] == "success":
                        return logAndRet("success", "Branch {0} renamed successfully.".format(pBranchName))
                    else:
                        return logAndRet("failure", "Cannot rename the branch {0}".format(pBranchName))
                else:
                    return logAndRet("failure", "Cannot rename the branch {0}".format(pBranchName))
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getBOTFile():
    """Method: This method gives the complete mapping details of folders alone :  branch id, name, type & parent id"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
    pk_bot_id as bot_id, bot_name, bot_description, TO_CHAR(TO_TIMESTAMP(created_date),'DD/MM/YYYY HH24:MI:SS') as created_date 
from 
    ai_bot_repo 
where 
    active_yn='Y' """
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    return logAndRet("failure", "Unable to fetch BOT File")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getBOTFiles(sBranchID):
    """Method: This method gives the complete mapping details of folders alone :  branch id, name, type & parent id"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
    pk_bot_id as bot_id, bot_name, bot_description, TO_CHAR(TO_TIMESTAMP(created_date),'DD/MM/YYYY HH24:MI:SS') as created_date 
from 
    ai_bot_repo 
where 
    active_yn='Y' and fk_branch_id=""" + sBranchID
                dRet = ConnPostgreSQL.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    return logAndRet("failure", "Unable to fetch BOT Files")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getDropDownDetails():
    """"Method: This method returns all the master details like bot type, bot lang, platform types, os types"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                dRet = {
                    "bot_type": ["R", "D"],
                    "bot_lang": ["yaml", "python", "bash", "powershell"],
                    "platform_type": ["Win32NT", "Linux", "Network", "Security", "Storage", "Database", "Application"],
                    "os_type": {
                        "Win32NT": ["Windows"],
                        "Linux": ["RedHat", "CentOS"],
                        "Network": ["cisco", "juniper"],
                        "Security": [],
                        "Storage": ["emc", "netapp"],
                        "Database": ["oracle", "mssql", "mysql", "postgres"],
                        "Application": ["iis", "tomcat", "glassfish"]
                    }
                }
                return json.dumps({"result": "success", "data": dRet})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getBOTFileByBotID(sBotID):
    """Method: This method gives the complete mapping details of folders alone :  branch id, name, type & parent id"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = """
select 
    bot_type, bot_name, bot_description, bot_language, script as bot_script, platform_type, os_type, component, botargs 
from 
    ai_bot_repo 
where 
    active_yn='Y' and pk_bot_id=""" + sBotID
                dRet = ConnPostgreSQL.returnSelectQueryResult(sQuery)
                if dRet["result"] == "success":
                    dRet["data"][0]["bot_script"] = decode('auto!ntell!', dRet["data"][0]["bot_script"])
                    return json.dumps(dRet)
                else:
                    return logAndRet("failure", "Unable to fetch BOT files")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateBOTContent(sBotID, dPayload):
    """Method: This method is used to update the bot details"""
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
                    sScript = dPayload["bot_script"]
                    sPlatform = dPayload["platform_type"]
                    sOS = dPayload["os_type"]
                    sCom = dPayload["component"]
                    sArgs = dPayload["botargs"]
                    iUpdateQuery = """
update 
    ai_bot_repo 
set 
    bot_type='%s', bot_name='%s', bot_description='%s', bot_language='%s', script='%s', platform_type='%s', os_type='%s', component='%s', botargs='%s' 
where 
    pk_bot_id=%s""" %(sBOTType, sBOTName, sBOTDesc, sBOTLang, encode('auto!ntell!', sScript), sPlatform, sOS, sCom, sArgs, sBotID)
                    dRet = ConnPostgreSQL.returnInsertResult(iUpdateQuery)
                    if dRet["result"] == "success":
                        return json.dumps({"result": "success", "data": "Bot has been updated successfully"})
                    else:
                        logERROR("Updating BOT content failed")
                        return json.dumps(dRet)
                else:
                    return logAndRet("failure", "Payload Error: Either key or value is missing")
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
                    sInsertQuery = """insert into ai_bot_repo(bot_type, bot_name, bot_description, bot_language, script, platform_type, os_type, component, modified_date, botargs, fk_branch_id, active_yn) 
values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', extract(epoch from now()), '%s', %s, 'Y') RETURNING pk_bot_id""" %(sBOTType, sBOTName, sBOTDesc, sBOTLang, sScript, sPlatform, sOS, sCom, sArgs, sBranchID)
                    dRet = ConnPostgreSQL.returnSelectQueryResultWithCommit(sInsertQuery)
                    if dRet["result"] == "success":
                        logINFO("New Bot created {0}".format(sBOTName))
                        return json.dumps({"result": "success", "data": dRet["data"][0]["pk_bot_id"]})
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

def deleteBOT(sBotID):
    """Methods: This method is used to delete a bot"""
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sDELQuery = "select count(*) as total from ai_bot_repo where pk_bot_id=" + sBotID
                dRet = ConnPostgreSQL.returnSelectQueryResult(sDELQuery)
                if dRet["result"] == "success":
                    iUpdateQuery = "update ai_bot_repo set active_yn='N' where pk_bot_id=" + sBotID
                    dURet = ConnPostgreSQL.returnInsertResult(iUpdateQuery)
                    if dURet["result"] == "success":
                        if dURet["data"] > 0:
                            logINFO("BOT {0} deleted".format(sBotID))
                            return json.dumps({"result": "success", "data": "BOT deleted successfully"})
                        else:
                            return logAndRet("failure", "BOT deletion failed")
                    else:
                        return json.dumps(dURet)
                else:
                    return logAndRet("failure", "The bot is not available to delete")
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing



















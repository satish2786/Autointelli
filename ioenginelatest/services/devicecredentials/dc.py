#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as conn
import services.utils.validator_many as val
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc
from werkzeug.utils import secure_filename

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

ALLOWED_EXTENSION = set(['pem', 'txt'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

# request.form with files
def createCredentials1(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                print(dPayload)
                out = dPayload.getlist("model")
                import json
                out = json.loads(out[0])
                for i in out:
                    print(i, out[i])
                lK = ["cred_name", "cred_type"]
                lM = ["cred_name", "cred_type"]
                if val.isPayloadValid(dPayload, lK, lM) or 1==1:
                    print(request.files)
                    if "files" not in request.files:
                        return json.dumps({'result': 'failure', 'data': 'No file in the request'})
                    files = request.files.getlist('files')
                    for eachFile in files:
                        if eachFile in allowed_file(eachFile.filename):
                            filename = secure_filename(eachFile.filename)
                            eachFile.save('/tmp/' + filename)
                            return json.dumps({'result': 'failure', 'data': 'File saved successfully'})
                        else:
                            return json.dumps({'result': 'failure', 'data': 'Extension not allowed'})
                else:
                    return json.dumps({"result": "failure", "data": "Key or Value is missing"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def createCredentials(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if "cred_type" in dPayload:

                    iQuery = ""
                    if "cred_name" in dPayload:
                        chkQuery = "select count(*) as total from ai_device_credentials where lower(cred_name)='" + \
                                   dPayload['cred_name'].lower() + "' and active_yn='Y'"
                        dRet = conn.returnSelectQueryResult(chkQuery)
                        if dRet["result"] == "success":
                            if dRet["data"][0]["total"] > 0:
                                return json.dumps({"result": "failure", "data": "Credential already exists. Choose a different name"})

                    if dPayload["cred_type"] == "WINRM" or dPayload["cred_type"] == "HTTP" or dPayload["cred_type"] == "HTTPS":
                        h = ['cred_name', 'cred_type', 'username', 'password']
                        m = ['cred_name', 'cred_type', 'username', 'password']
                        if val.isPayloadValid(dPayload, h, m):
                            iQuery += "insert into ai_device_credentials(cred_name, cred_type, username, password, active_yn) values('{0}', '{1}', '{2}', '{3}', 'Y')".format(
                                dPayload['cred_name'], dPayload['cred_type'], dPayload['username'], dPayload['password']
                            )
                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    elif dPayload["cred_type"] == "SSH":
                        h = ['cred_name', 'cred_type', 'username', 'password', 'sudo', 'enable']
                        m = ['cred_name', 'cred_type', 'username', 'password', 'sudo', 'enable']
                        if val.isPayloadValid(dPayload, h, m):
                            if dPayload['enable'] == True:
                                h.append('enable_password')
                                m.append('enable_password')
                                if val.isPayloadValid(dPayload, h, m):
                                    iQuery += "insert into ai_device_credentials(cred_name, cred_type, username, password, sudo_yn, enable_yn, enable_password, active_yn) values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', 'Y')".format(
                                        dPayload['cred_name'], dPayload['cred_type'], dPayload['username'],
                                        dPayload['password'], ('Y' if dPayload['sudo'] == True else 'N'),
                                        ('Y' if dPayload['enable'] == True else 'N'), dPayload['enable_password']
                                    )
                                else:
                                    return json.dumps({"result": "success", "data": "Enable password missing"})
                            else:
                                iQuery += "insert into ai_device_credentials(cred_name, cred_type, username, password, sudo_yn, enable_yn, active_yn) values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', 'Y')".format(
                                    dPayload['cred_name'], dPayload['cred_type'], dPayload['username'],
                                    dPayload['password'], ('Y' if dPayload['sudo'] == True else 'N'),
                                    ('Y' if dPayload['enable'] == True else 'N')
                                )
                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    elif dPayload["cred_type"] == "SSH KEY":
                        h = ['cred_name', 'cred_type', 'username', 'key', 'passphrase', 'sudo']
                        m = ['cred_name', 'cred_type', 'username', 'key', 'passphrase', 'sudo']
                        if val.isPayloadValid(dPayload, h, m):
                            iQuery += "insert into ai_device_credentials(cred_name, cred_type, username, key, passphrase, sudo_yn, active_yn) values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', 'Y')".format(
                                dPayload['cred_name'], dPayload['cred_type'], dPayload['username'],
                                dPayload['key'], dPayload['passphrase'],
                                ('Y' if dPayload['sudo'] == True else 'N')
                            )
                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    elif dPayload["cred_type"] == "SNMP":
                        h = ['cred_name', 'cred_type', 'version']
                        m = ['cred_name', 'cred_type', 'version']
                        if val.isPayloadValid(dPayload, h, m):
                            if dPayload['version'] == 'v2':
                                h.append('community_string')
                                m.append('community_string')
                                if val.isPayloadValid(dPayload, h, m):
                                    iQuery += "insert into ai_device_credentials(cred_name, cred_type, version, community_string, active_yn) values('{0}', '{1}', '{2}', '{3}', 'Y')".format(
                                        dPayload['cred_name'], dPayload['cred_type'], dPayload['version'],
                                        dPayload['community_string']
                                    )
                                else:
                                    return json.dumps({"result": "success", "data": "Community string missing"})
                            elif dPayload['version'] == 'v3':
                                h.extend(['username', 'password'])
                                m.extend(['username', 'password'])
                                if val.isPayloadValid(dPayload, h, m):
                                    iQuery += "insert into ai_device_credentials(cred_name, cred_type, version, username, password, active_yn) values('{0}', '{1}', '{2}', '{3}', '{4}', 'Y')".format(
                                        dPayload['cred_name'], dPayload['cred_type'], dPayload['version'],
                                        dPayload['username'], dPayload['password']
                                    )
                                else:
                                    return json.dumps({"result": "success", "data": "Credentials missing"})

                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    elif dPayload["cred_type"] == "PAM":
                        h = ['cred_name', 'cred_type', 'username']
                        m = ['cred_name', 'cred_type', 'username']
                        if val.isPayloadValid(dPayload, h, m):
                            iQuery += "insert into ai_device_credentials(cred_name, cred_type, username, active_yn) values('{0}', '{1}', '{2}', 'Y')".format(
                                dPayload['cred_name'], dPayload['cred_type'], dPayload['username']
                            )
                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    else:
                        return json.dumps({"result": "success", "data": "Cred Type not supported"})
                    dRet = conn.returnInsertResult(iQuery)
                    if dRet['result'] == 'success':
                        return json.dumps({"result": "success", "data": "Credential added successfully"})
                    else:
                        return json.dumps({"result": "success", "data": "Failed to add credential"})
                else:
                    return json.dumps({"result": "success", "data": "Information missing"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

# Old One
def createCredentialsOld(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                lK = ["cred_name", "cred_type", "username", "password", "port", "sudo"]
                lM = ["cred_name", "cred_type",  "password", "port"]
                if val.isPayloadValid(dPayload, lK, lM):

                    #check if credentials name already exists
                    chkQuery = "select count(*) as total from ai_device_credentials where lower(cred_name)='" + dPayload["cred_name"].lower() + "' and active_yn='Y'"
                    dRet = conn.returnSelectQueryResult(chkQuery)
                    if dRet["result"] == "success":
                        if dRet["data"][0]["total"] > 0:
                            return json.dumps({"result": "failure", "data": "Credential already exists."})

                    sCredName = dPayload["cred_name"]
                    sCredType = dPayload["cred_type"]
                    sUserName = dPayload["username"]
                    sPassword = dPayload["password"]
                    sSudo = dPayload["sudo"]
                    sPort = dPayload["port"]
                    sQuery = "insert into ai_device_credentials(cred_name, cred_type, username, password, sudo_yn, port, active_yn) values('%s', '%s', '%s', '%s', '%s', %s, '%s')" %(
                        sCredName, sCredType, sUserName, sPassword, sSudo, sPort, 'Y'
                    )
                    dRet = conn.returnInsertResult(sQuery)
                    if dRet["result"] == "success":
                        logINFO("New credentials added {0}".format(sCredName))
                        return json.dumps({"result": "success", "data": "Credential added successfully"})
                    else:
                        return logAndRet("failure", dRet["data"])
                else:
                    return json.dumps({"result": "success", "data": "Key or Value is missing"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def getCredentialList():
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sQuery = "select cred_id, cred_name, cred_type, username, sudo_yn, enable_yn, version from ai_device_credentials where active_yn='Y'"
                dRet = conn.returnSelectQueryResultAs2DList(sQuery)
                if dRet["result"] == "success":
                    return json.dumps(dRet)
                else:
                    logERROR("Unable to fetch Device Credentials from database.")
                    return json.dumps(dRet.update({"error": "Unable to fetch Device Credentials from database."}))
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def updateCredentials(cred_id, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                if "cred_type" in dPayload:

                    uQuery = ""
                    if "cred_name" in dPayload:
                        chkQuery = "select count(*) as total from ai_device_credentials where lower(cred_name)='{0}' and cred_id != {1} and active_yn='Y'".format(
                            dPayload['cred_name'], cred_id
                        )
                        dRet = conn.returnSelectQueryResult(chkQuery)
                        if dRet["result"] == "success":
                            if dRet["data"][0]["total"] > 0:
                                return json.dumps({"result": "failure", "data": "Credential already exists. Choose a different name"})

                    if dPayload["cred_type"] == "WINRM" or dPayload["cred_type"] == "HTTP" or dPayload["cred_type"] == "HTTPS":
                        h = ['cred_name', 'cred_type', 'username', 'password']
                        m = ['cred_name', 'cred_type', 'username', 'password']
                        if val.isPayloadValid(dPayload, h, m):
                            uQuery += "update ai_device_credentials set cred_name='{0}', cred_type='{1}', username='{2}', password='{3}' where cred_id={4}".format(
                                dPayload['cred_name'], dPayload['cred_type'], dPayload['username'], dPayload['password'], cred_id
                            )
                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    elif dPayload["cred_type"] == "SSH":
                        h = ['cred_name', 'cred_type', 'username', 'password', 'sudo', 'enable']
                        m = ['cred_name', 'cred_type', 'username', 'password', 'sudo', 'enable']
                        if val.isPayloadValid(dPayload, h, m):
                            if dPayload['enable'] == True:
                                h.append('enable_password')
                                m.append('enable_password')
                                if val.isPayloadValid(dPayload, h, m):
                                    uQuery += "update ai_device_credentials set cred_name='{0}', cred_type='{1}', username='{2}', password='{3}', sudo_yn='{4}', enable_yn='{5}', enable_password='{6}'  where cred_id={7}".format(
                                        dPayload['cred_name'], dPayload['cred_type'], dPayload['username'],
                                        dPayload['password'], ('Y' if dPayload['sudo'] == True else 'N'),
                                        ('Y' if dPayload['enable'] == True else 'N'), dPayload['enable_password'], cred_id
                                    )
                                else:
                                    return json.dumps({"result": "success", "data": "Enable password missing"})
                            else:
                                uQuery += "update ai_device_credentials set cred_name='{0}', cred_type='{1}', username='{2}', password='{3}', sudo_yn='{4}'  where cred_id={5}".format(
                                    dPayload['cred_name'], dPayload['cred_type'], dPayload['username'],
                                    dPayload['password'], ('Y' if dPayload['sudo'] == True else 'N'), cred_id
                                )
                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    elif dPayload["cred_type"] == "SSH KEY":
                        h = ['cred_name', 'cred_type', 'username', 'key', 'passphrase', 'sudo']
                        m = ['cred_name', 'cred_type', 'username', 'key', 'passphrase', 'sudo']
                        if val.isPayloadValid(dPayload, h, m):
                            uQuery += "update ai_device_credentials set cred_name='{0}', cred_type='{1}', username='{2}', key='{3}', passphrase='{4}', sudo_yn='{5}'  where cred_id={6}".format(
                                dPayload['cred_name'], dPayload['cred_type'], dPayload['username'],
                                dPayload['key'], dPayload['passphrase'],
                                ('Y' if dPayload['sudo'] == True else 'N'), cred_id
                            )
                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    elif dPayload["cred_type"] == "SNMP":
                        h = ['cred_name', 'cred_type', 'version']
                        m = ['cred_name', 'cred_type', 'version']
                        if val.isPayloadValid(dPayload, h, m):
                            if dPayload['version'] == 'v2':
                                h.append('community_string')
                                m.append('community_string')
                                if val.isPayloadValid(dPayload, h, m):
                                    uQuery += "update ai_device_credentials set cred_name='{0}', cred_type='{1}', version='{2}', community_string='{3}' where cred_id={4}".format(
                                        dPayload['cred_name'], dPayload['cred_type'], dPayload['version'],
                                        dPayload['community_string'], cred_id
                                    )
                                else:
                                    return json.dumps({"result": "success", "data": "Community string missing"})
                            elif dPayload['version'] == 'v3':
                                h.extend(['username', 'password'])
                                m.extend(['username', 'password'])
                                if val.isPayloadValid(dPayload, h, m):
                                    uQuery += "update ai_device_credentials set cred_name='{0}', cred_type='{1}', version='{2}', username='{3}', password='{4}' where cred_id={5}".format(
                                        dPayload['cred_name'], dPayload['cred_type'], dPayload['version'],
                                        dPayload['username'], dPayload['password'], cred_id
                                    )
                                else:
                                    return json.dumps({"result": "success", "data": "Credentials missing"})

                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    elif dPayload["cred_type"] == "PAM":
                        h = ['cred_name', 'cred_type', 'username']
                        m = ['cred_name', 'cred_type', 'username']
                        if val.isPayloadValid(dPayload, h, m):
                            uQuery += "update ai_device_credentials set cred_name='{0}', cred_type='{1}', username='{2}' where cred_id={3}".format(
                                dPayload['cred_name'], dPayload['cred_type'], dPayload['username'], cred_id
                            )
                        else:
                            return json.dumps({"result": "success", "data": "Information missing"})

                    else:
                        return json.dumps({"result": "success", "data": "Cred Type not supported"})
                    dRet = conn.returnInsertResult(uQuery)
                    if dRet['result'] == 'success':
                        return json.dumps({"result": "success", "data": "Credential updated successfully"})
                    else:
                        return json.dumps({"result": "success", "data": "Failed to update credential"})
                else:
                    return json.dumps({"result": "success", "data": "Information missing"})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

# Old One
def updateCredentialsOld(cred_name, dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                username = dPayload["username"]
                password = dPayload["password"]
                sChkQuery = "select count(*) as total from ai_device_credentials where lower(cred_name)='" + cred_name.lower() + "' and active_yn='Y'"
                dRetTot = conn.returnSelectQueryResult(sChkQuery)
                if dRetTot["result"] == "success":
                    iQuery = "update ai_device_credentials set username='" + username + "', password='" + password + "' where lower(cred_name)='" + cred_name.lower() + "' and active_yn='Y'"
                    dRetI = conn.returnInsertResult(iQuery)
                    if dRetI["result"] == "success" and dRetI["data"] > 0:
                        logINFO("Credential {0} updated".format(cred_name))
                        return json.dumps({"result": "success", "data": "Device Credential Updated"})
                    else:
                        logERROR("Failed to update credential {0}".format(cred_name))
                        return json.dumps(dRetI)
                else:
                    logINFO("Credential not found {0}".format(cred_name))
                    return json.dumps(dRetTot)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing

def removeCredentials(cred_id):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                sChkQuery = "select count(*) as total from ai_device_credentials where cred_id='{0}' and active_yn='Y'".format(cred_id)
                dRetTot = conn.returnSelectQueryResult(sChkQuery)
                if dRetTot["result"] == "success":
                    sChkQuery = "select count(pk_discovery_id) as total from ai_device_discovery where fk_cred_id in({0})".format(cred_id)
                    dRetChk = conn.returnSelectQueryResult(sChkQuery)
                    if dRetChk["result"] == "success":
                        if dRetChk["data"][0]["total"] < 1:
                            iQuery = "update ai_device_credentials set active_yn='N' where cred_id='{0}' and active_yn='Y'".format(cred_id)
                            dRetI = conn.returnInsertResult(iQuery)
                            if dRetI["result"] == "success" and dRetI["data"] > 0:
                                logINFO("Credential removed")
                                return json.dumps({"result": "success", "data": "Device Credentials Deleted"})
                            else:
                                return logAndRet("failure", dRetI["data"])
                        else:
                            return logAndRet("failure", "Devices are attached with this credential. Dettach and Try once again.")
                else:
                    logINFO("Credential not found {0}".format(cred_id))
                    return json.dumps(dRetTot)
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing
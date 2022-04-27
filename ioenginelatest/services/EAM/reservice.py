#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL
from services.utils import sessionkeygen
from copy import deepcopy
import requests as restcall
from services.utils.decoder import decode
import time
from services.utils.ConnLog import create_log_file
from services.utils.ValidatorSession import chkValidRequest, chkKeyExistsInHeader, lam_api_key_invalid, lam_api_key_missing
import services.utils.LFColors as lfc
import re

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

def validatePEAttribInternal(dPayload):
    try:
        pattern = dPayload['pattern']
        sample = dPayload['sample']
        subs = []
        try:
            ret = re.search(pattern, sample, re.M | re.I)
            if ret is None:
                return {'result': 'failure', 'data': "Pattern doesn't match with sample"}
            elif (ret is not None) and (ret.lastindex is None):
                return {'result': 'success', 'data': {'groups': subs}}
            else:
                for i in range(0, ret.lastindex):
                    subs.append(ret.group(i + 1))
                return {'result': 'success', 'data': {'groups': subs}}
        except Exception as e:
            return {'result': 'failure', 'data': str(e)}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

def validatePEAttrib(dPayload):
    if chkKeyExistsInHeader("SESSIONKEY"):
        if chkValidRequest(request.headers["SESSIONKEY"]):
            try:
                pattern = dPayload['pattern']
                sample = dPayload['sample']
                subs = []
                try:
                    ret = re.search(pattern, sample, re.M | re.I)
                    if ret is None:
                        return json.dumps({'result': 'failure', 'data': "Pattern doesn't match with sample"})
                    elif (ret is not None) and (ret.lastindex is None):
                        return json.dumps({'result': 'success', 'data': {'groups': subs}})
                    else:
                        for i in range(0, ret.lastindex):
                            subs.append(ret.group(i+1))
                        return json.dumps({'result': 'success', 'data': {'groups': subs}})
                except Exception as e:
                    return json.dumps({'result': 'failure', 'data': str(e)})
            except Exception as e:
                return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return lam_api_key_invalid
    else:
        return lam_api_key_missing


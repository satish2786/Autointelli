import requests as req
from services.utils.ConnLog import create_log_file

import services.utils.LFColors as lfc
lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def pushToWebSocket(pModule, pInfoType, pData, pAction):
    try:
        sURL = "http://localhost:8000/api/v2/async/"
        sURL = "http://127.0.0.1:3891/admin/api/v2/notifications/async"
        dHeader = {'content-type': 'application/json'}
        dData = {"Module": pModule, "InformationType": pInfoType, "Data": pData, "Action": pAction}
        ret = req.post(url=sURL, headers=dHeader, json=dData)
        if ret.status_code == 200:
            return {'result': 'success', 'data': 'Pushed Successfully'}
        else:
            return {'result': 'failure', 'data': 'Failed to push data'}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {'result': 'failure', 'data': 'Failed to push data'}
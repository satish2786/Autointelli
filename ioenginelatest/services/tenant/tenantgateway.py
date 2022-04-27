from flask import Flask, request
from flask_cors import CORS, cross_origin
from ConnLog import create_log_file
import LFColors as lfc
import json
import executor as execscript
# from services.execscript import multi_lang_executor as execscript

# Terminal Colors
lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

# Logging Objects
logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

apiVersion = "1.0"
rootUI = "/tenant/api" + apiVersion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/ui/*": {"origins": "http://localhost:port"}})

########################################################################################################################
# Multi Script Language Executor
# The below API are completely related to multi language executor
########################################################################################################################
@app.route(rootUI + "/execscript", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def funexecscript():
    logERROR("{0} {1}".format(request.url, request.method))
    obj = execscript.multilang()
    obj.global_vars = request.get_json()
    dRet = obj.execute()
    if dRet["result"] == "success":
        return json.dumps({'status': 'true', 'result': obj.global_vars['VARS'], "msg": dRet["std_out"]})
    else:
        return json.dumps({'status': 'false', 'result': obj.global_vars['VARS'], "msg": dRet["std_err"]})

if __name__ == '__main__':
   try:
       app.run(host='127.0.0.1', port=5001, debug=True)
       CORS(app)
   except Exception as e:
       print(str(e))
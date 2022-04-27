
from LDAPAdminService import ldap_api
from ARCONAdminService import arcon_api
from SMTPAdminService import smtpadmin_api
from PolicyEngineAdminService import policy_api
from GenericITSMService import itsm_api
from services.ITSMServices.SDP import itsmsdp_api
from itsmAdminBMCService import bmcadmin_api
#from SMTPService import smtp_api
from services.PatchModule.PatchAdminRest import patchadmin_api
from services.Monitoring.MonitoringData import monitoring_api
from flask import Flask
from sys import exit
from autointelliProcessInstance import proc_api
from botOutputapi import bot_api
from flask_cors import CORS, cross_origin


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.register_blueprint(patchadmin_api)
app.register_blueprint(monitoring_api)
app.register_blueprint(ldap_api)
app.register_blueprint(arcon_api)
app.register_blueprint(smtpadmin_api)
app.register_blueprint(policy_api)
app.register_blueprint(itsm_api)
app.register_blueprint(itsmsdp_api)
app.register_blueprint(proc_api)
app.register_blueprint(bot_api)
app.register_blueprint(bmcadmin_api)
cors = CORS(app, resources={r"/ui/*": {"origins": "http://localhost:port"}})

if __name__ == '__main__':
    try:
      app.run(host='0.0.0.0', port=3890,  threaded=True, debug=True)
    except Exception as e:
      print("Exception occured : "+str(e))
      exit()

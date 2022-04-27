#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================


from flask import Flask, request
from flask_cors import CORS, cross_origin
from services.administration import adminservice
from services.administration import ciname_user_mapping as cinu
from services.administration import customerservice as custserv
from services.EAM import eamservice
from services.dashboard import dashboardNew
from services.BOT import botservice
from services.devicecredentials import dc
from services.devicediscovery import devicediscovery
from services.devicediscovery import hypervisor as hyp
from services.devicediscovery import vmware_cloud as vcd
from services.devicediscovery import nsx
from services.devicediscovery import bandwidth as kvmnsx
from services.dynamicform import itsmdynamicform
from services.dynamicform import triagedynamicform
from services.licensing import licensing
from services.triage import triage
from services.ITSMServices import SDPTktMgmt as tktmgmt
from services.devicediscovery import machinegrouping as mgroup
from services.execscript import multi_lang_executor as execscript
from services.widgetsanddashboards import widgetdashboard as wd
from services.dashboard import dashboardPerformance as perf
from services.Monitoring import nagios_maria as nagmar
from services.customerservices import customeremailmapping as custmail
import json
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
from services.anomaly2event import anomaly2event as a2e
from services.perfrpt import perfreport as perfrpt
from services.orches import orches as kieserver
from services.perfrpt import vmsummaryreport as vmsummrpt
from services.inbound.nxtgen.billing import billing as inb
from services.perfrpt import export2pdf as ex2pdf
from services.execscript import prereq
from services.autoscale import autoscaleservice as autoscaleservice
from services.Monitoring import HAndHGMgmt as monmgmt
from services.Monitoring import SOP as sop
from services.Monitoring import filters as fil
from services.EAM import reservice as res
from services.marketplace.vmware import  vmwareservices as mpvmw
from services.personalize import personalize as pp

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
rootUI = "/ui/api" + apiVersion
rootEAM = "/evm/api" + apiVersion
rootDashboard = "/dashboard/api" + apiVersion
rootBOT = "/bot/api" + apiVersion
rootDD = "/dyndash/api" + apiVersion
rootInB = "/inbound/api" + apiVersion

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/ui/*": {"origins": "http://localhost:port"}})

########################################################################################################################
# Administration
# The below API are completely related to administration
# User Mgmt, Role Mgmt, Login/Logout, Profile Mgmt
########################################################################################################################
@app.route(rootUI + '/roles', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAllRoles():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getAllRoles()

@app.route(rootUI + '/tabs', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAllTabs():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getAllTabs()

@app.route(rootUI + '/permissions', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAllPermission():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getAllPermission()

@app.route(rootUI + '/rolemappers', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getRolesMappers():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getRolesMappers()

@app.route(rootUI + '/rolemappers/<role_name>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getRoleMappers(role_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getOneRoleMappers(role_name)

@app.route(rootUI + '/roles', methods=['POST', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def createRole():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.createRole(request.get_json())

@app.route(rootUI + '/roles/<role_name>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def removeRole(role_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.removeRole(role_name)

@app.route(rootUI + '/roles/<role_name>', methods=['PUT', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def updateRole(role_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.updateRole(role_name)

@app.route(rootUI + '/login', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def checkLogin():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.checkLogin(request.get_json())

@app.route(rootUI + '/loginregi', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def acceptSessionKey():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.acceptSessionKey(request.get_json())

@app.route(rootUI + '/logout', methods = ["DELETE", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def logout():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.logout()

@app.route(rootUI + '/zones', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAllTimeZone():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getAllTimeZone()

@app.route(rootUI + '/usertypes', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getUserTypes():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getUserTypes()

@app.route(rootUI + '/userid', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getUserIDs():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getUserIDs()

@app.route(rootUI + '/createuserprereq', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getUserCreationOneTimeData():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getUserCreationOneTimeData()

@app.route(rootUI + '/users/<user_name>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getSingleUser(user_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getSingleUser(user_name)

@app.route(rootUI + '/users', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getUsers():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getUsers()

@app.route(rootUI + '/users/admin/<user_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getUsersAdminSettings(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.getUsersAdminSettings(user_id)

@app.route(rootUI + '/users', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def createUser():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.createUser()

@app.route(rootUI + '/users/firstimeset', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def firstTimeLoginPwdReset():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.firstTimeLoginPwdReset()

@app.route(rootUI + '/users/<user_name>', methods = ["DELETE", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deleteUser(user_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.deleteUser(user_name)

@app.route(rootUI + '/users/<user_name>', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def modifyUser(user_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.modifyUser(user_name, request.get_json())

########################################################################################################################
# Alert & Event Management
# The below API are completely related to Event Mgmt
# Event Supression, Alert Creation, Drop & Promote Events, Automation Stages
########################################################################################################################
@app.route(rootEAM + "/alerts/<from_offset>/<count_limit>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlerts(from_offset, count_limit):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAlerts(from_offset, count_limit)

@app.route(rootEAM + "/alerts/<pStatus>/<from_offset>/<count_limit>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertsBasedOnStatus(pStatus, from_offset, count_limit):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAlertsBasedOnStatus(pStatus, from_offset, count_limit)

@app.route(rootEAM + "/events/<from_offset>/<count_limit>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getEvents(from_offset, count_limit):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getEvents(from_offset, count_limit)

@app.route(rootEAM + "/events/<pStatus>/<from_offset>/<count_limit>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getEventsBasedOnStatus(pStatus, from_offset, count_limit):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getEventsBasedOnStatus(pStatus, from_offset, count_limit)

@app.route(rootEAM + "/alerts/<alert_id>/<status>", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def updateAlertAndAssociatedEvents(alert_id, status):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.updateAlertAndAssociatedEvents(alert_id, status)

@app.route(rootEAM + "/alerts/status/groupby", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertsStatusGroupBy():
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAlertsStatusGroupBy()

@app.route(rootEAM + "/events/status/groupby", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getEventssStatusGroupBy():
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getEventssStatusGroupBy()

@app.route(rootEAM + "/alerts/<pStatus>/<from_offset>/<count_limit>", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertStatusBasedOnFilter(pStatus, from_offset, count_limit):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAlertsBasedOnFilter(pStatus, from_offset, count_limit, request.get_json())

@app.route(rootEAM + "/events/<pStatus>/<from_offset>/<count_limit>", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getEventStatusBasedOnFilter(pStatus, from_offset, count_limit):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getEventsBasedOnFilter(pStatus, from_offset, count_limit, request.get_json())

#All in one
@app.route(rootEAM + "/alerts_download/<pStatus>/<from_offset>/<count_limit>/<filter_key>/<filter_value>/<column_sort>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertsBasedOnStatusFilterOrderByDownload(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAlertsBasedOnStatusFilterOrderByDownload(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort)

# Alert Grid Load
@app.route(rootEAM + "/alerts_pinp/<pStatus>/<from_offset>/<count_limit>/<filter_key>/<filter_value>/<column_sort>/<user>/<pname>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertsBasedOnStatusFilterOrderByWithPINP(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort, user, pname):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAlertsBasedOnStatusFilterOrderByWithPINP(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort, user, pname)

@app.route(rootEAM + "/alerts_pin/<pStatus>/<from_offset>/<count_limit>/<filter_key>/<filter_value>/<column_sort>/<user>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertsBasedOnStatusFilterOrderByWithPIN(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort, user):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAlertsBasedOnStatusFilterOrderByWithPIN(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort, user)

@app.route(rootEAM + "/alerts/<pStatus>/<from_offset>/<count_limit>/<filter_key>/<filter_value>/<column_sort>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertsBasedOnStatusFilterOrderBy(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAlertsBasedOnStatusFilterOrderBy(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort)

@app.route(rootEAM + "/events/<pStatus>/<from_offset>/<count_limit>/<filter_key>/<filter_value>/<column_sort>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getEventsBasedOnStatusFilterOrderBy(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getEventsBasedOnStatusFilterOrderBy(pStatus, from_offset, count_limit, filter_key, filter_value, column_sort)

#Dropped Events
@app.route(rootEAM + "/dropped_events/<from_offset>/<count_limit>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAllDroppedEvents(from_offset, count_limit):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getDroppedEvents(from_offset, count_limit)

#Promote Events
@app.route(rootEAM + "/dropped_events/promote", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def promoteDroppedEvent():
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.promoteDroppedEvents(request.get_json())

#Execution Stage
@app.route(rootEAM + "/executionstage/<alertid>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def automationExecutionStageWithAlertID(alertid):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getAutomationExecutionStageWithAlertID(alertid)

@app.route(rootEAM + "/alerts/pin_unpin", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def pin_unpin():
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.pin_unpin(request.get_json())

@app.route(rootEAM + "/alerts/clear/<alert_id>", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def clearAlerts(alert_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.clearAlerts(alert_id)

########################################################################################################################
# BOT Repo Mgmt
# The below API are completely related to Bot Repo
# Bot Add, Modify & Delete
########################################################################################################################
@app.route(rootBOT + "/bottree", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getBOTTreeStructure():
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.getBOTMapping()

@app.route(rootBOT + "/bottree/branch", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def createBranch():
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.insertNewBOT(request.get_json())

@app.route(rootBOT + "/bottree/branch/<branch_id>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deleteBranch(branch_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.removeBOT(branch_id)

@app.route(rootBOT + "/bottree/branch/<branch_name>/<branch_id>", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def renameBranch(branch_name, branch_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.renameBOT(branch_name, branch_id)

@app.route(rootBOT + "/bottree/files", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getFilesForAllBranch():
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.getBOTFile()

@app.route(rootBOT + "/bottree/files/<branch_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getFilesForBranch(branch_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.getBOTFiles(branch_id)

#BotRepo Script Loading, Addition and Modification
@app.route(rootBOT + "/bottree/masters", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getMasterContents():
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.getDropDownDetails()

@app.route(rootBOT + "/bottree/filecontent/<bot_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getFilesForBotID(bot_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.getBOTFileByBotID(bot_id)

@app.route(rootBOT + "/bottree/filecontent/<bot_id>", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def updateBOTContent(bot_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.updateBOTContent(bot_id, request.get_json())

@app.route(rootBOT + "/bottree/filecontent/<branch_id>", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def createNewBOT(branch_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return sop.createNewBOT(branch_id, request.get_json())
    # return botservice.createNewBOT(branch_id, request.get_json())

@app.route(rootBOT + "/bottree/filecontent/<bot_id>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deleteBOT(bot_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return botservice.deleteBOT(bot_id)


########################################################################################################################
# Device Credentials Mgmt
# The below API are completely related to Device Credentials
# Credentials Mgmt
########################################################################################################################
@app.route(rootUI + "/devicecred/credentials", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getDeviceCredentialList():
    logERROR("{0} {1}".format(request.url, request.method))
    return dc.getCredentialList()

@app.route(rootUI + "/devicecred/credentials", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def insertDeviceCredentials():
    logERROR("{0} {1}".format(request.url, request.method))
    return dc.createCredentials(request.get_json())

@app.route(rootUI + "/devicecred/credentials/<cred_id>", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def updateDeviceCredentials(cred_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return dc.updateCredentials(cred_id, request.get_json())

@app.route(rootUI + "/devicecred/credentials/<cred_id>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def removeDeviceCredentials(cred_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return dc.removeCredentials(cred_id)


########################################################################################################################
# Device Discovery
# The below API are completely related to Device Discovery
########################################################################################################################

@app.route(rootUI + "/devicediscovery", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def initiateDiscovery():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.startDiscovery(request.get_json())

@app.route(rootUI + "/devicediscoverylist4machine", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getDeviceDiscoveryList4machine():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getDeviceYetToDiscoverList4machine()

@app.route(rootUI + "/devicediscoverylist", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getDeviceDiscoveryList():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getDeviceYetToDiscoverList()

@app.route(rootUI + "/devicecredentialmapper", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def createDeviceCredentialsMapping():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.createMappingDiscoveryAndCredentials(request.get_json())

@app.route(rootUI + "/deattachcredentials", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deattachcredentials():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.deAttachCredentailsFromMachine(request.get_json())

@app.route(rootUI + "/devicediscovery/<discovery_ids>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def removeDiscoveredMachines(discovery_ids):
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.removeDiscoveredMachine(discovery_ids)

@app.route(rootUI + "/devicediscovery/initiate", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def initiateRESTDiscovery():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.initiateRESTDiscovery(request.get_json())

########################################################################################################################
# Remoting

# To generate key
@app.route(rootUI + "/getRemotingKey", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getRemotingKey():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getRemotingKey(request.get_json())

# This is accessed by java client
@app.route(rootUI + "/getRemotingDetails", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getremotingDetials():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getRemotingDetails(request.get_json())

# get ip from hostname
@app.route(rootUI + "/getRemotingDetailsIP", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getremotingDetialsIP():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getIPAddress4Hostname(request.get_json())

@app.route(rootUI + "/getRemotingByAlert", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getVideos4AlertPage():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getVideos4AlertPage(request.get_json())

@app.route(rootUI + "/getRemotingByHDDM", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getVideos4HDDMPage():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getVideos4HDDMPage(request.get_json())

########################################################################################################################
# Device Discovery Hypervisor
# The below API are completely related to Device Discovery
########################################################################################################################

@app.route(rootUI + "/hypervisor", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getHypervisors():
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getHypervisors()

@app.route(rootUI + "/hypervisor", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def addHypervisor():
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.addHypervisor(request.get_json())

@app.route(rootUI + "/hypervisor/<hypervisor_id>", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def modifyHypervisor(hypervisor_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.modifyHypervisor(hypervisor_id, request.get_json())

@app.route(rootUI + "/hypervisor/<hypervisor_id>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deleteHypervisor(hypervisor_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.deleteHypervisor(hypervisor_id)

########################################################################################################################
# Device Discovery Hypervisor Explore Option
# The below API are completely related to Device Discovery
########################################################################################################################

# These are for VMWare vCenters

@app.route(rootUI + "/hypervisor_tot/<hypervisor_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getInventory(hypervisor_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getInventory(hypervisor_id)

@app.route(rootUI + "/hypervisor_totsumm/<hypervisor_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getInventoryNewCount(hypervisor_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getInventoryNewCount(hypervisor_id)

@app.route(rootUI + "/hypervisor_singleobject", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getSingleObjectDetails():
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getSingleObjectDetails(request.get_json())

# These are for KVMs

@app.route(rootUI + "/hypervisorkvm_totsumm", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getInventoryCountkvm():
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getInventoryCountkvm()

@app.route(rootUI + "/hypervisorkvm_singleobject/<type>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def singleObjectKVM(type):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.singleObjectKVM(type)

# these are for Firewall

@app.route(rootUI + "/hypervisorfirewall/<hypervisor_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getFirewallInven(hypervisor_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getFirewallInven(hypervisor_id)

# these are for Switch

@app.route(rootUI + "/hypervisorswitch/<hypervisor_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getSwitchInven(hypervisor_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getSwitchInven(hypervisor_id)

# these are for LBs

@app.route(rootUI + "/hypervisorlb/<hypervisor_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getLBInven(hypervisor_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getLBInven(hypervisor_id)

# these are for Routers

@app.route(rootUI + "/hypervisorrouter/<hypervisor_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getRInven(hypervisor_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return hyp.getRInven(hypervisor_id)


########################################################################################################################
# Device Discovery Cloud
# The below API are completely related to Device Discovery
########################################################################################################################
@app.route(rootUI + "/vmware/cloud/registry", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getClouds():
    logERROR("{0} {1}".format(request.url, request.method))
    return vcd.getClouds()

@app.route(rootUI + "/vmware/cloud/registry", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def addCloud():
    logERROR("{0} {1}".format(request.url, request.method))
    return vcd.addCloud(request.get_json())

@app.route(rootUI + "/vmware/cloud/registry/<cloud_id>", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def modifyCloud(cloud_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return vcd.modifyCloud(cloud_id, request.get_json())

@app.route(rootUI + "/vmware/cloud/registry/<cloud_id>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deleteCloud(cloud_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return vcd.deleteCloud(cloud_id)

@app.route(rootUI + "/vmware/cloud/map/<cloud_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getvCenterDetails4Mapping(cloud_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return vcd.getvCenterDetails4Mapping(cloud_id)

@app.route(rootUI + "/vmware/cloud/map", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def mapvcloudandvcenter():
    logERROR("{0} {1}".format(request.url, request.method))
    return vcd.mapvcloudandvcenter(request.get_json())

########################################################################################################################
# A2E
# The below API are completely related to Anomaly to Event
########################################################################################################################
@app.route(rootUI + "/anomaly2event", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost', headers=['Content- Type','Authorization'])
def anomaly2event():
    logERROR("{0} {1}".format(request.url, request.method))
    return a2e.anomaly2event(request.get_json())

########################################################################################################################
# Device Discovery: KVM Bandwidth
# The below API are completely related to Device Discovery
########################################################################################################################
@app.route(rootUI + "/kvmedge", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getBandwidthDetails():
    logERROR("{0} {1}".format(request.url, request.method))
    return kvmnsx.getBandwidthDetails()

@app.route(rootUI + "/kvmedge", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getBandwidthDownload():
    logERROR("{0} {1}".format(request.url, request.method))
    return kvmnsx.getBandwidthDownload(request.get_json())

@app.route(rootUI + "/kvmedge/grid/<user_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getBandwidthGrid(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return kvmnsx.getBandwidthGrid(user_id)

########################################################################################################################
# Device Discovery: Edge
# The below API are completely related to Device Discovery
########################################################################################################################
@app.route(rootUI + "/nsxedge", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getEdgeDetails():
    logERROR("{0} {1}".format(request.url, request.method))
    return nsx.getEdgeDetails()

@app.route(rootUI + "/nsxedge", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getEdgeUsage():
    logERROR("{0} {1}".format(request.url, request.method))
    return nsx.getEdgeUsage(request.get_json())


########################################################################################################################
# Add Machine Grouping
# Below functions are for Grouping machines
########################################################################################################################
@app.route(rootUI + "/mgroup/mgroups", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getMachineGroup():
    logERROR("{0} {1}".format(request.url, request.method))
    return mgroup.getMachineGroupDetails()

@app.route(rootUI + "/mgroup/machines", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getMachine():
    logERROR("{0} {1}".format(request.url, request.method))
    return mgroup.getMachines()

@app.route(rootUI + "/mgroup/mgroups", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def addMachineGroup():
    logERROR("{0} {1}".format(request.url, request.method))
    return mgroup.addNewGrouping(request.get_json())

@app.route(rootUI + "/mgroup/mgroups/<group_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getMachineGroupDetailsForEdit(group_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return mgroup.getOneMachineGroupDetails(group_id)

@app.route(rootUI + "/mgroup/mgroups", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def modifyMachineGroup():
    logERROR("{0} {1}".format(request.url, request.method))
    return mgroup.modifyMachineGroup(request.get_json())

@app.route(rootUI + "/mgroup/mgroups/<group_id>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deleteMachineGroup(group_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return mgroup.deleteGroup(group_id)

########################################################################################################################
# Add Software, Reosurce and Application Stack
# Below functionsare for adding Software, Resources and Application
########################################################################################################################
@app.route(rootUI + "/objectmaster/<class_name>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getMastersBasedOnName(class_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getMastersBasedOnName(class_name)

@app.route(rootUI + "/attributes", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAttributesBasedOnCondition():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getAttributes(request.get_json())

@app.route(rootUI + "/marstype", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def addType():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.createTypeEntry(request.get_json())

@app.route(rootUI + "/marstype", methods = ["PUT", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def modifyType():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.updateType(request.get_json())

@app.route(rootUI + "/marstype", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def removeType():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.removeType(request.get_json())

@app.route(rootUI + "/marstype/<mars_type>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getMARSDetails(mars_type):
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getMARSDetails(mars_type)

@app.route(rootUI + "/marstype/<mars_type>/<mars_name>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getMARSDetailsParticular(mars_type, mars_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.getMARSDetailsParticular(mars_type, mars_name)

@app.route(rootUI + "/machines/<machine_ids>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def removeMachines(machine_ids):
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.removeActualMachine(machine_ids)

@app.route(rootUI + "/machines_initiate/<machine_ids>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def removeMachinesAndInitiate(machine_ids):
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.removeActualMachineAndReinitiateDiscovery(machine_ids)

@app.route(rootUI + "/machines/downloadxlsx", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def downloadMachineXLSX():
    logERROR("{0} {1}".format(request.url, request.method))
    return devicediscovery.downloadMachineOnXLS()

########################################################################################################################
# Form Design : ITSM, Ticket Management
# The below API are completely related to form design
########################################################################################################################
@app.route(rootUI + "/itsmform/<itsm_name>/<ticket_action>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getITSMForm(itsm_name, ticket_action):
    logERROR("{0} {1}".format(request.url, request.method))
    return itsmdynamicform.getITSMFormDesign(itsm_name, ticket_action)

@app.route(rootUI + "/itsmform/masters", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getITSMFormMasters():
    logERROR("{0} {1}".format(request.url, request.method))
    return itsmdynamicform.getITSMMasters()

@app.route(rootUI + "/itsmform/masters/sub_category/<category_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getITSMFormMastersSubCategory(category_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return itsmdynamicform.getITSMMaster_SubCategory(category_id)

@app.route(rootUI + "/itsm/<itsm_name>/createticket", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def createdTicket(itsm_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return tktmgmt.TicketCreation(itsm_name, request.get_json())

@app.route(rootUI + "/itsm/<itsm_name>/changeticketstatus", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def changeTicketStatus(itsm_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return tktmgmt.ChangeStatus(itsm_name, request.get_json())

@app.route(rootUI + "/itsm/<itsm_name>/addticketworklog", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def addTicketWorklog(itsm_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return tktmgmt.UpdateWorklog(itsm_name, request.get_json())

@app.route(rootUI + "/itsm/<itsm_name>/resolveticket", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def resolveTicket(itsm_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return tktmgmt.ResolveTicket(itsm_name, request.get_json())

@app.route(rootUI + "/itsm/<itsm_name>/changegroup", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def changeTicketGroup(itsm_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return tktmgmt.UpdateGroup(itsm_name, request.get_json())

########################################################################################################################
# Triage
# The below API are completely related to Triage design and execution
########################################################################################################################
@app.route(rootUI + "/triage/<alert_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTriageList(alert_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return triagedynamicform.getTriageList(alert_id)

@app.route(rootUI + "/triageremote/<ci_name>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTriageCIRemoteMetaData(ci_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return triagedynamicform.getTriageCIRemoteMetaData(ci_name)

@app.route(rootUI + "/triage/<triage_name>/<alert_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getDynamicFormAndHistory(triage_name, alert_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return triagedynamicform.getTriageDynamicForm(triage_name, alert_id)

@app.route(rootUI + "/triage", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def executeTriage():
    logERROR("{0} {1}".format(request.url, request.method))
    return triagedynamicform.executeTriage(request.get_json())

@app.route(rootUI + "/triage/history/<alert_id>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTriageHistory(alert_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return triagedynamicform.getTriageHistory(alert_id)

########################################################################################################################
# Triage
# The below API are completely related to Triage design and execution
########################################################################################################################

@app.route(rootUI + "/triage/bots/service_status", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageServiceStatus():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.service(request.get_json())

@app.route(rootUI + "/triage/bots/ping", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriagePing():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.ping(request.get_json())

@app.route(rootUI + "/triage/bots/telnet", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageTelnet():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.telnet(request.get_json())

@app.route(rootUI + "/triage/bots/cpu_usage", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageCPUUsage():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.cpu_usage(request.get_json())

@app.route(rootUI + "/triage/bots/memory_usage", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageMemoryUsage():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.memory_usage(request.get_json())

@app.route(rootUI + "/triage/bots/disk_usage", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageDiskUsage():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.disk_usage(request.get_json())

@app.route(rootUI + "/triage/bots/exec_cmd", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageExecCmd():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.execute_command(request.get_json())

@app.route(rootUI + "/triage/bots/service_restart", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageServiceRestart():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.service_restart(request.get_json())

@app.route(rootUI + "/triage/bots/kill_process", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageKillProcess():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.kill_process(request.get_json())

@app.route(rootUI + "/triage/bots/kill_sql_session", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageKillSQLSession():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.kill_sql_session(request.get_json())

@app.route(rootUI + "/triage/bots/exec_sql_cmd", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def execTriageExecSQLCmd():
    logERROR("{0} {1}".format(request.url, request.method))
    return triage.exec_sql_cmd(request.get_json())

#triage/service_status

########################################################################################################################
# License
# The below API are completely related to Triage design and execution
########################################################################################################################
@app.route(rootUI + "/license/generate", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def generateLicense():
    logERROR("{0} {1}".format(request.url, request.method))
    return licensing.generateLicense(request.get_json())

@app.route(rootUI + "/license", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def insertLicense():
    logERROR("{0} {1}".format(request.url, request.method))
    return licensing.insertLicenseKey(request.get_json())

@app.route(rootUI + "/license", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getLicense():
    logERROR("{0} {1}".format(request.url, request.method))
    return licensing.getLicenseKey()

@app.route(rootUI + "/license/info", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getLicenseInformation():
    logERROR("{0} {1}".format(request.url, request.method))
    return licensing.getLicenseInformation()

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

########################################################################################################################
# Dynamic Dashboard
# The below API are completely related to make the user create their own dashboard
########################################################################################################################
@app.route(rootDD + "/dashboard", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def createDashboard():
    logERROR("{0} {1}".format(request.url, request.method))
    return wd.createDashboard(request.get_json())

@app.route(rootDD + "/mapdashrole", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def mapDashboardRole():
    logERROR("{0} {1}".format(request.url, request.method))
    return wd.mapDashboardRole(request.get_json())

@app.route(rootDD + "/cudashboard", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def createAndUpdateDashboard():
    logERROR("{0} {1}".format(request.url, request.method))
    return wd.createAndUpdateDashboard(request.get_json())

@app.route(rootDD + "/cudashboard/<dashboard_name>", methods = ["DELETE", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deleteDashboard(dashboard_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return wd.deleteDashboard(dashboard_name)

@app.route(rootDD + "/sheetwidcat", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getCategoryWidgetSheet():
    logERROR("{0} {1}".format(request.url, request.method))
    return wd.getCategoryWidgetSheet()

@app.route(rootDD + "/mapdashwidget", methods = ["POST", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def mapDashboardWidget():
    logERROR("{0} {1}".format(request.url, request.method))
    return wd.mapDashboardWidget(request.get_json())

@app.route(rootDD + "/dashboard/<role_name>", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def loadDashboardByRole(role_name):
    logERROR("{0} {1}".format(request.url, request.method))
    return wd.loadDashboardByRole(role_name)

@app.route(rootDD + "/dashboardrole", methods = ["GET", "OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def loadDashboardAndRoles():
    logERROR("{0} {1}".format(request.url, request.method))
    return wd.loadDashboardAndRoles()

########################################################################################################################
# Dashboard
# The below API are completely related to Dashboard
# Analytics
########################################################################################################################
@app.route(rootDashboard + '/suppressionpercent/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getSuppPercent(when, date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getSuppPercent(when, date)

@app.route(rootDashboard + '/top5ci/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTop5CI(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getTop5CI(when, date)

@app.route(rootDashboard + '/top3alertcomponent/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTop3AlertProducingComp(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getTop3AlertProducingComp(when, date)

@app.route(rootDashboard + '/alertbyseverity/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertBySeverity(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getAlertBySeverity(when, date)

@app.route(rootDashboard + '/weeklyheatmap', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getWeeklyHeatMap():
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getWeeklyHeatMap()

@app.route(rootDashboard + '/weeklyheatmap/<weeknumber>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getWeeklyHeatMapForParticularWeek(weeknumber):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getWeeklyHeatMapForParticularWeek(weeknumber)

@app.route(rootDashboard + '/alertseveritytrend', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def alertseveritytrendBC():
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.alertseveritytrendBC()

@app.route(rootDashboard + '/executiveheaders/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getExecutiveHeaders(when, date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getExecutiveHeaders(when, date)

@app.route(rootDashboard + '/executiveheadersdd/<when>/<date>/<what>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getExecutiveHeadersdd(when, date, what):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getExecutiveHeadersDyD(when, date, what)

@app.route(rootDashboard + '/alertseveritybc/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertBySeverityBC(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getAlertBySeverityBC(when, date)

@app.route(rootDashboard + '/ticketprioritybc/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTicketByStatusBC(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getTicketByStatusBC()

@app.route(rootDashboard + '/automationtypebc/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAutomationTypeBC(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getAutomationTypeBC(when, date)

@app.route(rootDashboard + '/workflowstatusbc/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getWorkflowByStatusBC(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getWorkflowByStatusBC(when, date)

@app.route(rootDashboard + '/alertstatus/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAlertBySeverityStatus(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getAlertBySeverityStatus(when, date)

@app.route(rootDashboard + '/automationstatus/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAutomationStatus(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getAutomationStatus(when, date)

@app.route(rootDashboard + '/ticketstatus/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTicketStatus(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getTicketStatus(when, date)

@app.route(rootDashboard + '/top5component/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTop5AlertProducingComp(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getTop5AlertProducingComp(when, date)

@app.route(rootDashboard + '/top5automation/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTop5Automation(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getTop5Automation(when, date)

@app.route(rootDashboard + '/top5workflow/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTop5Workflow(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getTop5Workflow(when, date)

@app.route(rootDashboard + '/suppression30days/<when>/<date>', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getSuppressionFor30Days(when,date):
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getSuppressionFor30Days(when, date)

@app.route(rootDashboard + '/automationstats', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAutomationStats():
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getAutomationStats()

@app.route(rootDashboard + '/marstree', methods=['GET', 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTreeOfMARS():
    logERROR("{0} {1}".format(request.url, request.method))
    return dashboardNew.getTreeOfMARS()

# Sony

@app.route(rootUI + '/cin_user', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getCINameUserOverAll():
    logERROR("{0} {1}".format(request.url, request.method))
    return cinu.getCINameUserOverAll()

@app.route(rootUI + '/cin_user/<user_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getCINames4User(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return cinu.getCINames4User(user_id)

@app.route(rootUI + '/cin_user', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def insertCINUMap():
    logERROR("{0} {1}".format(request.url, request.method))
    return cinu.insertCINUMap(request.get_json())

# RIL

@app.route(rootUI + '/autoclassify', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getAutoClassify():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.autoclassify()

@app.route(rootUI + '/modifylearning', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def updateLearning():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.updateLearning(request.get_json())


@app.route(rootUI + '/rbc_call', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def rbc_call():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.rbc_call()

@app.route(rootUI + '/bulkmodifylearning', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def bulkUpdate():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.bulkUpdate(request.get_json())

@app.route(rootUI + '/addlearning', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def insertLearning():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.insertLearning(request.get_json())

@app.route(rootUI + '/loadlearningmasters', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def loadClassificationMasterData():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.loadClassificationMasterData()

@app.route(rootUI + '/downloadactions', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def downloadMachineOnXLS():
    logERROR("{0} {1}".format(request.url, request.method))
    return adminservice.downloadMachineOnXLS()

@app.route(rootDashboard + '/getPerfIFrame', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getPerformaceOfHost():
    logERROR("{0} {1}".format(request.url, request.method))
    return perf.getPerformaceOfHost(request.get_json())

@app.route(rootUI + '/cust_service_map', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getCustomerServiceMap():
    logERROR("{0} {1}".format(request.url, request.method))
    return custserv.getCustomerServicesLoad()

@app.route(rootUI + '/cust_service_map', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def updateCustomerServiceMap():
    logERROR("{0} {1}".format(request.url, request.method))
    return custserv.mapCustomerService(request.get_json())

@app.route(rootUI + '/user_cust_map/<user_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getCustomer4User(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return custserv.getCustomer4User(user_id)

@app.route(rootUI + '/user_cust_map', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def mapUser2Customer():
    logERROR("{0} {1}".format(request.url, request.method))
    return custserv.mapUser2Customer(request.get_json())

@app.route(rootUI + '/client_vms/<customer_id>/<techno>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getVM4Customer(customer_id, techno):
    logERROR("{0} {1}".format(request.url, request.method))
    return custserv.getVM4Customer(customer_id, techno)

@app.route(rootUI + '/client_vms', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def enableService4VM():
    logERROR("{0} {1}".format(request.url, request.method))
    return custserv.enableService4VM(request.get_json())

@app.route(rootUI + '/clients', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getCustomers():
    logERROR("{0} {1}".format(request.url, request.method))
    return custserv.getCustomers()

@app.route(rootUI + '/mon_hosts/<contact>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getHostHostGroup4User(contact):
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.getHostHostGroup4User(contact)

@app.route(rootUI + '/mon_services/<host_object_id>/<filter>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getServiceDetails(host_object_id, filter):
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.getServiceDetails(host_object_id, filter)

@app.route(rootUI + '/mon_services', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getServiceDetailsPOST():
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.getServiceDetailsPOST(request.get_json())

@app.route(rootUI + '/mon_services_sev/<severity>/<filter>/<cust_type>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getServiceDetailsOverAll(severity, filter, cust_type):
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.getServiceDetailsOverAll(severity, filter, cust_type)

@app.route(rootUI + '/mon_hostservice/unknows', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getUnknowServices():
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.getUnknowServices()

@app.route(rootUI + '/mon_dashboard/overall/<user_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getDashboardDetails(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.getDashboardDetails(user_id)

@app.route(rootUI + '/mon_dashboard/typegrid', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getTypeGrid():
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.getTypeGrid(request.get_json())


########################################################################################################################
# Customer Email Mapping
# The below API are completely related to Customer Services
########################################################################################################################

@app.route(rootUI + '/customerservice/email/<customer_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getCustomerEmailGrid(customer_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return custmail.getCustomerEmailGrid(customer_id)

@app.route(rootUI + '/customerservice/email', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def mapCustomerEmail():
    logERROR("{0} {1}".format(request.url, request.method))
    return custmail.mapCustomerEmail(request.get_json())

@app.route(rootUI + '/customerservice/email', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def updateCustomerEmailMap():
    logERROR("{0} {1}".format(request.url, request.method))
    return custmail.updateCustomerEmailMap(request.get_json())

@app.route(rootUI + '/customerservice/email/<customer_id>', methods = ["DELETE", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def deleteCustomerEmailMap(customer_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return custmail.deleteCustomerEmailMap(customer_id)


########################################################################################################################
# Network Perf Report
# The below API are completely related to Bandwidth Utilization
########################################################################################################################

@app.route(rootUI + '/perfreport/network/router/master/<user_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def perfMaster(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return perfrpt.perfMaster(user_id)

@app.route(rootUI + '/perfreport/network/router', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def perfData():
    logERROR("{0} {1}".format(request.url, request.method))
    return perfrpt.perfData(request.get_json())

@app.route(rootUI + '/perfreport/network/router1', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def perfData1():
    logERROR("{0} {1}".format(request.url, request.method))
    return perfrpt.perfData1(request.get_json())

# @app.route(rootUI + '/perfreport/network/router1', methods = ["POST", 'OPTIONS'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
# def perfData1():
#     logERROR("{0} {1}".format(request.url, request.method))
#     return perfrpt.perfData1(request.get_json())

########################################################################################################################
# Item Master - Performance Report
# The below API are completely related to Bandwidth Utilization
########################################################################################################################

@app.route(rootUI + '/perfreport/main/items', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def perfDropDownItemMaster():
    logERROR("{0} {1}".format(request.url, request.method))
    return perfrpt.perfDropDownItemMaster()

@app.route(rootUI + '/perfreport/main/items/sidelist', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getperfDropDownList4SelectedItem():
    logERROR("{0} {1}".format(request.url, request.method))
    return perfrpt.getperfDropDownList4SelectedItem(request.get_json())

@app.route(rootUI + '/perfreport/main/items/metriclist', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getperfDropDownList4SelectedItemNetwork():
    logERROR("{0} {1}".format(request.url, request.method))
    return perfrpt.getperfDropDownList4SelectedItemNetwork(request.get_json())

@app.route(rootUI + '/perfreport/all', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def perfDataLatest():
    logERROR("{0} {1}".format(request.url, request.method))
    return perfrpt.perfDataLatest(request.get_json())

@app.route(rootUI + '/perfreport/all/decissue', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def perfDataLatestDECIssue():
    logERROR("{0} {1}".format(request.url, request.method))
    return perfrpt.perfDataLatest1(request.get_json())

@app.route(rootUI + '/perfreport/all/decissue/pdf', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def perfDataLatestDECIssueDownloadPDF():
    logERROR("{0} {1}".format(request.url, request.method))
    return ex2pdf.generatePDF(request.get_json())

########################################################################################################################
# Monitoring DropDowns
# The below API are completely related to Bandwidth Utilization
########################################################################################################################

@app.route(rootUI + '/mon_services/dp/hostgroups/<username>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def loadHostGroupDropDown(username):
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.loadHostGroupDropDown(username)

@app.route(rootUI + '/mon_services/dp/hosts', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def loadHostDropDown():
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.loadHostDropDown(request.get_json())

@app.route(rootUI + '/mon_services/dp/hosts_new', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def loadHostDropDownMix():
    logERROR("{0} {1}".format(request.url, request.method))
    return nagmar.loadHostDropDownMix(request.get_json())

########################################################################################################################
# Orch APIs
# The below API are completely related to Orchestration
########################################################################################################################

@app.route(rootUI + '/orches/registerlog', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def storeProcessInitiationDetail():
    logERROR("{0} {1}".format(request.url, request.method))
    return kieserver.storeProcessInitiationDetail(request.get_json())

@app.route(rootUI + '/orches/workflowstatus', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getWorkflowStatus():
    logERROR("{0} {1}".format(request.url, request.method))
    return kieserver.getWorkflowStatus()

@app.route(rootUI + '/orches/processbysd', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getProcessByStartDate():
    logERROR("{0} {1}".format(request.url, request.method))
    return kieserver.getProcessByStartDate()

@app.route(rootUI + '/orches/processbyed', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getProcessByEndDate():
    logERROR("{0} {1}".format(request.url, request.method))
    return kieserver.getProcessByEndDate()

@app.route(rootUI + '/orches/processbyruntime', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getProcessByRunningTime():
    logERROR("{0} {1}".format(request.url, request.method))
    return kieserver.getProcessByRunningTime()

@app.route(rootUI + '/orches/processcategory', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def getWorkflowByCategory():
    logERROR("{0} {1}".format(request.url, request.method))
    return kieserver.getWorkflowByCategory()

@app.route(rootUI + '/orches/processauditlog', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def auditLog():
    logERROR("{0} {1}".format(request.url, request.method))
    return kieserver.auditLog(request.get_json())

@app.route(rootUI + '/orches/roi', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def ROIDashboard():
    logERROR("{0} {1}".format(request.url, request.method))
    return kieserver.ROIDashboard()



@app.route(rootUI + '/reports/vmsumm/getcustomers/<tech>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type','Authorization'])
def getCustomerList(tech):
    logERROR("{0} {1}".format(request.url, request.method))
    return vmsummrpt.getCustomerList(tech)

@app.route(rootUI + '/reports/vmsumm/grid/<user_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type','Authorization'])
def loadgrid(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return vmsummrpt.loadgrid(user_id)

@app.route(rootUI + '/reports/vmsumm/download', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def fetchReport():
    logERROR("{0} {1}".format(request.url, request.method))
    return vmsummrpt.fetchReport(request.get_json())

# Inbound Notification - Billing
@app.route(rootInB + '/notify', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def billingNotification():
    logERROR("{0} {1}".format(request.url, request.method))
    return inb.billingNotification(request.get_json())


@app.route(rootUI + '/execprereq/<hostname>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def execprereq(hostname):
    logERROR("{0} {1}".format(request.url, request.method))
    return prereq.prereq(hostname)

# Auto Scale Mapping

@app.route(rootUI + '/autoscale/hypervisormapping', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def hypervisorMappingDetails():
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.hypervisorMappingDetails()

@app.route(rootUI + '/autoscale/tenants', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Contriagetent- Type', 'Authorization'])
def getTenantDetails():
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.getTenantDetails(request.get_json())

@app.route(rootUI + '/autoscale/vm2hypervisor', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def hypervisorVMList():
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.hypervisorVMList(request.get_json())

@app.route(rootUI + '/autoscale/autoscale', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def createAutoScale():
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.createAutoScale(request.get_json())

@app.route(rootUI + '/autoscale/autoscale', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getAutoScaleList():
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.getAutoScaleList()

@app.route(rootUI + '/autoscale/autoscale/<id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getAutoScaleDetails(id):
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.getAutoScaleDetails(id)

@app.route(rootUI + '/autoscale/autoscale', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def updateAutoScale():
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.updateAutoScale(request.get_json())

@app.route(rootUI + '/autoscale/autoscale', methods = ["DELETE", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def deleteAutoScale():
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.deleteAutoScale(request.get_json())

@app.route(rootUI + '/autoscale/analytics1/<autoscalename>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def analytics1(autoscalename):
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.analytics1(autoscalename)

@app.route(rootUI + '/autoscale/analytics2/<autoscalename>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def analytics2(autoscalename):
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.analytics2(autoscalename)

@app.route(rootUI + '/autoscale/analytics1/<autoscalename>/xls', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def analyticsXLS(autoscalename):
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.analyticsXLS(autoscalename)

@app.route(rootUI + '/autoscale/analytics2/<autoscalename>/xls', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def analytics2XLS(autoscalename):
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.analytics2XLS(autoscalename)

@app.route(rootUI + '/autoscale/audit/xls', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def autoscaleAuditReport():
    logERROR("{0} {1}".format(request.url, request.method))
    return autoscaleservice.autoscaleAuditReport()

# Monitoring config in front end

@app.route(rootUI + '/monitoring/templates', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getTemplates():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.getTemplates()

@app.route(rootUI + '/monitoring/accountsbytemplate', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getAccountBasedOnTechno():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.getAccountBasedOnTechno(request.get_json())

@app.route(rootUI + '/monitoring/objects', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getObjects():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.getObjects(request.get_json())

@app.route(rootUI + '/monitoring/hostgroup', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def createHostGroup():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.createHostGroup(request.get_json())

@app.route(rootUI + '/monitoring/mapuserhg', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def mapUserHostGroup():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.mapUserHostGroup(request.get_json())

@app.route(rootUI + '/monitoring/hostgroup/grid', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def loadHGGrid():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.loadHGGrid()

@app.route(rootUI + '/monitoring/users/unselectedselected/<hg_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def usersUnselectedSelectedList(hg_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.usersUnselectedSelectedList(hg_id)

@app.route(rootUI + '/monitoring/hosts/unselectedselected', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def hostUnselectedSelectedList():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.hostUnselectedSelectedList(request.get_json())

@app.route(rootUI + '/monitoring/hostgroup', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def updateHostGroup():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.updateHostGroup(request.get_json())

@app.route(rootUI + '/monitoring/hostgroup/<hg_id>', methods = ["DELETE", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def deleteHostGroup(hg_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.deleteHostGroup(hg_id)

@app.route(rootUI + '/monitoring/hosts/serviceconfigs', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getServiceCheckConfigForObject():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.getServiceCheckConfigForObject(request.get_json())

@app.route(rootUI + '/monitoring/hosts/serviceconfigs', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def updateServiceCheckConfigForObject():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.updateServiceCheckConfigForObject(request.get_json())

@app.route(rootUI + '/monitoring/hosts/flagconfigs', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def updateHostFlags():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.updateHostFlags(request.get_json())

@app.route(rootUI + '/monitoring/hostgroup/user/<user_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getHostGroupByUser(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.getHostGroupByUser(user_id)

@app.route(rootUI + '/monitoring/hosts/hostgroup', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getHostsByHostGroup():
    logERROR("{0} {1}".format(request.url, request.method))
    return monmgmt.getHostsByHostGroup(request.get_json())

# SOP

@app.route(rootUI + '/sop', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def createSOP():
    logERROR("{0} {1}".format(request.url, request.method))
    return sop.createSOP(request.get_json())

@app.route(rootUI + '/sop/grid', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getSOPList():
    logERROR("{0} {1}".format(request.url, request.method))
    return sop.getSOPList()

@app.route(rootUI + '/sop/<sop_id>', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def updateSOP(sop_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return sop.updateSOP(sop_id, request.get_json())

@app.route(rootUI + '/sop/<sop_id>', methods = ["DELETE", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def deleteSOP(sop_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return sop.deleteSOP(sop_id)

@app.route(rootUI + '/sop/qaapproval/<sop_id>', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def approveSOP(sop_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return sop.approveSOP(sop_id, request.get_json())

@app.route(rootUI + '/sop/history/<sop_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getSOPHistory(sop_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return sop.getSOPHistory(sop_id)

# Filters

@app.route(rootUI + '/filters', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def createFilters():
    logERROR("{0} {1}".format(request.url, request.method))
    return json.dumps(fil.createFilters(request.get_json()))

@app.route(rootUI + '/filters/grid', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getFilterList():
    logERROR("{0} {1}".format(request.url, request.method))
    return fil.getFilterList()

@app.route(rootUI + '/filters/<filter_id>', methods = ["PUT", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def updateFilter(filter_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return json.dumps(fil.updateFilter(filter_id, request.get_json()))

@app.route(rootUI + '/filters/<filter_id>/<action>', methods = ["DELETE", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def deleteFilter(filter_id, action):
    logERROR("{0} {1}".format(request.url, request.method))
    return fil.deleteFilter(filter_id, action)

@app.route(rootUI + '/filters/archieve/<filter_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getArchieveData(filter_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return fil.getArchieveData(filter_id)

# Filter retention
@app.route(rootUI + '/filters/retent', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getfilterRetention():
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.getfilterRetention()

@app.route(rootUI + '/filters/retent', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def filterRetention():
    logERROR("{0} {1}".format(request.url, request.method))
    return eamservice.filterRetention(request.get_json())

#personalize
@app.route(rootUI + '/personalize/<user_id>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getPeronalize(user_id):
    logERROR("{0} {1}".format(request.url, request.method))
    return pp.getPeronalize(user_id)

@app.route(rootUI + '/personalize', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def createPeronalize():
    logERROR("{0} {1}".format(request.url, request.method))
    return pp.createPeronalize(request.get_json())

@app.route(rootUI + '/personalize', methods = ["DELETE", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def deletePeronalize():
    logERROR("{0} {1}".format(request.url, request.method))
    return pp.deletePeronalize(request.get_json())


# Regex Validations
@app.route(rootUI + '/re/validation/match', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def validatePEAttrib():
    logERROR("{0} {1}".format(request.url, request.method))
    return res.validatePEAttrib(request.get_json())

#Market place
@app.route(rootUI + '/mp/vmware/vcenter', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def addvCenter():
    logERROR("{0} {1}".format(request.url, request.method))
    return mpvmw.addvCenter(request.get_json())

@app.route(rootUI + '/mp/map/<vendor>', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getvCenterDetails(vendor):
    logERROR("{0} {1}".format(request.url, request.method))
    return mpvmw.getvCenterDetails(vendor)

@app.route(rootUI + '/mp/vmware/vcenter/vm', methods = ["POST", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def createVirtualMachine():
    logERROR("{0} {1}".format(request.url, request.method))
    return mpvmw.createVirtualMachine(request.get_json())

@app.route(rootUI + '/mp/vmware/result', methods = ["GET", 'OPTIONS'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def getGrid():
    logERROR("{0} {1}".format(request.url, request.method))
    return mpvmw.getGrid()



#
#if __name__ == '__main__':
#    try:
#        app.run(host='127.0.0.1', port=5001, debug=True)
#        CORS(app)
#    except Exception as e:
#        print(str(e))

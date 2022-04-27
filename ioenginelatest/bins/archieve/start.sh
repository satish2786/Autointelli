#!/usr/bin/env bash

# This is only useful when the code is executed in order to debug and solve some live issues

EnginePath=/usr/local/autointelli/ioengine
JBPMPath=/opt/jbpm
export PYTHONPATH=/usr/local/autointelli/ioengine
export LD_LIBRARY_PATH=/usr/local/lib
#source /root/aicognitive/bin/activate

#Gateway - Main API
cd ${EnginePath}/services/router
nohup python3.6 apigateway.py >> /tmp/admin.log 2>&1 &

#Event Receiver - Gateway for other moniroting tools
cd ${EnginePath}/services/EAMEndPoint
nohup python3.6 eventreceiver.py >> /tmp/admin.log 2>&1 &

#Event Worker - For Supression and Correlation
cd ${EnginePath}/services/EAM
nohup python3.6 eamworker.py >> /tmp/admin.log 2>&1 &

#Discovery - device discovery in landscape
cd ${EnginePath}/services/devicediscovery
nohup python3.6 devicediscoveryworker.py >> /tmp/admin.log 2>&1 &

#Automation Engine - for incident management
cd ${EnginePath}/services/automation
nohup python3.6 1.BOT_CheckInput.py &
nohup python3.6 2.BOT_CheckAutomation.py &
nohup python3.6 3.BOT_CreateAutomationID.py &
nohup python3.6 4.BOT_CreateTicket.py &
nohup python3.6 5.BOT_Retrieve_Host_Information.py &
nohup python3.6 6.BOT_Update_Ticket.py &
nohup python3.6 7.BOT_GET_Rule_or_BOT_Informations.py &
nohup python3.6 8.BOT_Execute_Action.py &
nohup python3.6 9.BOT_Resolve_Ticket.py &
nohup python3.6 10.BOT_Move_Ticket.py &
nohup python3.6 11.BOT_Exception_Handling.py &

#CMDB - for machine management
cd ${EnginePath}/services/cmdb
nohup python3.6 cmdbRest.py &

#Policy Engine - for policy engine
cd ${EnginePath}/services/administration
nohup python3.6 automation_gateway.py &

#Async - for all async communication for all components
cd ${EnginePath}/services/ai_async
nohup python3.6 ai_socketio.py &

#JBPM API - for workflow management
#cd ${JBPMPath}/Form-Designer
#nohup python3.6 app.py &

#KieWB
cd ${JBPMPath}/kiewb/bin
nohup ./standalone.sh -c standalone-full.xml &

cd ${JBPMPath}/kieserver/bin
nohup ./standalone.sh -c standalone-full.xml &
#!/usr/bin/env bash

pat=/usr/local/autointelli/ioenginelatest
export PYTHONPATH=$pat
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

#Main API
nohup python3.9 $pat/services/router/apigateway.py &

#Other
nohup python3.9 $pat/services/administration/automation_gateway.py &
nohup python3.9 $pat/services/cmdb/cmdbRest.py &

# Automation
nohup python3.9 $pat/services/schedulers/ciRemotingWorker.py &
nohup python3.9 $pat/services/executeAutomation/executeAutomation.py &
nohup python3.9 $pat/services/executeAutomation/botExecutionParser.py &

#Event Management
nohup python3.9 $pat/services/EAMEndPoint/guni_eventreceiver.py &
nohup python3.9 $pat/services/EAM/datalake2validation.py &
nohup python3.9 $pat/services/EAM/eamfilterworker.py &
nohup python3.9 $pat/services/EAM/eampeworker.py &
nohup python3.9 $pat/services/EAM/eamworker.py &
nohup python3.9 $pat/services/EAM/eampeworker4newKB.py &
nohup python3.9 $pat/services/EAM/eambatchprocessingKB.py &

#Marketplace
nohup python3.9 $pat/services/marketplace/vmware/vmwareworker.py &
#00 00 * * * nohup python3.9 ${pat}/services/marketplace/vmware/vmwareworker.py &

#Discovery
nohup python3.9 $pat/services/devicediscovery/devicediscoveryworker.py > device.log &
nohup python3.9 $pat/services/devicediscovery/d2mworker.py > d2m.log &

#Monitoring Worker
nohup python3.9 $pat/services/Monitoring/monackworker.py &
nohup python3.9 $pat/services/perfrpt/vmsummaryworker.py &
nohup python3.9 $pat/services/perfrpt/kvmsummaryworker.py &

#Async Server Side
nohup python3.9 $pat/services/ai_async/ai_socketio.py &

#KieWB
JBPMPath=/opt/aiorch
cd ${JBPMPath}/central/bin
./StartWildfly.sh
#
cd ${JBPMPath}/engine/bin
./StartWildfly.sh

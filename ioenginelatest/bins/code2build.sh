#!/usr/bin/env bash

projectpath=/usr/local/autointelli/factory/ioengine

# Export PYTHON PATH
export PYTHONPATH=${projectpath}

# Declare BUILD PATH
finalbuildpath=${projectpath}/../
mkdir ${finalbuildpath}/build
finalbuildpath=${projectpath}/../build

# Each Binary Path
eventreceiverpath=${projectpath}/services/EAMEndPoint
apigateway=${projectpath}/services/router
eamworker=${projectpath}/services/EAM
ddworker=${projectpath}/services/devicediscovery
monworker=${projectpath}/services/Monitoring

cmdb=${projectpath}/services/cmdb
autogateway=${projectpath}/services/administration
async=${projectpath}/services/ai_async

automation=${projectpath}/services/automation
# Engine Array
arrsers=(1.BOT_CheckInput.py 2.BOT_CheckAutomation.py 3.BOT_CreateAutomationID.py 4.BOT_CreateTicket.py 5.BOT_Retrieve_Host_Information.py 6.BOT_Update_Ticket.py 7.BOT_GET_Rule_or_BOT_Informations.py 8.BOT_Execute_Action.py 9.BOT_Resolve_Ticket.py 10.BOT_Move_Ticket.py 11.BOT_Exception_Handling.py)


slp(){
        sleep 5
}

builder(){
        echo "Executing ${1}";
        cd $1;
        pyinstaller $2 --onefile --distpath=${finalbuildpath} --hidden-import pkg_resources.py2_warn;
        slp
        rm -rf build/ __pycache__/ *.spec;
}

builder ${eventreceiverpath} eventreceiver.py
builder ${apigateway} apigateway.py
builder ${eamworker} eamworker.py
builder ${ddworker} devicediscoveryworker.py
builder ${autogateway} automation_gateway.py
builder ${monworker} worker_availability.py
builder ${async} ai_socketio.py

# --hidden imports
cd ${cmdb};
pyinstaller cmdbRest.py --onefile --distpath=${finalbuildpath} --hidden-import pkg_resources.py2_warn --hidden-import configparser --hidden-import celery.fixups.django --hidden-import celery.loaders.app --hidden-import celery.app.amqp --hidden-import kombu.transport.pyamqp --hidden-import celery.backends.database --hidden-import celery.app.events --hidden-import celery.events --hidden-import celery.bin.worker --hidden-import celery.apps.worker --hidden-import celery.app.log --hidden-import celery.concurrency.prefork --hidden-import celery.worker.components --hidden-import celery.worker.autoscale --hidden-import celery.worker.consumer --hidden-import celery.app.control --hidden-import celery.events.state --hidden-import celery.worker.strategy


for i in ${arrsers[*]}
do
    builder ${automation} ${i}
done;

cd ${projectpath}/../
zip -r build.zip build/

md5sum build.zip > build.md5

rm -rf build/
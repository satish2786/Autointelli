#!/usr/bin/env bash

mkdir /etc/autointelli;
mkdir /var/log/autointelli;

read -r -d '' conf <<EOF
{
	"ui":{
        "dbname" : "autointelli",
        "username" : "autointelli",
        "password" : "w4LDqsOow57CisOcw6jDisOYw5jCig==",
        "dbip" : "127.0.0.1",
        "dbport" : 5432
    },
    "jbpm":{
        "dbname" : "kieserver",
        "username" : "kieserver",
        "password" : "w4zDnsOZw6LChsOgw6rDisOe",
        "dbip" : "127.0.0.1",
        "dbport" : 5432
    },
     "monitor": {
            "url": "https://localhost:81"
    },
    "perf": {
            "url": "localhost:81"
    }
	"maindb": {
		"dbname": "autointelli",
		"username": "autointelli",
		"password": "w4LDqsOow57CisOcw6jDisOYw5jCig==",
		"dbip": "127.0.0.1",
		"dbport": 5432
	}
}
EOF
echo "$conf" >  "/etc/autointelli/autointelli.conf";

enabler(){
    read -r -d '' servicecontent <<EOF
# It's not recommended to modify this file in-place, because it will be
# overwritten during package upgrades.  If you want to customize, the
# best way is to create a file '/etc/systemd/system/<user-defined name>',
# containing
#       .include /lib/systemd/system/<user-defined name>
#       ...make your changes here...
# For more info about custom unit files, contact Autointelli Support Team

# Note: changing this file will typically require adjusting SELinux
#       configuration as well.

# Note: do not use a pathname containing spaces, or you will
#       break autointelli-setup.
[Unit]
Description=${1}
After=multi-user.target

[Service]
Type=idle
ExecStart=${2}

[Install]
WantedBy=multi-user.target
EOF
    echo "Converting to service: ${1}";
    echo "$servicecontent" > "${3}.service";
    echo "service file created";
    sleep 2;
    chmod 644 "${3}.service";
    echo "permission enabled";
    sleep 2;
    systemctl enable "${3}.service";
    echo "enabled on reboot";
    sleep 2;
    systemctl start "${4}.service";
    echo "started service";
    sleep 2;
    echo "Below is the status";
    systemctl status "${4}.service";
    sleep 2;
}

arrsers=(1.BOT_CheckInput 2.BOT_CheckAutomation 3.BOT_CreateAutomationID 4.BOT_CreateTicket 5.BOT_Retrieve_Host_Information 6.BOT_Update_Ticket 7.BOT_GET_Rule_or_BOT_Informations 8.BOT_Execute_Action 9.BOT_Resolve_Ticket 10.BOT_Move_Ticket 11.BOT_Exception_Handling)

#Event Receiver
description="Event Receiver run on port 5006"
path="/usr/local/autointelli/ioengine/services/eventreceiver"
filename="/usr/lib/systemd/system/ai_eventreceiver"
enabler "${description}" "${path}" "${filename}" "ai_eventreceiver"

#API Gateway
description="API Gateway run on port 5001"
path="/usr/local/autointelli/ioengine/services/apigateway"
filename="/usr/lib/systemd/system/ai_apigateway"
enabler "${description}" "${path}" "${filename}" "ai_apigateway"

#EAM Worker
description="This is EAM Worker"
path="/usr/local/autointelli/ioengine/services/eamworker"
filename="/usr/lib/systemd/system/ai_eamworker"
enabler "${description}" "${path}" "${filename}" "ai_eamworker"

#Device Discovery Worker
description="This is Device Discovery Worker"
path="/usr/local/autointelli/ioengine/services/devicediscoveryworker"
filename="/usr/lib/systemd/system/ai_devicediscoveryworker"
enabler "${description}" "${path}" "${filename}" "ai_devicediscoveryworker"

#Availability Report Worker
description="This is Availability Report Worker"
path="/usr/local/autointelli/ioengine/services/worker_availability"
filename="/usr/lib/systemd/system/ai_worker_availability"
enabler "${description}" "${path}" "${filename}" "ai_worker_availability"

#Automation Gateway
description="This is Automation gateway"
path="/usr/local/autointelli/ioengine/services/automation_gateway"
filename="/usr/lib/systemd/system/ai_automation_gateway"
enabler "${description}" "${path}" "${filename}" "ai_automation_gateway"

#CMDB
description="This is CMDB"
path="/usr/local/autointelli/ioengine/services/cmdbRest"
filename="/usr/lib/systemd/system/ai_cmdbRest"
enabler "${description}" "${path}" "${filename}" "ai_cmdbRest"

#Async
description="This is Async"
path="/usr/local/autointelli/ioengine/services/ai_socketio"
filename="/usr/lib/systemd/system/ai_socketio"
enabler "${description}" "${path}" "${filename}" "ai_socketio"


#Automation Flow Workers
for i in ${arrsers[*]}
do
    description="This is Worker: ${i}"
    path="/usr/local/autointelli/ioengine/services/${i}"
    filename="/usr/lib/systemd/system/ai_${i}"
    enabler "${description}" "${path}" "${filename}" "ai_${i}"
done;




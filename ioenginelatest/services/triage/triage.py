#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

from flask import Flask, jsonify, request
import json
from services.utils import ConnPostgreSQL as conn
from services.utils import ConnRemote as rem
import subprocess
import socket
import services.utils.ED_AES256 as aes
from services.utils.ConnLog import create_log_file
import services.utils.LFColors as lfc
from services.utils import ConnArcon as pam1

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

pam = ""
try:
    pam = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['pvault']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

def logAndRet(s, x):
    if s == "failure":
        logERROR(x)
    else:
        logINFO(x)
    return json.dumps({"result": s, "data": x})

def decrypt(pwd):
    k = '@ut0!ntell!'.encode()
    passwd = pwd.encode()
    return aes.decrypt(passwd, k).decode('utf-8')

def getMachineDetails(pAlertID):
    try:
        if not str(pAlertID).__contains__('AL'):
            pAlertID = 'AL' + str(pAlertID).rjust(13, '0')
        sql = """
                SELECT 
                	m.ip_address, m.machine_fqdn, m.platform, m.osname, m.osversion, c.cred_type, c.username, c.password, m.backend_port port 
                from 
                	ai_machine m left join ai_device_credentials c on(m.fk_cred_id = c.cred_id) 
                where 
                	trim(lower(m.machine_fqdn)) = (select trim(lower(ci_name)) from alert_data where concat('AL',lpad(cast(pk_alert_id as text),13,'0')) = '%s')""" % pAlertID
        dRet = conn.returnSelectQueryResult(sql)
        if dRet['result'] == 'success':
            if dRet['data'][0]['cred_type'].lower() == 'pam':
                retPAM = {}
                if pam.lower() == 'iress':
                    retPAM = pam1.queryPassword(dRet['data'][0]['machine_fqdn'], dRet['data'][0]['username'],
                                               dRet['data'][0]['platform'], pam)
                else:
                    retPAM = pam1.queryPassword(dRet['data'][0]['ip_address'], dRet['data'][0]['username'],
                                               dRet['data'][0]['platform'], pam)
                if retPAM['result'] == 'success':
                    dRet['data'][0]['username'] = retPAM['data']['username']
                    dRet['data'][0]['password'] = retPAM['data']['password']
                else:
                    dRet['result'] = 'failure'
        return dRet
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {'result': 'failure', 'data': str(e)}

def StoreAndReturnOutputOrErr(pTriageName, pAlertID, pOutput):
    try:
        iQuery = "insert into ai_triage_history(fk_triage_id, fk_alert_id, output, created_dt) values((select pk_triage_id from ai_triage_master where lower(triage_name) = '%s'),%d,'%s',now()) RETURNING pk_triage_history_id" % (pTriageName, pAlertID, pOutput.replace("'", "''"))
        dRet = conn.returnSelectQueryResultWithCommit(iQuery)
        if dRet['result'] == 'success':
            sQuery = "select output, to_char(created_dt, 'DD/MM/YYYY hh:mi') as datetime from ai_triage_history where pk_triage_history_id=%d" % (dRet['data'][0]['pk_triage_history_id'])
            dRet = conn.returnSelectQueryResult(sQuery)
            return {'result': 'success', 'data': dRet['data'][0]}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {'result': 'failure', 'data': str(e)}

def service(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']
        service_name = user_in['Service Name']

        if service_name.strip() == "":
            return json.dumps({'result': 'failure', 'data': 'Please supply service name'})

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    sCmd = 'systemctl' + ' ' + 'status' + ' ' + service_name
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='service status', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = ["sc query %s" % service_name, '/all']
                    lCmd = ["Get-Service %s" % service_name]
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='service status', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def ping(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']

            # Snippet for Ping
            iAlertID = int(pAlertID.strip('AL'))
            output = subprocess.check_output(['ping', '-c', '3', '-w', '3', '-q', ip_address])
            dRet = StoreAndReturnOutputOrErr(pTriageName='ping', pAlertID=iAlertID, pOutput=output.decode('utf-8'))
            return json.dumps(dRet)
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def telnet(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']
        pPort = user_in['Port']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']

            # Snippet for Telnet
            iAlertID = int(pAlertID.strip('AL'))
            hosts, ports = ip_address, pPort
            port_en = int(ports)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            output = sock.connect_ex((hosts, port_en))
            result = ''
            if int(output) == 0:
                result = 'Able to Telnet to Port %s ' % str(port_en)
            else:
                result = 'Failed to Telnet to Port %s ' % str(port_en)
            dRet = StoreAndReturnOutputOrErr(pTriageName='telnet', pAlertID=iAlertID, pOutput='Able to Telnet to Port %s ' % str(port_en) )
            return json.dumps(dRet)
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

#CPU Usage
def cpu_usage(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    sCmd = 'ps -eo %cpu,cmd --sort=-%cpu |head -6|tail -10'
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='cpu usage', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows - Not Working
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = ["Get-Process | Sort CPU -descending | Select -first 5 -Property ID,ProcessName,CPU | format-table -autosize"]
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='cpu usage', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def memory_usage(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    sCmd = 'free -m'
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='memory usage', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows - Not Working
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = ['systeminfo | findstr /C:"Physical Memory"', '/all']
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='memory usage', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def disk_usage(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    sCmd = 'df -h'
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='disk usage', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows - Not Working
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = ['WMIC LOGICALDISK GET Name,Size,FreeSpace', '/all']
                    lCmd = ['''Get-WmiObject -Class Win32_logicaldisk -Filter "DriveType = '3'" | Select-Object -Property DeviceID, DriveType, VolumeName, @{L='FreeSpaceGB';E={"{0:N2} GB" -f ($_.FreeSpace /1GB)}}, @{L="Capacity";E={"{0:N2} GB" -f ($_.Size/1GB)}}''']
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='disk usage', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def execute_command(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']
        pCommand = user_in['Command']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=pCommand)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='execute command', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows - Not Working
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = [pCommand]
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='execute command', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def service_restart(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']
        pCommand = user_in['Service Name']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    sCmd = 'sudo service %s restart' %(pCommand)
                    sChkCmd = 'systemctl status %s' %(pCommand)
                    dRetRes = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sCmd)
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sChkCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='service restart', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows - Not Working
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = ['Restart-Service %s' %(pCommand)]
                    lChkCmd = ['Get-Service %s' % (pCommand)]
                    dRetRes = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd)
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lChkCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='service restart', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def kill_process(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']
        pCommand = user_in['Process ID']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    sCmd = 'sudo kill -9 %s' %(str(pCommand))
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='kill process', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows - Not Working
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = ['taskkill /F /PID %s' %(str(pCommand))]
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd, hidden='cmd')
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='kill process', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def kill_sql_session(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']
        pCommand = user_in['Session ID']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    sCmd = 'sudo kill -9 %s' %(str(pCommand))
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='kill sql session', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows - Not Working
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = ["""sqlcmd -S 127.0.0.1 -Usa -Pautointelli -d Master -Q " kill %s " """ %str(pCommand)]
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd, hidden='cmd')
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='kill sql session', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

def exec_sql_cmd(dPayload):
    try:
        # Unbox Payload
        user_in = dPayload
        pAlertID = user_in['alert_id']
        pCommand = user_in['Command']

        # Get Connection Details
        dRet = getMachineDetails(pAlertID)
        if dRet['result'] == 'success':
            ip_address = dRet['data'][0]['ip_address']
            platform = dRet['data'][0]['platform']
            user_name = dRet['data'][0]['username']
            password = dRet['data'][0]['password'] if dRet['data'][0]['cred_type'].lower() == 'pam' else decrypt(dRet['data'][0]['password'])
            port = dRet['data'][0]['port']
            iAlertID = int(pAlertID.strip('AL'))

            # Snippet for Linux
            if platform == "Linux":
                try:
                    sCmd = 'sudo kill -9 %s' %(str(pCommand))
                    dRet = rem.execSSH(hostname=ip_address, port=port, username=user_name, password=password, cmd=sCmd)
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='exec sql cmd', pAlertID= iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))

            # Snippet for Windows - Not Working
            elif platform == "Win32" or "Windows":
                try:
                    lCmd = ["""sqlcmd -S 127.0.0.1 -Usa -Pautointelli -d Master -Q " %s " """ %str(pCommand)]
                    dRet = rem.execWINRM(hostname=ip_address, username=user_name, password=password, cmd=lCmd, hidden='cmd')
                    if dRet['result'] == 'success':
                        dRet = StoreAndReturnOutputOrErr(pTriageName='exec sql cmd', pAlertID=iAlertID, pOutput=dRet['data'])
                        return json.dumps(dRet)
                    else:
                        logERROR("Error: {0}".format(dRet))
                        return json.dumps(dRet)
                except Exception as e:
                    return logAndRet("failure", "Exception: {0}".format(str(e)))
        else:
            return logAndRet("failure", "Unable to fetch Machine details to execute triage")
    except Exception as e:
        return logAndRet("failure", "Exception: {0}".format(str(e)))

#sqlcmd -S 127.0.0.1 -Usa -Pautointelli -d Master -Q \" kill 52 \"


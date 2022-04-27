# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================

import paramiko
import winrm
from services.utils.ConnLog import create_log_file

import services.utils.LFColors as lfc
lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file()
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

def decodeWinOutput(content):
    if type(content) == type(bytes(0)):
        content = content.decode('utf-8')
    if content.__contains__('\r\n'):
        content = content.replace('\r\n', '\n')
    return content

def execSSH(hostname, port, username, password, cmd):
    try:
        sOut = ""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(hostname=hostname, port=port, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(cmd)
        retCode = stdout.channel.recv_exit_status()
        if (retCode == 0):
            return {'result': 'success', 'data': '\n'.join(stdout.readlines())}
        else:
            return {'result': 'success', 'data': '\n'.join(stderr.readlines())}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {'result': 'failure', 'data': str(e)}

def execWINRM(hostname, username, password, cmd = [], hidden=''):
    try:
        # cmd = ['sc' + ' ' + 'query' + ' ' + service_name, '/all']
        sOut, ret = "", ""
        Auth = winrm.Session(hostname, auth=(username, password), transport='ntlm')
        if hidden == 'cmd':
            ret = Auth.run_cmd(cmd[0])
        else:
            if len(cmd) == 1:
                ret = Auth.run_ps(cmd[0])
            else:
                ret = Auth.run_cmd(cmd[0], cmd[1:])

        if ret.status_code == 0:
            sOut = ret.std_out
        else:
            sOut = ret.std_err
        sOut = decodeWinOutput(sOut)
        return {'result': 'success', 'data': sOut}
    except Exception as e:
        logERROR("Exception: {0}".format(str(e)))
        return {'result': 'failure', 'data': str(e)}





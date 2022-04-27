import re
import random
import string
import os
import subprocess
import copy
import winrm
import paramiko as pmk
import ED_AES256 as aes
from ConnLog import create_log_file
import LFColors as lfc
import time
import ConnArcon as pam
import requests as req
import json

lfcObj = lfc.bcolors()
CERROR, CWARN = lfcObj.printerr, lfcObj.printwar

logObj = create_log_file("/var/log/autointelli/orch.log")
if not logObj:
    CERROR("Not able to create logfile")
    exit(0)
logERROR, logWARN, logINFO = logObj.error, logObj.warn, logObj.info

class multilang:

    global_vars = {}
    LANG_Support = {'python': ['2.7', '3.6'], 'bash': 'any', 'powershell': 'any'}
    RUNTIME_FILE = ""
    NEWLINE = "\n"
    HOSTNAME = ""
    USERNAME = ""
    PASSWORD = ""
    PORT = ""

    def type_cast_exception(self, value):
        try:
            value = float(value)
            return "int"
        except ValueError as e:
            return "str"

    def decodeWinOutput(self, content):
        if type(content) == type(bytes(0)):
            content = content.decode('utf-8')
        if content.__contains__('\r\n'):
            content = content.replace('\r\n', '\n')
        return content

    def chk_lang_support(self):
        try:
            sLang = self.global_vars['LANG']
            sVersion = self.global_vars['LANG_VERSION']
            if sLang in self.LANG_Support:
                return True
            else:
                return False
        except Exception as e:
            return False

    def get_where_to_execute(self):
        try:
            if 'target' in list(self.global_vars['VARS'].keys()):
                # Below snippet pulls, hostname, username, password, port
                self.HOSTNAME = self.global_vars['VARS']['target']
                if self.HOSTNAME == "localhost":
                    return True
                # Requests call of get should happen here
                sURL = "https://r2d2.nxtgen.com/ui/api1.0/execprereq/{0}".format(self.HOSTNAME)
                dHeader = {'Content-Type': 'application/json', 'sessionlesssecret': 'R@g@s!V@^^'}
                print(sURL, dHeader)
                ret = req.get(url=sURL, headers=dHeader, verify=False)
                print(ret.status_code)
                if not (ret.status_code == 200 or ret.status_code == 201):
                    return False
                dRet = json.loads(ret.text)
                # sQuery = """select
                #                 am.machine_fqdn, am.platform, am.ip_address, ad.cred_type, ad.username, ad.password, ad.port
                #             from
                #                 ai_machine am inner join ai_device_credentials ad on(am.fk_cred_id=ad.cred_id)
                #             where
                #                 am.machine_fqdn='{0}' or am.ip_address='{1}'""".format(self.HOSTNAME, self.HOSTNAME)
                # dRet = dbconn.returnSelectQueryResult(sQuery)
                if dRet['result'] == 'success':
                    if dRet['data'][0]['cred_type'].lower() == 'arcon':
                        ret = pam.queryPassword(dRet['data'][0]['ip_address'], dRet['data'][0]['username'], dRet['data'][0]['platform'])
                        if ret["result"] == "success":
                            self.USERNAME = dRet['data'][0]['username']
                            self.PASSWORD = ret["data"]
                            self.PORT = dRet['data'][0]['port']
                        else:
                            return False
                    else:
                        self.USERNAME = dRet['data'][0]['username']
                        k = '@ut0!ntell!'.encode()
                        fromDB = dRet['data'][0]['password'].encode()
                        self.PASSWORD = aes.decrypt(fromDB, k).decode('utf-8')
                        self.PORT = dRet['data'][0]['port']
                return True
            else:
                return False
        except Exception as e:
            return False

    def kcontext_replacer(self):
        try:
            sScript = self.global_vars['SCRIPT']
            sNewScript = ""
            sNewLine = "\n"

            # get var replacer
            get_vars = re.findall(r"kcontext.getVariable\(\"(\w+)\"\)", sScript)
            for eachFind in get_vars:
                sScript = sScript.replace("kcontext.getVariable(\"{0}\")".format(eachFind), "\"{0}\"".format(self.global_vars['VARS'][eachFind]))
            #print(sScript)

            # set var replacer
            for eachLine in sScript.splitlines():
                set_vars = re.search(r"kcontext.setVariable\(\"(\w+)\".(.+)\)", eachLine)
                if set_vars:
                    if set_vars.lastindex == 2:
                        sNewScript += "print(\"{0}=\" + str({1})){2}".format(set_vars.group(1), set_vars.group(2), sNewLine)
                else:
                    sNewScript += "{0}{1}".format(eachLine, sNewLine)

            self.global_vars['SCRIPT'] = sNewScript
            return True
        except Exception as e:
            return False

    def randomString(self, stringLength=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def execute_script(self):
        try:
            # write modified script to random file
            cwd = os.getcwd()
            randomFileName = "{0}\{1}.py".format(cwd, self.randomString(16))
            self.RUNTIME_FILE = randomFileName
            fObj = open(randomFileName, 'w')
            fObj.write(self.global_vars['SCRIPT'])
            fObj.close()
            print(randomFileName)

            # execute the script
            cmd = "{0} {1}".format("E:\\software_installation\\Python36-32\\python.exe", randomFileName)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            out, err = p.communicate()
            out = out.decode('utf-8') if type(out) == type(b'') else out
            err = err.decode('utf-8') if type(err) == type(b'') else err
            self.global_vars['VARS']['status_code'], self.global_vars['VARS']['stdout'], self.global_vars['VARS']['stderr']  = p.returncode, out, err
            if p.returncode == 0:
                for eachOutputLine in out.splitlines():
                    if eachOutputLine.find('=') >= 0:
                        var_found = eachOutputLine.split('=')[0].lower()
                        if var_found in list(self.global_vars['VARS'].keys()):
                            self.global_vars['VARS'][var_found] = '='.join(eachOutputLine.split('=')[1:])
        except Exception as e:
            return False

    def vars_prefixer(self):
        try:
            dTmp = self.global_vars
            script = dTmp['SCRIPT']
            for eachVARS in list(dTmp['VARS'].keys()):
                if not (dTmp['VARS'][eachVARS] == '' or type(dTmp['VARS'][eachVARS]) == type(None)):
                    if self.type_cast_exception(dTmp['VARS'][eachVARS]) == "str":
                        script = "{0}{1}{2}".format((eachVARS + '=\"' + dTmp['VARS'][eachVARS]) + '\"', self.NEWLINE, script)
                    else:
                        script = "{0}{1}{2}".format((eachVARS + '=' + dTmp['VARS'][eachVARS]) , self.NEWLINE, script)
            self.global_vars['SCRIPT'] = script
            return True
        except Exception as e:
            return False

    def destroy(self):
        os.remove(self.RUNTIME_FILE)

    def execute_script_python(self):
        try:
            retJSON = {}
            tempobj = copy.deepcopy(self.global_vars['VARS'])
            logINFO("Payload Received: {0}".format(tempobj))
            exec(self.global_vars['SCRIPT'], {}, tempobj)
            for (k, v) in self.global_vars['VARS'].items():
                retJSON[k] = tempobj[k]
            self.global_vars['VARS'] = retJSON
            logINFO("Payload Sent: {0}".format(self.global_vars['VARS']))
        except Exception as e:
            self.global_vars['VARS']['autointelli_log'] = str(e)
            logERROR("Execution Error: {0}".format(str(e)))

    def execute_script_bash(self):
        try:
            retJSON, PreS, PostS = {}, "", ""
            tmpScript = self.global_vars['SCRIPT']
            tempobj = copy.deepcopy(self.global_vars['VARS'])
            logINFO("Payload Received: {0}".format(tempobj))

            # Prefix Input Vars
            # for K in list(tempobj.keys()):
            #     #    if K not in ["router", "target", "autointelli_log"]:
            #     PreS += "{0}=\"{1}\";{2}".format(K, tempobj[K], self.NEWLINE)
            # tmpScript = PreS + tmpScript + self.NEWLINE
            # logINFO("Generated Prefix: {0}".format(PreS))
            for K in list(tempobj.keys()):
                #    if K not in ["router", "target", "autointelli_log"]:
                if tempobj[K].strip() != "" and len(tempobj[K].strip().splitlines()) > 1:
                    PreS += "read -d '' {0} <<EOF\n{1}\nEOF{2}".format(K, tempobj[K], self.NEWLINE)
                else:
                    PreS += "{0}=\"{1}\";{2}".format(K, tempobj[K], self.NEWLINE)
            tmpScript = PreS + tmpScript + self.NEWLINE
            logINFO("Generated Prefix: {0}".format(PreS))

            # Postfix Output VARS
            # tmpScript += "echo \"#123#123#\";"
            # for K in list(tempobj.keys()):
            #     #    if K not in ["router", "target", "autointelli_log"]:
            #     PostS += "echo %s=\"${%s}\";" % (K, K)
            # tmpScript += PostS
            # logINFO("Generated Postfix: {0}".format(PostS))
            tmpScript += "echo \"#123#123#\";"
            for K in list(tempobj.keys()):
                #    if K not in ["router", "target", "autointelli_log"]:
                PostS += "echo %s__keyvalue__${%s}__endofsingle__;" % (K, K)
            tmpScript += PostS
            logINFO("Generated Postfix: {0}".format(PostS))

            # exec Process
            logINFO('#' * 100)
            logINFO("Script: {0}".format(tmpScript))
            logINFO('#' * 100)
            logINFO("Remoting to: {0}".format(self.HOSTNAME))
            sFinalOut = ""
            if self.HOSTNAME.lower() == "localhost" or self.HOSTNAME.lower() == "127.0.0.1":
                s = time.time()
                outObj = subprocess.Popen(tmpScript, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                while outObj.returncode is None:
                    for line in outObj.stdout:
                        sFinalOut += line.decode('utf-8')
                    outObj.poll()
                logINFO("Remoting Time Execution: {0}".format(time.time() - s))
            else:
                remote = pmk.SSHClient()
                remote.set_missing_host_key_policy(pmk.AutoAddPolicy())
                remote.connect(self.HOSTNAME, username=self.USERNAME, password=self.PASSWORD, port=self.PORT)
                stdin, stdout, stderr = remote.exec_command(tmpScript, get_pty=False)
                retCode = stdout.channel.recv_exit_status()
                if (retCode == 0):
                    sFinalOut += '\n'.join(stdout.readlines())
                else:
                    sFinalOut += '\n'.join(stderr.readlines())

            # Restore current value of variables
            logINFO("Remoting Output: {0}".format(sFinalOut))
            if sFinalOut.find("#123#123#") >= 0:
                #restorePart = sFinalOut.split("#123#123#")[1].strip().splitlines()
                # dItems = [(i.split("=")[0], "=".join(i.split("=")[1:])) for i in restorePart if
                #           i.split("=")[0].strip() != ""]
                restorePart = sFinalOut.split("#123#123#")[1].strip().split('__endofsingle__')
                dItems = [(i.split("__keyvalue__")[0].strip(), "__keyvalue__".join(i.split("__keyvalue__")[1:]).strip()) for i in restorePart if i.split("__keyvalue__")[0].strip() != ""]
                self.global_vars['VARS'] = dict(dItems)
            logINFO("Payload Sent: {0}".format(self.global_vars['VARS']))
        except Exception as e:
            logERROR("Execution Error: {0}".format(str(e)))

    def execute_script_powershell(self):
        retJSON, PreS, PostS = {}, "", ""
        NEWLINE = "\r\n"
        tmpScript = self.global_vars['SCRIPT']
        tempobj = copy.deepcopy(self.global_vars['VARS'])

        # Prefix Input Vars
        for K in list(tempobj.keys()):
            PreS += "${0}=\"{1}\"{2}".format(K, tempobj[K], NEWLINE)
        tmpScript = PreS + tmpScript + NEWLINE

        # Postfix Output VARS
        tmpScript += "Write-Host \"#123#123#\";"
        for K in list(tempobj.keys()):
            PostS += "Write-Host %s=${%s};" % (K, K)
        tmpScript += PostS

        # exec Process
        sFinalOut = ""
        if self.HOSTNAME.lower() == "localhost":
            pass
        else:
            # Remoting
            try:
                ret = ""
                try:
                    connObject = winrm.Session(self.HOSTNAME, auth=(self.USERNAME, self.PASSWORD), transport='ntlm')
                    ret = connObject.run_ps(tmpScript)
                    print(ret.status_code)
                except Exception as e:
                    print("NTLM Exception {0}".format(str(e)))
                    try:
                        connObject = winrm.Session(self.HOSTNAME, auth=(self.USERNAME, self.PASSWORD), transport='basic')
                        ret = connObject.run_ps(tmpScript)
                        print(ret.status_code)
                    except Exception as e:
                        print("Basic Exception {0}".format(str(e)))
                if ret.status_code == 0:
                    sFinalOut = ret.std_out
                else:
                    sFinalOut = ret.std_err
                sFinalOut = self.decodeWinOutput(sFinalOut)
            except Exception as e:
                return {'result': 'failure', 'data': str(e)}
            # try:
            #     connObject = winrm.Session(self.HOSTNAME, auth=(self.USERNAME, self.PASSWORD), transport='ntlm')
            #     ret = connObject.run_ps(tmpScript)
            #     if ret.status_code == 0:
            #         sFinalOut = ret.std_out
            #     else:
            #         sFinalOut = ret.std_err
            #     sFinalOut = self.decodeWinOutput(sFinalOut)
            # except Exception as e:
            #     return {'result': 'failure', 'data': str(e)}

        # Restore current value of variables
        if sFinalOut.find("#123#123#") >= 0:
            restorePart = sFinalOut.split("#123#123#")[1].strip().splitlines()
            dItems = [(i.split("=")[0], "=".join(i.split("=")[1:])) for i in restorePart]
            self.global_vars['VARS'] = dict(dItems)

    def execute1(self):
        if self.chk_lang_support() == True:
            if self.vars_prefixer() == True:
                print(self.global_vars)
                self.execute_script()
                print(self.global_vars)
                self.destroy()
            else:
                return {"result": "failure", "std_in": "", "std_out": "", "std_err": "Error in set and get variable."}
        else:
             return {"result": "failure", "std_in": "", "std_out": "", "std_err": "Language not supported."}

    def execute(self):
        if self.chk_lang_support() == True:
            if self.get_where_to_execute() == True:
                logINFO('='*200)
                print(self.global_vars)
                if self.global_vars['LANG'].lower() == 'python':
                    self.execute_script_python()
                elif self.global_vars['LANG'].lower() == 'bash':
                    self.execute_script_bash()
                elif self.global_vars['LANG'].lower() == 'powershell':
                    self.execute_script_powershell()
                logINFO("Output => {0}".format(self.global_vars['VARS']))
                logINFO('=' * 200)
                return {'result': 'success', "std_in": "", "std_out": "Script execution success", "std_err": ""}
                #self.destroy()
            else:
                logERROR("{0}".format({"result": "failure", "std_in": "", "std_out": "", "std_err": "Target varibale is missing or empty."}))
                return {"result": "failure", "std_in": "", "std_out": "", "std_err": "Target varibale is missing or empty."}
        else:
            o = {"result": "failure", "std_in": "", "std_out": "", "std_err": "Language {0} not supported.".format(self.global_vars['LANG'])}
            logERROR("{0}".format(o))
            return o


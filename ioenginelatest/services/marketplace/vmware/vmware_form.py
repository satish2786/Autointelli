#!/usr/bin/python3.6

#https://vdc-download.vmware.com/vmwb-repository/dcr-public/1cd28284-3b72-4885-9e31-d1c6d9e26686/71ef7304-a6c9-43b3-a3cd-868b2c236c81/doc/index.html
import requests as req
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
from copy import deepcopy
from subprocess import check_output
from pymongo import MongoClient
import sys
import configparser as cp
from pyVim.connect import SmartConnectNoSSL, Disconnect
import time

req.packages.urllib3.disable_warnings(InsecureRequestWarning)
location = {}
try:
    location = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['pam']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

# void
def comment_uncomment(action):
    if action == "comment":
        out_b = check_output("sed -i '/enable_plugins = vmware_vm_inventory/s/^/#/g' /root/.ansible.cfg", shell=True)
    elif action == "uncomment":
        out_b = check_output("sed -i '/#enable_plugins = vmware_vm_inventory/s/^#//g' /root/.ansible.cfg", shell=True)
def pullTemplate():
    comment_uncomment("uncomment")
    out_b = check_output("ansible-inventory -i /root/vmware/collectall.vmware.yml --list", shell=True)
    st_s = out_b.decode('utf-8')
    js = json.loads(st_s)
    lTemplate = [js['_meta']['hostvars'][i]['config.name'] for i in list(js['_meta']['hostvars'].keys()) if (js['_meta']['hostvars'][i]['config.template'] == True)]
    comment_uncomment("comment")
    return lTemplate

def getPassword(pIP, pOS, pUser):
    try:
        url = "https://10.21.21.143:9091/arconToken"
        pwdurl = "https://10.21.21.143:9091/api/ServicePassword/GetTargetDevicePassKey"
        payload = "grant_type=password&username={0}&password={1}".format("cGFtYXBpdGVzdA==", "VGVzdEAx")
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = req.post(url, data=payload, headers=headers, verify=False)
        _data = json.loads(response.text)
        new_headers = {'Authorization': 'bearer ' + _data['access_token'], 'Content-Type': 'application/json'}
        new_payload = []
        if pOS.lower() == "linux":
            new_payload = [{'ServerIp': pIP, 'ServiceTypeId': 7, 'UserName': pUser, 'OpenForHours': '2'}]
        elif pOS.lower() == "windows":
            new_payload = [{'ServerIp': pIP, 'ServiceTypeId': 1, 'UserName': pUser, 'OpenForHours': '2'}]
        elif pOS.lower() == "vcenter":
            new_payload = [{'ServerIp': pIP, 'ServiceTypeId': 36, 'UserName': pUser, 'OpenForHours': '2'}]
        response = req.post(pwdurl, data=json.dumps(new_payload), headers=new_headers, verify=False)
        _output = json.loads(response.text)
        # print(_output)
        if _output['Success']:
            for result in _output['Result']:
                return {"result": "success", "data": result['Password']}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        return {"result": "failure", "data": str(e)}

def formBuilder(pWorkflowName, pVCenterIP, pOS, pUser, pPassword=""):
    s = time.time()
    session_id, password = "", ""
    if pPassword:
        password = pPassword
    else:
        retPwd = getPassword(pVCenterIP, pOS, pUser)
        print(retPwd)
        if retPwd['result'] == 'failure':
            return 0
        else:
            password = retPwd['data']
    vauth = (pUser, password)
    vip = "https://{0}".format(pVCenterIP)
    dHeader = {'content-type': 'application/json'}

    surl = vip + "/rest/com/vmware/cis/session"
    obj = req.post(url=surl, auth=vauth, headers=dHeader, verify=False)
    print(obj.status_code)
    if obj.status_code == 200 or obj.status_code == 201:
        retDict = json.loads(obj.text)
        session_id = retDict["value"]
    else:
        print("Unable to create session. Error: {0}".format(req.text))
        return 0
    print(session_id)

    # Received session_id
    dHeader.update({'vmware-api-session-id': session_id})

    # Pull All information like cluster, network, datacenter, datastore
    dFinal, dOthers = {}, {}
    out_pull = {'cluster': 'name', 'network': 'name', 'datacenter': 'name', 'datastore': 'name'}
    rest_urls = {'cluster': '/rest/vcenter/cluster', 'host': '/rest/vcenter/host',
                 'resource_pool': '/rest/vcenter/resource-pool', 'vm': '/rest/vcenter/vm',
                 'network': '/rest/vcenter/network', 'datacenter': '/rest/vcenter/datacenter',
                 'datastore': '/rest/vcenter/datastore',
                 'folder': '/rest/vcenter/folder'}  # , 'ovf': '/rest/com/vmware/vcenter/ovf'} #/export-flag'}
    loop_over = list(rest_urls.keys())
    for each_loop_over in loop_over:
        lo_ip = vip + rest_urls[each_loop_over]
        obj = req.get(url=lo_ip, auth=vauth, headers=dHeader, verify=False)
        dRestRet = json.loads(obj.text)
        print("{0} ---------- {1}".format(lo_ip, obj.status_code))
        print(dRestRet)
        if each_loop_over in out_pull:
            if each_loop_over.lower() == "datastore" and 'value' in list(dRestRet.keys()):
                dFinal[each_loop_over] = [
                    (str("%0.2f" % (i['free_space'] / (1024 * 1024 * 1024))) + " GB : " + i[out_pull[each_loop_over]])
                    for i in dRestRet['value']]
            elif 'value' in list(dRestRet.keys()):
                dFinal[each_loop_over] = [i[out_pull[each_loop_over]] for i in dRestRet['value']]
        else:
            dOthers[each_loop_over] = dRestRet

    dFinal["template"] = pullTemplate()
    print('-' * 100)
    print(dFinal)
    print("Time Taken: pull from api {0} secs".format(time.time() - s))
    s = time.time()

    dMongoLooper = {'Data Center': 'datacenter', 'Cluster': 'cluster', 'Template': 'template', 'Network': 'network',
                    'Data Store': 'datastore'}  # , 'Softwares': 'softwares'}
    dpMaster = {mitem: dFinal[dMongoLooper[mitem]] for mitem in list(dMongoLooper.keys())}
    dpMaster['Domain'] = ['sfl.ad', 'sfl-sis.sfl.ad']
    print(dpMaster)

    client = MongoClient("localhost:27017")
    db = client.designerDB
    for i in db.AutoIntelliFormStore.find({}):
        print(i['processid'], pWorkflowName, len(i['processid']), len(pWorkflowName), (i['processid']==pWorkflowName))
        if i['processid'].lower().strip() == pWorkflowName.lower().strip():
            lManipulateLater = []
            ll = json.loads(i['formcontent'])
            print(ll)
            for eachElement in ll:
                print("eachElement:{0}".format(eachElement))
                if eachElement['type'] == 'select' or eachElement['type'] == 'checkbox-group':
                    tmp = deepcopy(eachElement)
                    tmp["values"] = []
                    tmp["values"] = [{'label': eachDP, 'value': eachDP} for eachDP in dpMaster[eachElement['label']]]
                    tmp["values"][0]["selected"] = True
                    lManipulateLater.append(tmp)
                    # Update comes here
                else:
                    lManipulateLater.append(eachElement)

    print(lManipulateLater)

    i = db.AutoIntelliFormStore.update(
        {"processid": pWorkflowName},
        {"$set": {"formcontent": json.dumps(lManipulateLater)}})
    print(i)

    print("Time Taken save to db: {0} secs".format(time.time() - s))
    return 1

def discoverVCenter(pVCenterIP, pUser, pPassword=""):
    try:
        password = ""
        if pPassword:
            password = pPassword
        else:
            retPwd = getPassword(pVCenterIP, 'vcenter', pUser)
            print(retPwd)
            if retPwd['result'] == 'failure':
                return 0
            else:
                password = retPwd['data']

        print("Objects Discoverd for vCenter:{0}".format(pVCenterIP))

        s, e = time.time(), 0
        si = SmartConnectNoSSL(host=pVCenterIP, user=pUser, pwd=password)
        content = si.RetrieveContent()
        children = content.rootFolder.childEntity

        dC = {}
        for eachDC in children:
            dc_name = eachDC.name
            try:
                dC[dc_name] = {}
                templates = []
                print("Datacenter: {0}".format(dc_name))
                for eC in eachDC.hostFolder.childEntity:
                    if str(type(eC)) != "<class 'pyVmomi.VmomiSupport.vim.ClusterComputeResource'>":
                        continue
                    dC[dc_name][eC.name] = {}
                    lDS, lN = [], []
                    print("Cluster: {0}".format(eC.name))
                    if len(eC.datastore) > 0:
                        for eD in eC.datastore:
                            print("Datastore: {0}".format(eD.name))
                            lDS.append(eD.name)
                    if len(eC.network) > 0:
                        for eN in eC.network:
                            print("Network: {0}".format(eN.name))
                            lN.append(eN.name)
                    if len(eC.host) > 0:
                        for eachHost in eC.host:
                            for eachVM in eachHost.vm:
                                if eachVM.config.template == True:
                                    templates.append(eachVM.config.name)

                    dC[dc_name][eC.name]['datastore'] = lDS
                    dC[dc_name][eC.name]['network'] = lN
                dC[dc_name]['template'] = templates
            except Exception as e:
                print(str(e))

        print('Time Taken for vCenter: {0}, Object Discovery: {1}'.format(pVCenterIP, (time.time() - s)))
        Disconnect(si)

        return {"result": "success", "data": dC}
    except Exception as e:
        return {"result": "failure", "data": str(e)}

if __name__ == '__main__':
    # Create Session in order to communicate
    dynamicFormExecutionLoc = {}
    creds = {}
    try:
        parse = cp.ConfigParser()
        parse.read('/opt/aiorch/wa_scripts/vmware_inv/vmware.conf')
        for eachSec in parse.sections():
            if eachSec == "dynamicform":
                for k, v in parse.items(eachSec):
                    dynamicFormExecutionLoc[k] = v
            elif eachSec.__contains__("pam") or eachSec.__contains__("hc"):
                tmp = {}
                for k, v in parse.items(eachSec):
                    tmp[k] = v
                creds[eachSec.split(":")[0]] = {"type": eachSec.split(":")[1]}
                creds[eachSec.split(":")[0]].update(tmp)
    except Exception as e:
        print("File missing: /opt/aiorch/wa_scripts/vmware_inv/vmware.conf \n{0}".format(str(e)))
        sys.exit(0)

    print(dynamicFormExecutionLoc)
    print(creds)

    if dynamicFormExecutionLoc == {}:
        print("No Mapping available to execute this cron. Please check: /opt/aiorch/wa_scripts/vmware_inv/vmware.conf")
        sys.exit(0)

    for i in dynamicFormExecutionLoc:
        print(i)
        x = None
        if creds[dynamicFormExecutionLoc[i]]['type'] == 'pam':
            print(i, dynamicFormExecutionLoc[i], creds[dynamicFormExecutionLoc[i]]['os'],
                  creds[dynamicFormExecutionLoc[i]]['username'])
            x = discoverVCenter(dynamicFormExecutionLoc[i], creds[dynamicFormExecutionLoc[i]]['username'])
            # x = formBuilder(i, dynamicFormExecutionLoc[i], creds[dynamicFormExecutionLoc[i]]['os'], creds[dynamicFormExecutionLoc[i]]['username'])
        elif creds[dynamicFormExecutionLoc[i]]['type'] == 'hc':
            print(i, dynamicFormExecutionLoc[i], creds[dynamicFormExecutionLoc[i]]['os'],
                  creds[dynamicFormExecutionLoc[i]]['username'], creds[dynamicFormExecutionLoc[i]]['password'])
            x = discoverVCenter(dynamicFormExecutionLoc[i], creds[dynamicFormExecutionLoc[i]]['username'],
                                creds[dynamicFormExecutionLoc[i]]['password'])
            # x = formBuilder(i, dynamicFormExecutionLoc[i], creds[dynamicFormExecutionLoc[i]]['os'],
            #                 creds[dynamicFormExecutionLoc[i]]['username'], creds[dynamicFormExecutionLoc[i]]['password'])
        if x == 0:
            print("Failed to create dynamic form: {0}, {1}".format(i, dynamicFormExecutionLoc[i]))

        print(x)



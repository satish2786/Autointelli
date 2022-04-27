from pyVim.connect import SmartConnectNoSSL
import services.utils.ConnPostgreSQL as pcon
import services.utils.ED_AES256 as aes
from datetime import datetime as dt
import time
import json

dFinalvCD = {}
currentact = ""
iQuery = "insert into vcloud_from_vcenter(customer_id, vm_ref, vm_name, active_yn) values('{0}', '{1}', '{2}', 'Y')"
s, f = 0, 0

def recurseive(m, acct, q):
    try:
        # print('ACCT::::{0}::::{1}'.format(m, m.name))
        for k in m.childEntity:
            if k:
                try:
                    if hasattr(k, 'childEntity'):
                        # print("ACCT Child::::{0}::::{1}".format(k, k.name))
                        # print(k._wsdlName, k.overallStatus, k.configStatus, k.availableField, k.childEntity, k.tag, k.value )
                        recurseive(k, acct, q)
                    else:
                        # print('{0}$$$${1}'.format(k, k.name))
                        print('====>{0}::::{1}::::{2}::::{3}::::{4}'.format(k, k.name, k.summary.config.uuid,
                                                                            k.summary.config.managedBy.extensionKey,
                                                                            k.summary.config.managedBy.type))
                        dRet = pcon.returnInsertResult(q.format(acct, str(k).strip("'").split(":")[-1], k.name))
                        print(dRet)
                        dFinalvCD[acct].append((str(k).strip("'").split(":")[-1], k.name))
                except Exception as e:
                    try:
                        print('====>{0}::::{1}::::{2}::::{3}::::{4}'.format(k, k.name, k.summary.config.uuid,
                                                                            k.summary.config.managedBy.extensionKey,
                                                                            k.summary.config.managedBy.type))
                        dRet = pcon.returnInsertResult(q.format(acct, str(k).strip("'").split(":")[-1], k.name))
                        print(dRet)
                        dFinalvCD[acct].append((str(k).strip("'").split(":")[-1], k.name))
                    except Exception as e:
                        print('==>{0}---------------------------{1}::::{2}'.format(str(e), k, k.name))
                        dRet = pcon.returnInsertResult(q.format(acct, str(k).strip("'").split(":")[-1], k.name))
                        print(dRet)
                        dFinalvCD[acct].append((str(k).strip("'").split(":")[-1], k.name))
    except Exception as e:
        pass
        # print('Err ACCT::::{0}::::{1}::::{2}'.format(m, m.name, str(e)))


def discoverVCenter(ip, username, password):
    try:
        print("Objects Discoverd for vCenter:{0}".format(ip))
        s, e = time.time(), 0

        si = SmartConnectNoSSL(host=ip, user=username, pwd=password)
        content = si.RetrieveContent()
        children = content.rootFolder.childEntity

        for i in content.rootFolder.childEntity:
            for j in i.vmFolder.childEntity:
                if j.name == 'nxgblrvcd':
                    for xyz in j.childEntity:
                        print('-' * 80)
                        print('ACCT::::{0}::::{1}'.format(xyz, xyz.name))
                        currentact = xyz.name
                        dFinalvCD[currentact] = []
                        recurseive(xyz, currentact, iQuery)
        print(dFinalvCD)
        print('Time Taken for vCenter: {0}, Object Discovery: {1}'.format(ip, (time.time() - s)))
        return {"result": "success", "data": dFinalvCD}
    except Exception as e:
        return {"result": "failure", "data": str(e)}

if __name__ == '__main__':
    print('=' * 100)
    print("CRON Execute Summary below for {0}".format(dt.now().strftime('%d-%m-%Y %H:%M:%S')))
    stime = time.time()
    sQuery = """
            select 
	            h.pk_hypervisor_id, h.hypervisor_name, h.hypervisor_ip_address, c.cred_type, c.username, c.password 
            from 
	            hypervisor_details h inner join ai_device_credentials c on(h.hypervisor_cred=c.cred_id) 
            where 
	            h.hypervisor_type='vmware' and h.active_yn='Y' """
    # Testing: and h.hypervisor_ip_address='172.16.64.100'
    dRet = pcon.returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        for eachVCenter in dRet["data"]:
            try:
                # Discover Hypervisor Objects
                id = eachVCenter["pk_hypervisor_id"]
                ip = eachVCenter["hypervisor_ip_address"]
                username = eachVCenter["username"]
                password = aes.decrypt(eachVCenter["password"].encode(), '@ut0!ntell!'.encode()).decode('utf-8')
                print("Discovery for {0} with {1} credentials".format(ip, username))
                ret = discoverVCenter(ip, username, password)
                if ret["result"] == "failure":
                    print(
                        "Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachVCenter, ret["data"]))
            except Exception as e:
                print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachVCenter, str(e)))
    else:
        print("Failed: No Hypervisor found to run the discovery. Code Error:{0}".format(dRet["data"]))
    print("CRON Execute Time :{0}".format(time.time() - stime))


'''def Walk(root):
    if root._wsdlName == "Folder":
        print(root.name)
        for child in root.childEntity:
            Walk(child)
    elif root._wsdlName == "Datacenter":
        for child in root.vmFolder.childEntity:
            Walk(child)
    elif root._wsdlName == "VirtualMachine":
        print(root.name)
    elif root._wsdlName == "VirtualApp":
        pass
    else:
        raise VSError("Unable to recognise node type '%s'" % root._wsdlName)
'''
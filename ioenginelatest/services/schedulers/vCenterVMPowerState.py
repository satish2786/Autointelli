from pyVim.connect import SmartConnectNoSSL
import services.utils.ConnPostgreSQL as pcon
import services.utils.ED_AES256 as aes
from datetime import datetime as dt
import time
import schedule

def discoverVCenter(ip, username, password):
    try:
        print("Objects Discoverd for vCenter:{0}".format(ip))
        c_clus, c_host, c_vm = 0, 0, 0
        inven = {}
        data = {}
        c = 0
        insertQuery = []

        import time
        s, e = time.time(), 0

        si = SmartConnectNoSSL(host=ip, user=username, pwd=password)
        content = si.RetrieveContent()
        children = content.rootFolder.childEntity

        dcTmp = {}
        for eachDC in children:
            lCluster, lEsxiHost, lVM, lDatastores = [], [], [], []
            lVMRef = []
            dc_name = eachDC.name

            try:
                Datastores = eachDC.datastoreFolder.childEntity
            except Exception as e:
                continue
            for eachDS in Datastores:
                print('Datastore=>{0}'.format(eachDS.name))
                lDatastores.append(eachDS.name)

            try:
                Clusters = eachDC.hostFolder.childEntity
            except Exception as e:
                continue
            clusTmp = {}
            for eachCluster in Clusters:
                print('ESXi Cluster=>{0}'.format(eachCluster.name))
                cluster_name = eachCluster.name

                try:
                    EsxiHosts = eachCluster.host
                except Exception as e:
                    continue

                esxTmp = {}
                if EsxiHosts:
                    for eachEsxiHost in EsxiHosts:
                        esxihost_name = eachEsxiHost.summary.config.name
                        print('ESXi Host==>{0}'.format(eachEsxiHost.summary.config.name))
                        lEsxiHost.append(eachEsxiHost.summary.config.name)

                        try:
                            VirtualMachines = eachEsxiHost.vm
                        except Exception as e:
                            continue
                        vmTmp = []
                        if VirtualMachines:
                            for eachVM in VirtualMachines:
                                #vmTmp.append(eachVM.summary.config.name.strip())
                                print('------------------------------{0}'.format(eachVM.summary.runtime.powerState))
                                vmTmp.append([str(eachVM.summary.config.name).strip(), str(eachVM.summary.vm).strip().split(':')[-1].strip("'"), str(eachVM.summary.runtime.powerState)])
                                print('ESXi VM===>{0}, {1}, {2}'.format(str(eachVM.summary.config.name).strip(), str(eachVM.summary.vm).strip().split(':')[-1].strip("'"), str(eachVM.summary.runtime.powerState)))
                                lVM.append([str(eachVM.summary.config.name).strip(), str(eachVM.summary.vm).strip().split(':')[-1].strip("'"), str(eachVM.summary.runtime.powerState)])
                                lVMRef.append(str(eachVM.summary.vm).strip().split(':')[-1].strip("'"))
                        esxTmp[esxihost_name] = vmTmp
                clusTmp[cluster_name] = esxTmp
            dcTmp[dc_name] = {"cluster": clusTmp, "datastore": lDatastores}
            # print('-'*50)
            # print(json.dumps(dcTmp))
            # print('-' * 50)

        print('Time Taken for vCenter: {0}, Object Discovery: {1}'.format(ip, (time.time() - s)))
        print(lVMRef)
        return {"result": "success", "data": dcTmp}

    except Exception as e:
        return {"result": "failure", "data": str(e)}

def updateVMStatus(dPayload):
    try:
        iDCQuery = "select pk_object_id dc_id from vcenter_object_inventory where object_type like 'datacenter' and object_name='{0}'"
        iRefQuery = "select object_ref from vcenter_object_state where dc_id in({0}) and object_ref is not null and object_ref != ''"
        iRef = "insert into vcenter_object_state(dc_id, object_type, object_name, object_ref, object_state, last_modified_date) values({0}, '{1}', '{2}', '{3}', '{4}', now())"
        uRef = "update vcenter_object_state set object_state='{0}', last_modified_date=now() where object_ref='{1}' and dc_id={2}"
        iS, iF, uS, uF = 0, 0, 0, 0
        for eachDC in dPayload:
            dc_name = eachDC

            # Get DC ID
            dc_id = None
            q = iDCQuery.format(eachDC)
            ret = pcon.returnSelectQueryResult(q)
            if ret["result"] == "success":
                dc_id = ret["data"][0]["dc_id"].strip()

                # Get ESXIVM References for the dc_id
                refList = []
                qq = iRefQuery.format(dc_id)
                ret = pcon.returnSelectQueryResultAsList(qq)
                if ret["result"] == "success":
                    refList = ret["data"]["object_ref"]
                else:
                    refList = []

                    # Loop Over and Store Power State for Virtual Machines
                    for eachCluster in list(dPayload[dc_name]['cluster'].keys()):
                        print("DML Action on Cluster: {0}".format(eachCluster))

                        for eachHost in list(dPayload[eachDC]['cluster'][eachCluster].keys()):
                            print("DML Action on ESXiHost: {0}".format(eachHost))

                            for eachVM in dPayload[eachDC]['cluster'][eachCluster][eachHost]:
                                print("DML Action on ESXi VM: {0}".format(eachVM))
                                vm_name = eachVM[0].strip()
                                vm_common_ref = eachVM[1].strip()
                                vm_power_state = eachVM[2].strip()

                                if vm_common_ref in refList:
                                    tq = uRef.format(vm_power_state, vm_common_ref, dc_id)
                                    tRet = pcon.returnInsertResult(tq)
                                    print("update {0}".format(tq))
                                    if tRet["result"] == "success":
                                        uS += 1
                                    else:
                                        uF += 1
                                else:
                                    tq = iRef.format(dc_id, 'esxivm', vm_name, vm_common_ref, vm_power_state)
                                    tRet = pcon.returnInsertResult(tq)
                                    print("insert {0}".format(tq))
                                    if tRet["result"] == "success":
                                        iS += 1
                                    else:
                                        iF += 1
            else:
                print("Inorder to get the Power State for DC:{0}, the vCenter Object Inventory JOB has to be executed. Contact your Administrator".format(dc_name))
        print("Final Result Summary:: Insert-> success:{0}, failure{1}, Update-> success:{2}, failure{3}".format(iS, iF, uS, uF))
    except Exception as e:
        print("Power State CRON Error: {0}".format(str(e)))

def mainfunc():
    print('=' * 100)
    print("CRON Execute Summary below for {0}".format(dt.now().strftime('%d-%m-%Y %H:%M:%S')))
    stime = time.time()
    sQuery = """
            select 
	            h.pk_hypervisor_id, h.hypervisor_name, h.hypervisor_ip_address, c.cred_type, c.username, c.password 
            from 
	            hypervisor_details h inner join ai_device_credentials c on(h.hypervisor_cred=c.cred_id) 
            where 
	            lower(trim(h.hypervisor_type))='vmware vcenter' and h.active_yn='Y' """
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
                    print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachVCenter, ret["data"]))
                    continue
                updateVMStatus(ret["data"])
            except Exception as e:
                print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachVCenter, str(e)))
    else:
        print("Failed: No Hypervisor found to run the discovery. Code Error:{0}".format(dRet["data"]))
    print("CRON Execute Time :{0}".format(time.time() - stime))

#schedule.every().day.at("00:00").do(mainfunc)
#schedule.every(30).minutes.do(mainfunc)

#while True:
#    schedule.run_pending()
#    time.sleep(300)

mainfunc()

# #Loop Logic:
# import json
# d = json.loads(open('E:/Implementation/11 NxtGen/r&D/vcenterdiscovery/dc.json', 'r').read())
# for eachDC in d:
#     dc_name = eachDC
#     for eachCluster in list(d[dc_name]['cluster'].keys()):
#         cluster_name = eachCluster
#         for eachHost in list(d[eachDC]['cluster'][cluster_name].keys()):
#             host_name = eachHost
#             for eachVM in d[eachDC]['cluster'][cluster_name][host_name]:
#                 print(eachVM)
#     for eachDatastore in d[dc_name]['datastore']:
#         print(eachDatastore)

from pyVim.connect import SmartConnectNoSSL
import json
import services.utils.ConnPostgreSQL as pcon
import services.utils.ED_AES256 as aes
import services.utils.ConnMQ as mqcon
from datetime import datetime as dt
import time

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
                                vmTmp.append(eachVM.summary.config.name.strip())
                                print('ESXi VM===>{0}'.format(eachVM.summary.config.name.split('(')[0].strip()))
                                lVM.append(eachVM.summary.config.name.strip())
                                print(eachVM.summary.vm.strip())
                        esxTmp[esxihost_name] = vmTmp
                clusTmp[cluster_name] = esxTmp
            dcTmp[dc_name] = {"cluster": clusTmp, "datastore": lDatastores}
            # print('-'*50)
            # print(json.dumps(dcTmp))
            # print('-' * 50)

        print('Time Taken for vCenter: {0}, Object Discovery: {1}'.format(ip, (time.time() - s)))
        return {"result": "success", "data": dcTmp}

    except Exception as e:
        return {"result": "failure", "data": str(e)}

def pushObject2MQ(hypervisor_ip_address, type, name):
    dMQPushAdd = {
        "hypervisor_ip": hypervisor_ip_address,
        "object_type": type,
        "object_name": name
    }
    print("Push to MQ => {0}".format(dMQPushAdd))
    mqcon.send2MQ(pQueue="vmware_monitoring", pExchange="monitoring", pRoutingKey="vmware_monitoring", pData=json.dumps(dMQPushAdd))

def insert4FirstTime(hypervisor_ip_address, id, dPayload):
    # Fetch Hypervisor Address
    # hypervisor_ip_address = ""
    # iIPQuery = "select hypervisor_ip_address from hypervisor_details where pk_hypervisor_id={0}".format(id)
    # iIPRet = pcon.returnSelectQueryResult(iIPQuery)
    # if iIPRet["result"] == "success":
    #     hypervisor_ip_address = iIPRet["data"][0]["hypervisor_ip_address"]

    iNPQuery = """insert into vcenter_object_inventory(fk_hypervisor_id, object_type, object_name, obj_created_on, obj_created_by, obj_modified_on, obj_modified_by, obj_remark, active_yn) 
    values({0},'{1}', '{2}', {3}, {4}, {5}, {6}, '{7}', '{8}') RETURNING pk_object_id"""
    iQuery = """insert into vcenter_object_inventory(fk_hypervisor_id, object_type, object_name, object_parent_id, obj_created_on, obj_created_by, obj_modified_on, obj_modified_by, obj_remark, active_yn, dc_id) 
        values({0},'{1}', '{2}', {3}, {4}, {5}, {6}, {7}, '{8}', '{9}', {10}) RETURNING pk_object_id"""
    s, f = 0, 0
    for eachDC in dPayload:
        dc_name = eachDC
        dcparentid = 0

        q = iNPQuery.format(id, 'datacenter', dc_name, 'now()', '1', 'now()', '1', '', 'Y')
        iRet = pcon.returnSelectQueryResultWithCommit(q)
        if iRet["result"] == "success":
            s += 1
            dcparentid = iRet["data"][0]["pk_object_id"]
            print("Success insert query:{0}".format(q))
        else:
            f += 1
            print("Failed insert query:{0}".format(q))


        for eachDatastore in dPayload[dc_name]['datastore']:
            print("DML Action on Datastore: {0}".format(eachDatastore))
            datastore_name = eachDatastore

            q = iQuery.format(id, 'datastore', datastore_name, dcparentid, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid)
            iRet = pcon.returnSelectQueryResultWithCommit(q)
            if iRet["result"] == "success":
                pushObject2MQ(hypervisor_ip_address, 'datastore', datastore_name)
                print("Success insert query:{0}".format(q))
                s += 1
            else:
                f += 1
                print("Failed insert query:{0}".format(q))

        for eachCluster in list(dPayload[dc_name]['cluster'].keys()):
            print("DML Action on Cluster: {0}".format(eachCluster))
            cluster_name = eachCluster
            cparent_id = 0

            q = iQuery.format(id, 'cluster', cluster_name, dcparentid, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid)
            iRet = pcon.returnSelectQueryResultWithCommit(q)
            if iRet["result"] == "success":
                pushObject2MQ(hypervisor_ip_address, 'cluster', cluster_name)
                print("Success insert query:{0}".format(q))
                s += 1
                cparent_id = iRet["data"][0]["pk_object_id"]
            else:
                f += 1
                print("Failed insert query:{0}".format(q))

            for eachHost in list(dPayload[eachDC]['cluster'][cluster_name].keys()):
                print("DML Action on ESXiHost: {0}".format(eachHost))
                host_name = eachHost
                hparent_id = 0

                q = iQuery.format(id, 'esxihost', host_name, cparent_id, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid)
                iRet = pcon.returnSelectQueryResultWithCommit(q)
                if iRet["result"] == "success":
                    pushObject2MQ(hypervisor_ip_address, 'esxihost', host_name)
                    print("Success insert query:{0}".format(q))
                    s += 1
                    hparent_id = iRet["data"][0]["pk_object_id"]
                else:
                    f += 1
                    print("Failed insert query:{0}".format(q))

                for eachVM in dPayload[eachDC]['cluster'][cluster_name][host_name]:
                    print("DML Action on ESXi VM: {0}".format(eachVM))
                    vm_name = eachVM
                    vparent_id = 0

                    q = iQuery.format(id, 'esxivm', vm_name, hparent_id, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid)
                    iRet = pcon.returnSelectQueryResultWithCommit(q)
                    if iRet["result"] == "success":
                        pushObject2MQ(hypervisor_ip_address, 'esxivm', vm_name)
                        print("Success insert query:{0}".format(q))
                        s += 1
                        vparent_id = iRet["data"][0]["pk_object_id"]
                    else:
                        f += 1
                        print("Failed insert query:{0}".format(q))
    print("First Time Insert Final Result Summary:: success:{0}, failure{1}".format(s, f))

def insertAfterFirstTime(hypervisor_ip_address, hypervisor_id, dPayload):
    # Fetch Hypervisor Address
    # hypervisor_ip_address = ""
    # iIPQuery = "select hypervisor_ip_address from hypervisor_details where pk_hypervisor_id={0}".format(hypervisor_id)
    # iIPRet = pcon.returnSelectQueryResult(iIPQuery)
    # if iIPRet["result"] == "success":
    #     hypervisor_ip_address = iIPRet["data"][0]["hypervisor_ip_address"]

    # Data Center filter Query
    pullDBQuery = """
select 
	object_type, object_name 
from 
	vcenter_object_inventory 
where 
	dc_id=(select pk_object_id from vcenter_object_inventory where fk_hypervisor_id={0} and object_name='{1}')"""

    for eachDC in dPayload:
        dc_name = eachDC

        # from Payload
        fromPayload = []
        for cls in dPayload[dc_name]['cluster']:
            fromPayload.append(['cluster', cls, dc_name, dc_name])
            for esx in dPayload[dc_name]['cluster'][cls]:
                fromPayload.append(['esxihost', esx, cls, dc_name])
                for esxvm in dPayload[dc_name]['cluster'][cls][esx]:
                    fromPayload.append(['esxivm', esxvm, esx, dc_name])
        for dt in dPayload[dc_name]['datastore']:
            fromPayload.append(['datastore', dt, dc_name, dc_name])
        sFromPayload = {tuple([i[0], i[1]]) for i in fromPayload}
        print("Objects retrieved for vCenter:{0}, vDC:{1}\n{2}".format(hypervisor_ip_address, dc_name, ('-'*100)))
        if len(sFromPayload) == 0:
            print("Zero Objects fetched for vCenter:{0}, vDC:{1}".format(hypervisor_ip_address, dc_name))
            exit(0)

        # from DB
        sQuery = pullDBQuery.format(hypervisor_id, dc_name)
        dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
        if dRet["result"] == "failure":
            print("Zero Objects fetched from Database for vCenter:{0}, vDC:{1}. Wrong function got executed. It should be insert4FirstTime()".format(hypervisor_ip_address, dc_name))
            exit(0)
        fromDB = dRet["data"][1:]
        sFromDB = {tuple(i) for i in fromDB}
        # open('/tmp/fromPayload.json', 'w').write(json.dumps(fromPayload))
        # open('/tmp/fromDB.json', 'w').write(json.dumps(fromDB))

        # Newly added
        s, f = 0, 0
        sDifference = sFromPayload.difference(sFromDB)
        if len(sDifference) > 0:
            sDiffWithParent = [tuple(j) for i in sDifference for j in fromPayload if (j[0], j[1]) == i]
            sMetaQuery = """
            select
            	pk_object_id, dc_id
            from
            	vcenter_object_inventory
            where
            	object_name='{0}' and dc_id=(select pk_object_id from vcenter_object_inventory where object_type='datacenter' and object_name='{1}')"""
            iQuery = """insert into vcenter_object_inventory(fk_hypervisor_id, object_type, object_name, object_parent_id, obj_created_on, obj_created_by, obj_modified_on, obj_modified_by, obj_remark, active_yn, dc_id)
                            values({0},'{1}', '{2}', {3}, {4}, {5}, {6}, {7}, '{8}', '{9}', {10}) RETURNING pk_object_id"""
            for eachItem in sDiffWithParent:
                iiQuery = sMetaQuery.format(eachItem[2], eachItem[3])
                dRet = pcon.returnSelectQueryResult(iiQuery)
                if dRet["result"] == "success":
                    printit = iQuery.format(hypervisor_id, eachItem[0], eachItem[1], dRet["data"][0]["pk_object_id"], 'now()', 1, 'now()', 1, 'green:Adding Monitoring Service', 'Y', dRet["data"][0]["dc_id"])
                    iNewRet = pcon.returnInsertResult(printit)
                    if iNewRet["result"] == "success":
                        pushObject2MQ(hypervisor_ip_address, eachItem[0], eachItem[1])
                        print("New object added Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
                        s += 1
                    else:
                        print("Failed to insert new object into database: type:{0} with the name:{1}. Query Used:{2}".format(eachItem[0], eachItem[1], printit))
                        f += 1
                else:
                    print("Unable to fetch details of Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
            print("Insert Final Result Summary:: success:{0}, failure{1}".format(s, f))
        else:
            print("Not found new objects to add to Database")

        # Removde Existsing
        s, f = 0, 0
        sDifference = sFromDB.difference(sFromPayload)
        if len(sDifference) > 0:
            sDiffWithParent = [tuple(j) for i in sDifference for j in fromPayload if (j[0], j[1]) == i]
            sMetaQuery = """
                        select
                        	pk_object_id, dc_id
                        from
                        	vcenter_object_inventory
                        where
                        	object_name='{0}' and dc_id=(select pk_object_id from vcenter_object_inventory where object_type='datacenter' and object_name='{1}')"""
            uQuery = """update vcenter_object_inventory set obj_remark='{0}', obj_modified_on={1}, obj_modified_by={2} where object_parent_id={3} and dc_id={4} and object_type={5} and object_name={6}"""
            for eachItem in sDiffWithParent:
                iiQuery = sMetaQuery.format(eachItem[2], eachItem[3])
                dRet = pcon.returnSelectQueryResult(iiQuery)
                if dRet["result"] == "success":
                    printit = uQuery.format('red:Removed from vCenter', 'now()', 1, dRet["data"][0]["pk_object_id"], dRet["data"][0]["dc_id"], eachItem[0], eachItem[1])
                    uNewRet = pcon.returnInsertResult(printit)
                    if uNewRet["result"] == "success":
                        print("Existing object removed Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
                        s += 1
                    else:
                        print("Failed to make remove entry of existing object into database: type:{0} with the name:{1}. Query Used:{2}".format(eachItem[0], eachItem[1], printit))
                        f += 1
                else:
                    print("Unable to fetch details of Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
            print("Remove Final Result Summary:: success:{0}, failure{1}".format(s, f))
        else:
            print("Not found absent of objects to be removed from Database")

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
                    print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachVCenter, ret["data"]))
                    continue
                # Check for First Time Discovery
                chkQuery = "select * from vcenter_object_inventory where fk_hypervisor_id={0}".format(id)
                chkRet = pcon.returnSelectQueryResult(chkQuery)
                if chkRet["result"] == "failure":
                    print("Selected First Time Insert:")
                    insert4FirstTime(ip, id, ret["data"])
                else:
                    print("Selected Existing Comparison Insert & Remove:")
                    insertAfterFirstTime(ip, id, ret["data"])
            except Exception as e:
                print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachVCenter, str(e)))
    else:
        print("Failed: No Hypervisor found to run the discovery. Code Error:{0}".format(dRet["data"]))
    print("CRON Execute Time :{0}".format(time.time() - stime))

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


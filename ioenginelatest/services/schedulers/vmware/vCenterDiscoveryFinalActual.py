#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================
from pyVim.connect import SmartConnectNoSSL, Disconnect
import json
import services.utils.ConnPostgreSQL as pcon
import services.utils.ED_AES256 as aes
import services.utils.ConnMQ as mqcon
from datetime import datetime as dt
import time
import schedule
import services.utils.mailservice as ms

lFromDBCust, dRefAndCust = {}, {}
mailsenddevices = []

mon_hosts = []

def addmailsenddevices(p):
    mailsenddevices.append(p)

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
                                print(eachVM.summary.guest.ipAddress)
                                if 'template' in [str(xxx.value).lower().strip() for xxx in eachVM.summary.customValue]:
                                    print(eachVM.summary.config.name)
                                else:
                                    _tmpName = str(eachVM.summary.config.name).strip() if not eachVM.summary.config.name == None else ''
                                    _tmpRef = str(eachVM.summary.vm).strip().split(':')[-1].strip("'") if not eachVM.summary.vm == None else ''
                                    _tmpIP = str(eachVM.summary.guest.ipAddress).strip() if not eachVM.summary.guest.ipAddress == None else ''
                                    vmTmp.append([_tmpName, _tmpRef, _tmpIP])
                                    print('ESXi VM===>{0}, {1}, {2}'.format(_tmpName, _tmpRef, _tmpIP))
                                    lVM.append([_tmpName, _tmpRef, _tmpIP])
                                    lVMRef.append(_tmpRef)
                        esxTmp[esxihost_name] = vmTmp
                clusTmp[cluster_name] = esxTmp
            dcTmp[dc_name] = {"cluster": clusTmp, "datastore": lDatastores}
            # print('-'*50)
            # print(json.dumps(dcTmp))
            # print('-' * 50)

        print('Time Taken for vCenter: {0}, Object Discovery: {1}'.format(ip, (time.time() - s)))
        print(lVMRef)
        Disconnect(si)
        return {"result": "success", "data": dcTmp}


    except Exception as e:
        return {"result": "failure", "data": str(e)}

def pushObject2MQ(hypervisor_ip_address, type, name, action):
    dMQPush = {
        "hypervisor_ip": hypervisor_ip_address,
        "object_type": type,
        "object_name": name,
        "action": action
    }
    print("Save for MQ => {0}".format(dMQPush))
    mon_hosts.append(dMQPush)
    # mqcon.send2MQ(pQueue="vmware_monitoring", pExchange="monitoring", pRoutingKey="vmware_monitoring", pData=json.dumps(dMQPushAdd))

def getRefAndCust():
    try:
        global dRefAndCust
        # Existing customer
        sQuery = "select trim(vm_vcenter_ref) vm_vcenter_ref, trim(customer_id) customer_id from vcloud_object_inventory where vm_vcenter_ref != '' and vm_vcenter_ref is not null"
        dRet = pcon.returnSelectQueryResultConvert2Col2Dict(sQuery)
        if dRet["result"] == "success":
            dRefAndCust = dRet["data"]
    except Exception as e:
        print("KVM Exception: {0}".format(str(e)))

def discoveryCustFromDB():
    try:
        global lFromDBCust
        # Existing customer
        sQuery = "select trim(customer_id) customer_id, cust_pk_id pk_id from tbl_customer where technology_loc ='vmware' and active_yn='Y'"
        dRet = pcon.returnSelectQueryResultConvert2Col2Dict(sQuery)
        if dRet["result"] == "success":
            lFromDBCust = dRet["data"]
    except Exception as e:
        print("KVM Exception: {0}".format(str(e)))

def insertNxtGenMgmtDevices(hypervisor_ip_address, object_name, object_type):
    try:
        print("insertNxtGenMgmtDevices")
        # lFromDBCust['NxtGen Mgmt vmware']
        iQuery = "insert into tbl_vms(customer_id, vm_id, vm_name, vm_os, active_yn, device_type, techno) " \
                 "values('{0}', '{1}', '{2}', '{3}', 'N', '{4}', '{5}')".format('NxtGen Mgmt vmware', hypervisor_ip_address.strip(), object_name.strip(), object_type.strip(), object_type.strip(), 'vmware')
        dRet = pcon.returnInsertResult(iQuery)
        print("Insert into tbl_vms query: {0}".format(iQuery))
        addmailsenddevices([object_name.strip(), object_type.strip(), 'Added'])
        if dRet["result"] == "success":
            return True
        else:
            return False
    except Exception as e:
        return False

def insertACCTDevices(acct, object_name, object_type, object_ref, vm_ip):
    try:
        print("insertACCTDevices")
        acctid, iQuery = "", ""
        try:
            acctid = dRefAndCust[object_ref]
            # lFromDBCust[acctid]
            iQuery = """insert into tbl_vms(customer_id, vm_id, vm_name, vm_os, active_yn, device_type, reference, techno, vm_ip) 
                                select '{0}', vm_id, '{1}', vm_os, 'N', '{2}', '{3}', '{5}', '{6}' from (select vm_id, vm_os from vcloud_object_inventory where vm_vcenter_ref='{4}') A 
                             """.format(acctid.strip(), object_name.strip(), object_type.strip(), object_ref.strip(), object_ref.strip(), 'vmware', vm_ip)
            addmailsenddevices([object_name.strip(), object_type.strip(), 'Added'])
        except Exception as KeyError:
            iQuery = """insert into tbl_vms(vm_name, active_yn, device_type, reference, techno, vm_ip) 
                                select '{0}', 'N', '{1}', '{2}', '{3}', '{4}'
                             """.format(object_name.strip(), object_type.strip(), object_ref.strip(), 'vmware', vm_ip)
            addmailsenddevices([object_name.strip(), object_type.strip(), 'Added'])
        dRet = pcon.returnInsertResult(iQuery)
        print("Insert into tbl_vms query: {0}".format(iQuery))
        if dRet["result"] == "success":
            return True
        else:
            return False
    except Exception as e:
        return False

def insert4FirstTime(hypervisor_ip_address, id, dPayload):

    iNPQuery = """insert into vcenter_object_inventory(fk_hypervisor_id, object_type, object_name, obj_created_on, obj_created_by, obj_modified_on, obj_modified_by, obj_remark, active_yn) 
    values({0},'{1}', '{2}', {3}, {4}, {5}, {6}, '{7}', '{8}') RETURNING pk_object_id"""
    iQuery = """insert into vcenter_object_inventory(fk_hypervisor_id, object_type, object_name, object_parent_id, obj_created_on, obj_created_by, obj_modified_on, obj_modified_by, obj_remark, active_yn, dc_id, object_ref, object_ip) 
        values({0},'{1}', '{2}', {3}, {4}, {5}, {6}, {7}, '{8}', '{9}', {10}, '{11}', '{12}') RETURNING pk_object_id"""
    s, f = 0, 0
    for eachDC in dPayload:
        dc_name = eachDC
        dcparentid = 0

        q = iNPQuery.format(id, 'datacenter', dc_name.strip(), 'now()', '1', 'now()', '1', '', 'Y')
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

            q = iQuery.format(id, 'datastore', datastore_name.strip(), dcparentid, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid, '', '')
            iRet = pcon.returnSelectQueryResultWithCommit(q)
            if iRet["result"] == "success":
                insertNxtGenMgmtDevices(hypervisor_ip_address, datastore_name, 'datastore')
                pushObject2MQ(hypervisor_ip_address, 'datastore', datastore_name, 'ADD')
                print("Success insert query:{0}".format(q))
                s += 1
            else:
                f += 1
                print("Failed insert query:{0}".format(q))

        for eachCluster in list(dPayload[dc_name]['cluster'].keys()):
            print("DML Action on Cluster: {0}".format(eachCluster))
            cluster_name = eachCluster
            cparent_id = 0

            q = iQuery.format(id, 'cluster', cluster_name.strip(), dcparentid, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid, '', '')
            iRet = pcon.returnSelectQueryResultWithCommit(q)
            if iRet["result"] == "success":
                insertNxtGenMgmtDevices(hypervisor_ip_address, cluster_name, 'cluster')
                pushObject2MQ(hypervisor_ip_address, 'cluster', cluster_name, 'ADD')
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

                q = iQuery.format(id, 'esxihost', host_name.strip(), cparent_id, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid, '', '')
                iRet = pcon.returnSelectQueryResultWithCommit(q)
                if iRet["result"] == "success":
                    insertNxtGenMgmtDevices(hypervisor_ip_address, host_name, 'esxihost')
                    pushObject2MQ(hypervisor_ip_address, 'esxihost', host_name, 'ADD')
                    print("Success insert query:{0}".format(q))
                    s += 1
                    hparent_id = iRet["data"][0]["pk_object_id"]
                else:
                    f += 1
                    print("Failed insert query:{0}".format(q))

                for eachVM in dPayload[eachDC]['cluster'][cluster_name][host_name]:
                    print("DML Action on ESXi VM: {0}".format(eachVM))
                    vm_name = eachVM[0]
                    vm_common_ref = eachVM[1]
                    vm_ip = eachVM[2]
                    vparent_id = 0

                    q = iQuery.format(id, 'esxivm', vm_name.strip(), hparent_id, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid, vm_common_ref.strip(), vm_ip)
                    iRet = pcon.returnSelectQueryResultWithCommit(q)
                    if iRet["result"] == "success":
                        insertACCTDevices(vm_common_ref, vm_name, 'esxivm', vm_common_ref, vm_ip)
                        pushObject2MQ(hypervisor_ip_address, 'esxivm', vm_name, 'ADD')
                        print("Success insert query:{0}".format(q))
                        s += 1
                        vparent_id = iRet["data"][0]["pk_object_id"]
                    else:
                        f += 1
                        print("Failed insert query:{0}".format(q))
    print("First Time Insert Final Result Summary:: success:{0}, failure{1}".format(s, f))

def insertAfterFirstTime(hypervisor_ip_address, hypervisor_id, dPayload):

    # Data Center filter Query
    pullDBQuery = """
select 
	trim(object_type) object_type, trim(object_name) || '::' || trim(object_ref) 
from 
	vcenter_object_inventory  
where 
	dc_id=(select pk_object_id from vcenter_object_inventory  where fk_hypervisor_id={0} and object_name='{1}')"""

    for eachDC in dPayload:
        dc_name = eachDC

        # from Payload
        _ip = {} #
        fromPayload = []
        for cls in dPayload[dc_name]['cluster']:
            fromPayload.append(['cluster', cls + "::", dc_name, dc_name])
            for esx in dPayload[dc_name]['cluster'][cls]:
                fromPayload.append(['esxihost', esx + "::", cls, dc_name])
                for esxvm in dPayload[dc_name]['cluster'][cls][esx]:
                    fromPayload.append(['esxivm', "{0}::{1}".format(esxvm[0], esxvm[1]), esx, dc_name])
                    _ip["{0}::{1}".format(esxvm[0], esxvm[1])] = esxvm[2] #
        for dt in dPayload[dc_name]['datastore']:
            fromPayload.append(['datastore', dt + "::", dc_name, dc_name])
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
            sMetaQueryTop1 = "select pk_object_id from vcenter_object_inventory where object_type='datacenter' and object_name='{0}'"
            iQuery = """insert into vcenter_object_inventory(fk_hypervisor_id, object_type, object_name, object_parent_id, obj_created_on, obj_created_by, obj_modified_on, obj_modified_by, obj_remark, active_yn, dc_id, object_ref, object_ip) 
                            values({0},'{1}', '{2}', {3}, {4}, {5}, {6}, {7}, '{8}', '{9}', {10}, '{11}', '{12}') RETURNING pk_object_id"""
            for eachItem in sDiffWithParent:
                iiQuery = ""
                if eachItem[0].strip() == 'cluster' or eachItem[0].strip() == 'datastore':
                    iiQuery = sMetaQueryTop1.format(eachItem[2].strip())
                else:
                    iiQuery = sMetaQuery.format(eachItem[2].strip(), eachItem[3].strip())
                dRet = pcon.returnSelectQueryResult(iiQuery)
                if dRet["result"] == "success":

                    ipaddr = ""
                    if eachItem[1] in _ip:
                        ipaddr = _ip[eachItem[1]]

                    dc_id = dRet["data"][0]['dc_id'] if "dc_id" in dRet["data"][0].keys() else dRet["data"][0]['pk_object_id']
                    printit = iQuery.format(hypervisor_id, eachItem[0].strip(), eachItem[1].split('::')[0].strip(),
                                                dRet["data"][0]["pk_object_id"], 'now()', 1, 'now()', 1,
                                                'green:Adding Monitoring Service', 'Y', dc_id,
                                                eachItem[1].split('::')[1].strip(), ipaddr)
                    iNewRet = pcon.returnInsertResult(printit)
                    if iNewRet["result"] == "success":
                        if eachItem[0] == "esxihost" or eachItem[0] == "cluster" or eachItem[0] == "datastore":
                            insertNxtGenMgmtDevices(hypervisor_ip_address, eachItem[1], eachItem[0])
                        else:
                            insertACCTDevices(eachItem[1].split('::')[1], eachItem[1].split('::')[0], 'esxivm', eachItem[1].split('::')[1], ipaddr)
                        pushObject2MQ(hypervisor_ip_address, eachItem[0], eachItem[1], 'ADD')
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
        pullDBQuery = """
        select 
        	trim(object_type) object_type, trim(object_name) || '::' || trim(object_ref), object_parent_id, dc_id
        from 
        	vcenter_object_inventory  
        where 
        	dc_id=(select pk_object_id from vcenter_object_inventory  where fk_hypervisor_id={0} and object_name='{1}')"""
        sQuery = pullDBQuery.format(hypervisor_id, dc_name)
        dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
        if dRet["result"] == "failure":
            print(
                "Zero Objects fetched from Database for vCenter:{0}, vDC:{1}. Wrong function got executed. It should be insert4FirstTime()".format(
                    hypervisor_ip_address, dc_name))
            exit(0)
        fromDB = dRet["data"][1:]
        tmpDB = dict([((i[0], i[1]), (i[2], i[3])) for i in fromDB])
        # sFromDB = {tuple(i) for i in fromDB}
        sFromDB = set(tmpDB.keys())
        s, f, d, m = 0, 0, 0, 0
        sDiff = sFromDB.difference(sFromPayload)
        if len(sDiff) > 0:
            # sDiffWithParent = [tuple(j) for i in sDifference for j in fromPayload if (j[0], j[1]) == i]
            # sMetaQuery = """
            #                     select
            #                     	pk_object_id, dc_id
            #                     from
            #                     	vcenter_object_inventory
            #                     where
            #                     	object_name='{0}' and dc_id=(select pk_object_id from vcenter_object_inventory where object_type='datacenter' and object_name='{1}')"""
            uQuery = """update vcenter_object_inventory set active_yn='N', obj_remark='{0}', obj_modified_on={1}, obj_modified_by={2} where object_parent_id={3} and dc_id={4} and object_type='{5}' and object_name='{6}' and object_ref='{7}'"""
            for eachItem in sDiff:
                printit = uQuery.format('red:Removed from vCenter', 'now()', 1, tmpDB[eachItem][0],
                                        tmpDB[eachItem][1], eachItem[0].strip(),
                                        eachItem[1].split('::')[0].strip(), eachItem[1].split('::')[1].strip())
                print(printit)
                uNewRet = pcon.returnInsertResult(printit)
                if uNewRet["result"] == "success":
                    print("Existing object removed: Info Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(
                        tmpDB[eachItem][0], tmpDB[eachItem][1], eachItem[0], eachItem[1]))
                    vmiQuery = "insert into tbl_vms_deleted select * from tbl_vms where techno='vmware' and vm_name='{0}' and device_type='{1}'".format(
                        eachItem[1].split('::')[0].strip(), eachItem[0].strip()
                    )
                    vmdQuery = "delete from tbl_vms where techno='vmware' and vm_name='{0}' and device_type='{1}'".format(
                        eachItem[1].split('::')[0].strip(), eachItem[0].strip()
                    )
                    vmiRet = pcon.returnInsertResult(vmiQuery)
                    vmdRet = pcon.returnInsertResult(vmdQuery)
                    if vmiRet['result'] == 'success':
                        m += 1
                    if vmdRet['result'] == 'success':
                        d += 1
                    s += 1
                    if vmiRet['result'] == 'success' and vmdRet['result'] == 'success' and uNewRet["result"] == "success":
                        pushObject2MQ(hypervisor_ip_address, eachItem[0], eachItem[1], 'DEL')
                        addmailsenddevices([eachItem[1], eachItem[0], 'Removed'])
                else:
                    print(
                        "Failed to make remove entry of existing object into database: type:{0} with the name:{1}. Query Used:{2}".format(
                            eachItem[0], eachItem[1], printit))
                    f += 1

                # iiQuery = sMetaQuery.format(eachItem[2].strip(), eachItem[3].strip())
                # dRet = pcon.returnSelectQueryResult(iiQuery)
                # if dRet["result"] == "success":
                #     printit = uQuery.format('red:Removed from vCenter', 'now()', 1, dRet["data"][0]["pk_object_id"],
                #                             dRet["data"][0]["dc_id"], eachItem[0].strip(),
                #                             eachItem[1].split('::')[0].strip(), eachItem[1].split('::')[1].strip())
                #     print(printit)
                #     uNewRet = pcon.returnInsertResult(printit)
                #     pushObject2MQ(hypervisor_ip_address, eachItem[0], eachItem[1], 'DEL')
                #     if uNewRet["result"] == "success":
                #         print("Existing object removed Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(
                #             eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
                #         s += 1
                #     else:
                #         print(
                #             "Failed to make remove entry of existing object into database: type:{0} with the name:{1}. Query Used:{2}".format(
                #                 eachItem[0], eachItem[1], printit))
                #         f += 1
                #     addmailsenddevices([eachItem[1], eachItem[0], 'Removed'])
                # else:
                #     print("Unable to fetch details of Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(
                #         eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
            print("Remove Final Result Summary:: success:{0}, failure:{1}, deleted:{2}, moved:{3} ".format(s, f, d, m))
        else:
            print("Not found absent of objects to be removed from Database")

        # s, f = 0, 0
        # sDifference = sFromDB.difference(sFromPayload)
        # if len(sDifference) > 0:
        #     sDiffWithParent = [tuple(j) for i in sDifference for j in fromPayload if (j[0], j[1]) == i]
        #     sMetaQuery = """
        #                 select
        #                 	pk_object_id, dc_id
        #                 from
        #                 	vcenter_object_inventory
        #                 where
        #                 	object_name='{0}' and dc_id=(select pk_object_id from vcenter_object_inventory where object_type='datacenter' and object_name='{1}')"""
        #     uQuery = """update vcenter_object_inventory set active_yn='N', obj_remark='{0}', obj_modified_on={1}, obj_modified_by={2} where object_parent_id={3} and dc_id={4} and object_type={5} and object_name='{6}' and object_ref='{7}'"""
        #     for eachItem in sDiffWithParent:
        #         iiQuery = sMetaQuery.format(eachItem[2].strip(), eachItem[3].strip())
        #         dRet = pcon.returnSelectQueryResult(iiQuery)
        #         if dRet["result"] == "success":
        #             printit = uQuery.format('red:Removed from vCenter', 'now()', 1, dRet["data"][0]["pk_object_id"], dRet["data"][0]["dc_id"], eachItem[0].strip(), eachItem[1].split('::')[0].strip(), eachItem[1].split('::')[1].strip())
        #             print(printit)
        #             uNewRet = pcon.returnInsertResult(printit)
        #             pushObject2MQ(hypervisor_ip_address, eachItem[0], eachItem[1], 'DEL')
        #             if uNewRet["result"] == "success":
        #                 print("Existing object removed Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
        #                 s += 1
        #             else:
        #                 print("Failed to make remove entry of existing object into database: type:{0} with the name:{1}. Query Used:{2}".format(eachItem[0], eachItem[1], printit))
        #                 f += 1
        #             addmailsenddevices([eachItem[1], eachItem[0], 'Removed'])
        #         else:
        #             print("Unable to fetch details of Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
        #     print("Remove Final Result Summary:: success:{0}, failure{1}".format(s, f))
        # else:
        #     print("Not found absent of objects to be removed from Database")

#if __name__ == '__main__':
def mainfunc():
    global mailsenddevices
    print('=' * 100)
    print("CRON Execute Summary below for {0}".format(dt.now().strftime('%d-%m-%Y %H:%M:%S')))
    stime = time.time()
    # Some Refreshes
    discoveryCustFromDB()
    getRefAndCust()

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
                h_name = eachVCenter["hypervisor_name"]
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
                if len(mailsenddevices) > 0:
                    msub = "VMWare Discovery for vCenter - {0}".format(h_name)
                    mto = ['dinosh.daniel@nxtgen.com']
                    mcc = ['dinosh.daniel@nxtgen.com', 'dinesh@autointelli.com']
                    mbody = "Find the discovered objects:<BR/>"
                    mbody += "<table border='1'>"
                    mbody += "<tr><th>Object Name</th><th>Object Type</th></tr>"
                    for i in mailsenddevices:
                        mbody += "<tr>"
                        for j in i:
                            mbody += "<td>{0}</td>".format(j)
                        mbody += "</tr>"
                    mbody += "</table>"
                    ms.sendmail(sSubject=msub, lTo=mto, lCC=mcc, sBody=mbody)
                    mailsenddevices = []
            except Exception as e:
                print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachVCenter, str(e)))
    else:
        print("Failed: No Hypervisor found to run the discovery. Code Error:{0}".format(dRet["data"]))
    print("CRON Execute Time :{0}".format(time.time() - stime))

#schedule.every().day.at("00:00").do(mainfunc)
#schedule.every(5).minutes.do(mainfunc)

#while True:
#    schedule.run_pending()
#    time.sleep(300)

'''{
        "hypervisor_ip": hypervisor_ip_address,
        "object_type": type,
        "object_name": name,
        "action": action
    }'''

def comm2mon():
    templateMapping = {'datastore': 'VMWare_vCenter_ESXIDataStore', 'esxihot': 'VMWare_vCenter_ESXIHost',
                       'esxivm': 'VMWare_vCenter_ESXIVM'}
    tsQuery = "select t.pk_template_id template_id, t.template_name, s.pk_service_id service_id, s.service_name, s.default_threshold_warning, s.default_threshold_critical, s.default_threshold_unit, s.default_check_interval, s.default_retry_interval, s.default_max_check_attempts, s.check_type from mon_templates t inner join mon_services s on(t.pk_template_id=s.fk_template_id) where t.template_name='{0}' and t.active_yn='Y' and s.active_yn='Y'"
    hQuery = "insert into mon_hosts(hostname, address, downtime_yn, created_by, created_on, active_yn) values('{0}', '{1}', 'N', 'system', now(), 'N') RETURNING pk_host_id"
    ackQuery = "insert into mon_ack(request_json, status) values('{0}', 'open') RETURNING pk_ack_id"
    scQuery = "insert into mon_host_service_config(fk_host_id, fk_template_id, fk_service_id, threshold_warning, threshold_critical, threshold_unit, check_interval, retry_interval, max_check_attempts, check_type, created_by, created_on, active_yn) values({0}, {1}, {2}, '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', 'system', now(), 'Y')"
    for supportedTemplate in templateMapping:
        # template
        tsQueryFormatted = tsQuery.format(templateMapping[supportedTemplate])
        tsRet = pcon.returnSelectQueryResult(tsQueryFormatted)
        if tsRet['result'] == 'success':

            # objects
            objects = [i for i in mon_hosts if i['object_type'] == supportedTemplate]
            for eachObject in objects:

                # add
                if eachObject['action'] == 'ADD':
                    hQueryFormatted = hQuery.format(eachObject['object_name'], eachObject['object_name'])
                    dRet = pcon.returnSelectQueryResultWithCommit(hQueryFormatted)
                    if dRet['result'] == 'success':
                        hID = dRet['data'][0]['pk_host_id']

                        # Host Service Config
                        push2MQtemplate = {}
                        push2MQService = []
                        for eachService in tsRet['data']:
                            push2MQService.append({'service_name': eachService['service_name'], 'threshold_warning': eachService['default_threshold_warning'],
                                'threshold_critical': eachService['default_threshold_critical'], 'threshold_unit': eachService['default_threshold_unit'], 'check_interval': eachService['default_check_interval'],
                                'retry_interval': eachService['default_retry_interval'], 'max_check_attempts': eachService['default_max_check_attempts'], 'check_type': eachService['check_type']})
                            scQueryFormatted = scQuery.format(
                                hID, eachService['template_id'], eachService['service_id'], eachService['default_threshold_warning'],
                                eachService['default_threshold_critical'], eachService['default_threshold_unit'], eachService['default_check_interval'],
                                eachService['default_retry_interval'], eachService['default_max_check_attempts'], eachService['check_type'])
                            scQueryRet = pcon.returnInsertResult(scQueryFormatted)
                            if scQueryRet['result'] == 'success':
                                print('Successfully Pushed Service Config for the object: {0}'.format(eachObject['object_name']))
                            else:
                                print('Failed to Push Service Config for the object: {0}'.format(eachObject['object_name']))

                        # Push to ACK & MQ
                        push2MQtemplate['template_name'] = templateMapping[supportedTemplate]
                        push2MQtemplate['services'] = push2MQService
                        push2MQtemplate['hostname'] = eachObject['object_name']
                        push2MQtemplate['hypervisor_ip'] = eachObject['hypervisor_ip']
                        push2MQtemplate['action'] = eachObject['action']
                        push2MQtemplate['host_type'] = eachObject['object_type']
                        ackQueryFormatted = ackQuery.format(json.dumps(push2MQtemplate))
                        ackQueryRet = pcon.returnSelectQueryResultWithCommit(ackQueryFormatted)
                        if ackQueryRet['result'] == 'success':
                            push2MQtemplate['id'] = ackQueryRet['data'][0]['pk_ack_id']
                            print('Made an entry in ack table for object: {0}'.format(eachObject['object_name']))
                        else:
                            push2MQtemplate['id'] = ''
                            print('Failed to make an entry in ack table for object: {0}'.format(eachObject['object_name']))

                        # Push to MQ
                        mqcon.send2MQ(pQueue="vmware_monitoring", pExchange="monitoring",
                                      pRoutingKey="vmware_monitoring", pData=json.dumps(push2MQtemplate))
                    else:
                        print("Failed to make entry in host table. Host Name: {0}".format(eachObject['object_name']))
                # del
                elif eachObject['action'] == 'DEL':
                    # Push to ACK & MQ
                    push2MQtemplate = {}
                    push2MQtemplate['template_name'] = templateMapping[supportedTemplate]
                    push2MQtemplate['services'] = []
                    push2MQtemplate['hostname'] = eachObject['object_name']
                    push2MQtemplate['hypervisor_ip'] = eachObject['hypervisor_ip']
                    push2MQtemplate['action'] = eachObject['action']
                    push2MQtemplate['host_type'] = eachObject['object_type']
                    ackQueryFormatted = ackQuery.format(json.dumps(push2MQtemplate))
                    ackQueryRet = pcon.returnSelectQueryResultWithCommit(ackQueryFormatted)
                    if ackQueryRet['result'] == 'success':
                        push2MQtemplate['id'] = ackQueryRet['data'][0]['pk_ack_id']
                        print('Made an entry in ack table for object: {0}'.format(eachObject['object_name']))
                    else:
                        push2MQtemplate['id'] = ''
                        print('Failed to make an entry in ack table for object: {0}'.format(
                            eachObject['object_name']))

                    # Push to MQ
                    mqcon.send2MQ(pQueue="vmware_monitoring", pExchange="monitoring",
                                  pRoutingKey="vmware_monitoring", pData=json.dumps(push2MQtemplate))

        else:
            print("Template information not found in master templates. Template Type: {0}".format(supportedTemplate))

mainfunc()

comm2mon()

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


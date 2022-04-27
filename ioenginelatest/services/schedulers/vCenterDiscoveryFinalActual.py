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

def pushObject2MQ(hypervisor_ip_address, type, name):
    dMQPushAdd = {
        "hypervisor_ip": hypervisor_ip_address,
        "object_type": type,
        "object_name": name
    }
    print("Push to MQ => {0}".format(dMQPushAdd))
    mqcon.send2MQ(pQueue="vmware_monitoring", pExchange="monitoring", pRoutingKey="vmware_monitoring", pData=json.dumps(dMQPushAdd))

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

            q = iQuery.format(id, 'cluster', cluster_name.strip(), dcparentid, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid, '', '')
            iRet = pcon.returnSelectQueryResultWithCommit(q)
            if iRet["result"] == "success":
                insertNxtGenMgmtDevices(hypervisor_ip_address, cluster_name, 'cluster')
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

                q = iQuery.format(id, 'esxihost', host_name.strip(), cparent_id, 'now()', '1', 'now()', '1', 'green:Adding Monitoring Service', 'Y', dcparentid, '', '')
                iRet = pcon.returnSelectQueryResultWithCommit(q)
                if iRet["result"] == "success":
                    insertNxtGenMgmtDevices(hypervisor_ip_address, host_name, 'esxihost')
                    pushObject2MQ(hypervisor_ip_address, 'esxihost', host_name)
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
                        pushObject2MQ(hypervisor_ip_address, 'esxivm', vm_name)
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
            iQuery = """insert into vcenter_object_inventory(fk_hypervisor_id, object_type, object_name, object_parent_id, obj_created_on, obj_created_by, obj_modified_on, obj_modified_by, obj_remark, active_yn, dc_id, object_ref, object_ip) 
                            values({0},'{1}', '{2}', {3}, {4}, {5}, {6}, {7}, '{8}', '{9}', {10}, '{11}', '{12}') RETURNING pk_object_id"""
            for eachItem in sDiffWithParent:
                iiQuery = sMetaQuery.format(eachItem[2].strip(), eachItem[3].strip())
                dRet = pcon.returnSelectQueryResult(iiQuery)
                if dRet["result"] == "success":

                    ipaddr = ""
                    if eachItem[1] in _ip:
                        ipaddr = _ip[eachItem[1]]

                    printit = iQuery.format(hypervisor_id, eachItem[0].strip(), eachItem[1].split('::')[0].strip(),
                                                dRet["data"][0]["pk_object_id"], 'now()', 1, 'now()', 1,
                                                'green:Adding Monitoring Service', 'Y', dRet["data"][0]["dc_id"],
                                                eachItem[1].split('::')[1].strip(), ipaddr)
                    iNewRet = pcon.returnInsertResult(printit)
                    if iNewRet["result"] == "success":
                        if eachItem[0] == "esxihost" or eachItem[0] == "cluster" or eachItem[0] == "datastore":
                            insertNxtGenMgmtDevices(hypervisor_ip_address, eachItem[1], eachItem[0])
                        else:
                            insertACCTDevices(eachItem[1].split('::')[1], eachItem[1].split('::')[0], 'esxivm', eachItem[1].split('::')[1], ipaddr)
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
            uQuery = """update vcenter_object_inventory set obj_remark='{0}', obj_modified_on={1}, obj_modified_by={2} where object_parent_id={3} and dc_id={4} and object_type={5} and object_name='{6}' and object_ref='{7}'"""
            for eachItem in sDiffWithParent:
                iiQuery = sMetaQuery.format(eachItem[2].strip(), eachItem[3].strip())
                dRet = pcon.returnSelectQueryResult(iiQuery)
                if dRet["result"] == "success":
                    printit = uQuery.format('red:Removed from vCenter', 'now()', 1, dRet["data"][0]["pk_object_id"], dRet["data"][0]["dc_id"], eachItem[0].strip(), eachItem[1].split('::')[0].strip(), eachItem[1].split('::')[1].strip())
                    uNewRet = pcon.returnInsertResult(printit)
                    if uNewRet["result"] == "success":
                        print("Existing object removed Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
                        s += 1
                    else:
                        print("Failed to make remove entry of existing object into database: type:{0} with the name:{1}. Query Used:{2}".format(eachItem[0], eachItem[1], printit))
                        f += 1
                    addmailsenddevices([eachItem[1], eachItem[0], 'Removed'])
                else:
                    print("Unable to fetch details of Parent:{0}, and DC:{1} for type:{2} with the name:{3}".format(eachItem[2], eachItem[3], eachItem[0], eachItem[1]))
            print("Remove Final Result Summary:: success:{0}, failure{1}".format(s, f))
        else:
            print("Not found absent of objects to be removed from Database")

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
                    mto = ['dinosh.daniel@nxtgen.com', 'dinsoka@nxtgen.com']
                    mcc = ['dinosh.daniel@nxtgen.com', 'dinsoka@nxtgen.com', 'dinesh@autointelli.com']
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


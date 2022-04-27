import services.utils.ConnPostgreSQL as pcon
import services.utils.ED_AES256 as aes
import requests as req
import json
from datetime import datetime as dt
import time
import services.utils.ConnMQ as mqcon

sURLVM = "https://{0}/virtual_machines.json"
sURLH = "https://{0}/hypervisors.json"
sURLU = "https://{0}/users.json"
sHeader = {"Accept": "application/json"}
lUser, lVM, lHyp, lFromDBCust = {}, {}, {}, {}
dHostNxtGenMgmt = {}
location = "" # "blr-" # "amd-" # "fbd-"

# While Deploying, uncomment the below and comment the hardcoded
try:
    location = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['onapploc']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

def singleQuoteIssue(value):
    if type('') == type(value):
        return value.replace("'", "''").strip()
    else:
        return value

def discoverKVMs(ip, user, passwd):
    try:
        global lUser, lVM, lHyp

        dAuth = (user, passwd)

        # User
        dRetUser = req.get(url=sURLU.format(ip), auth=dAuth, headers=sHeader, verify=False)
        # Virtual Machine
        dRetVirtualMachine = req.get(url=sURLVM.format(ip), auth=dAuth, headers=sHeader, verify=False)
        # Hypervisor
        dRetHypervisor = req.get(url=sURLH.format(ip), auth=dAuth, headers=sHeader, verify=False)

        print(dRetUser.status_code, dRetVirtualMachine.status_code, dRetHypervisor.status_code)
        if dRetUser.status_code == 200 and dRetHypervisor.status_code == 200 and dRetVirtualMachine.status_code == 200:
            lUser = json.loads(dRetUser.text)
            lVM = json.loads(dRetVirtualMachine.text)
            lHyp = json.loads(dRetHypervisor.text)
            del dRetVirtualMachine
            del dRetHypervisor
            del dRetUser
            print("Successfully fetched all records")
        else:
            print("Failed to fetch records")
            return {"result": "failure"}
        print(len(lUser))
        print(len(lVM))
        print(len(lHyp))

        return {"result": "success"}
    except Exception as e:
        print("KVM Exception: {0}".format(str(e)))
        return {"result": "failure"}

def discoveryCustFromDB():
    try:
        global lFromDBCust
        # Existing customer
        sQuery = "select trim(customer_id) login, cust_pk_id pk_id from tbl_customer where technology_loc ='kvm' and active_yn='Y'"
        dRet = pcon.returnSelectQueryResultConvert2Col2Dict(sQuery)
        if dRet["result"] == "success":
            lFromDBCust = dRet["data"]
    except Exception as e:
        print("KVM Exception: {0}".format(str(e)))

def pushObject2MQ(dPayload):
    try:
        print("Push to MQ => {0}".format(dPayload))
        mqcon.send2MQ(pQueue="kvm_monitoring", pExchange="monitoring", pRoutingKey="kvm_monitoring", pData=json.dumps(dPayload))
    except Exception as e:
        print("Failed pushing to MQ:{0}".format(str(e)))

def HostHostIPMapping(loc):
    try:
        global dHostNxtGenMgmt
        sQuery = "select distinct trim(h_host) h_host, trim(h_ip) h_ip from onapp_object_inventory where lower(h_label) like '%{0}%'".format(loc)
        dRet = pcon.returnSelectQueryResultConvert2Col2Dict(sQuery)
        if dRet['result'] == 'success':
            dHostNxtGenMgmt = dRet['data']
    except Exception as e:
        print("Fetching mapping Host & Host IP:{0}".format(str(e)))

def insertNxtGenMgmtDevices(hypervisor_ip_address, object_name, object_type):
    try:
        # lFromDBCust['NxtGen Mgmt kvm']
        ip = dHostNxtGenMgmt[object_name]
        iQuery = "insert into tbl_vms(customer_id, vm_id, vm_name, vm_os, active_yn, device_type, techno) " \
                 "values('{0}', '{1}', '{2}', '{3}', 'N', '{4}', '{5}')".format('NxtGen Mgmt kvm', ip.strip(), object_name.strip(), object_type.strip(), object_type.strip(), 'kvm')
        dRet = pcon.returnInsertResult(iQuery)
        if dRet["result"] == "success":
            return True
        else:
            return False
    except Exception as e:
        return False

def insertACCTDevices(acct, object_id, object_name, object_os, object_type):
    try:
        # lFromDBCust[acct]
        iQuery = "insert into tbl_vms(customer_id, vm_id, vm_name, vm_os, active_yn, device_type, techno) " \
                 "values('{0}', '{1}', '{2}', '{3}', 'N', '{4}', '{5}')".format(acct.strip(), object_id.strip(), object_name.strip(), object_os.strip(), object_type.strip(), 'kvm')
        dRet = pcon.returnInsertResult(iQuery)
        if dRet["result"] == "success":
            return True
        else:
            return False
    except Exception as e:
        return False

def insertin2DB():
    try:
        global lUser, lVM, lHyp
        s, f, nc = 0, 0, 0

        # Hypervisor Details
        lHypBlr = [i for i in lHyp if i["hypervisor"]["label"].lower().__contains__(location)]
        lHypBlrID = [i["hypervisor"]["id"] for i in lHypBlr if i["hypervisor"]["label"].lower().__contains__(location)]
        lHypBlrD = {}
        for i in lHypBlr:
            lHypBlrD[i["hypervisor"]["id"]] = [i["hypervisor"]["hypervisor_type"], i["hypervisor"]["host"],
                                               i["hypervisor"]["id"],
                                               i["hypervisor"]["label"], i["hypervisor"]["cloud_boot_os"],
                                               i["hypervisor"]["os_version"], i["hypervisor"]["ip_address"]]
        del lHyp
        del lHypBlr

        # Virtual Machine Details
        lVMBlr = [i for i in lVM if i["virtual_machine"]["hypervisor_id"] in lHypBlrID]
        del lHypBlrID
        del lVM

        # ACCT Details
        lUsersD = {}
        for eachUser in lUser:
            lUsersD[eachUser["user"]["id"]] = [
                eachUser["user"]["first_name"].strip() + "," + eachUser["user"]["last_name"].strip(),
                eachUser["user"]["login"]]
        del lUser

        # From API
        lAllInOne = []
        for eachVM in lVMBlr:
            d = {}
            hid = eachVM["virtual_machine"]["hypervisor_id"]
            d["h_id"] = hid
            d["h_type"] = singleQuoteIssue(lHypBlrD[hid][0])
            d["h_host"] = singleQuoteIssue(lHypBlrD[hid][1])
            d["h_label"] = singleQuoteIssue(lHypBlrD[hid][3])
            d["h_os"] = singleQuoteIssue(lHypBlrD[hid][4])
            d["h_osv"] = singleQuoteIssue(lHypBlrD[hid][5])
            d["h_ip_address"] = singleQuoteIssue(lHypBlrD[hid][6])
            d["v_domain"] = singleQuoteIssue(eachVM["virtual_machine"]["domain"])
            d["v_hostname"] = singleQuoteIssue(eachVM["virtual_machine"]["hostname"])
            d["v_label"] = singleQuoteIssue(eachVM["virtual_machine"]["label"])
            d["v_identifier"] = singleQuoteIssue(eachVM["virtual_machine"]["identifier"])
            d["v_operating_system"] = singleQuoteIssue(eachVM["virtual_machine"]["operating_system"])
            d["v_operating_system_distro"] = singleQuoteIssue(eachVM["virtual_machine"]["operating_system_distro"])
            uid = eachVM["virtual_machine"]["user_id"]
            d["c_id"] = uid
            d["c_name"] = singleQuoteIssue(lUsersD[uid][0])  # getCustomerName(eachVM["virtual_machine"]["user_id"])
            d["c_login"] = singleQuoteIssue(lUsersD[uid][1])
            d["v_local_remote_access_ip_address"] = singleQuoteIssue(eachVM["virtual_machine"]["local_remote_access_ip_address"])
            lAddr = []
            for eachAddr in eachVM["virtual_machine"]["ip_addresses"]:
                lAddr.append(eachAddr["ip_address"]["address"])
            d["v_nic_count"] = len(lAddr)
            d["v_ip_addresses"] = " | ".join(lAddr)
            d["v_power_state"] = 'POWEREDOFF' if len(lAddr) == 0 else 'POWEREDON'
            lAllInOne.append(d)
            del d

        # From DB
        oaAll, identity = [], []
        sQuery = "select h_host, v_identifier from onapp_object_inventory where lower(h_label) like '%{0}%'".format(location)
        dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
        if dRet['result'] == 'success':
            oaAll = dRet['data'][1:]
        identity = dict([(i[1], i[0]) for i in oaAll])

        # Push to tbl_customer table
        iQuery = "insert into tbl_customer(customer_id, customer_name, technology_loc, created_by, created_on, active_yn) values('{0}', '{1}', 'kvm', 'admin', now(), 'Y')"
        ddlKVMCustDB = []
        iN, iM = 0, 0
        sQuery = "select trim(customer_id) customer_id, trim(customer_name) customer_name from tbl_customer where lower(technology_loc)='kvm' and active_yn='Y'"
        dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
        if dRet['result'] == 'success':
            ddlKVMCustDB = dRet['data'][1:]
        sKVMFromDB = set([(i[0], i[1]) for i in ddlKVMCustDB])
        sKVMFromT = set([(i["c_login"], i["c_name"]) for i in lAllInOne])
        sDiffT = sKVMFromT.difference(sKVMFromDB)
        sDiffDB = sKVMFromDB.difference(sKVMFromT)
        for i in sDiffT:
            print("New Customer: {0}".format(i))
            iQ = iQuery.format(singleQuoteIssue(i[0]), singleQuoteIssue(i[1]))
            ret = pcon.returnInsertResult(iQ)
            if ret["result"] == "success":
                iN += 1
        for i in sDiffDB:
            print("Missing Customer(Available in DB, Not in KVM): {0}".format(i))
            iM += 1
            # Add remark, and also an option to be provided with which someone can deactivate
        print("OverAll Summary. New Customers found:{0}, Missing Customers from kvm API:{1}".format(iN, iM))

        # Refresh Customer References
        discoveryCustFromDB()

        # Hosts to be pushed to tbl_vms table to register as NxtGen Mgmt Devices
        setCurrData = {i['h_host'] for i in lAllInOne}
        setOAAll = {i[0] for i in oaAll}
        setNewHost = setCurrData.difference(setOAAll)
        print("Have to add these new hosts to database which will be manged by NxtGen Mgmt: {0}".format(setNewHost))
        HostHostIPMapping(location) # This is waste because all the data which will flow are new data. Not existing host.
        for i in setNewHost:
            # New Host Data
            insertNxtGenMgmtDevices('blrngcs.nxtgen.com', i, 'kvmhost')

        # Existing host is removed in API
        # Add remark, and also an option to be provided with which someone can deactivate
        setOldHost = setOAAll.difference(setCurrData)
        # Existing vms is removed in API
        # Add remark, and also an option to be provided with which someone can deactivate
        setCurrData = {(i['h_host'], i['v_identifier']) for i in lAllInOne}
        setOAAll = {(i[0], i[1]) for i in oaAll}
        print("Have to set these to inactive in database: {0}".format(setOAAll.difference(setCurrData)))

        # Loop over current data compare with DB data. 1. Send new record, as well 2. Moved VM
        iQuery = """insert into onapp_object_inventory(h_id, h_type, h_host, h_label, h_os, h_osv, h_ip, v_domain, v_hostname, v_label, v_identifier, v_operating_system, v_operating_system_distro, 
        c_id, c_name, c_login, v_local_remote_access_ip_address, v_nic_count, v_ip_addresses, v_power_state, active_yn) 
        values({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}', '{17}', '{18}', '{19}', '{20}')"""
        for d in lAllInOne:
            if not [d["h_host"], d["v_identifier"]] in oaAll:
                print("yes change: {0}".format([d["h_id"], d["v_identifier"]]))
                query = iQuery.format(d["h_id"], d["h_type"], singleQuoteIssue(d["h_host"]), singleQuoteIssue(d["h_label"]), d["h_os"], d["h_osv"], singleQuoteIssue(d["h_ip_address"]),
                                      singleQuoteIssue(d["v_domain"]), singleQuoteIssue(d["v_hostname"]), singleQuoteIssue(d["v_label"]), d["v_identifier"],
                                      singleQuoteIssue(d["v_operating_system"]),
                                      singleQuoteIssue(d["v_operating_system_distro"]), d["c_id"], singleQuoteIssue(d["c_name"]), singleQuoteIssue(d["c_login"]),
                                      singleQuoteIssue(d["v_local_remote_access_ip_address"]), d["v_nic_count"], singleQuoteIssue(d["v_ip_addresses"]),
                                      d["v_power_state"], 'Y')
                dRet = pcon.returnInsertResult(query)
                if dRet["result"] == "success":
                    s += 1
                    if d['v_identifier'] in identity:
                        pushObject2MQ({'host': d["h_host"], 'vmlabel': d["v_label"], 'vmhostname': d['v_hostname'],
                                       'moved': 'yes', 'old_host': identity[d['v_identifier']]})
                    else:
                        insertACCTDevices(d["c_login"], d["v_identifier"], d["v_label"], d["v_operating_system"], 'kvmguest')
                        pushObject2MQ({'host': d["h_host"], 'vmlabel': d["v_label"], 'vmhostname': d['v_hostname'],
                                       'moved': 'no', 'old_host': ''})
                else:
                    f += 1
                    print("Failed Query: {0}".format(query))
            else:
                print("no change: {0}".format([d["h_id"], d["v_identifier"]]))
                nc += 1

        # # Push to tbl_customer table
        # iQuery = "insert into tbl_customer(customer_id, customer_name, technology_loc, created_by, created_on, active_yn) values('{0}', '{1}', 'kvm', 'admin', now(), 'Y')"
        # ddlKVMCustDB = []
        # iN, iM = 0, 0
        # sQuery = "select customer_id, customer_name from tbl_customer where lower(technology_loc)='kvm' and active_yn='Y'"
        # dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
        # if dRet['result'] == 'success':
        #     ddlKVMCustDB = dRet['data'][1:]
        # sKVMFromDB = set([(i[0], i[1]) for i in ddlKVMCustDB])
        # sKVMFromT = set([(d["c_login"], d["c_name"]) for i in lAllInOne])
        # sDiffT = sKVMFromT.difference(sKVMFromDB)
        # sDiffDB = sKVMFromDB.difference(sKVMFromT)
        # for i in sDiffT:
        #     print("New Customer: {0}".format(i))
        #     iQ = iQuery.format(i[0], i[1])
        #     ret = pcon.returnInsertResult(iQ)
        #     if ret["result"] == "success":
        #         iN += 1
        # for i in sDiffDB:
        #     print("Missing Customer: {0}".format(i))
        #     iM += 1
        #     # Add remark
        # print("OverAll Summary. New Customers found:{0}, Missing Customers:{1}".format(iN, iM))
        #
        # #Hosts to be pushed to tbl_vms table
        # setCurrData = {i['h_host'] for i in lAllInOne}
        # setOAAll = {i[0] for i in oaAll}
        # setNewHost = setOAAll.difference(setCurrData)
        # print("Have to set these to inactive in database: {0}".format(setNewHost))
        # for i in setNewHost:
        #     insertNxtGenMgmtDevices('blrngcs.nxtgen.com', i, 'kvmhost')
        #
        # setCurrData = {(i['h_host'], i['v_identifier']) for i in lAllInOne}
        # setOAAll = {(i[0], i[1])  for i in oaAll}
        # print("Have to set these to inactive in database: {0}".format(setOAAll.difference(setCurrData)))




        print("Result Summary: Success:{0}, Failued:{1}, No Change:{2}".format(s, f, nc))

    except Exception as e:
        print("DB Insertion Exception: {0}".format(str(e)))

if __name__ == "__main__":
    print('=' * 100)
    print("CRON Execute Summary below for {0}".format(dt.now().strftime('%d-%m-%Y %H:%M:%S')))
    stime = time.time()
    sQuery = """
                select 
    	            h.pk_hypervisor_id, h.hypervisor_name, h.hypervisor_ip_address, c.cred_type, c.username, c.password 
                from 
    	            hypervisor_details h inner join ai_device_credentials c on(h.hypervisor_cred=c.cred_id) 
                where 
    	            lower(h.hypervisor_type)='onapp kvm' and h.active_yn='Y' """
    # Testing: and h.hypervisor_ip_address='172.16.64.100'
    dRet = pcon.returnSelectQueryResult(sQuery)
    if dRet["result"] == "success":
        for eachKVM in dRet["data"]:
            try:
                id = eachKVM["pk_hypervisor_id"]
                ip = eachKVM["hypervisor_ip_address"]
                username = eachKVM["username"]
                password = aes.decrypt(eachKVM["password"].encode(), '@ut0!ntell!'.encode()).decode('utf-8')
                print("Discovery for {0} with {1} credentials".format(ip, username))
                ret = discoverKVMs(ip, username, password)
                if ret["result"] == "failure":
                    print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachKVM, ret["data"]))
                    continue
                insertin2DB()
            except Exception as e:
                print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachKVM, str(e)))
    else:
        print("Failed: No Hypervisor found to run the discovery. Code Error:{0}".format(dRet["data"]))
    print("CRON Execute Time :{0}".format(time.time() - stime))

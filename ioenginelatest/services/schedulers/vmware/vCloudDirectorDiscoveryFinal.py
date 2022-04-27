#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================
import requests
import json
import time
from copy import deepcopy
from services.utils import ConnPostgreSQL as pcon
from datetime import datetime as dt

location = ''
try:
    location = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['onapploc']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

dIPFQDN = {'blr-': {'IP': '172.16.112.51', 'FQDN': 'clientportal.nxtgen.com'},
           'amd-': {'IP': '172.29.112.51', 'FQDN': 'clientportal2.nxtgen.com'},
           'fbd-': {'IP': '172.32.112.51', 'FQDN': 'clientportal3.nxtgen.com'},
           'mum-': {'IP': '172.19.112.51', 'FQDN': 'clientportal1.nxtgen.com'}}
sBaseIP = dIPFQDN[location]['IP']
sFQDN = dIPFQDN[location]['FQDN']
sBaseURL = "https://{0}".format(sBaseIP)
vDCType = "application/vnd.vmware.vcloud.vdc+xml"
vAppType = "application/vnd.vmware.vcloud.vApp+xml"
lFromDBCust = {}

def singleQuoteIssue(value):
    if not type(value) == type(None):
        return value.replace("'", "''").strip()
    else:
        return ""

def discoveryCustFromDB():
    try:
        global lFromDBCust
        # Existing customer
        sQuery = "select customer_id, cust_pk_id pk_id from tbl_customer where technology_loc ='vmware' and active_yn='Y'"
        dRet = pcon.returnSelectQueryResultConvert2Col2Dict(sQuery)
        if dRet["result"] == "success":
            lFromDBCust = dRet["data"]
    except Exception as e:
        print("KVM Exception: {0}".format(str(e)))

def createSession(pAuth):
    #Session
    sURL = "{0}/api/sessions".format(sBaseURL)
    sHeader = {"Accept": "application/*+json;version=27.0"}
    ret = requests.post(url=sURL.replace(sFQDN, sBaseIP), auth=pAuth, headers=sHeader, verify=False)
    if ret.status_code != 200:
        raise Exception("Status Code: {0}, Return: {1}".format(ret.status_code, ret.content))

    authorization_key = ret.headers['x-vcloud-authorization']
    sHeader['x-vcloud-authorization'] = authorization_key
    return sHeader

def deleteSession(pAuthHeader, pAuth):
    #Session
    sURL = "{0}/api/sessions".format(sBaseURL)
    sHeader = pAuthHeader
    ret = requests.delete(url=sURL.replace(sFQDN, sBaseIP), auth=pAuth, headers=sHeader, verify=False)
    if ret.status_code != 204:
        raise Exception("Status Code: {0}, Return: {1}".format(ret.status_code, ret.content))

    print("Logged out session:{0} successfully".format(pAuthHeader['x-vcloud-authorization']))

def getOrganisationList(pAuthHeader, pAuth):
    dOrgList = {}
    sURL = "{0}/api/org".format(sBaseURL)
    sHeader = pAuthHeader
    dAuth = pAuth
    ret = requests.get(url=sURL.replace(sFQDN, sBaseIP), auth=dAuth, headers=sHeader, verify=False)
    if ret.status_code != 200:
        raise Exception("Status Code: {0}, Return: {1}".format(ret.status_code, ret.content))

    d = json.loads(ret.content)
    if d.keys().__contains__('org'):
        for eachOrg in d['org']:
            print("{0}\t{1}".format(eachOrg['name'], eachOrg['href']))
            dOrgList[eachOrg['name']] = eachOrg['href']
        return {"result": "success", "data": dOrgList}
    else:
        return {"result": "failure", "data": "none"}

def getOrganisationDetails(pAuthHeader, pAuth, pOrgList):
    lFinalOrg = []
    s = time.time()
    dHeader = pAuthHeader
    tAuth = pAuth
    for eachOrgName in list(pOrgList.keys()): #[0:2]:
        print("Inside Org :{0}, Collecting VDC Details".format(eachOrgName))
        sURL = pOrgList[eachOrgName]
        ret = requests.get(url=sURL.replace(sFQDN, sBaseIP), auth=tAuth, headers=dHeader, verify=False, timeout=120)
        #if ret.status_code != 200:
        #    raise Exception("Status Code: {0}, Return: {1}".format(ret.status_code, ret.content))

        dOut = json.loads(ret.content)
        ret.close()

        dTmp = {}
        dTmp["org_name"] = eachOrgName
        if dOut.keys().__contains__('majorErrorCode'):
            dTmp["result"] = "failed"
            dTmp["error_info"] = {"majorErrorCode": dOut["majorErrorCode"], "minorErrorCode": dOut["minorErrorCode"], "message": dOut["message"]}
        else:
            dTmp["result"] = "success"
            dTmp["fullName"] = dOut["fullName"]
            dTmp["description"] = dOut["description"]

            lTmpvDC = []
            for eachvDC in dOut["link"]:
                if eachvDC["type"] == vDCType:
                    lTmpvDC.append({"name": eachvDC["name"], "link": eachvDC["href"]})
            dTmp["vdc"] = lTmpvDC

        lFinalOrg.append(dTmp)
        del dTmp
    print("Time taken to collect VCD Details is : {0}".format(time.time() - s))
    return lFinalOrg

def getVirtualDataCenterDetails(pAuthHeader, pAuth, pOrgDetail):
    lFinalvDC = []
    dHeader = pAuthHeader
    tAuth = pAuth
    for eachOrganization in pOrgDetail:
        print("Inside Org :{0}".format(eachOrganization["org_name"]))
        dOrg = deepcopy(eachOrganization)
        lvdc = []
        if dOrg.keys().__contains__("vdc"):
            for eachvDC in dOrg["vdc"]:
                sURL = eachvDC["link"]
                print("VDC={0}".format(eachvDC["name"]))
                ret = requests.get(url=sURL.replace(sFQDN, sBaseIP), auth=tAuth, headers=dHeader, verify=False)
                dOut = json.loads(ret.content)

                dTmp = {}
                if dOut.keys().__contains__('majorErrorCode'):
                    dTmp["result"] = "failed"
                    dTmp["error_info"] = {"majorErrorCode": dOut["majorErrorCode"],
                                          "minorErrorCode": dOut["minorErrorCode"], "message": dOut["message"]}
                else:
                    dTmp["result"] = "success"
                    dTmp["name"] = dOut["name"]
                    dTmp["description"] = dOut["description"]
                    dTmp["allocationModel"] = dOut["allocationModel"]

                    lTmpvApp = []
                    for eachvApp in dOut["resourceEntities"]["resourceEntity"]:
                        if eachvApp["type"] == vAppType:
                            lTmpvApp.append({"name": eachvApp["name"], "link": eachvApp["href"]})
                    dTmp["vapp"] = lTmpvApp
                lvdc.append(dTmp)
        dOrg["vdc"] = lvdc
        lFinalvDC.append(dOrg)
    return lFinalvDC

def getvAppAndItsVMDetails(pAuthHeader, pAuth, pOrgDetail):
    lFinalOrganisation = []
    dHeader = pAuthHeader
    tAuth = pAuth
    l, c = len(pOrgDetail), 1
    for eachOrg in pOrgDetail:
        print("{0} out of {1}".format(c, l))
        dOrg = deepcopy(eachOrg)
        lvDCNew = []
        for eachvDC in dOrg["vdc"]:
            if eachvDC["result"] == "success":
                lvAppList, lvAppNew = eachvDC["vapp"], []
                for eachvAapp in lvAppList:
                    sURL = eachvAapp["link"]
                    ret = requests.get(url=sURL.replace(sFQDN, sBaseIP), auth=tAuth, headers=dHeader, verify=False)
                    dOut = json.loads(ret.content)
                    # print("vm details")
                    # print(dOut)

                    dTmp = {}
                    if dOut.keys().__contains__('majorErrorCode'):
                        dTmp["result"] = "failed"
                        dTmp["error_info"] = {"majorErrorCode": dOut["majorErrorCode"],
                                              "minorErrorCode": dOut["minorErrorCode"], "message": dOut["message"]}
                    else:
                        dTmp["result"] = "success"
                        dTmp["name"] = dOut["name"]
                        lVMs = []
                        if not dOut["children"] == None:
                            for eachVM in dOut["children"]["vm"]:
                                dVM = {}
                                dVM["name"] = eachVM["name"]
                                print(eachVM["name"])
                                if eachVM["name"].__contains__("ATA Server 2"):
                                    print(eachVM)
                                dVM["vmid"] = eachVM["id"].split(":")[-1].strip()
                                dVM["vmvCenterRef"] = eachVM["environment"]["otherAttributes"]["{http://www.vmware.com/schema/ovfenv}vCenterId"] if eachVM["environment"] else ''
                                for eachConfig in eachVM["section"]:
                                    if eachConfig["info"]["value"].lower() == "Specifies the operating system installed".lower():
                                        try:
                                            dVM["os"] = eachConfig["description"]["value"]
                                        except Exception as e:
                                            dVM["os"] = ""
                                    if eachConfig["info"]["value"].lower() == "Specifies the available VM network connections".lower():
                                        lEth = []
                                        for eachEth in eachConfig["networkConnection"]:
                                            dSEth = {}
                                            dSEth["network"] = eachEth["network"]
                                            dSEth["networkConnectionIndex"] = eachEth["networkConnectionIndex"]
                                            dSEth["ipAddress"] = eachEth["ipAddress"]
                                            dSEth["networkAdapterType"] = eachEth["networkAdapterType"]
                                            lEth.append(dSEth)
                                        dVM["network"] = lEth
                                lVMs.append(dVM)
                        dTmp["vms"] = lVMs
                    lvAppNew.append(dTmp)
                    del dTmp
                eachvDC["vapp"] = lvAppNew
            lvDCNew.append(eachvDC)
        dOrg["vdc"] = lvDCNew
        lFinalOrganisation.append(dOrg)
    return lFinalOrganisation

tAuth = ("autointelli@system", "cIcr@joxlnA7rLG7R#ra")
dAuthHeader = createSession(pAuth=tAuth)
if not dAuthHeader.keys().__contains__('x-vcloud-authorization'):
    raise Exception("Failed to Login")

dOrgList = getOrganisationList(pAuthHeader=dAuthHeader, pAuth=tAuth)
#print(dOrgList)
if dOrgList["result"] == "failure":
    print("No Organisation retrieved to proceed with inventory")
    exit(0)

lOrgDetailed = getOrganisationDetails(pAuthHeader=dAuthHeader, pAuth=tAuth, pOrgList=dOrgList["data"])
#print(lOrgDetailed)
if len(lOrgDetailed) < 1:
    print("Organisation detailed list retrieval failed")
    exit(0)

lvDCDetails = getVirtualDataCenterDetails(pAuthHeader=dAuthHeader, pAuth=tAuth, pOrgDetail=lOrgDetailed)
#print(lvDCDetails)
if len(lvDCDetails) < 1:
    print("Organisation's vDC detailed list retrieval failed")
    exit(0)

lAllInOne = getvAppAndItsVMDetails(pAuthHeader=dAuthHeader, pAuth=tAuth, pOrgDetail=lvDCDetails)
print('-' * 1000)
print(lAllInOne)

# deleteSession(pAuthHeader=dAuthHeader, pAuth=tAuth) # Receiving method not allowed

open("{0}.txt".format(dt.now().timestamp()), "w").write(json.dumps(lAllInOne))

# Push to tbl_customer table
ddlVCDCustDB = []
sQuery = "select trim(customer_id) customer_id, trim(customer_name) customer_name from tbl_customer where lower(technology_loc)='vmware' and active_yn='Y'"
dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
if dRet['result'] == 'success':
    ddlVCDCustDB = dRet['data'][1:]

iQuery = "insert into tbl_customer(customer_id, customer_name, technology_loc, created_by, created_on, active_yn) values('{0}', '{1}', 'vmware', 'admin', now(), 'Y')"
iN, iM, iNA = 0, 0, 0
sVCDFromDB = set([(i[0], i[1]) for i in ddlVCDCustDB])
lAllInOne = [i for i in lAllInOne if 'fullName' in i]
sVCDFromT = set([(i["org_name"].strip(), i["fullName"].strip()) for i in lAllInOne])
sDiffT = sVCDFromT.difference(sVCDFromDB)
sDiffDB = sVCDFromDB.difference(sVCDFromT)
for i in sDiffT:
    print("New Customer: {0}".format(i))
    iQ = iQuery.format(singleQuoteIssue(i[0]), singleQuoteIssue(i[1]))
    print('insert into customer: {0}'.format(iQ))
    ret = pcon.returnInsertResult(iQ)
    if ret["result"] == "success":
        iN += 1
iQuery = "update tbl_customer set active_yn='N' where customer_id='{0}' and customer_name='{1}'"
for i in sDiffDB:
    print("Missing Customer(Available in DB, Not in VCD): {0}".format(i))
    iQ = iQuery.format(singleQuoteIssue(i[0]), singleQuoteIssue(i[1]))
    print("customer missing so in-active: {0}".format(iQ))
    iRet = pcon.returnInsertResult(iQ)
    if iRet['result'] == 'success':
        iNA += 1
    iM += 1
    # Add Remarks Column in tbl_customer and update the same column
print("OverAll Summary. New Customers found:{0}, Missing Customers from VCD API:{1}, Inactivate: {2}".format(iN, iM, iNA))

# Refresh the customer records
discoveryCustFromDB()

ddlVCD = []
sQuery = "select trim(customer_id) customer_id, trim(vdc_name) vdc_name, trim(vapp_name) vapp_name, trim(vm_id) vm_id, trim(vm_vcenter_ref) vm_vcenter_ref from vcloud_object_inventory where active_yn='Y'"
dRet = pcon.returnSelectQueryResultAs2DList(sQuery)
if dRet['result'] == 'success':
    ddlVCD = dRet['data'][1:]

ddlVCDWORef = dict([(tuple(i[:-1]), i[-1]) for i in ddlVCD])

#customer_id    customer_name       vm_id       vm_name     hostname     vm_os              nic_count       nic
#Org Name       Org Full Name       VM ID       VM Name                  VM OS              NIC Count       VM IP
#Customer ID    Customer Name       Identifier  VMName      Hostname     Operating System   NIC Count       IP Addrs
#print("Org Name, Org Full Name, Org Desc, vDC Name, vDC Desc, vDC AllocModel, vApp Name, VM ID, VM Name, VM OS, NIC Count, VM IP")

lTransactionDetails = []
out = "Org Name;; Org Full Name;; Org Desc;; vDC Name;; vDC Desc;; vDC AllocModel;; vApp Name;; VM ID;; VM Name;; VM OS;; NIC Count;; VM vCenter Ref;; VM IP"
iQueryvCD = """insert into vcloud_object_inventory(customer_id, customer_name, customer_desc, vdc_name, vdc_desc, vdc_alloc_model, vapp_name, vm_id, vm_vcenter_ref, vm_name, vm_os, nic_count, vm_ip, active_yn) values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', {11},'{12}', 'Y')"""
s, f, nc, ref = 0, 0, 0, 0
for eachOrg in lAllInOne:
    if eachOrg["result"] == "failed":
        continue
    name = singleQuoteIssue(eachOrg["org_name"])
    full_name = singleQuoteIssue(eachOrg["fullName"])
    description = singleQuoteIssue(eachOrg["description"])
    for eachvdc in eachOrg["vdc"]:
        vdcname = singleQuoteIssue(eachvdc["name"])
        vdcallocationModel = singleQuoteIssue(eachvdc["allocationModel"])
        vdcdescription = singleQuoteIssue(eachvdc["description"])
        for eachvapp in eachvdc["vapp"]:
            vappname = singleQuoteIssue(eachvapp["name"])
            for eachvm in eachvapp["vms"]:
                vmname = singleQuoteIssue(eachvm["name"])
                vmid = singleQuoteIssue(eachvm["vmid"])
                vmos = singleQuoteIssue(eachvm["os"])
                vmref = singleQuoteIssue(eachvm["vmvCenterRef"])
                lTransactionDetails.append((name, vdcname, vappname, vmid))
                lip = []
                for eachip in eachvm["network"]:
                    ip = "{0} {1} {2} {3}".format(eachip["networkConnectionIndex"], eachip["network"], eachip["networkAdapterType"], eachip["ipAddress"])
                    lip.append(ip)
                out += "{0};; {1};; {2};; {3};; {4};; {5};; {6};; {7};; {8};; {9};; {10};; {11};; {12} \n".format(name, full_name, description, vdcname, vdcdescription,
                                                                                    vdcallocationModel, vappname, vmid, vmname, vmos, len(lip), vmref, " | ".join(lip))
                _ref = ''
                try:
                    _ref = ddlVCDWORef[(name, vdcname, vappname, vmid)]
                except Exception as e:
                    pass

                # If new object identified in vCD which not in DB, add in vcloud_object_inventory, update customer details in tbl_vms
                if not (name, vdcname, vappname, vmid) in ddlVCDWORef:
                    print("yes change: {0}".format([name, vdcname, vappname, vmid]))
                    query = iQueryvCD.format(name, full_name, description, vdcname, vdcdescription,
                                                                                    vdcallocationModel, vappname, vmid, vmref, vmname, vmos, len(lip), " | ".join(lip))
                    print("insert into vcloud: {0}".format(query))
                    dRet = pcon.returnInsertResult(query)
                    if dRet["result"] == "success":
                        s += 1
                    else:
                        f += 1
                    if vmref.strip() != '':
                        sQueryUVM = "update tbl_vms set customer_id='{0}' where reference='{1}'".format(name, vmref)
                        print("update vms: {0}".format(sQueryUVM))
                        ddRet = pcon.returnInsertResult(sQueryUVM)
                    else:
                        # If new object is in powered off which inventory gathering, it doesn't update the customer details in tbl_vms
                        iQuerySVM = "select * from tbl_vms where device_type ='esxivm' and lower(vm_name) like lower('{0}%') and (length(vm_name)=length('{1}')+5 or lower(vm_name)=lower('{2}'))".format(
                            vmname, vmname, vmname
                        )
                        dRet = pcon.returnSelectQueryResult(iQuerySVM)
                        if dRet['result'] == 'success':
                            if len(dRet['data']) == 1:
                                iUQueryUVM1 = "update tbl_vms set customer_id='{0}' where vm_pk_id={1} RETURNING reference".format(
                                    name, dRet['data'][0]['vm_pk_id']
                                )
                                iURet = pcon.returnSelectQueryResultWithCommit(iUQueryUVM1)
                                if iURet['result'] == 'success':
                                    print("Updated customer without reference and with vm name : {0}".format(vmname))
                                    iUref = iURet['data'][0]['reference']
                                    vmref = iUref
                                    iUvCDQuery = "update vcloud_object_inventory set vm_vcenter_ref='{0}' where customer_id='{1}' and vdc_name='{2}' and vapp_name='{3}' and vm_name='{4}'".format(
                                        iUref, name, vdcname, vappname, vmname
                                    )
                                    iUvCDRet = pcon.returnInsertResult(iUvCDQuery)
                                    if iUvCDRet['result'] == 'success':
                                        print(
                                            "Updated reference that is picked from tbl_vms <- from vcenter_object_inventroy. ref:{0}".format(
                                                iUref))
                                    else:
                                        print("Updating reference in vcloud_object_inventory failed ref:{0}".format(
                                            iUref))
                                else:
                                    print("Failed to update customer with VM Name. Error: {0}".format(iURet['data']))
                            elif len(dRet['data']) > 1:
                                print("Tried to update customer with VM Name multiple output: {0}".format(dRet['data']))
                        else:
                            print("Tried to update customer with VM Name match failed: Query: {0}".format(iQuerySVM))
                # First time object is powered off, then powered on, in such case update the reference in vcloud_object_inventory and tbl_vms
                elif ((name, vdcname, vappname, vmid) in ddlVCDWORef) and vmref != '' and (_ref == '' or _ref == None):
                    sQueryUvCD = "update vcloud_object_inventory set vm_vcenter_ref='{0}' where vmid='{1}'".format(vmref, vmid)
                    print("update vcloud: {0}".format(sQueryUvCD))
                    ddRet = pcon.returnInsertResult(sQueryUvCD)
                    sQueryUVM1 = "update tbl_vms set customer_id='{0}' where reference='{1}'".format(name, vmref)
                    print("update vms: {0}".format(sQueryUVM1))
                    ddRet = pcon.returnInsertResult(sQueryUVM1)
                    ref += 1
                # Even if there is no reference in vcloud_object_inventory, we match with vm name and pick ref from tbl_vms and update in vcloud_object_inventory
                elif ((name, vdcname, vappname, vmid) in ddlVCDWORef) and vmref == '' and (_ref == '' or _ref == None):
                    iQuerySVM1 = "select * from tbl_vms where device_type ='esxivm' and lower(vm_name) like lower('{0}%') and (length(vm_name)=length('{1}')+5 or lower(vm_name)=lower('{2}'))".format(
                        vmname, vmname, vmname
                    )
                    dRet = pcon.returnSelectQueryResult(iQuerySVM1)
                    if dRet['result'] == 'success':
                        if len(dRet['data']) == 1:
                            iUQueryUVM2 = "update tbl_vms set customer_id='{0}' where vm_pk_id={1} RETURNING reference".format(
                                name, dRet['data'][0]['vm_pk_id']
                            )
                            iURet = pcon.returnSelectQueryResultWithCommit(iUQueryUVM2)
                            if iURet['result'] == 'success':
                                print("Updated customer without reference and with vm name : {0}".format(vmname))
                                iUref = iURet['data'][0]['reference']
                                vmref = iUref
                                iUvCDQuery1 = "update vcloud_object_inventory set vm_vcenter_ref='{0}' where customer_id='{1}' and vdc_name='{2}' and vapp_name='{3}' and vm_name='{4}'".format(
                                    iUref, name, vdcname, vappname, vmname
                                )
                                iUvCDRet = pcon.returnInsertResult(iUvCDQuery1)
                                if iUvCDRet['result'] == 'success':
                                    print("Updated reference that is picked from tbl_vms <- from vcenter_object_inventroy. ref:{0}".format(iUref))
                                else:
                                    print("Updating reference in vcloud_object_inventory failed ref:{0}".format(iUref))
                            else:
                                print("Failed to update customer with VM Name. Error: {0}".format(iURet['data']))
                        elif len(dRet['data']) > 1:
                            print("Tried to update customer with VM Name multiple output: {0}".format(dRet['data']))
                    else:
                        print("Tried to update customer with VM Name match failed: Query: {0}".format(iQuerySVM1))
                # No Change
                else:
                    print("no change: {0}".format([name, vdcname, vappname, vmid]))
                    nc += 1
                # Update Interface Details
                if vmref != "":
                    uIPQuery = "update tbl_vms set vm_ip='{0}' where techno='vmware' and device_type='esxivm' and reference='{1}'".format(
                        " | ".join(lip), vmref
                    )
                    uIPRet = pcon.returnInsertResult(uIPQuery)
                    if uIPRet['result'] == 'success':
                        print("IP updated for ref:{0}".format(vmref))
                    else:
                        print("IP Updation failed for ref:{0}".format(vmref))
print("DML Summary: Success:{0}, Failure:{1}, No Change:{2}".format(s, f, nc))

print("Remove Customers that are inactive from Database")
setCustomer = set(ddlVCDWORef.keys())
setTran = set(lTransactionDetails)
setInactiveCusts = setCustomer.difference(setTran)
for i in setInactiveCusts:
    iQueryUvCD = "update vcloud_object_inventory set active_yn='N' where customer_id='{0}' and vdc_name='{1}' and vapp_name='{2}' and vm_id='{3}'".format(
        i[0], i[1], i[2], i[3]
    )
    dRet = pcon.returnInsertResult(iQueryUvCD)
    if dRet['result'] == 'success':
        print("VM: {0} inactivated".format(i[3]))
    else:
        print("VM: {0} Inactivation failed".format(i[3]))

#name
#children, vm[]
#            name, section[{}, {}],
#                            info,value:Specifies the operating system installed
#                                description, value => os
#                            info, value:Specifies the available VM network connections
#                                networkConnection[]
#                                    network, networkConnectionIndex, ipAddress, networkAdapterType, => network
#                            #info, value:Specifies Guest OS Customization Settings
#                            #        computerName =>hostname
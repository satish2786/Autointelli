#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================
import requests
import json
from services.utils import ConnPostgreSQL as pcon

location = ''
try:
    location = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['onapploc']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

dIPFQDN = {'blr-': {'IP': '172.16.112.51', 'FQDN': 'clientportal.nxtgen.com'},
           'amd-': {'IP': '172.29.112.51', 'FQDN': 'clientportal2.nxtgen.com'},
           'fbd-': {'IP': '172.32.112.51', 'FQDN': 'clientportal3.nxtgen.com'}}
sBaseIP = dIPFQDN[location]['IP']
sFQDN = dIPFQDN[location]['FQDN']
sBaseURL = "https://{0}".format(sBaseIP)
vDCType = "application/vnd.vmware.vcloud.vdc+xml"
vAppType = "application/vnd.vmware.vcloud.vApp+xml"

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

def getNSXEdge4Organisations(pAuthHeader, pAuth):
    dEdgeList = []
    sURL = "{0}/network/edges".format(sBaseURL)
    sHeader = pAuthHeader
    dAuth = pAuth
    ret = requests.get(url=sURL.replace(sFQDN, sBaseIP), auth=dAuth, headers=sHeader, verify=False)
    if ret.status_code != 200:
        raise Exception("Status Code: {0}, Return: {1}".format(ret.status_code, ret.content))

    d = json.loads(ret.content)
    if d.keys().__contains__('edgePage'):
        for eachEdge in d['edgePage']["data"]:
            print("{0}\t{1}\t{2}".format(eachEdge["objectId"], eachEdge["name"], eachEdge["datacenterName"]))
            dEdgeList.append({"object_id": eachEdge["objectId"], "id": eachEdge["id"], "name": eachEdge["name"], "dcname": eachEdge["datacenterName"]})
        return {"result": "success", "data": dEdgeList}
    else:
        return {"result": "failure", "data": "no data"}

tAuth = ("autointelli@system", "cIcr@joxlnA7rLG7R#ra")
dAuthHeader = createSession(pAuth=tAuth)
if not dAuthHeader.keys().__contains__('x-vcloud-authorization'):
    raise Exception("Failed to Login")

dRetList = getNSXEdge4Organisations(pAuthHeader=dAuthHeader, pAuth=tAuth)
print(dRetList)
if dRetList["result"] == "failure":
    print("No Organisation retrieved to proceed with inventory")
    exit(0)

s, f, nc, eList = 0, 0, 0, []
sQuery = "select edge_id from vnsx_edge_discovery where active_yn='Y'"
dRet = pcon.returnSelectQueryResultAsList(sQuery)
if dRet["result"] == "success":
    eList = dRet["data"]["edge_id"]
iQuery = "insert into vnsx_edge_discovery(edge_id, edge_object_id, edge_name, edge_dc_name, active_yn) values('{0}', '{1}', '{2}', '{3}', '{4}')"
# for i in dRetList["data"]:
#     print(i['id'], i['object_id'], i['name'], i['dcname'])
for i in dRetList["data"]:
    if not i['id'] in eList:
        query = iQuery.format(i['id'], i['object_id'], i['name'], i['dcname'], 'Y')
        dRet = pcon.returnInsertResult(query)
        if dRet["result"] == "success":
            s += 1
        else:
            f += 1
    else:
        nc += 1
print("Final Summary: success:{0}, failure:{1}, no change:{2}".format(s, f, nc))



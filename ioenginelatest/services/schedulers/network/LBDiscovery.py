#============================================================================================
# Author        : Dinesh Balaraman
# Created On    :
# (c) Copyright by Autointelli Technologies
#============================================================================================
import services.utils.ConnPostgreSQL as pcon
import services.utils.ED_AES256 as aes
from datetime import datetime as dt
from pysnmp.hlapi import *
import time

def singleQuoteIssue(value):
    return value.replace("'", "''").strip()

def discoverFirewallInterfaces(ip, comm_string):
    try:
        finalIFs = []
        t = dt.utcnow()
        timestamp = t.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        epoch = time.mktime(t.timetuple()) + t.microsecond / 1e6

        HOSTNAME = ip
        COMMUNITY = comm_string

        for _, _, _, varBinds in nextCmd(
                SnmpEngine(),
                CommunityData(COMMUNITY, mpModel=0),
                UdpTransportTarget((HOSTNAME, 161)),
                ContextData(),
                ObjectType(ObjectIdentity('IF-MIB', 'ifIndex')),
                ObjectType(ObjectIdentity('IF-MIB', 'ifName')),
                ObjectType(ObjectIdentity('IF-MIB', 'ifOperStatus')),
                ObjectType(ObjectIdentity('IF-MIB', 'ifSpeed')),
                lexicographicMode=False):
            index, name, status, speed = varBinds  # unpack the list of resolved objectTypes
            iface_index = index[1].prettyPrint()
            iface_name = name[1].prettyPrint()  # access the objectSyntax and get its human-readable form
            iface_status = status[1].prettyPrint()
            iface_speed = speed[1].prettyPrint()

            if (iface_status == 'up') and (iface_speed != "0"):
                finalIFs.append([iface_index, iface_name])
                # qData = "{hostname}#@#{interface}#@#{community}#@#'{desc}'#@#{speed}#@#{status}#@#{timestamp}#@#{epoch}".format(
                #     hostname=HOSTNAME, interface=iface_index, community=COMMUNITY, desc=iface_name, speed=iface_speed,
                #     status=iface_status, timestamp=timestamp, epoch=epoch)
                # print(qData)
        if len(finalIFs) > 0:
            return {'result': 'success', 'data': finalIFs}
        else:
            return {'result': 'failure', 'data': 'no data'}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}


def insertin2DB(id, ip, ints):
    try:
        # Pull Existing
        sExist = {}
        sQuery = "select lb_ip, int_id, int_name from lb_object_inventory where lb_ip='{0}' and active_yn='Y'".format(ip)
        sRet = pcon.returnSelectQueryResultAs2DList(sQuery)
        if sRet['result'] == 'success':
            sExist = set([tuple(i) for i in sRet['data'][1:]])

        iQuery = "insert into lb_object_inventory(fk_hypervisor_id, lb_ip, int_id, int_name, created_date, created_by, active_yn) " \
                 "values({0}, '{1}', '{2}', '{3}', 'now()', 'admin', 'Y')"
        s, f, nc = 0, 0, 0
        for i in ints:
            _id = i[0]
            _name = singleQuoteIssue(i[1])
            if not (ip, _id, _name) in sExist:
                q = iQuery.format(id, ip, _id, _name)
                iRet = pcon.returnInsertResult(q)
                if iRet['result'] == 'success':
                    s += 1
                else:
                    f += 1
            else:
                nc += 1
        return {'result': 'success', 'data': {'transaction': {'success': s, 'failure': f, 'no change': nc}}}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

if __name__ == "__main__":
    try:
        print('=' * 100)
        print("CRON Execute Summary below for {0}".format(dt.now().strftime('%d-%m-%Y %H:%M:%S')))
        stime = time.time()
        sQuery = """
                        select 
            	            h.pk_hypervisor_id, h.hypervisor_name, h.hypervisor_ip_address, c.cred_type, c.username, c.password 
                        from 
            	            hypervisor_details h inner join ai_device_credentials c on(h.hypervisor_cred=c.cred_id) 
                        where 
            	            lower(trim(h.hypervisor_type))='load balancer' and h.active_yn='Y' """
        # Testing: and h.hypervisor_ip_address='172.16.64.100'
        dRet = pcon.returnSelectQueryResult(sQuery)
        if dRet["result"] == "success":
            for eachKVM in dRet["data"]:
                try:
                    id = eachKVM["pk_hypervisor_id"]
                    ip = eachKVM["hypervisor_ip_address"]
                    username = eachKVM["username"]
                    comm_string = aes.decrypt(eachKVM["password"].encode(), '@ut0!ntell!'.encode()).decode('utf-8')
                    print("Discovery for {0} with {1} credentials".format(ip, username))
                    ret = discoverFirewallInterfaces(ip, comm_string)
                    if ret["result"] == "failure":
                        print(
                            "Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachKVM, ret["data"]))
                        continue
                    dResultSumm = insertin2DB(id, ip, ret['data'])
                    print(dResultSumm)
                except Exception as e:
                    print("Failed: Discovery failed for hypervisor:{0}, Code Error:{1}".format(eachKVM, str(e)))
        else:
            print("Failed: No Hypervisor found to run the discovery. Code Error:{0}".format(dRet["data"]))
        print("CRON Execute Time :{0}".format(time.time() - stime))
    except Exception as e:
        print("Exception: {0}".format(str(e)))

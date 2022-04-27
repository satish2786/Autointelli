from services.utils import ConnPostgreSQL as pcon
from services.utils import ConnMaria as mar

# Push Hosts
print("Migrate Hosts")
hgSQL = "select alias hostgroupname from nagios_hostgroups"
hgret = mar.returnSelectQueryResult(hgSQL)
if hgret["result"] == "success":
    hgPSQL = "insert into mon_hostgroups(hostgroup_name, hostgroup_desc, instance_id, active_yn) values('{0}', '{1}', '10.239.45.205', 'Y')"
    for i in hgret["data"]:
        hgPFinal = hgPSQL.format(i["hostgroupname"], i["hostgroupname"])
        iRet = pcon.returnInsertResult(hgPFinal)
        if iRet["result"] == "success":
            print("+ HostGroup: {0}, Post".format(i["hostgroupname"]))
        else:
            print("x HostGroup: {0}, Post".format(i["hostgroupname"]))

print("Migrate Hosts")
hSQL = """select A.hostgroup_name, A.host_name, A.host_description, A.host_display_name, A.host_address from (
select 
	hosts.host_object_id, hosts.host_id, hosts.name host_name, hosts.description host_description, hosts.display_name host_display_name, hosts.address host_address, hostgroups.hostgroup_object_id, hostgroups.hostgroup_id, hostgroups.name hostgroup_name, hostgroups.description hostgroup_description 
from 
	(select o.object_id host_object_id, h.host_id, o.name1 name, h.alias description, h.display_name, h.address from nagios_objects o inner join nagios_hosts h on(o.object_id=h.host_object_id) where o.is_active=1) hosts
	inner join nagios_hostgroup_members hgm on (hgm.host_object_id=hosts.host_object_id)
	inner join (select object_id hostgroup_object_id, hostgroup_id, name1 name, alias description from nagios_objects inner join nagios_hostgroups on(nagios_objects.object_id=nagios_hostgroups.hostgroup_object_id) where nagios_objects.is_active=1) hostgroups on(hgm.hostgroup_id=hostgroups.hostgroup_id)   ) A
where A.hostgroup_name in('{0}')"""
hPHGSQL = "select pk_hostgroup_id hgid, hostgroup_name from mon_hostgroups where active_yn='Y'"
dRet = pcon.returnSelectQueryResult(hPHGSQL)
if dRet["result"] == "success":
    for i in dRet["data"]:
        idd = i["hgid"]
        sTmp = hSQL.format(i["hostgroup_name"])
        ddRet = mar.returnSelectQueryResult(sTmp)
        if ddRet["result"] == "success":
            iPHQuery = "insert into mon_hosts(hostname, address, downtime_yn, created_by, created_on, fk_hostgroup_id, active_yn) values('{0}', '{1}', 'N', 'administrator', now(), {2}, 'Y')".format(
                i["host_name"], i["host_address"], idd
            )
            iPHRet = pcon.returnInsertResult(iPHQuery)
            if iPHRet["result"] == "success":
                print("+ Host: {0}, Post".format(i["host_name"]))
            else:
                print("- Host: {0}, Post".format(i["host_name"]))
        else:
            print("- Host for HostGroup, Maria")
else:
    print("- HostGroup List, Post")


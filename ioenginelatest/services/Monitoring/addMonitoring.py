import sys, os, json, logging, psycopg2
from services.utils.decoder import decode
from logging.handlers import TimedRotatingFileHandler
from celery import Celery
from services.utils.utils import monitoringNameConvert
from services.utils import ConnPostgreSQL


# Reading the configuration file for db connection string
conn = ""
data = json.load(open('/etc/autointelli/autointelli.conf'))
if not os.path.isfile('/etc/autointelli/autointelli.conf'):
  print(" [x] Worker Cannot Start, Config not found")
  sys.exit(1)
dbuser = data['maindb']['username']
dbname = data['maindb']['dbname']
dbhost = data['maindb']['dbip']
dbport = data['maindb']['dbport']

# Decoding the Password
maindbpassword = decode('auto!ntell!',data['maindb']['password'])

# Adding the Logging Configurations
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
handler = TimedRotatingFileHandler('/var/log/autointelli/monitoringAutomation.log', when='midnight', interval=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Get MQ Connections
conn = psycopg2.connect(database=dbname, user=dbuser, password=maindbpassword, host=dbhost, port=dbport)
conn.autocommit = True
cur = conn.cursor()
cur.execute('select configip,configport,dbname,username,password from configuration where configname=\'MQ\'')
esbdata = cur.fetchall()
esbdata = esbdata[0]
esbip = esbdata[0]
esbuser = esbdata[3]
esbpass = esbdata[4]
vhost = esbdata[2]
esbpass = decode('auto!ntell!',esbpass)


# Create the app and set the broker location (RabbitMQ)
app = Celery('addMonitoring',
             broker='pyamqp://{0}:{1}@{2}/{3}'.format(esbuser, esbpass, esbip, "monitoring"),
             backend = 'db+postgresql://{0}:{1}@{2}:{3}/{4}'.format(dbuser, maindbpassword, dbhost, dbport, dbname),
             result_persistent = True)

@app.task
def addesxiCluster(hypervisorip, vmname):
  try:
    #Hostgroup Functionality
    hostGrpDirectory="/usr/local/nagios/etc/objects/hostgroups/ESXCLUSTERS/{0}".format(hypervisorip)
    isDir = os.path.isdir(hostGrpDirectory)
    if not isDir:
      os.makedirs(hostGrpDirectory)
      hostgroupvar="""define hostgroup{{
        hostgroup_name  ESX CLUSTER {0} ; The name of the hostgroup
        alias           ESX CLUSTER {0} ; Long name of the group
        }}""".format(hypervisorip)
      FH = open('{1}/Cluster_{0}.cfg'.format(hypervisorip,hostGrpDirectory), 'w')
      FH.write(hostgroupvar)
      FH.close()

    hostDirectory="/usr/local/nagios/etc/objects/servers/ESXCLUSTERS/{0}".format(hypervisorip)
    isDir = os.path.isdir(hostDirectory)
    if not isDir:
      os.makedirs(hostDirectory)
    vmname_modified = monitoringNameConvert(vmname)
    output = ""
    vmname_modified = output.join(vmname_modified)
    hostvar = """
    define host{{
        use                     linux-server            ; Name of host template to use
        host_name               {1}
        alias                   {1}
        address                 {2}
        _host_component         ESX CLUSTER
        hostgroups              ESX CLUSTER {2}
        contact_groups          admins
        }}
   
    define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Cluster Resource Information - {1}
        _service_component              ESX CLUSTER INFO
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Cluster_Resource_Info --cluster "{1}"'
        }}

    define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Cluster CPU Usage - {1}
        _service_component              ESX CLUSTER CPU
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Cluster_CPU_Usage --cluster "{1}" --warning cpu_free%:30 --critical cpu_free%:15'
        }}

    define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Cluster Memory Usage - {1}
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Cluster_Memory_Usage --cluster "{1}" --warning warning_free%:30 --critical memory_free%:15'
        _service_component              ESX CLUSTER MEMORY
        }}    

    define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Cluster Time Drift - {1}
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Cluster_Time_Drift --cluster "{1}" --warning time_drift:1500 --critical time_drift:3000'
        }}""".format(vmname_modified,vmname, hypervisorip)
    FH = open('{1}/{0}.cfg'.format(vmname,hostDirectory), 'w')
    FH.write(hostvar)
    FH.close()
    Query="""update vcenter_object_inventory set obj_remark='' where object_name='{0}' and object_type='cluster' and fk_hypervisor_id=(select pk_hypervisor_id from hypervisor_details  where hypervisor_ip_address='{1}')""".format(vmname,hypervisorip)
    retESBResult = ConnPostgreSQL.returnInsertResult(Query)
  except Exception as e:
    logger.error(str(e))
    return False

@app.task
def addesxiHost(hypervisorip, vmname):
  try:
    #Hostgroup Functionality
    hostGrpDirectory="/usr/local/nagios/etc/objects/hostgroups/ESXHOSTS/{0}".format(hypervisorip)
    isDir = os.path.isdir(hostGrpDirectory)
    if not isDir:
      os.makedirs(hostGrpDirectory)
      hostgroupvar="""define hostgroup{{
        hostgroup_name  ESX HOST {0} ; The name of the hostgroup
        alias           ESX HOST {0} ; Long name of the group
        }}""".format(hypervisorip)
      FH = open('{1}/ESXHOST_{0}.cfg'.format(hypervisorip,hostGrpDirectory), 'w')
      FH.write(hostgroupvar)
      FH.close()

    hostDirectory="/usr/local/nagios/etc/objects/servers/ESXHOSTS/{0}".format(hypervisorip)
    isDir = os.path.isdir(hostDirectory)
    if not isDir:
      os.makedirs(hostDirectory)
    vmname_modified = monitoringNameConvert(vmname)
    output = ""
    vmname_modified = output.join(vmname_modified)
    hostvar = """
      define host{{
        use                     generic-server
        host_name               {1}
        alias                   {1}
        address                 {2}
        _host_component         ESX HOST
        hostgroups              ESX HOST {2}
        contact_groups		admins
        }}
  
  define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             ESX HOST CPU Usage
        _service_component              ESX HOST CPU
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Host_CPU_Usage --host "{1}" --perfdata_option CPU_Free:1,CPU_Free%:1,CPU_Total:1,CPU_Used:1,CPU_Used%:1 --warning cpu_free%:25 --critical cpu_free%:15'
        }}

  define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Host Uptime
        _service_component              ESX Uptime
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Host_Up_Down_State --host "{1}"'
        }}

  define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Host License Status
        _service_component              ESX Host License
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Host_License_Status --host "{1}"'
        }}

  define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             Memory Usage
          _service_component              ESX Memory
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Host_Memory_Usage --host "{1}" --perfdata_option Memory_Free:1,Memory_Free%:1,Memory_Total:1,Memory_Used:1,Memory_Used%:1 --warning memory_free%:25 --critical memory_free%:15' 
          }}
  
  define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             Host pNIC Status
          _service_component              ESX pNIC
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Host_pNIC_Status --host "{1}"'
          }}
  
  define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             Overall Host Status
          _service_component              ESX Status
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Host_Status --host "{1}"'
          }}
  
  define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Host Switch Status
        _service_component              ESX Switch
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Host_Switch_Status --host "{1}"'
        }}

  define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Host vNIC Status
        _service_component              ESX vNIC
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Host_vNIC_Status --host "{1}"'
        }}""".format(vmname_modified,vmname, hypervisorip)
    FH = open('{1}/{0}.cfg'.format(vmname,hostDirectory), 'w')
    FH.write(hostvar)
    FH.close()
    Query="""update vcenter_object_inventory set obj_remark='' where object_name='{0}' and object_type='esxihost' and fk_hypervisor_id=(select pk_hypervisor_id from hypervisor_details  where hypervisor_ip_address='{1}')""".format(vmname,hypervisorip)
    retESBResult = ConnPostgreSQL.returnInsertResult(Query)
  except Exception as e:
    logger.error(str(e))
    return False


@app.task
def addesxiDatastore(hypervisorip, vmname):
  try:
    #Hostgroup Functionality
    hostGrpDirectory="/usr/local/nagios/etc/objects/hostgroups/ESXCLUSTERS/{0}".format(hypervisorip)
    isDir = os.path.isdir(hostGrpDirectory)
    if not isDir:
      os.makedirs(hostGrpDirectory)
      hostgroupvar="""define hostgroup{{
        hostgroup_name  ESX DATASTORE {0} ; The name of the hostgroup
        alias           ESX DATASTORE {0} ; Long name of the group
        }}""".format(hypervisorip)
      FH = open('{1}/Datastore_{0}.cfg'.format(hypervisorip,hostGrpDirectory), 'w')
      FH.write(hostgroupvar)
      FH.close()

    hostDirectory="/usr/local/nagios/etc/objects/servers/ESXDATASTORES/{0}".format(hypervisorip)
    isDir = os.path.isdir(hostDirectory)
    if not isDir:
      os.makedirs(hostDirectory)
    vmname_modified = monitoringNameConvert(vmname)
    output = ""
    vmname_modified = output.join(vmname_modified)
    hostvar = """
    define host{{
        use                     linux-server            ; Name of host template to use
        host_name               {1}
        alias                   {1}
        address                 {2}
        _host_component         ESX DATASTORE
        hostgroups              ESX DATASTORE {2}
        contact_groups          admins
        }}

    define service{{
        use                             generic-service         ; Name of service template to use
        host_name                       {1}
        service_description             Datastore Usage
        check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Datastore_Usage --name "{1}" --perfdata_option Datastore_Capacity:1,Datastore_Free:1,Datastore_Free%:1,Datastore_Used:1,Datastore_Used%:1 --warning datastore_free%:25 --critical datastore_free%:25'
        }}""".format(vmname_modified,vmname, hypervisorip)
    FH = open('{1}/{0}.cfg'.format(vmname,hostDirectory), 'w')
    FH.write(hostvar)
    FH.close()
    Query="""update vcenter_object_inventory set obj_remark='' where object_name='{0}' and object_type='datastore' and fk_hypervisor_id=(select pk_hypervisor_id from hypervisor_details  where hypervisor_ip_address='{1}')""".format(vmname,hypervisorip)
    retESBResult = ConnPostgreSQL.returnInsertResult(Query)
  except Exception as e:
    logger.error(str(e))
    return False



@app.task
def addesxiVirtualMachine(hypervisorip, vmname):
  try:
    #Hostgroup Functionality
    hostGrpDirectory="/usr/local/nagios/etc/objects/hostgroups/ESXVMS/{0}".format(hypervisorip)
    isDir = os.path.isdir(hostGrpDirectory)
    if not isDir:
      os.makedirs(hostGrpDirectory)
      hostgroupvar="""define hostgroup{{
        hostgroup_name  ESX VMS {0} ; The name of the hostgroup
        alias           ESX VMS {0} ; Long name of the group
        }}""".format(hypervisorip)
      FH = open('{1}/ESXVMS_{0}.cfg'.format(hypervisorip,hostGrpDirectory), 'w')
      FH.write(hostgroupvar)
      FH.close()
   
    hostDirectory="/usr/local/nagios/etc/objects/servers/ESXVMS/{0}".format(hypervisorip)
    isDir = os.path.isdir(hostDirectory)
    if not isDir:
      os.makedirs(hostDirectory)
    vmname_modified = monitoringNameConvert(vmname)
    output = ""
    vmname_modified = output.join(vmname_modified)
    hostvar = """
    define host{{
          use                     generic-server
          host_name               {1}
          alias                   {1}
          address                 {2}
          _host_component         ESX VM
          hostgroups              ESX VMS {2}
          contact_groups	  admins
          }}
    
    define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             ESX VM CPU Usage
          _service_component              ESX VM CPU
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Guest_CPU_Usage --guest "{1}" --perfdata_option CPU_Free:1,CPU_Free%:1,CPU_Used:1,CPU_Used%:1,CPU_Available:1,CPU_Ready_Time:1 --warning cpu_free%:25' 
          }}
    
    define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             ESX VM Disk Usage
          _service_component              ESX VM DISK
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Guest_Disk_Usage --guest "{1}" --perfdata_option Disk_Capacity:1,Disk_Free:1,Disk_Free%:1,Disk_Size_On_Datastore:1,Disk_Snapshot_Space:1,Disk_Suspend_File:1,Disk_Swap_File:1,Disk_Swap_Userworld:1,Disk_Usage:1 --warning disk_free%:25 --critical disk_free%:15'
          }}

    define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             ESX VM Memory Usage
          _service_component              ESX VM MEMORY
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Guest_Memory_Usage --guest "{1}" --perfdata_option Memory_Active:1,Memory_Ballooned:1,Memory_Consumed:1,Memory_Consumed%:1,Memory_Free:1,Memory_Free%:1,Memory_Overhead:1,Memory_Shared:1,Memory_Swap:1,Memory_Total:1 --critical memory_free%:15 --warning memory_free%:25'
          }}

    define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             ESX VM NIC Usage
          _service_component              ESX VM NIC
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Guest_NIC_Usage --guest "{1}"'
          }}

    define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             ESX VM Snapshot 
          _service_component              ESX VM SNAPSHOT  
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Guest_Snapshot --guest "{1}"'
          }}

    define service{{
          use                             generic-service         ; Name of service template to use
          host_name                       {1}
          service_description             ESX VM Status
          _service_component              ESX VM STATUS  
          check_command                   check_vmware!-t NxtG3n -M 'plugins/box293_check_vmware.pl' -a '--concurrent_checks 700 --server {2} --check Guest_Status --guest "{1}"'
          }}""".format(vmname_modified,vmname, hypervisorip)
    FH = open('{1}/{0}.cfg'.format(vmname,hostDirectory), 'w')
    FH.write(hostvar)
    FH.close()
    Query="""update vcenter_object_inventory set obj_remark='' where object_name='{0}' and object_type='esxivm' and fk_hypervisor_id=(select pk_hypervisor_id from hypervisor_details  where hypervisor_ip_address='{1}')""".format(vmname,hypervisorip)
    retESBResult = ConnPostgreSQL.returnInsertResult(Query)
  except Exception as e:
    logger.error(str(e))
    return False

if __name__ == "__main__":
    argv = ['worker', '--loglevel=info', '--concurrency=20','-n monitoring@nxtgen']
    app.worker_main(argv)

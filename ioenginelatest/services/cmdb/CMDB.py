import sys, os, paramiko, json, logging, psycopg2
from services.utils.decoder import decode
from logging.handlers import TimedRotatingFileHandler
from pymongo import MongoClient
import nmap
from celery import Celery
import subprocess
import requests
import winrm

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
handler = TimedRotatingFileHandler('/var/log/autointelli/cmdbworker.log', when='midnight', interval=1)
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


# Open Reading Key
key = open(os.path.expanduser('~/.ssh/id_rsa.pub')).read()
key = key.replace('\r\n','')
key = key.replace('\n','')
SECRETDIR = '/usr/local/autointelli/.ssh'

# GET CMDB COnnection
cur.execute('select configip,configport,dbname,username,password from configuration where configname=\'CMDB\'')
mongodata = cur.fetchall()
mongodata = mongodata[0]

# Create the app and set the broker location (RabbitMQ)
app = Celery('CMDB',
             broker='pyamqp://{0}:{1}@{2}/{3}'.format(esbuser, esbpass, esbip, vhost),
             backend = 'db+postgresql://{0}:{1}@{2}:{3}/{4}'.format(dbuser, maindbpassword, dbhost, dbport, dbname),
             result_persistent = True)


""" Generates an SSH RSA KEY For the Particular Host """
def gen_key(hostname,SECRETDIR):
    """Generate a SSH Key."""
    os.chdir(SECRETDIR)
    os.system('ssh-keygen -t rsa -N \'\' -f '+ SECRETDIR+'/'+hostname)

""" Checks to See if an SSH Public Key Already present for the Hostname """
def key_present(hostname,SECRETDIR):
    os.system('mkdir -p '+SECRETDIR+'/'+hostname)
    if hostname  in os.listdir(SECRETDIR+'/'+hostname):
        return True
    else:
        return False


@app.task
def insertLinuxHost(ipaddress,username,password,cred_id):
  try:
    client=paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ipaddress, username=username, password=password)
    command = "python -c 'import platform;print(platform.system()+\"#@#\"+platform.linux_distribution()[0]+\"#@#\"+platform.linux_distribution()[1]+\"#@#\"+platform.node())'"
    stdin, stdout, stderr = client.exec_command(command)
    if stdout:
      output = stdout.read().decode('ascii').strip("\n").split("#@#")
      hostname = output[3]
      system = output[0]
      distribution = output[1]
      version = output[2]
      cur.execute("""select count(*) from ai_machine where ip_address='{0}'""".format(ipaddress))
      machine_count = cur.fetchone()
      if machine_count[0] == 0:
        cur.execute("""insert into ai_machine (machine_fqdn, platform, osname, osversion, ip_address, fk_cred_id, remediate, active_yn) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', {5}, 'N', 'Y')""".format(hostname, system, distribution, version, ipaddress, cred_id))
      else:
        cur.execute("""update ai_machine set machine_fqdn='{0}', platform='{1}', osname='{2}', osversion='{3}', ip_address='{4}', fk_cred_id={5} where ip_address='{4}'""".format(hostname, system, distribution, version, ipaddress,cred_id))
      return True
    else:
      output1 = stderr.read().decode('ascii').strip("\n").lower()
      return False
  except Exception as e:
    print(str(e))
    return False

#@app.task
#def insertLinuxHost(ipaddress, username, password, cred_id):
#  try:
#    client=paramiko.SSHClient()
#    client.load_system_host_keys()
#    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#    client.connect(ipaddress, username=username, password=password)
#    stdin, stdout, stderr = client.exec_command("hostname") 
#    hostname = stdout.read().decode('ascii').strip("\n").lower()
#    hostname = 'AIOPs-R2D2'
#    returnCode = key_present(hostname,SECRETDIR)
#    if returnCode:
#        logger.info('Key Already Present')
#    else:
#      os.system('mkdir -p '+SECRETDIR+'/'+hostname)
#      gen_key(hostname,SECRETDIR+'/'+hostname)
#
#    #Insert Key to Target Host
#    key = open(os.path.expanduser(SECRETDIR+'/'+hostname+'/'+hostname+'.pub')).read()
#    key = key.replace('\r\n','')
#    key = key.replace('\n','')
#
#    stdin, stdout, stderr = client.exec_command("mkdir -p ~/.ssh/")
#    stdin, stdout, stderr = client.exec_command("echo %s >> ~/.ssh/authorized_keys" % (key))
#    #stdout.readlines()
#    stdin, stdout, stderr = client.exec_command("chmod 644 ~/.ssh/authorized_keys")
#    stdin, stdout, stderr = client.exec_command("chmod 700 ~/.ssh") 
#   
#    """ Add Entry in Mongo """
#    mclient = MongoClient(mongodata[0], int(mongodata[1]))
#    db = mclient.cmdb
#    db.cimetadata.update({"_id": 1}, {"$set": {"_meta.hostvars."+hostname:{"ansible_ssh_private_key_file": SECRETDIR+'/'+hostname+'/'+hostname, "ansible_become_method": "sudo", "ansible_become_pass": "{{ mypass }}", "ansible_user": username, "ansible_become": "yes"}}, "$addToSet": {"group.hosts": hostname}})
#    if hostname in open('/etc/hosts').read():
#      logger.info(hostname+' exists in hosts file')
#    else:
#      os.system("echo %s    %s >> /etc/hosts" % (ipaddress, hostname))
#    
#    # STEP 2 Create a Text File and save the username and Password 
#    os.environ["ANSIBLE_VAULT_PASSWORD_FILE"] = "/usr/local/autointelli/NxtGen/ioengine/services/cmdb/.secrets/.vaultpassdb"
#    filename = "/usr/local/autointelli/NxtGen/ioengine/services/cmdb/.secrets/{0}.yml".format(hostname)
#    if ( os.path.isfile(filename)):
#      pass
#    else:
#      os.system("echo -e \"ansible_become_pass\": %s >> %s" %  (password,filename))
#      os.system("ansible-vault encrypt {0}".format(filename))
#
#    """ Gather Facts from the added machine"""
#    command = 'export ANSIBLE_HOST_KEY_CHECKING=False;ANSIBLE_STDOUT_CALLBACK=json ansible-playbook -i /usr/local/autointelli/NxtGen/ioengine/services/cmdb/inventory.py /usr/local/autointelli/NxtGen/ioengine/services/KIS/System/Default/GatherFacts.yml -e KPI={0} -l {0}'.format(hostname)
#    print(command)
#    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
#    output = process.communicate()
#    output = output[0].decode('utf8')
#    try:
#      output = json.loads(output)
#    except:
#      output = json.loads(output[output.index('\n')+1:])
#    
#    diskdata = {}
#    system = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_system']
#    distribution = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_distribution']
#    version = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_distribution_major_version']
#    fqdn = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_hostname']
#    processor_count = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_processor_count']
#    memory_total = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_memtotal_mb']
#    swap_total = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_swaptotal_mb']
#    architecture = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_architecture']
#    mounts =  output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_mounts']
#    for mount in mounts:
#      partition  = mount['mount']
#      if 'size_total' in mount:
#        mount_total_gbytes = mount['size_total'] / 1024 / 1024 / 1024
#        mount_total_gbytes = round(mount_total_gbytes,0)
#      diskvalues = {partition: mount_total_gbytes}
#      diskdata.update(diskvalues)
#    inventory_data = {'IPADDRESS': ipaddress, 'PROCESSOR_COUNT': processor_count, 'MEMORY_TOTAL': memory_total, 'SWAP_TOTAL': swap_total, 'ARCHITECTURE': architecture, 'PLATFORM': system, 'OSNAME': distribution, 'VERSION': version, 'HOSTNAME': fqdn, 'DISK': diskdata}
#    print(inventory_data)
#    cur.execute("""select count(*) from ai_machine where ip_address='{0}'""".format(ipaddress))
#    machine_count = cur.fetchone()
#    if machine_count[0] == 0:
#      payload = {'Module': 'cmdb', 'InformationType': 'Data', 'Action': 'Insert', 'Data': {'Hostname': fqdn, 'IPAddress': ipaddress, 'Platform': system, 'OSName': distribution, 'Version': version, 'Action': 'D'}}
#      headers = {'Content-Type': 'Application/json'}
#      notify = requests.post("http://localhost:3890/admin/api/v2/notifications/async", data=json.dumps(payload), headers=headers)
#      #print(notify.text)
#      cur.execute("""insert into ai_machine (machine_fqdn, platform, osname, osversion, ip_address, fk_cred_id, remediate, active_yn, inventory) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', {5}, 'N', 'Y', '{6}')""".format(hostname, system, distribution, version, ipaddress, cred_id, json.dumps(inventory_data)))
#    else:
#      cur.execute("""update ai_machine set machine_fqdn='{0}', platform='{1}', osname='{2}', osversion='{3}', ip_address='{4}', fk_cred_id={5}, inventory='{6}' where ip_address='{4}'""".format(hostname, system, distribution, version, ipaddress,cred_id, json.dumps(inventory_data)))
#      payload = {'Module': 'cmdb', 'InformationType': 'Data', 'Action': 'Update', 'Data': {'Hostname': fqdn, 'IPAddress': ipaddress, 'Platform': system, 'OSName': distribution, 'Version': version, 'Action': 'D'}}
#      headers = {'Content-Type': 'Application/json'}
#      notify = requests.post("http://localhost:3890/admin/api/v2/notifications/async", data=json.dumps(payload), headers=headers)
#      #print(notify.text)
#      
#    conn.commit()
#    return True
#  except Exception as e:
#    logger.error(str(e))
#    return False


@app.task
def osDetect(ipaddress):
  try:
    nm = nmap.PortScanner()
    machine = nm.scan(ipaddress,arguments='-O')
    return(machine['scan'][ipaddress]['osmatch'][0]['osclass'][0]['osfamily'])
  except Exception as e:
    logger.error(str(e))
    return False

@app.task
def insertWindowsHost(ipaddress,username,password,cred_id):
  try:
    s = winrm.Session(ipaddress, auth=(username, password), transport='ntlm')
    r = s.run_cmd('hostname')
    if r.status_code == 0:
      hostname = r.std_out.decode('utf-8').strip().lower()
      hostname_normal = r.std_out.decode('utf-8').strip() #Because of ansible_hostname in varsfile in playbook
    else:
      return False
    # Pre-Requisite for this step is to have python-kerberos module, krb5-workstation module
    mclient = MongoClient(mongodata[0], int(mongodata[1]))
    db = mclient.cmdb
    ## Username Verification for Domain and Local ##
    db.cimetadata.update({"_id": 1}, {"$set": {"_meta.hostvars."+hostname:{"ansible_host": hostname, "ansible_port": 5986, "ansible_connection": "winrm", "ansible_winrm_transport": "ntlm", "ansible_winrm_server_cert_validation": "ignore", "validate_certs": "false"}}, "$addToSet": {"group.hosts": hostname}})
    #STEP 1 """ Add Entry in Mongo """
    if hostname in open('/etc/hosts').read():
      logger.info(hostname+' exists in hosts file')
    else:
      os.system("echo %s    %s >> /etc/hosts" % (ipaddress, hostname))
    # STEP 2 Create a Text File and save the username and Password 
    os.environ["ANSIBLE_VAULT_PASSWORD_FILE"] = "/usr/local/autointelli/ioengine/services/cmdb/.secrets/.vaultpassdb"
    filename = "/usr/local/autointelli/ioengine/services/cmdb/.secrets/{0}.yml".format(hostname)
    os.system("echo -e \"ansible_user\": %s > %s" %  (username,filename))
    os.system("echo -e \"ansible_password\": %s >> %s" % (password,filename))
    os.system("ansible-vault encrypt {0}".format(filename))

    # STEP 3 Gather the Facts
    command = 'export ANSIBLE_HOST_KEY_CHECKING=False;ANSIBLE_STDOUT_CALLBACK=json ansible-playbook -i /usr/local/autointelli/ioengine/services/cmdb/inventory.py /usr/local/autointelli/ioengine/services/KIS/System/Default/GatherFactsWin.yml -e KPI={0} -l {1}'.format(hostname, hostname)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    output = process.communicate()
    output = output[0].decode('utf8')
    print(output)
    try:
      output = json.loads(output)
    except:
      output = json.loads(output[output.index('\n')+1:])
    system = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_os_family']
    distribution = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_os_name']
    version = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_distribution_major_version']
    fqdn = output['plays'][0]['tasks'][0]['hosts'][hostname]['ansible_facts']['ansible_hostname']
    cur.execute("""select count(*) from ai_machine where ip_address='{0}'""".format(ipaddress))
    machine_count = cur.fetchone()
    if machine_count[0] == 0:
      payload = {'Module': 'cmdb', 'InformationType': 'Data', 'Action': 'Insert', 'Data': {'Hostname': fqdn, 'IPAddress': ipaddress, 'Platform': system, 'OSName': distribution, 'Version': version, 'Remediate': 'N'}}
      headers = {'Content-Type': 'Application/json'}
      notify = requests.post("http://localhost:3890/admin/api/v2/notifications/async", data=json.dumps(payload), headers=headers)
      #print(notify.text)
      cur.execute("""insert into ai_machine (machine_fqdn, platform, osname, osversion, ip_address, fk_cred_id, remediate, active_yn) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', {5}, 'N', 'Y')""".format(fqdn, system, distribution, version, ipaddress, cred_id))
    else:
      cur.execute("""update ai_machine set machine_fqdn='{0}', platform='{1}', osname='{2}', osversion='{3}', ip_address='{4}', fk_cred_id={5} where ip_address='{4}'""".format(fqdn, system, distribution, version, ipaddress,cred_id))
      payload = {'Module': 'cmdb', 'InformationType': 'Data', 'Action': 'Update', 'Data': {'Hostname': fqdn, 'IPAddress': ipaddress, 'Platform': system, 'OSName': distribution, 'Version': version, 'Remediate': 'N'}}
      headers = {'Content-Type': 'Application/json'}
      notify = requests.post("http://localhost:3890/admin/api/v2/notifications/async", data=json.dumps(payload), headers=headers)
      #print(notify.text)

    conn.commit()
    return True

    # STEP 5 Return Success
    return True
  except Exception as e:
    logger.error(str(e))
    return False


@app.task
def insertIOSHost(ipaddress,hostname,username,password):
  try:
    # Pre-Requisite for this step is to have python-kerberos module, krb5-workstation module
    mclient = MongoClient(mongodata[0], int(mongodata[1]))
    db = mclient.cmdb
    #STEP 1 """ Add Entry in Mongo """
    db.cimetadata.update({"_id": 1}, {"$set": {"_meta.hostvars."+hostname:{"ansible_host": hostname, "ansible_connection": "network_cli", "ansible_become": "yes", "ansible_become_method": "enable", "ansible_network_os": "ios"}}, "$addToSet": {"group.hosts": hostname}})
    if hostname in open('/etc/hosts').read():
      logger.info(hostname+' exists in hosts file')
    else:
      os.system("echo %s    %s >> /etc/hosts" % (ipaddress, hostname))
    # STEP 2 Create a Text File and save the username and Password 
    os.environ["ANSIBLE_VAULT_PASSWORD_FILE"] = "/usr/local/autointelli/ioengine/services/cmdb/.secrets/.vaultpassdb"
    filename = "/usr/local/autointelli/ioengine/services/cmdb/.secrets/{0}.yml".format(hostname)
    if ( os.path.isfile(filename)):
      pass
    else:
      os.system("echo -e \"ansible_user\": %s >> %s" %  (username,filename))
      os.system("echo -e \"ansible_ssh_pass\": %s >> %s" % (password,filename))
      os.system("ansible-vault encrypt {0}".format(filename))

    # STEP 3 Gather the Facts
    command = 'ansible-playbook -i /usr/local/autointelli/ioengine/services/cmdb/inventory.py /usr/local/autointelli/ioengine/services/KIS/System/Default/GatherFactsIOS.yml -e KPI={0} -l {1}'.format(hostname, hostname)
    # STEP 5 Return Success
    return True
  except Exception as e:
    logger.error(str(e))
    return False


if __name__ == "__main__":
    argv = ['worker', '--loglevel=info', '-n worker@autointelllidev']
    app.worker_main(argv)

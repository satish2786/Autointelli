import sys, paramiko, os

ipaddress = "192.168.56.102"
hostname = "centosdev002"
username = "root"
password = "root123"
command = "ifconfig"
port = 22

key = open(os.path.expanduser('~/.ssh/id_rsa.pub')).read()
key = key.replace('\r\n','')
key = key.replace('\n','')

try:
  client=paramiko.SSHClient()
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

  client.connect(ipaddress,port=port, username=username, password=password)
  stdin, stdout, stderr = client.exec_command("mkdir -p ~/.ssh/")
  stdin, stdout, stderr = client.exec_command("echo %s >> ~/.ssh/authorized_keys" % (key))
  stdout.readlines()
  stdin, stdout, stderr = client.exec_command("chmod 644 ~/.ssh/authorized_keys")
  stdin, stdout, stderr = client.exec_command("chmod 700 ~/.ssh")
  os.system("echo %s	%s >> /etc/hosts" % (ipaddress, hostname))

except Exception as e:
  print("Failure in Connecting")
  print(str(e))
  
finally:
  client.close()
  

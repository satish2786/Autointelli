from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim
import json
import sys
import requests as req

lEsxiMetrics = ["EsxiHost.CPU.Used_Percent", "EsxiHost.MEM.Used_Percent",
                "EsxiHost.pNIC.vmnic4.nicrx", "EsxiHost.pNIC.vmnic4.nictx", "EsxiHost.pNIC.vmnic4.packetsrx", "EsxiHost.pNIC.vmnic4.packetstx",
                "EsxiHost.pNIC.vmnic5.nicrx", "EsxiHost.pNIC.vmnic5.nictx", "EsxiHost.pNIC.vmnic5.packetsrx", "EsxiHost.pNIC.vmnic5.packetstx",
                "EsxiHost.pNIC.vmnic6.nicrx", "EsxiHost.pNIC.vmnic6.nictx", "EsxiHost.pNIC.vmnic6.packetsrx", "EsxiHost.pNIC.vmnic6.packetstx",
                "EsxiHost.pNIC.vmnic7.nicrx", "EsxiHost.pNIC.vmnic7.nictx", "EsxiHost.pNIC.vmnic7.packetsrx", "EsxiHost.pNIC.vmnic7.packetstx"]
#4,5,6,7

lClusterMetrics = ["Cluster.CPU.CPU_Used_Percent", "Cluster.CPU.CPU_Effective", "Cluster.MEM.Memory_Used_Percent",
                   "Cluster.MEM.Memory_Effective"]
lDatastoreMetrics = ["Datastore.Used_Percent"]
lVMMetrics = ["esxivm.CPU.Used_Percent", "esxivm.MEM.Used_Percent",
              "esxivm.NIC.Network adapter 1.nic_rx", "esxivm.NIC.Network adapter 1.nic_tx", "esxivm.NIC.Network adapter 1.packets_rx", "esxivm.NIC.Network adapter 1.packets_tx"]

#lEsxiMetrics = ["EsxiHost.CPU.Used_Percent", "EsxiHost.MEM.Used_Percent", "EsxiHost.pNIC.vmnic7.nicrx", "EsxiHost.pNIC.vmnic7.nictx",
#                "EsxiHost.pNIC.vmnic7.packetsrx", "EsxiHost.pNIC.vmnic7.packetstx"]
#lClusterMetrics = ["Cluster.CPU.CPU_Used_Percent", "Cluster.CPU.CPU_Effective", "Cluster.MEM.Memory_Used_Percent",
#                   "Cluster.MEM.Memory_Effective"]
#lDatastoreMetrics = ["Datastore.Used_Percent"]
#lVMMetrics = ["esxivm.CPU.Used_Percent", "esxivm.MEM.Used_Percent"]

#["cpu.percent", "mem.used_pct", "swap.used_pct", "interface.ens18.bytes_recv", "interface.ens18.bytes_sent","interface.ens18.packets_sent", "interface.ens18.packets_recv"]

def getNICs(summary, guest):
    nics = {}
    for nic in guest.net:
        if nic.network:  # Only return adapter backed interfaces
            if nic.ipConfig is not None and nic.ipConfig.ipAddress is not None:
                nics[nic.macAddress] = {}  # Use mac as uniq ID for nic
                nics[nic.macAddress]['netlabel'] = nic.network
                ipconf = nic.ipConfig.ipAddress
                i = 0
                nics[nic.macAddress]['ipv4'] = {}
                for ip in ipconf:
                    if ":" not in ip.ipAddress:  # Only grab ipv4 addresses
                        nics[nic.macAddress]['ipv4'][i] = ip.ipAddress
                        nics[nic.macAddress]['prefix'] = ip.prefixLength
                        nics[nic.macAddress]['connected'] = nic.connected
                i = i+1
    return nics

def vmsummary(summary, guest):
    print(summary.quickStats)
    vmsum = {}
    config = summary.config
    net = getNICs(summary, guest)
    vmsum['mem'] = str(config.memorySizeMB / 1024)
    vmsum['diskGB'] = str("%.2f" % (summary.storage.committed / 1024**3))
    vmsum['cpu'] = str(config.numCpu)
    vmsum['ostype'] = config.guestFullName
    vmsum['state'] = summary.runtime.powerState
    vmsum['net'] = net
    return vmsum


def discoverVCenter(ip, username, password):
    try:
        c_clus, c_host, c_vm = 0, 0, 0
        inven = {}
        data = {}
        c = 0

        import time
        s, e = time.time(), 0

        si = SmartConnectNoSSL(host=ip, user=username, pwd=password)
        content = si.RetrieveContent()
        children = content.rootFolder.childEntity

        d = {}
        for eachDC in children:
            lCluster, lEsxiHost, lVM, lDatastores = [], [], [], []

            try:
                Datastores = eachDC.datastoreFolder.childEntity
            except Exception as e:
                continue
            for eachDS in Datastores:
                print('--{0}'.format(eachDS.name))
                lDatastores.append(eachDS.name)

            try:
                Clusters = eachDC.hostFolder.childEntity
            except Exception as e:
                continue
            for eachCluster in Clusters:
                print('--{0}'.format(eachCluster.name))
                lCluster.append(eachCluster.name)

                try:
                    EsxiHosts = eachCluster.host
                except Exception as e:
                    continue
                if EsxiHosts:
                    for eachEsxiHost in EsxiHosts:
                        print('----{0}'.format(eachEsxiHost.summary.config.name))
                        lEsxiHost.append(eachEsxiHost.summary.config.name)

                        try:
                            VirtualMachines = eachEsxiHost.vm
                        except Exception as e:
                            continue
                        if VirtualMachines:
                            for eachVM in VirtualMachines:
                                print('------{0}'.format(eachVM.summary.config.name.strip()))
                                lVM.append(eachVM.summary.config.name.strip())
                                #lVM.append(eachVM.summary.config.name.split('(')[0].strip())

            #d[eachDC.name] = {'EsxiHost': {'Name': lEsxiHost, 'Count': len(lEsxiHost)},
            #                  'Cluster': {'Name': lCluster, 'Count': len(lCluster)},
            #                  'VirtualMachine': {'Name': lVM, 'Count': len(lVM)},
            #                  'Datastore': {'Name': lDatastores, 'Count': len(lDatastores)}}
            d[eachDC.name] = {'{0}_vmware_esxihost_metric'.format(ip): {'type': 'EsxiHost', 'host_key': 'EsxiHost.Name', 'hostname': lEsxiHost, 'count': len(lEsxiHost), 'metrics': lEsxiMetrics},
                              '{0}_vmware_cluster_metric'.format(ip): {'type': 'Cluster', 'host_key': 'Cluster.Name', 'hostname': lCluster, 'count': len(lCluster), 'metrics': lClusterMetrics},
                              '{0}_vmware_esxivm_metric'.format(ip): {'type': 'VirtualMachine', 'host_key': 'esxivm.Name', 'hostname': lVM, 'count': len(lVM), 'metrics': lVMMetrics},
                              '{0}_vmware_datastore_metric'.format(ip): {'type': 'Datastore', 'host_key': 'Datastore.Name', 'hostname': lDatastores, 'count': len(lDatastores), 'metrics': lDatastoreMetrics}}
        print('Time Taken: {0}'.format(time.time() - s))
        return d

    except Exception as e:
        return str(e)


def getAllDC(content):
  try:
      DC = []
      data = {}
      children = content.rootFolder.childEntity
      for child in children:
        dc = child
        DC.append(dc.name)
      data = DC
      return({'status': True, 'data':data})
  except Exception as e:
    return({'status': False, 'data': str(e)})


if __name__ == '__main__':
    # print(discoverVCenter('172.16.64.100', 'ng_r2d2@vsphere.local', 'AUP@ssw0rd@321$#!'))
    inp = {'vcenter.100': {'ip': '172.16.64.100', 'username': 'ng_r2d2@vsphere.local', 'password': 'AUP@ssw0rd@321$#!'}}
    #       'vcenter.111': {'ip': '172.16.64.111', 'username': 'ng_r2d2@vsphere.local', 'password': 'AUP@ssw0rd@321$#!'},
    #       'vcenter.10.225.105.10': {'ip': '10.225.105.10', 'username': 'R2D2@vsphere.local',
    #                                 'password': 'Se@0rspc123'}}

    # inp = {'vcenter.10.225.105.10': {'ip': '10.225.105.10', 'username': 'R2D2@vsphere.local', 'password': 'Se@0rspc123'}}
    # ip='172.16.64.100'
    # username='ng_r2d2@vsphere.local'
    # password='AUP@ssw0rd@321$#!'
    # si= SmartConnectNoSSL(host=ip, user=username, pwd=password)
    # content=si.RetrieveContent()
    # print(getAllDC(content))
    # print(getClustersForDC(content, 'HDDC'))

    dd = []
    for eachVCenter in inp:
        print('-'*1000)
        d = discoverVCenter(inp[eachVCenter]['ip'], inp[eachVCenter]['username'], inp[eachVCenter]['password'])
        dd.append(d)

    headers = {'Content-Type': 'application/json'}
    data = {'data': dd}
    print(data)
    location = "bangalore"
    URL = "https://10.227.45.114/inv/api1.0/inv_receiver/{0}".format(location)
    print(URL)
    try:
        ret = req.post(url=URL, data=json.dumps(data), headers=headers, verify=False)
        if ret.status_code == 200 or ret.status_code == 201:
            print("succesfully pushed data to db")
    except Exception as e:
        print("Failed to push {0}".format(str(e)))

    #import json
    #f = open('/tmp/invn_vmware_blr.json', 'a')
    #f.write(json.dumps(data))
    #f.write('-' * 1000)
    #f.close()
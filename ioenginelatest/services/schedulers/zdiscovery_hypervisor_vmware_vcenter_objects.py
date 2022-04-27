from pyVim.connect import SmartConnectNoSSL
import json
import sys
import requests as req

def discoverVCenter(ip, username, password):
    try:
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

        d = []
        for eachDC in children:
            lCluster, lEsxiHost, lVM, lDatastores = [], [], [], []

            try:
                Datastores = eachDC.datastoreFolder.childEntity
            except Exception as e:
                continue
            for eachDS in Datastores:
                print('Datastore--{0}'.format(eachDS.name))
                lDatastores.append(eachDS.name)

            try:
                Clusters = eachDC.hostFolder.childEntity
            except Exception as e:
                continue
            for eachCluster in Clusters:
                print('ESXi Cluster--{0}'.format(eachCluster.name))
                clusTmp = {}
                clusTmp['object_type'] = "cluster"
                clusTmp['object_name'] = eachCluster.name

                try:
                    EsxiHosts = eachCluster.host
                except Exception as e:
                    continue
                esxlTmp = []
                if EsxiHosts:
                    for eachEsxiHost in EsxiHosts:
                        esxTmp = {}
                        esxTmp['object_type'] = "esxihost"
                        esxTmp['object_name'] = eachEsxiHost.summary.config.name
                        print('ESXi Host----{0}'.format(eachEsxiHost.summary.config.name))
                        lEsxiHost.append(eachEsxiHost.summary.config.name)

                        try:
                            VirtualMachines = eachEsxiHost.vm
                        except Exception as e:
                            continue
                        vmTmp = []
                        if VirtualMachines:
                            for eachVM in VirtualMachines:
                                vmTmp.append({'object_type': "esxivm", 'object_name': eachVM.summary.config.name.strip()})
                                print('ESXi VM------{0}'.format(eachVM.summary.config.name.split('(')[0].strip()))
                                lVM.append(eachVM.summary.config.name.strip())
                            esxTmp['object_children'] = vmTmp
                        esxlTmp.append(esxTmp)
                clusTmp['object_children'] = esxlTmp
                lCluster.append(clusTmp)
            d.append({'object_type': 'datacenter', 'object_name': eachDC.name, 'object_children': [lDatastores, lCluster]})
            print('-'*50)
            print(json.dumps(d))
            print('-' * 50)

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

    inp = {'vcenter.100': {'ip': '172.16.64.100', 'username': 'ng_r2d2@vsphere.local', 'password': 'AUP@ssw0rd@321$#!'}}

    dd = []
    for eachVCenter in inp:
        print('-'*1000)
        d = discoverVCenter(inp[eachVCenter]['ip'], inp[eachVCenter]['username'], inp[eachVCenter]['password'])
        dd.append(d)

# import json
# d = json.loads(open('E:/Implementation/11 NxtGen/r&D/vcenterdiscovery/dc.json', 'r').read())

# d = []
# for eachDC in d:
#     dc_name = eachDC['object_name']
#     for eachObject in eachDC['object_children']:



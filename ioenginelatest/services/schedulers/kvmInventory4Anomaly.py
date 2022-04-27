import requests as req
import json
from services.utils import ConnPostgreSQL as psql
import ast

CFGDIR="/usr/local/nagios/etc/objects/servers/kvmvms/"
TOKEN = "NxtG3n"

def getKVMNICS(HYPERVISOR):
    try:
        APIURL = "https://{hypervisor}:5693/api/plugins/kvm_discovery.sh?token=NxtG3n".format(hypervisor=HYPERVISOR)
        r = req.get(APIURL, verify=False)
        if r.status_code == 200 or r.status_code == 201:
            output = json.loads(r.text)
            if output['returncode'] == 0:
                # ast.literal_eval(output['stdout'])
                return {'status': 'success', 'data': output['stdout']}
            else:
                return {'status': 'failure', 'data': 'no data'}
    except Exception as e:
        return {'status': 'failure', 'data': str(e)}


def getHosts():
    try:
        sQuery = "select distinct h_ip from onapp_object_inventory"
        dRet = psql.returnSelectQueryResultAsList(sQuery)
        if dRet['result'] == 'success':
            return dRet['data']['h_ip']
        else:
            return []
    except Exception as e:
        return {'status': 'failure', 'data': str(e)}


if __name__ == "__main__":
    try:
        l = getHosts()
        for i in l:
            out = getKVMNICS(i)
    except Exception as e:
        print("Exception: {0}".format(str(e)))
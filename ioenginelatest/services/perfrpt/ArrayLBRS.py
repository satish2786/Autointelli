import sys
#import config
import requests
import json

#sys.path.append('/usr/local/autointelli/ioengine')
#sys.path.append('/etc/autointelli/')

DATA = {
        '10.210.11.184': {
                'PORT': 9997,
                'USER': 'ai-user',
                'PASS': 'autointelli@123',
                'IMPIP': '10.210.45.119',
                'IMPPORT': 3890
        }
}

uatLB = {
    'LBIP': '117.239.183.62',
    'LBPort': '9997',
    'LBUsername': 'arrayai',
    'LBPassword': 'arrayai'
}

def getRealServices(LBIP):
    try:
        LBPORT = DATA[LBIP]['PORT']
        LBUSER = DATA[LBIP]['USER']
        LBPASS = DATA[LBIP]['PASS']
        RSURL = 'https://{0}:{1}/rest/apv/loadbalancing/slb/rs/RealService'.format(LBIP, LBPORT)

        output = requests.get(RSURL, auth=(LBUSER, LBPASS), verify=False, timeout=3)
        sFinal = {}
        sFinal['items'] = []
        sFinal['items'].append(['pk_object_id', 'object_name'])
        if output.status_code == 200:
            rsdata = json.loads(output.text)
            i = 1
            for RS in rsdata['RealService']:
                sFinal['items'].append([i, RS['instance_id']])
                i = i + 1
            sFinal['metrics'] = ['Connection_Count', 'Outstanding_Request', 'Bytes_IN', 'Bytes_OUT', 'Packets_IN',
                                 'Packets_OUT', 'Average_Bandwidth_IN', 'Average_Bandwidth_Out']
            return {'result': 'success', 'data': sFinal}
        else:
            return {'result': 'failure', 'data': 'no data'}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

def getRealServiceGroupMembers(realserviceGroup):
    try:
        rsGURL = "https://{0}:{1}/rest/apv/loadbalancing/slb/group/Group/{2}/members".format(
            uatLB['LBIP'], uatLB['LBPort'], realserviceGroup.strip()
        )
        auth = (uatLB['LBUsername'], uatLB['LBPassword'])
        dHeader = {'Content-Type': 'application/json'}
        ret = requests.get(url=rsGURL, auth=auth, verify=False, headers=dHeader)
        print("Array LB:{0}".format(ret.text))
        if ret.status_code == 200 or ret.status_code == 201:
            js = json.loads(ret.text)
            if not 'msg' in js.keys():
                out = [i['real_service'] for i in js['Group']['members']]
                dResult = {}
                for eachRS in out:
                    rs = "https://{0}:{1}/rest/apv/loadbalancing/slb/rs/RealService/{2}/ip".format(
                        uatLB['LBIP'], uatLB['LBPort'], eachRS.strip()
                    )
                    ret = requests.get(url=rs, auth=auth, verify=False, headers=dHeader)
                    print("Array LB:{0}".format(ret.text))
                    if ret.status_code == 200 or ret.status_code == 201:
                        js = json.loads(ret.text)
                        if not 'msg' in js.keys():
                            dResult[js['RealService']['ip']] = eachRS
                        else:
                            return {'result': 'failure', 'data': 'Failed to get real service member ip: {0}'.format(js)}
                    else:
                        return {'result': 'failure', 'data': 'Failed to get real service member ip: {0}'.format(ret.text)}
                return {'result': 'success', 'data': dResult}
            else:
                return {'result': 'failure', 'data': 'Failed to get real service member details: {0}'.format(js)}
        else:
            return {'result': 'failure', 'data': 'Failed to get real service member details: {0}'.format(ret.text)}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

def getStats(pRealService):
    try:
        rsGURL = "https://{0}:{1}/rest/apv/loadbalancing/slb/rs/RealService/{2}/statistics".format(
            uatLB['LBIP'], uatLB['LBPort'], pRealService.strip()
        )
        auth = (uatLB['LBUsername'], uatLB['LBPassword'])
        dHeader = {'Content-Type': 'application/json'}
        ret = requests.get(url=rsGURL, auth=auth, verify=False, headers=dHeader)
        print("Array LB:{0}".format(ret.text))
        if ret.status_code == 200 or ret.status_code == 201:
            js = json.loads(ret.text)
            if not 'msg' in js.keys():
                return {'result': 'success', 'data': js['RealService']}
            else:
                return {'result': 'failure', 'data': 'Failed to get real service member details: {0}'.format(js)}
        else:
            return {'result': 'failure', 'data': 'Failed to get real service member details: {0}'.format(ret.text)}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

def enableRealService(pRealService):
    try:
        rsGURL = "https://{0}:{1}/rest/apv/loadbalancing/slb/rs/RealService/_Enable".format(
            uatLB['LBIP'], uatLB['LBPort']
        )
        auth = (uatLB['LBUsername'], uatLB['LBPassword'])
        dHeader = {'Content-Type': 'application/json'}
        dPayload = {'targets': pRealService.strip()}
        ret = requests.post(url=rsGURL, auth=auth, verify=False, headers=dHeader, data=json.dumps(dPayload))
        print("Array LB Enable Real Service:{0}".format(ret.text))
        if ret.status_code == 200 or ret.status_code == 201:
            js = json.loads(ret.text)
            if not 'msg' in js.keys() or js['msg'].strip() == '':
                return {'result': 'success', 'data': "Config Changes: {0}".format(js['config_change'])}
            else:
                return {'result': 'failure', 'data': 'Failed to enable real service: {0}'.format(js)}
        else:
            return {'result': 'failure', 'data': 'Failed to enable real service: {0}'.format(ret.text)}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

def disableRealService(pRealService):
    try:
        rsGURL = "https://{0}:{1}/rest/apv/loadbalancing/slb/rs/RealService/_Disable".format(
            uatLB['LBIP'], uatLB['LBPort']
        )
        auth = (uatLB['LBUsername'], uatLB['LBPassword'])
        dHeader = {'Content-Type': 'application/json'}
        dPayload = {'targets': pRealService.strip()}
        ret = requests.post(url=rsGURL, auth=auth, verify=False, headers=dHeader, data=json.dumps(dPayload))
        print("Array LB Enable Real Service:{0}".format(ret.text))
        if ret.status_code == 200 or ret.status_code == 201:
            js = json.loads(ret.text)
            if not 'msg' in js.keys() or js['msg'].strip() == '':
                return {'result': 'success', 'data': "Config Changes: {0}".format(js['config_change'])}
            else:
                return {'result': 'failure', 'data': 'Failed to disable real service: {0}'.format(js)}
        else:
            return {'result': 'failure', 'data': 'Failed to disable real service: {0}'.format(ret.text)}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}

# if __name__ == "__main__":
#  getRealServices('10.210.11.184')

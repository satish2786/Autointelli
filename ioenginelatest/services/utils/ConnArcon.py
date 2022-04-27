import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from services.utils import ConnPostgreSQL
from services.utils import ED_AES256 as aes
from services.utils import decoder
import os
from requests_ntlm import HttpNtlmAuth

os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

Query = "select configip, configport, username, password,communicationtype from configuration where configname='ARCON'"
dRet = ConnPostgreSQL.returnSelectQueryResult(Query)
if dRet["result"] == "success":
    configip = dRet['data'][0]['configip']
    configport = dRet['data'][0]['configport']
    arconuser = dRet['data'][0]['username']
    # arconpwd  = decoder.decode('auto!ntell!', dRet['data'][0]['password'])
    arconpwd = aes.decrypt(dRet['data'][0]['password'].encode(), '@ut0!ntell!'.encode()).decode('utf-8')
    commtype = dRet['data'][0]['communicationtype']


def queryPasswordIRESS(ip, username="", os=""):
    try:
        url = "{0}://{1}:{2}/intranet/api/MachinePassword".format(commtype, configip, configport)
        headers = {'Content-Type': 'application/json'}
        auth = HttpNtlmAuth(arconuser, arconpwd)
        response = requests.get(url, data=json.dumps({'MachineName': ip}), headers=headers, verify=False, auth=auth)
        print(url)
        print(json.dumps({'MachineName': ip}))
        print(response.text, response.status_code)
        if response.status_code == 200 or response.status_code == 201:
            outJSON = json.loads(response.text)
            outJSON = outJSON[0]
            print(outJSON)

            if 'UserName' in outJSON and 'Password' in outJSON:
                return {'result': 'success', 'data': {'username': outJSON['UserName'], 'password': outJSON['Password']}}
            else:
                return {'result': 'failure', 'data': 'no data'}
        else:
            return {'result': 'failure', 'data': 'no data'}
    except Exception as e:
        return {"result": "failure", "data": str(e)}


def queryPasswordARCON(ip, username, os):
    try:
        url = commtype + "://" + configip + ":" + str(configport) + "/arconToken"
        pwdurl = commtype + "://" + configip + ":" + str(configport) + "/api/ServicePassword/GetTargetDevicePassKey"
        payload = "grant_type=password&username={0}&password={1}".format(arconuser, arconpwd)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=payload, headers=headers, verify=False)
        _data = json.loads(response.text)
        new_headers = {'Authorization': 'bearer ' + _data['access_token'], 'Content-Type': 'application/json'}
        new_payload = None
        if os == 'vcenter':
            new_payload = [{'ServerIp': ip, 'UserName': username, 'DbInstanceName': '', 'OpenForHours': '2', 'ServiceTypeId': '36'}]
        else:
            new_payload = [{'ServerIp': ip, 'TargetType': os, 'UserName': username, 'DbInstanceName': '', 'OpenForHours': '2'}]
        response = requests.post(pwdurl, data=json.dumps(new_payload), headers=new_headers, verify=False)
        _output = json.loads(response.text)
        # print(_output)
        if _output['Success']:
            for result in _output['Result']:
                return {"result": "success", "data": {'username': username, 'password': result['Password']}}
        else:
            return {"result": "failure", "data": "no data"}
    except Exception as e:
        return {"result": "failure", "data": str(e)}


def queryPassword(ip, username, os, pam):
    if pam.lower() == 'arcon':
        return queryPasswordARCON(ip, username, os)
    elif pam.lower() == 'iress':
        return queryPasswordIRESS(ip, username, os)


if __name__ == "__main__":
    print("Main function:")
    # output = queryPassword('10.10.100.161', 'root', 'Linux')
    # print(output)

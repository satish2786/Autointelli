import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

configip = ''
configport = ''
arconuser = ''
arconpwd = ''
#arconpwd = aes.decrypt('@ut0!ntell!@123'.encode(), arconpwd.encode()).decode('utf-8')
commtype = ''


def queryPassword(ip,username,os):
  try:
    url = commtype + "://" + configip +":"+str(configport)+"/arconToken"
    pwdurl = commtype + "://" + configip +":"+str(configport)+"/api/ServicePassword/GetTargetDevicePassKey"
    payload = "grant_type=password&username={0}&password={1}".format(arconuser,arconpwd)
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(url,data=payload,headers=headers,verify=False)
    _data = json.loads(response.text)
    new_headers = {'Authorization': 'bearer '+_data['access_token'], 'Content-Type': 'application/json'}
    new_payload = [{'ServerIp': ip, 'TargetType': os,'UserName': username, 'DbInstanceName': '','OpenForHours': '2'}]
    response = requests.post(pwdurl,data=json.dumps(new_payload),headers=new_headers, verify=False)
    _output = json.loads(response.text)
    #print(_output)
    if _output['Success']:
      for result in _output['Result']:
        return {"result": "success", "data": result['Password']}
    else:
      return {"result": "failure", "data": "no data"}
  except Exception as e:
    return {"result": "failure", "data": str(e)}


if __name__ == "__main__":
  output = queryPassword('10.10.100.161','root','Linux')
  print(output)

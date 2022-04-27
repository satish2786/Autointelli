from services.utils import ConnPostgreSQL as pcon
import services.utils.ED_AES256 as aes
from services.utils import ConnArcon as pam1
import json

pam = ""
try:
    pam = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['pvault']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

def getCredentials(name):
    try:
        sQuery = "select cred_type, username, password  from ai_device_credentials where active_yn='Y' and lower(cred_name)=lower('{0}')".format(name)
        dRet = pcon.returnSelectQueryResult(sQuery)
        if dRet['result'] == 'success':
            if dRet['data'][0]['cred_type'].lower() == 'pam':
                ret = {}
                if pam.lower() == 'iress':
                    ret = pam1.queryPassword(dRet['data'][0]['machine_fqdn'], dRet['data'][0]['username'],
                                             dRet['data'][0]['platform'], pam)
                else:
                    ret = pam1.queryPassword(dRet['data'][0]['ip_address'], dRet['data'][0]['username'],
                                             dRet['data'][0]['platform'], pam)
                if ret["result"] == "success":
                    USERNAME = ret["data"]['username']
                    PASSWORD = ret["data"]['password']
                    return {'username': USERNAME, 'password': PASSWORD}
                else:
                    return {'username': '', 'password': ''}
            else:
                k = '@ut0!ntell!'.encode()
                fromDB = dRet['data'][0]['password'].encode()
                PASSWORD = aes.decrypt(fromDB, k).decode('utf-8')
                return {'username': dRet['data'][0]['username'], 'password': PASSWORD}
        else:
            return {'username': '', 'password': ''}
    except Exception as e:
        return {'username': '', 'password': ''}

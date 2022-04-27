import json
from services.utils import ConnPostgreSQL as conn

location = {}
try:
    location = json.load(open('/etc/autointelli/autointelli.conf', 'r'))['pam']
except Exception as e:
    print("Couldn't start the CRON because the location is missing in conf file")

if __name__ == '__main__':
    iQuery = "select nofdays from filters_retention where active_yn='Y'"
    dRet = conn.returnSelectQueryResult(iQuery)
    if dRet['result'] == 'success':
        days = dRet['data'][0]['nofdays']
        dQuery = "delete from filtered_records_24 where created_on < (now() - INTERVAL '{0} DAYS')".format(days)
        dRet = conn.returnInsertResult(dQuery)
        if dRet['result'] == 'success':
            print("Filter retention job executed successfully")
        else:
            print("Failed to execute the retention for filters. Reason:{0}".format(dRet['data']))
    else:
        print("Filter retention configuration fetch failed. Reason:{0}".format(dRet['data']))
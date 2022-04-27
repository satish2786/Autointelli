from services.utils import ConnPostgreSQL as dbconn
import json

def prereq(hostname):
    try:
        sQuery = """select 
                                        am.machine_fqdn, am.platform, am.ip_address, ad.cred_type, ad.username, ad.password, ad.port 
                                    from 
                                        ai_machine am inner join ai_device_credentials ad on(am.fk_cred_id=ad.cred_id) 
                                    where 
                                        lower(am.machine_fqdn)=lower('{0}') or am.ip_address='{1}'""".format(hostname.strip(),
                                                                                               hostname.strip())
        dRet = dbconn.returnSelectQueryResult(sQuery)
        return json.dumps(dRet)
    except Exception as e:
        return json.dumps({'result': 'failure', 'data': str(e)})
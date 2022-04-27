from pymongo import MongoClient
import json

def mongoAction(action="", group_name="", fqdn_list=[]):
    try:
        client = MongoClient("localhost:27017")
        db = client.cmdb
        ret = db.cimetadata.find({"_id": 1})
        d, mgroup, ips = {}, group_name, fqdn_list
        for i in ret:
            d = i
        dGroups = d['group']
        if action.lower() == 'create' or action.lower() == 'update':
            dGroups[mgroup] = ips
        elif action.lower() == 'delete':
            del dGroups[mgroup]
        db.cimetadata.update({"_id": 1}, {"$set": {"group": json.dumps(dGroups)}})
        return {'result': 'success', 'data': 'data pushed to mongo'}
    except Exception as e:
        return {'result': 'failure', 'data': str(e)}


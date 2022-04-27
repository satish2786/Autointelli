from pymongo import MongoClient
IP = "AIDEV-MEM"
client = MongoClient('192.168.1.100',27017)
db = client.cmdb
db.cimetadata.update({"_id": 1}, {"$set": {"_meta.hostvars": {}}, "$addToSet": {"group.hosts": IP}})

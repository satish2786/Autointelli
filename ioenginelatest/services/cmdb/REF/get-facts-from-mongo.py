from pymongo import MongoClient

con = MongoClient('localhost', 27017)
db = con['ansible']
coll = db.cache

data = coll.find()

for row in data:
  cmdbdata = {}
  print(row)
  HOSTADDRESS = row['data']['ansible_default_ipv4']['address']
  #print(HOSTADDRESS)
  cmdbvalues = {HOSTADDRESS: {'System': row['data']['ansible_system'], 'Architecture': row['data']['ansible_architecture'], 'Distribution': row['data']['ansible_distribution'], 'FQDN': row['data']['ansible_fqdn'], 'IPAddress': HOSTADDRESS}}
  cmdbdata.update(cmdbvalues)
  print(cmdbdata)

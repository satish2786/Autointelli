#!/usr/bin/python3.6

import sys
import json
import psycopg2
from services.utils.decoder import decode, encode
from pymongo import MongoClient
import argparse


# Reading the configuration file for db connection string
conn = ""
data = json.load(open('/etc/autointelli/autointelli.conf'))
# Decoding the Password
maindbpassword = decode('auto!ntell!',data['maindb']['password'])


try:
  conn = psycopg2.connect(database=data['maindb']['dbname'], user=data['maindb']['username'], password=maindbpassword, host=data['maindb']['dbip'], port=data['maindb']['dbport'])
  cur = conn.cursor()
  cur.execute('select configip,configport,dbname,username,password from configuration where configname=\'CMDB\'')
  mongodata = cur.fetchall()
  mongodata = mongodata[0]
except Exception as e:
  print("Exception Occured " + str(e))
  sys.exit()


parser = argparse.ArgumentParser()
parser.add_argument("--list", help="test", action="store_true")
args = parser.parse_args()

client = MongoClient(mongodata[0], int(mongodata[1]))
db = client.cmdb
cimeta = db.cimetadata
if args.list:
  inventory = cimeta.find_one({"_id": 1})
  inventory.pop("_id",None)
  print(inventory)


#!/usr/bin/env python

import redis
import json

r = redis.StrictRedis(host='localhost', port=6379, db=0)
key = "ansible_facts" + "centosdev001"
val = r.get(key).decode('utf-8')

data = json.loads(val)
print(data['ansible_system'])  # => 7811
print(data['ansible_architecture'])  # => 7811
print(data['ansible_distribution'])  # => 7811
print(data['ansible_fqdn'])  # => 7811
print(data['ansible_default_ipv4']['address'])  # => 7811

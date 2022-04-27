#!/usr/bin/env python

from services.utils.decoder import encode

FILE="""
---
- hosts: all
  gather_facts: False
  vars_files:
    - /usr/local/autointelli/ioengine/services/cmdb/.secrets/{{ AIHOST }}.yml
  tasks:
    - name: Start a service
      win_service:
        name: "{{ KPI }}"
        state: started
    - debug: msg="Service Started Successfully"
"""

FILE1="""
---
- hosts: all
  gather_facts: False
  become: yes
  vars_files:
    - /usr/local/autointelli/ioengine/services/cmdb/.secrets/{{ AIHOST }}.yml
  tasks:
    - name: Check Service Status
      service:
        name: "{{ KPI }}"
        state: started
        enabled: yes
    - debug: msg="Service Started Successfully"
"""

FILE3="""
---
- hosts: 127.0.0.1
  connection: local
  gather_facts: false
  tasks:
  - name: Execute a local command
    command: /opt/jbpm/SCRIPTS/SQLSERVER/CPUBUSY/CPUBUSYQUERYANDKILL.py {{ alert_id }}
    delegate_to: localhost
    register: result

  - name: Show results
    debug:
      var: result.stdout
    delegate_to: localhost
"""


output = encode('auto!ntell!',FILE3)
print(output)

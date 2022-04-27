Autointelli Backend Engine
--------------------------

1. CMDB Graphs Added
2. Network Support Added
3. Policy Engine in UI
4. LDAP Configuraiton in UI
5. New Looks on Automation Catalog
6. SMTP Configuration in UI
7. New Engine Based on Workers

Execute Engine:
--------------
EnginePath=/usr/local/autointelli/ioengine
export PYTHONPATH=/usr/local/autointelli/ioengine
export LD_LIBRARY_PATH=/usr/local/lib

source /root/aicognitive/bin/activate

cd ${EnginePath}/services/administration
nohup python3.5 adminservice.py >> /tmp/admin.log 2>&1 &

cd ${EnginePath}/services/EAMEndPoint
nohup python3.5 eventreceiver.py >> /tmp/admin.log 2>&1 &

cd ${EnginePath}/services/EAM
nohup python3.5 eamworker.py >> /tmp/admin.log 2>&1 &

cd ${EnginePath}/services/EAM
nohup python3.5 eamservice.py >> /tmp/admin.log 2>&1 &

cd ${EnginePath}/services/dashboard
nohup python3.5 dashboard.py >> /tmp/admin.log 2>&1 &
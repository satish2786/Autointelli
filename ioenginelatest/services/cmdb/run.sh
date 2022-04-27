python cmdb.py >> logs/cmdb.log 2>&1 &
python cmdbWorker.py >> logs/kpi.log 2>&1 &
celery -A CMDB worker --loglevel=info -n worker1@autointellidev >> logs/worker.log 2>&1 &

#!/usr/bin/env bash

touch schema_data.sql;
#touch data.sql;

#BackUp Schema

echo "Backup schema first: autointelli";
PGPASSWORD="autointelli" pg_dump --schema-only  autointelli -U autointelli >> /root/schema_data.sql;

#BackUp Table with Data
tables_req_data=(`cat TableReqData.csv`);

for i in ${tables_req_data[*]}
do
        echo "Backup Table :${i}";
        PGPASSWORD="autointelli" pg_dump --column-inserts --data-only --table="${i}" autointelli -U autointelli >> /root/schema_data.sql;
done;

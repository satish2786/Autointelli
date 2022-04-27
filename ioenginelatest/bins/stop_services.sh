#!/usr/bin/env bash

# Kill Python Processes
kill $(ps -ef | grep python | awk '{print $2}')

# Kill Java Processes
cd /opt/aiorch/central/bin
./StopWildfly.sh

cd /opt/aiorch/engine/bin
./StopWildfly.sh

sleep 5

kill $(ps -ef | grep java | awk '{print $2}')

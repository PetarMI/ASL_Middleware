#!/bin/bash

# Init all server names
SERVERS=("foraslvms6"
         "foraslvms7"
         "foraslvms8"
         "foraslvms9"
         "foraslvms10"
         )

# Init all client names
CLIENTS=("foraslvms1"
         "foraslvms2"
         "foraslvms3"
         "foraslvms4"
         "foraslvms5"
         )

MIDDLEWARE="foraslvms11"

USER="ivanovpe"
MACHINE='.westeurope.cloudapp.azure.com'

MEM_FOLDER="/home/ivanovpe/libmemcached-1.0.18/clients"
WORK_CONFIG="/home/ivanovpe/memaslap-workloads/smallvalueread.cfg"

MEMASLAP_LOGS="/home/ivanovpe/tps_logs"
MIDDLEWARE_LOGS=""

L_GREEN='\033[1;32m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "### Setting up servers"
# Save all internal IPs of memcached servers
for ((i=0; i < ${#SERVERS[@]}; i++)); do
echo "Getting Internal IP of ${SERVERS[$i]}";
# ssh -T "${USER}@${USER}${SERVERS[$i]}${MACHINE}" << 'EOF'
#     ip route get 8.8.8.8 | awk "{print \$NF; exit}" > "ipinternal.log";
# EOF
echo "SSH-ing to get internal IP"
# INTERNAL_IP=$(ssh ${USER}@${USER}${SERVERS[$i]}${MACHINE} "cat ipinternal.log")
echo "Adding internal IP to list"
INTERNAL_IPS="${INTERNAL_IPS} ${INTERNAL_IP}:11212"
echo "${INTERNAL_IPS}"
done

echo "### Finished getting IPs from memcached servers"
echo ""

VIRTUAL_CLIENTS=100
THREADS=8

# 13 values for clients in total
for ((i=1; i < 4; i++)); do
VIRTUAL_CLIENTS=$((VIRTUAL_CLIENTS + 100))
printf "${L_GREEN}##### Running instance ${i} -> ${VIRTUAL_CLIENTS} #####${NC}\n" 
# Replication of 3 per experiment instance
for ((j=0; j < 3; j++));do
printf "${GREEN}### Running replication ${j}${NC}\n"
# Start all memcached instances
printf "${CYAN}Starting Servers${NC}\n"
for ((k=0; k < 5; k++));do
    echo "Starting memcached on ${SERVERS[$k]}"
    command="sudo pkill memcached; memcached -p 11212 -t1 > log"
    ssh -T "${USER}@${USER}${SERVERS[$k]}${MACHINE}" "$command" &
pid=$!
done
# Start middleware
printf "${CYAN}RUNNING MIDDLEWARE with parameters${NC}\n"
echo "Threads in thread pool"
echo $THREADS
echo "Memcached servers" 
echo $INTERNAL_IPS
# ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" << EOF
#     echo "Killing previous Java instance"
#     sudo pkill java
#     cd asl/
#     nohup java -jar 'dist/middleware-ivanovpe.jar' -l \$(cat "internalip.log") -p 9090 -t $THREADS -r 3 -m $INTERNAL_IPS > run.log &
# EOF
echo "Middleware started"
# Start clients
printf "${CYAN}Starting clients with ${THREADS} each${NC}\n"
for ((p=0; p < 5; p++));do
echo "RUNNING ${CLIENTS[$p]}"
printf "${RED}Writing into ${MEMASLAP_LOGS}/max_tps_${VIRTUAL_CLIENTS}_${p}_${j}.log${NC}\n"
ssh -T "${USER}@${USER}${CLIENTS[$i]}${MACHINE}" << EOF
    cd $MEM_FOLDER
    nohup ./memaslap -s ${MIDDLEWARE_IP}:9090 -T $VIRTUAL_CLIENTS -c $VIRTUAL_CLIENTS -w "2k" -o 0.99 -S "20s" -t "5m" -F $WORK_CONFIG > "${MEMASLAP_LOGS}/max_tps_${VIRTUAL_CLIENTS}_${p}_${j}.log" &
EOF
done

# Rename timestamp log on middleware
TIMESTAMP_LOG="RequestLog_${VIRTUAL_CLIENTS}_${j}.log"
printf "${RED}${TIMESTAMP_LOG}${NC}\n"
# ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" << EOF
#     mv "/home/ivanovpe/asl/RequestLog.log" "/home/ivanovpe/MaxTps/${TIMESTAMP_LOG}"
# EOF
printf "${GREEN}### Finished replication ${j}${NC}\n"
done
printf "${L_GREEN}##### Finished instance ${i} #####${NC}\n\n"
done
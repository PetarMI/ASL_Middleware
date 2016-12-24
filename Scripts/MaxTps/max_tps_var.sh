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
    echo "SSH-ing to get internal IP"
    INTERNAL_IP=$(ssh ${USER}@${USER}${SERVERS[$i]}${MACHINE} "cat ipinternal.log")
    echo "Adding internal IP to list"
    INTERNAL_IPS="${INTERNAL_IPS} ${INTERNAL_IP}:11212"
    echo "${INTERNAL_IPS}"
done

echo "### Finished getting IPs from memcached servers"
echo ""

VIRTUAL_CLIENTS=88
THREAD_VALS=(8 16 32 64 128)
THREADS=32

for ((i=1; i < 6; i++)); do
    THREADS=$((THREADS * 2))
    printf "${L_GREEN}##### Running instance with ${VIRTUAL_CLIENTS} clients and ${THREADS} threads #####${NC}\n" 
    
    # Replication of 3 per experiment instance
    for ((j=1; j < 2; j++));do
        printf "${GREEN}### Running replication ${j}${NC}\n"
        
        # Start all memcached instances
        printf "${CYAN}Setting up Servers${NC}\n"
        for ((k=0; k < 5; k++));do
            echo "Starting memcached on ${SERVERS[$k]}"
            command="sudo pkill memcached  > log; memcached -p 11212 -t1"
            ssh -T "${USER}@${USER}${SERVERS[$k]}${MACHINE}" "$command" &
        done

        sleep 5

        # Start the middleware 
        printf "${CYAN}RUNNING MIDDLEWARE with parameters${NC}\n"
        echo "Threads in thread pool"
        echo $THREADS
        echo "Memcached servers" 
        echo $INTERNAL_IPS
        command="cd asl/;  nohup java -jar \"dist/middleware-ivanovpe.jar\" -l \$(cat \"internalip.log\") -p 9090 -t $THREADS -r 1 -m $INTERNAL_IPS > run.log &"
        ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" "$command" &
        echo "Middleware started"

        sleep 10

        # Start clients
        printf "${CYAN}Starting clients with ${THREADS} each${NC}\n"
        date +"%H:%M"
        pids=""
        for ((p=0; p < 5; p++));do
            echo "RUNNING ${CLIENTS[$p]}"
            # printf "${RED}Writing into ${MEMASLAP_LOGS}/max_tps_${VIRTUAL_CLIENTS}_${p}_${j}.log${NC}\n"
            command="sudo pkill memaslap; cd $MEM_FOLDER; ./memaslap -s 10.0.0.9:9090 -T $VIRTUAL_CLIENTS -c $VIRTUAL_CLIENTS -w \"1k\" -o 0.99 -S \"2s\" -t \"120s\" -F $WORK_CONFIG > \"${MEMASLAP_LOGS}/max_tps_${VIRTUAL_CLIENTS}_${THREADS}_${p}_${j}.log\""
            ssh -T "${USER}@${USER}${CLIENTS[$p]}${MACHINE}" "$command" &
            pids="$pids $!"
        done
        echo $pids
        wait $pids

        echo "Killing previous JAVA instance"
        ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" "sudo pkill java"

        # Rename timestamp log on middleware
        TIMESTAMP_LOG="RequestLog_${VIRTUAL_CLIENTS}_${j}.log"
        # printf "${RED}${TIMESTAMP_LOG}${NC}\n"
        command="mv \"/home/ivanovpe/asl/RequestLog.log\" \"/home/ivanovpe/MaxTps/${TIMESTAMP_LOG}\""
        ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" "$command"
        printf "${GREEN}### Finished replication ${j}${NC}\n"
    done
    
    printf "${L_GREEN}##### Finished instance ${i} #####${NC}\n\n"
done
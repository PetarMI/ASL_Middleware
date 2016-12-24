#!/bin/bash

# Init all server names
SERVERS=(
         "foraslvms4"
         "foraslvms5"
         "foraslvms6"
         # "foraslvms7"
         # "foraslvms8"
         # "foraslvms9"
         # "foraslvms10"
         )

# Init all client names
CLIENTS=("foraslvms1"
         "foraslvms2"
         "foraslvms3"
         )

MIDDLEWARE="foraslvms11"

USER="ivanovpe"
MACHINE='.westeurope.cloudapp.azure.com'

MEM_FOLDER="/home/ivanovpe/libmemcached-1.0.18/clients"
WORK_CONFIG="/home/ivanovpe/memaslap-workloads/smallvalue.cfg"

MEMASLAP_LOGS="/home/ivanovpe/tps_logs"
MIDDLEWARE_LOGS=""

L_GREEN='\033[1;32m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BACKENDS=7
VIRTUAL_CLIENTS=120
THREADS=24
REPLICATION=(1 4 7)

echo "### Setting up servers"
# Save all internal IPs of memcached servers
for ((i=0; i < $BACKENDS; i++)); do
    echo "SSH-ing to get internal IP"
    INTERNAL_IP=$(ssh ${USER}@${USER}${SERVERS[$i]}${MACHINE} "cat ipinternal.log")
    echo "Adding internal IP to list"
    INTERNAL_IPS="${INTERNAL_IPS} ${INTERNAL_IP}:11212"
    echo "${INTERNAL_IPS}"
done

echo "### Finished getting IPs from memcached servers"
echo ""

for ((i=0; i < 3; i++)); do
    printf "${L_GREEN}##### Running instance with replication = ${REPLICATION[$i]} #####${NC}\n" 
    
    # Replication of 3 per experiment instance
    for ((r=0; r < 3; r++));do
        printf "${GREEN}### Running replication ${r}${NC}\n"
        
        # Start all memcached instances
        printf "${CYAN}Setting up Servers${NC}\n"
        for ((k=0; k < $BACKENDS; k++));do
            echo "Starting memcached on ${SERVERS[$k]}"
            command="sudo pkill memcached  > log; memcached -p 11212 -t1"
            ssh -T "${USER}@${USER}${SERVERS[$k]}${MACHINE}" "$command" &
        done

        sleep 5

        # Start the middleware 
        printf "${CYAN}RUNNING MIDDLEWARE with parameters${NC}\n"
        echo "Replication factor" 
        echo ${REPLICATION[$i]}
        echo "Memcached servers" 
        echo $INTERNAL_IPS
        command="cd asl/;  nohup java -jar \"dist/middleware-ivanovpe.jar\" -l \$(cat \"internalip.log\") -p 9090 -t $THREADS -r ${REPLICATION[$i]} -m $INTERNAL_IPS > run.log &"
        echo $command
        ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" "$command" &
        echo "Middleware started"

        sleep 10

        # Start clients
        printf "${CYAN}Starting clients${NC}\n"
        date +"%H:%M"
        pids=""
        for ((p=0; p < 3; p++));do
            echo "RUNNING ${CLIENTS[$p]}"
            command="sudo pkill memaslap; cd $MEM_FOLDER; ./memaslap -s 10.0.0.9:9090 -T $VIRTUAL_CLIENTS -c $VIRTUAL_CLIENTS -o 0.99 -S \"1s\" -t \"120s\" -F $WORK_CONFIG > \"${MEMASLAP_LOGS}/repl_${BACKENDS}_${REPLICATION[$i]}_${p}_${r}.log\""
            ssh -T "${USER}@${USER}${CLIENTS[$p]}${MACHINE}" "$command" &
            pids="$pids $!"
        done
        echo $pids
        wait $pids

        echo "Killing previous JAVA instance"
        ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" "sudo pkill java"

        # Rename timestamp log on middleware
        TIMESTAMP_LOG="RequestLog_${BACKENDS}_${REPLICATION[$i]}_${r}.log"
        # printf "${RED}${TIMESTAMP_LOG}${NC}\n"
        command="mv \"/home/ivanovpe/asl/RequestLog.log\" \"/home/ivanovpe/MaxTps/${TIMESTAMP_LOG}\""
        ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" "$command"
        printf "${GREEN}### Finished replication ${j}${NC}\n"
    done
    
    printf "${L_GREEN}##### Finished instance ${i} #####${NC}\n\n"
done
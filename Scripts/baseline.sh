#!/bin/bash

# Init all machine names
CLIENTS=("foraslvms1"
         "foraslvms2")

SERVER="foraslvms4"

USER="ivanovpe"
MACHINE='.westeurope.cloudapp.azure.com'

# Start the VMs
# for ((i=0; i < ${#CLIENTS[@]}; i++)); do
#     azure vm start "FOR_ASL" ${CLIENTS[$i]}
# done

# # Start the middleware
# azure vm start "FOR_ASL" ${SERVER}

# # Update SSH key before connecting to the VM

# for ((i=0; i < ${#CLIENTS[@]}; i++)); do
#     echo "UPDATING SSH KEY FOR ${CLIENTS[$i]}"
#     ssh-keygen -f "/home/petar/.ssh/known_hosts" -R "${USER}${CLIENTS[$i]}${MACHINE}"
# done

# #echo "UPDATING SSH KEY FOR SERVER"
# ssh-keygen -f "/home/petar/.ssh/known_hosts" -R "${USER}${SERVER}${MACHINE}"

# Start memcached and save IP

echo "SSH-ing into ${SERVER}";
ssh -T "${USER}@${USER}${SERVER}${MACHINE}" << 'EOF'
    sudo pkill memcached
    echo "Starting memcached"
    nohup memcached -p 11212 -t1 > log &
    echo "Getting Internal IP"
    ip route get 8.8.8.8 | awk "{print \$NF; exit}" > "ipinternal.log";
EOF
echo "SSH-ing to get internal IP"
SERVER_IP=$(ssh ${USER}@${USER}${SERVER}${MACHINE} "cat ipinternal.log")

# Run the clients
WORKLOAD="/home/ivanovpe/memaslap-workloads/smallvalue.cfg" 
MEMASLAP_LOC="/home/ivanovpe/libmemcached-1.0.18/clients/"

for ((i=1; i<65; i++)); do
echo "Running for ${i}"
for ((j=1; j<6; j++)); do
echo "Run number ${j}"          
ssh -T "${USER}@${USER}${CLIENTS[0]}${MACHINE}" << EOF
    cd $MEMASLAP_LOC
    ./memaslap -s ${SERVER_IP}:11212 -T $i -c $i -o 0.99 -S 1s -t "30s" -F $WORKLOAD > "/home/ivanovpe/logs/microbench${i}-${j}.log"
EOF
done
#echo "Copy generated files to local system"
for ((k=1; k<6; k++)); do
    scp "${USER}@${USER}${CLIENTS[0]}${MACHINE}:/home/ivanovpe/logs/microbench${i}-${k}.log" "/home/petar/AutumnSemester/AdvancedSystems/Baselogs"
done
echo "------------------"
done
echo "FINISHED UNTIL 64"

# Start the second client

for ((i=1; i<65; i++)); do
echo "Running for 64 + ${i}"
for ((j=1; j<6; j++)); do
echo "Run number ${j}"
ssh -T "${USER}@${USER}${CLIENTS[0]}${MACHINE}" << EOF
    cd $MEMASLAP_LOC
    nohup ./memaslap -s ${SERVER_IP}:11212 -T 64 -c 64 -o 0.99 -S 1s -t "30s" -F $WORKLOAD > "/home/ivanovpe/logs/microbench64_${i}_${j}_c1.log" &
EOF
ssh -T "${USER}@${USER}${CLIENTS[1]}${MACHINE}" << EOF
    cd $MEMASLAP_LOC
    ./memaslap -s ${SERVER_IP}:11212 -T $i -c $i -o 0.99 -S 1s -t "31s" -F $WORKLOAD > "/home/ivanovpe/logs/microbench64_${i}_${j}_c2.log"
EOF
done
#echo "Copy generated files to local system"
for ((k=1; k<6; k++)); do
    scp "${USER}@${USER}${CLIENTS[0]}${MACHINE}:/home/ivanovpe/logs/microbench64_${i}_${k}_c1.log" "/home/petar/AutumnSemester/AdvancedSystems/Baselogs"
    scp "${USER}@${USER}${CLIENTS[1]}${MACHINE}:/home/ivanovpe/logs/microbench64_${i}_${k}_c2.log" "/home/petar/AutumnSemester/AdvancedSystems/Baselogs"
done
echo "------------------"
done

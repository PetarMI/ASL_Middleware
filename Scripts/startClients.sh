#!/bin/bash

# Init all machine names
CLIENTS=("foraslvms1"
		 "foraslvms2"
	     "foraslvms3"
	     )

MIDDLEWARE="foraslvms11"

USER="ivanovpe"
MACHINE='.westeurope.cloudapp.azure.com'

MEM_FOLDER="/home/ivanovpe/libmemcached-1.0.18/clients"
WORK_CONFIG="/home/ivanovpe/memaslap-workloads/smallvalue.cfg"

# # Start the VMs
# for ((i=0; i < ${#CLIENTS[@]}; i++)); do
# 	echo "Starting ${CLIENTS[$i]}"
# 	azure vm start "FOR_ASL" ${CLIENTS[$i]}
# done

# # Update SSH key before connecting to the VM
# for ((i=0; i < ${#CLIENTS[@]}; i++)); do
#     echo "Updating key for ${CLIENTS[$i]}"
#     ssh-keygen -f "/home/petar/.ssh/known_hosts" -R "${USER}${CLIENTS[$i]}${MACHINE}"
# done

# SSH into Middleware VM and get the Internal IP
echo "Fetching Middleware IP address"
MIDDLEWARE_IP=$(ssh -T ${USER}@${USER}${MIDDLEWARE}${MACHINE} "cat asl/internalip.log")

# SSH AND START CLIENTS
for ((i=0; i < ${#CLIENTS[@]}; i++)); do
echo "RUNNING ${CLIENTS[$i]}"
ssh -T "${USER}@${USER}${CLIENTS[$i]}${MACHINE}" << EOF
    cd $MEM_FOLDER
    nohup ./memaslap -s ${MIDDLEWARE_IP}:9090 -T 64 -c 64 -o 0.99 -S "1s" -t "60m" -F $WORK_CONFIG > "/home/ivanovpe/stability${i}.log" &
EOF
done

echo "CLIENTS RUNNING"

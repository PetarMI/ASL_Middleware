#!/bin/bash

# Init all machine names
SERVERS=(
         "foraslvms4"
         "foraslvms5"
         "foraslvms6"
         "foraslvms7"
         "foraslvms8"
         "foraslvms9"
         "foraslvms10"
         )

MIDDLEWARE="foraslvms11"

USER="ivanovpe"
MACHINE='.westeurope.cloudapp.azure.com'

# Start the Server VMs
for ((i=0; i < ${#SERVERS[@]}; i++)); do
  azure vm start "FOR_ASL" ${SERVERS[$i]}
done

# Start the middleware
azure vm start "FOR_ASL" ${MIDDLEWARE}

sleep 60

# Update SSH key before connecting to the VM
for ((i=0; i < ${#SERVERS[@]}; i++)); do
  echo "UPDATING SSH KEY FOR ${SERVERS[$i]}"
  ssh-keygen -f "/home/petar/.ssh/known_hosts" -R "${USER}${SERVERS[$i]}${MACHINE}"
done

echo "UPDATING SSH KEY FOR MIDDLEWARE"
ssh-keygen -f "/home/petar/.ssh/known_hosts" -R "${USER}${MIDDLEWARE}${MACHINE}"

# Connect once to all machines
for ((i=0; i < ${#SERVERS[@]}; i++)); do
ssh -T "${USER}@${USER}${SERVERS[$i]}${MACHINE}" << 'EOF'
    echo "Getting Internal IP"
    ip route get 8.8.8.8 | awk "{print \$NF; exit}" > "ipinternal.log";
EOF
done

# echo "SENDING SOURCES TO VM"
# scp -r src/ "${USER}@${USER}${MIDDLEWARE}${MACHINE}:/home/ivanovpe/asl"

# Connect to middleware
echo "Saving Middleware VM internal IP"
ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" << "EOF"
    cd asl/
    echo "BUILDING APPLICATION ON VM"
    ant | tail -2
    echo "SAVING LOCAL ADDRESS"
    ip route get 8.8.8.8 | awk "{print \$NF; exit}" > "internalip.log"
    cat "internalip.log"
EOF
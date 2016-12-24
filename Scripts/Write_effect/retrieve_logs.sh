#!/bin/bash

# Init all machine names
CLIENTS=("foraslvms1"
         "foraslvms2"
         "foraslvms3"
         # "foraslvms4"
         # "foraslvms5"
         )

MIDDLEWARE="foraslvms11"

USER="ivanovpe"
MACHINE='.westeurope.cloudapp.azure.com'

#echo "SSH INTO MIDDLEWARE"
ssh -T "${USER}@${USER}${MIDDLEWARE}${MACHINE}" << 'EOF'
    echo "STOPPING SERVICE"
    sudo pkill java
EOF

echo "Transfering LOG file"
scp -r "${USER}@${USER}${MIDDLEWARE}${MACHINE}:/home/ivanovpe/MaxTps/" "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/Write_Effect"

echo "Transfering client Logs"

# SSH AND START CLIENTS
for ((i=0; i < ${#CLIENTS[@]}; i++)); do
    scp -r "${USER}@${USER}${CLIENTS[$i]}${MACHINE}:/home/ivanovpe/tps_logs" "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/Write_Effect"
done
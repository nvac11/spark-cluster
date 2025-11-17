#!/bin/bash

# Exporte le nom d'hôte pour que docker-compose puisse le lire
export HOSTNAME=$(hostname)

if [ ! -f master.ip ]; then
    echo "➡️ MASTER = $HOSTNAME"
    echo $HOSTNAME > master.ip
    export SPARK_MODE=master
    export SPARK_MASTER_URL="" # Inutile pour le master, mais clair
else
    MASTER_NAME=$(cat master.ip)
    echo "➡️ WORKER → Master = $MASTER_NAME"
    export SPARK_MODE=worker
    export SPARK_MASTER_URL="spark://$MASTER_NAME:7077"
fi

docker compose build
docker compose up -d
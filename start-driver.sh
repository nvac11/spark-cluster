#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./start-driver.sh <IP_MASTER>"
    exit 1
fi

MASTER_IP="$1"
NAME=driver

echo "[DRIVER] Suppression de l'ancien conteneur..."
docker rm -f $NAME 2>/dev/null || true

echo "[DRIVER] Lancement du job Spark sur spark://$MASTER_IP:7077..."

docker run \
  --name $NAME \
  --network host \
  -e SPARK_MASTER_URL="spark://$MASTER_IP:7077" \
  -e SPARK_EXECUTOR_MEMORY="${SPARK_EXECUTOR_MEMORY:-8g}" \
  -e SPARK_DRIVER_MEMORY="${SPARK_DRIVER_MEMORY:-4g}" \
  -e SPARK_EXECUTOR_CORES="${SPARK_EXECUTOR_CORES:-2}" \
  -e SPARK_TASKS_PER_CORE="${SPARK_TASKS_PER_CORE:-1}" \
  -e SPARK_MIN_PARTITIONS="${SPARK_MIN_PARTITIONS:-8}" \
  spark-driver

echo "[DRIVER] Job terminé."

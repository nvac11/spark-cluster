#!/bin/bash
set -e

NAME="driver"

# Détection IP de la machine locale
DRIVER_IP=$(./detect_ip.sh)

# IP master fournie en paramètre → prioritaire
if [[ -n "$1" ]]; then
    MASTER_IP="$1"
else
    # Demande manuelle si pas d’argument
    read -p "[DRIVER] IP MASTER ? : " MASTER_IP
fi

echo "[DRIVER] Driver IP = $DRIVER_IP"
echo "[DRIVER] Master = spark://$MASTER_IP:7077"

echo "[DRIVER] Suppression ancien conteneur..."
docker rm -f $NAME 2>/dev/null || true

echo "[DRIVER] Lancement du job Spark..."

docker run \
  --name $NAME \
  --network host \
  -e SPARK_LOCAL_IP="$DRIVER_IP" \
  -e SPARK_MASTER_URL="spark://$MASTER_IP:7077" \
  -e SPARK_EXECUTOR_MEMORY="${SPARK_EXECUTOR_MEMORY:-12g}" \
  -e SPARK_DRIVER_MEMORY="${SPARK_DRIVER_MEMORY:-12g}" \
  -e SPARK_EXECUTOR_CORES="${SPARK_EXECUTOR_CORES:-3}" \
  -e SPARK_TASKS_PER_CORE="${SPARK_TASKS_PER_CORE:-1}" \
  -e SPARK_MIN_PARTITIONS="${SPARK_MIN_PARTITIONS:-80}" \
  -e SPARK_CORES_MAX="${SPARK_CORES_MAX:-3}" \
  spark-driver



echo "[DRIVER] Job terminé."

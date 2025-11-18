#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./start-worker.sh <IP_MASTER>"
  exit 1
fi

MASTER_IP="$1"
NAME="worker1"

echo "[WORKER] Master : $MASTER_IP"

echo "[WORKER] Suppression de l'ancien conteneur..."
docker rm -f $NAME 2>/dev/null || true

echo "[WORKER] Démarrage du conteneur..."
docker run -d \
  --name $NAME \
  --network host \
  -e SPARK_MASTER_URL="spark://$MASTER_IP:7077" \
  spark-worker

echo "[WORKER] OK → connecté à spark://$MASTER_IP:7077"

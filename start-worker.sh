#!/bin/bash
set -e

NAME="worker1"

# Détecte IP LAN de la machine
WORKER_IP=$(hostname -I | awk '{print $1}')

if [ -z "$1" ]; then
    echo "Usage: ./start-worker.sh <IP_MASTER>"
    exit 1
fi

MASTER_IP="$1"

echo "[WORKER] IP locale détectée : $WORKER_IP"
echo "[WORKER] Connexion au master : $MASTER_IP"

echo "[WORKER] Suppression de l'ancien conteneur..."
docker rm -f $NAME >/dev/null 2>&1 || true

echo "[WORKER] Démarrage du conteneur..."
docker run -d \
  --name $NAME \
  --network host \
  -e SPARK_MASTER_URL="spark://$MASTER_IP:7077" \
  -e SPARK_LOCAL_IP="$WORKER_IP" \
  spark-worker

echo "[WORKER] LANCÉ → Worker annoncé sous $WORKER_IP"

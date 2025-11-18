#!/bin/bash
set -e

NAME=master

# IP LAN de la machine qui héberge le master
HOST_IP=${1:-$(hostname -I | awk '{print $1}')}

echo "[MASTER] IP détectée : $HOST_IP"
echo "[MASTER] Suppression de l'ancien conteneur..."
docker rm -f $NAME 2>/dev/null || true

echo "[MASTER] Démarrage du conteneur..."
docker run -d \
  --name $NAME \
  --network host \
  -e MASTER_HOST="$HOST_IP" \
  -e MASTER_PORT=7077 \
  -e MASTER_WEBUI_PORT=8080 \
  spark-master

echo "[MASTER] Master : spark://$HOST_IP:7077"
echo "[MASTER] Web UI : http://$HOST_IP:8080"

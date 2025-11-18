#!/bin/bash
set -e

NAME="driver"

# Détection de l’IP locale
DRIVER_IP=$(./detect_ip.sh)

# Détection automatique du master (ARP)
MASTER_IP=$(arp -a | grep -i "spark" | awk '{print $2}' | sed 's/[()]//')

# Si non trouvé → fallback
if [[ -z "$MASTER_IP" ]]; then
    echo "[DRIVER] Impossible de détecter le master automatiquement."
    read -p "IP MASTER ? : " MASTER_IP
fi

echo "[DRIVER] Driver IP = $DRIVER_IP"
echo "[DRIVER] Master = spark://$MASTER_IP:7077"

echo "[DRIVER] Suppression ancien conteneur..."
docker rm -f $NAME 2>/dev/null || true

echo "[DRIVER] Lancement du job sur spark://$MASTER_IP:7077..."

docker run \
  --name $NAME \
  --network host \
  -e SPARK_MASTER_URL="spark://$MASTER_IP:7077" \
  -e SPARK_EXECUTOR_MEMORY="${SPARK_EXECUTOR_MEMORY:-1g}" \
  -e SPARK_DRIVER_MEMORY="${SPARK_DRIVER_MEMORY:-1g}" \
  -e SPARK_EXECUTOR_CORES="${SPARK_EXECUTOR_CORES:-3}" \
  -e SPARK_TASKS_PER_CORE="${SPARK_TASKS_PER_CORE:-1}" \
  -e SPARK_MIN_PARTITIONS="${SPARK_MIN_PARTITIONS:-80}" \
  spark-driver

echo "[DRIVER] Job terminé."

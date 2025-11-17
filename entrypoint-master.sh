#!/bin/bash
set -e

MASTER_HOST=${MASTER_HOST:-192.168.2.137}
MASTER_PORT=${MASTER_PORT:-7077}
MASTER_WEBUI_PORT=${MASTER_WEBUI_PORT:-8080}

echo "==== Spark MASTER node ===="
echo "Host       : $MASTER_HOST"
echo "RPC port   : $MASTER_PORT"
echo "Web UI     : $MASTER_WEBUI_PORT"
echo "==========================="

# 1) Lancer le master Spark en arrière-plan
/opt/spark/bin/spark-class org.apache.spark.deploy.master.Master \
  --host "$MASTER_HOST" \
  --port "$MASTER_PORT" \
  --webui-port "$MASTER_WEBUI_PORT" &

MASTER_PID=$!

# 2) On laisse 5 secondes pour qu'il démarre
sleep 5

# 3) Lancer ton script Python comme driver
export SPARK_MASTER_URL="spark://${MASTER_HOST}:${MASTER_PORT}"
echo "Running app.py with SPARK_MASTER_URL=$SPARK_MASTER_URL"

python3 /app/app.py

echo "app.py finished, shutting down master..."
kill "$MASTER_PID" || true
wait "$MASTER_PID" || true

echo "Done. Exiting container."

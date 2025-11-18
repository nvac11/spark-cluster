#!/bin/bash
set -e

MASTER_HOST=${MASTER_HOST:-0.0.0.0}
MASTER_PORT=${MASTER_PORT:-7077}
MASTER_WEBUI_PORT=${MASTER_WEBUI_PORT:-8080}

echo "==== Spark MASTER node ===="
echo "Host       : $MASTER_HOST"
echo "RPC port   : $MASTER_PORT"
echo "Web UI     : $MASTER_WEBUI_PORT"
echo "==========================="

exec /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master \
  --host "$MASTER_HOST" \
  --port "$MASTER_PORT" \
  --webui-port "$MASTER_WEBUI_PORT"

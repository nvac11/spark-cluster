#!/bin/bash
set -e

if [ -z "$SPARK_MASTER_URL" ]; then
  echo "ERROR: SPARK_MASTER_URL is not set (e.g. spark://192.168.2.137:7077)"
  exit 1
fi

echo "==== Spark WORKER node ===="
echo "Connecting to master: $SPARK_MASTER_URL"
echo "==========================="

# Tu peux ajouter ici des options mémoire / CPU
/opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
  "$SPARK_MASTER_URL"

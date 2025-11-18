#!/bin/bash
set -e

export SPARK_ROLE=driver

# On attend que SPARK_MASTER_URL soit donné par start-driver.sh
if [ -z "$SPARK_MASTER_URL" ]; then
  echo "ERROR: SPARK_MASTER_URL is not set (ex: spark://192.168.2.137:7077)"
  exit 1
fi

echo "==== Spark DRIVER ===="
echo "Using master: $SPARK_MASTER_URL"
echo "======================"

exec /opt/spark/bin/spark-submit \
  --master "$SPARK_MASTER_URL" \
  /app/app.py

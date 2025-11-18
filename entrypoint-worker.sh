#!/bin/bash
set -e

# Force l’IP utilisée par Spark
if [ -n "$SPARK_LOCAL_IP" ]; then
    export SPARK_LOCAL_IP
fi

echo "Worker IP annoncée : $SPARK_LOCAL_IP"

/opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
    $SPARK_MASTER_URL

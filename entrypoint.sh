#!/bin/bash

# $HOSTNAME est maintenant passé depuis docker-compose
echo "Démarrage du conteneur sur l'hôte : $HOSTNAME"
echo "Mode de fonctionnement : $SPARK_MODE"

if [ "$SPARK_MODE" = "master" ]; then
    echo "➡️ Lancement du MASTER sur $HOSTNAME"
    exec /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master \
        --host $HOSTNAME --port 7077 --webui-port 8080

elif [ "$SPARK_MODE" = "worker" ]; then
    echo "➡️ Lancement d’un WORKER (connexion à $SPARK_MASTER_URL)"
    # Le worker utilise l'URL du master fournie
    exec /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
        $SPARK_MASTER_URL

else
    echo "ERREUR : La variable SPARK_MODE n'est pas définie ou est incorrecte."
    echo "Valeur reçue : '$SPARK_MODE'"
    exit 1
fi
Spark Distributed Cluster (Standalone Mode)
Ce projet déploie un cluster Apache Spark en mode standalone entièrement conteneurisé avec Docker :

1 Spark Master
1 ou plusieurs Spark Workers
1 Driver Python pour exécuter des applications PySpark
Possibilité d’ajouter des workers sur d’autres machines du même réseau local

Structure du projet
spark-cluster/
├── docker-compose.yml
├── Dockerfile.master
├── Dockerfile.worker
├── Dockerfile.driver
├── entrypoint-master.sh
├── entrypoint-worker.sh
├── master.ip                  # À modifier sur les machines distantes
├── app.py                     # Script d’exemple (test de scaling)
├── kddcup.data                # Jeu de données KDD Cup 1999
└── kdd_scaling.png            # Graphique généré (à récupérer)
Prérequis

Docker
Docker Compose (version récente)
Toutes les machines sur le même réseau local (WiFi ou Ethernet)

1. Lancer le cluster
``` bash
docker compose up -d
Vérifier que tout est démarré :
docker compose ps
```
2. Utiliser PySpark interactivement
docker exec -it spark-driver bash
puis à l’intérieur du container :
pyspark --master spark://spark-master:7077
3. Exécuter le script app.py
docker exec -it spark-driver python app.py
Le script charge le dataset KDD Cup, effectue des transformations et génère un graphique de scaling.
4. Récupérer le graphique
docker cp spark-driver:/app/kdd_scaling.png .
Le fichier kdd_scaling.png apparaît dans votre dossier courant.
5. Ajouter un Worker sur une autre machine
Sur la machine distante :

Installer Docker + Docker Compose
Copier tout le projet
Éditer master.ip et indiquer l’IP du Master, par exemple :
192.168.2.137
Lancer uniquement le worker :
``` bash
docker compose up -d worker
```

Le worker apparaît automatiquement dans l’interface http://<ip-master>:8080
6. Commandes utiles
Voir les logs :
``` bash
docker logs -f spark-master
docker logs -f spark-worker-1
docker logs -f spark-driver
```
Arrêter tout :
``` bash
docker compose down
```
Redémarrer :
``` bash
docker compose down && docker compose up -d
```

Nettoyage complet :
``` bash
docker compose down --volumes --remove-orphans
docker system prune -a --volumes
```

7. Ajuster les ressources Spark
Dans app.py, modifier par exemple :
``` python
conf.set("spark.executor.memory", "2g")
conf.set("spark.executor.cores", "2")
Allocation dynamique (fortement recommandé avec plusieurs workers) :
conf.set("spark.dynamicAllocation.enabled", "true")
conf.set("spark.dynamicAllocation.minExecutors", "1")
conf.set("spark.dynamicAllocation.maxExecutors", "20")
conf.set("spark.shuffle.service.enabled", "true")
```

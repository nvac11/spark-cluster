# Spark Distributed Cluster (Standalone Mode)

Ce projet déploie un **cluster Apache Spark** en mode *standalone*, entièrement conteneurisé avec **Docker**.  
Il permet d’exécuter des applications PySpark en distribuant la charge sur plusieurs machines du même réseau local.

## 📌 Architecture du cluster

- **1 Spark Master**
- **1 ou plusieurs Spark Workers**
- **1 Driver Python** pour exécuter les applications PySpark
- Possibilité d’ajouter facilement des workers sur d’autres machines du réseau (Wi-Fi ou Ethernet)

Le script principal charge le dataset **KDD Cup**, effectue des transformations et génère un graphique de scaling.

---

## 🛠️ Prérequis

- **Docker** installé sur toutes les machines
- Toutes les machines connectées au **même réseau local**
- Dataset **KDD Cup** disponible dans le projet ou récupéré via script

---

## 🚀 Construction et lancement du cluster

### 1. Builder les images Docker

```bash
docker build -t spark-master -f Dockerfile.master .
docker build -t spark-worker -f Dockerfile.worker .
docker build -t spark-driver -f Dockerfile.driver .
./start-master.sh
./start-worker.sh
./start-driver.sh
```
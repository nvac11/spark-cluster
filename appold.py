from pyspark.sql import SparkSession
import random

# --- Configurations de l'application Spark (Optimisation 40 Cœurs) ---
# Si vous êtes sur un cluster Standalone, utilisez 'spark://alfa:7077'
MASTER_URL = "spark://alfa:7077" 
APP_NAME = "MaxedOutSparkJob"

# 1. Ressources par Executor :
# C'est souvent plus efficace d'utiliser 4-5 cœurs par Executor pour une bonne isolation JVM.
EXECUTOR_CORES = "4" 

# 2. Nombre d'Executors :
# Pour 40 cœurs : 40 / 4 cœurs/Executor = 10 Executors.
# Note : Sur un cluster, vous pouvez définir le nombre total d'Executors 
# via la commande `spark-submit --num-executors 10` ou le paramètre `spark.dynamicAllocation.maxExecutors`. 
# Nous définissons ici les ressources par Executor.

# 3. Mémoire : Allouez une quantité substantielle de mémoire par Executor.
EXECUTOR_MEMORY = "8g" # 8 Go par Executor est une bonne base pour les tâches lourdes.
DRIVER_MEMORY = "8g"   # Mémoire pour le Driver.

# 4. Parallélisme (Partitions de Shuffle) :
# Le parallélisme doit être supérieur au nombre total de cœurs.
# 40 cœurs * 2 = 80 partitions est un bon point de départ.
DEFAULT_PARALLELISM = "800" 

# --- Paramètres de l'ensemble de données ---
NUM_ELEMENTS = 5_000_000_000 # 5 Milliards d'éléments (comme votre exemple initial)
NUM_PARTITIONS = 80         # Le nombre de partitions initiales est clé pour la parallélisation

# --- Initialisation de SparkSession avec les configurations d'optimisation ---
spark = SparkSession.builder \
    .appName(APP_NAME) \
    .master(MASTER_URL) \
    .config("spark.executor.memory", EXECUTOR_MEMORY) \
    .config("spark.executor.cores", EXECUTOR_CORES) \
    .config("spark.driver.memory", DRIVER_MEMORY) \
    .config("spark.default.parallelism", DEFAULT_PARALLELISM) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- Création et Traitement du RDD (Opération gourmande en ressources) ---
print(f"--- Préparation de {NUM_ELEMENTS:,} éléments sur {NUM_PARTITIONS} partitions ---")

# Création du RDD avec un nombre de partitions adapté (80)
data_rdd = spark.sparkContext.parallelize(range(NUM_ELEMENTS), NUM_PARTITIONS)

# Opération : map (calcul du carré) et reduceByKey (shuffle et agrégation)
# Cette opération garantit une charge de travail importante pour tous les Executors.
processed_rdd = data_rdd.map(lambda x: (x % 100, x * x))

print(f"--- DÉBUT DU CALCUL INTENSIF (Shuffle sur {DEFAULT_PARALLELISM} partitions) ---")
sum_by_key = processed_rdd.reduceByKey(lambda a, b: a + b)

# Récupération du résultat (petit, car seulement 100 clés)
final_result = sum_by_key.collect()

print("--- FIN DU CALCUL ---")
print(f"Nombre de résultats (clés) : {len(final_result)}")

# Arrêter la session Spark
spark.stop()
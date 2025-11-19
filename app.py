import time
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, isnan
from pyspark.sql.types import DoubleType, BooleanType

from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# ==========================================================
# SPARK CLUSTER CONFIG 
# ==========================================================

def getenv_or(name, default=None):
    v = os.getenv(name)
    return v if v not in (None, "") else default

spark_master = getenv_or("SPARK_MASTER_URL")  # injecté par les scripts/containers

builder = SparkSession.builder.appName("Scalability-Baseline-Netflix")

# Si on connaît le master, on le fixe, sinon on laisse spark-submit décider
if spark_master:
    builder = builder.master(spark_master)

executor_mem   = getenv_or("SPARK_EXECUTOR_MEMORY")
executor_cores = getenv_or("SPARK_EXECUTOR_CORES")
driver_mem     = getenv_or("SPARK_DRIVER_MEMORY")
log_level      = getenv_or("SPARK_LOG_LEVEL", "WARN")
max_cores      = getenv_or("SPARK_CORES_MAX")

# On n'impose des valeurs que si elles sont fournies
if executor_mem:
    builder = builder.config("spark.executor.memory", executor_mem)
if executor_cores:
    builder = builder.config("spark.executor.cores", executor_cores)
if driver_mem:
    builder = builder.config("spark.driver.memory", driver_mem)
if max_cores:
    builder = builder.config("spark.cores.max", max_cores)


spark = builder.getOrCreate()
sc = spark.sparkContext
sc.setLogLevel(log_level)

# Auto-détection des ressources du cluster
try:
    cluster_cores = sc.defaultParallelism
    if not cluster_cores or cluster_cores <= 0:
        raise ValueError
except Exception:
    cluster_cores = int(getenv_or("SPARK_FALLBACK_CORES", "4"))

tasks_per_core = int(getenv_or("SPARK_TASKS_PER_CORE", "2"))
min_partitions = getenv_or("SPARK_MIN_PARTITIONS")

if min_partitions:
    min_partitions = int(min_partitions)
    target_partitions = max(cluster_cores * tasks_per_core, min_partitions)
else:
    target_partitions = cluster_cores * tasks_per_core

spark.conf.set("spark.default.parallelism", target_partitions)
spark.conf.set("spark.sql.shuffle.partitions", target_partitions)

# ==========================================================
# 1. Charger et préparer le dataset Netflix
# ==========================================================

csv_path = "netflix_cleaned_20251011_141144.csv"

df_base = (
    spark.read.option("header", "true").csv(csv_path)
    .select(
        "subscription_plan", "watch_duration_minutes", "progress_percentage",
        "age", "monthly_spend", "device_type", "action", "quality",
        "user_rating", "genre_primary", "is_active"
    )
)

# Casts
df_base = df_base \
    .withColumn("watch_duration_minutes", col("watch_duration_minutes").cast(DoubleType())) \
    .withColumn("progress_percentage",    col("progress_percentage").cast(DoubleType())) \
    .withColumn("age",                    col("age").cast(DoubleType())) \
    .withColumn("monthly_spend",          col("monthly_spend").cast(DoubleType())) \
    .withColumn("is_active",              col("is_active").cast(BooleanType()))

# Boolean → 0/1
df_base = df_base.withColumn(
    "is_active_num",
    when(col("is_active") == True, 1.0).otherwise(0.0)
).drop("is_active")

# Imputation
num_cols = ["watch_duration_minutes", "progress_percentage", "age", "monthly_spend", "is_active_num"]
cat_cols = ["device_type", "action", "quality", "user_rating", "genre_primary"]

for c in num_cols:
    df_base = df_base.withColumn(
        c,
        when(col(c).isNull() | isnan(col(c)), 0.0).otherwise(col(c))
    )

for c in cat_cols:
    df_base = df_base.withColumn(
        c,
        when(col(c).isNull(), "unknown").otherwise(col(c))
    )

df_base = df_base.cache()
original_count = df_base.count()
print(f"Dataset Netflix de base : {original_count:,} lignes")

# ==========================================================
# 2. Pipeline (DecisionTreeClassifier)
# ==========================================================

target = "subscription_plan"

indexers = [
    StringIndexer(inputCol=c, outputCol=c + "_idx", handleInvalid="keep")
    for c in cat_cols
]

assembler = VectorAssembler(
    inputCols=[c + "_idx" for c in cat_cols] + num_cols,
    outputCol="features",
    handleInvalid="keep"
)

label_indexer = StringIndexer(
    inputCol=target,
    outputCol="label",
    handleInvalid="keep"
)

dt = DecisionTreeClassifier(
    labelCol="label",
    featuresCol="features",
    seed=42
)

pipeline = Pipeline(stages=indexers + [assembler, label_indexer, dt])

# ==========================================================
# 3. Multiplier le dataset par 32
# ==========================================================

df_big = df_base
for i in range(5):  # 2^5 = 32
    df_big = df_big.unionByName(df_big)

df_big = df_big.repartition(target_partitions).cache()
big_count = df_big.count()
factor = big_count / original_count if original_count > 0 else float("nan")
print(f"Dataset étendu : {big_count:,} lignes (facteur ≈ {factor:.1f}x)")

# ==========================================================
# 4. Entraînement + mesure du temps (DecisionTree)
# ==========================================================

print("\n=== Entraînement DecisionTree sur dataset 32 ===")
start_time = time.time()
model = pipeline.fit(df_big)
end_time = time.time()

train_duration = end_time - start_time
print(f"Temps d'entraînement DecisionTree sur dataset 32 : {train_duration:.2f} secondes\n")

# ==========================================================
# 5. Évaluation (Accuracy)
# ==========================================================

# On applique le modèle sur les données d'entraînement (ou df_base) pour évaluer
predictions = model.transform(df_big)

evaluator = MulticlassClassificationEvaluator(
    labelCol="label", 
    predictionCol="prediction", 
    metricName="accuracy"
)

accuracy = evaluator.evaluate(predictions)
print(f"Accuracy du modèle : {accuracy:.4f}")
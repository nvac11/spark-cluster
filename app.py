import time
import matplotlib.pyplot as plt
import numpy as np
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, isnan, lit
from pyspark.sql.types import DoubleType

from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import DecisionTreeClassifier


# ==========================================================
# SPARK CLUSTER CONFIG
# ==========================================================

spark = (
    SparkSession.builder
    .appName("KDDCup-Scaling")
    .master("spark://alfa:7077")              # cluster standalone
    .config("spark.executor.memory", "8g")
    .config("spark.executor.cores", 4)
    .config("spark.driver.memory", "8g")
    .config("spark.default.parallelism", "400")
    .config("spark.sql.shuffle.partitions", "400")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# ==========================================================
# KDD CUP COLUMN NAMES
# ==========================================================

kdd_cols = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes","land",
    "wrong_fragment","urgent","hot","num_failed_logins","logged_in","num_compromised",
    "root_shell","su_attempted","num_root","num_file_creations","num_shells",
    "num_access_files","num_outbound_cmds","is_host_login","is_guest_login",
    "count","srv_count","serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate",
    "same_srv_rate","diff_srv_rate","srv_diff_host_rate","dst_host_count",
    "dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate","dst_host_serror_rate",
    "dst_host_srv_serror_rate","dst_host_rerror_rate","dst_host_srv_rerror_rate",
    "label"
]

numeric_cols = [
    "duration","src_bytes","dst_bytes","wrong_fragment","urgent","hot",
    "num_failed_logins","logged_in","num_compromised","root_shell","su_attempted",
    "num_root","num_file_creations","num_shells","num_access_files",
    "num_outbound_cmds","is_host_login","is_guest_login","count","srv_count",
    "serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate",
    "same_srv_rate","diff_srv_rate","srv_diff_host_rate","dst_host_count",
    "dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate","dst_host_srv_diff_host_rate",
    "dst_host_serror_rate","dst_host_srv_serror_rate","dst_host_rerror_rate",
    "dst_host_srv_rerror_rate"
]

cat_cols = ["protocol_type", "service", "flag", "land"]


# ==========================================================
# LOAD KDD CUP AND PREPARE MINI BASE DATASET (scalable)
# ==========================================================

df = spark.read.csv("kddcup.data", header=False).toDF(*kdd_cols)

# cast + impute
for c in numeric_cols:
    df = df.withColumn(c, col(c).cast(DoubleType()))
    df = df.withColumn(c, when(col(c).isNull() | isnan(col(c)), 0.0).otherwise(col(c)))

for c in cat_cols:
    df = df.withColumn(c, when(col(c).isNull(), "unknown").otherwise(col(c)))

df.cache()
full_count = df.count()
print(f"Dataset KDD Cup complet chargé : {full_count:,} lignes")

# on prend une base de 50k (accélère scaling mais reste réel)
BASE_SIZE = 50_000
df_base = df.limit(BASE_SIZE).cache()


# ==========================================================
# BUILD LIGHT PIPELINE (fast training)
# ==========================================================

indexers = [StringIndexer(inputCol=c, outputCol=c+"_idx", handleInvalid="keep")
            for c in cat_cols + ["label"]]

assembler = VectorAssembler(
    inputCols=[c+"_idx" for c in cat_cols] + numeric_cols,
    outputCol="features"
)

classifier = DecisionTreeClassifier(
    labelCol="label_idx",
    featuresCol="features",
    maxDepth=5,
    maxBins=64,
    seed=42
)

pipeline = Pipeline(stages=indexers + [assembler, classifier])


# ==========================================================
# SCALING EXPERIMENT
# ==========================================================

MULTIPLIERS = [1, 2, 4, 8, 16, 32]
BASE_DATASET_GB = 0.025  # estimation 50k ≈ 25MB

sizes = []
times = []

print("\n=== SCALING EXPERIMENT ON REAL KDD CUP ===")
print(f"{'Mult':<6} {'Rows':>10} {'GB':>8} {'Time(s)':>10} {'Rate (GB/s)':>12}")
print("-" * 60)

for m in MULTIPLIERS:

    df_big = df_base.crossJoin(
        spark.range(m).select(lit(1).alias("x"))
    ).drop("x").repartition(200)

    row_count = df_big.count()
    size_gb = BASE_DATASET_GB * m

    start = time.time()
    pipeline.fit(df_big)
    elapsed = time.time() - start

    rate = size_gb / elapsed

    print(f"x{m:<5} {row_count:>10,} {size_gb:>8.3f} {elapsed:>10.2f} {rate:>12.3f}")

    sizes.append(size_gb)
    times.append(elapsed)


# ==========================================================
# SAVE SCALABILITY PLOT
# ==========================================================

sizes = np.array(sizes)
times = np.array(times)

scale_factor = sizes / sizes[0]
exec_factor = times / times[0]

plt.figure(figsize=(10, 6))

plt.plot(
    sizes, scale_factor, color="red", marker="^",
    linewidth=2.5, markersize=10, label="Dataset size (scale factor)"
)

plt.plot(
    sizes, exec_factor, color="blue", marker="o",
    linewidth=3, markersize=9, label="Execution time (normalized)"
)

plt.xlabel("Dataset size (GB)", fontsize=14)
plt.ylabel("Scale factor", fontsize=14)
plt.title("Pipeline scalability on KDD Cup (distributed)", fontsize=16)
plt.grid(True, linestyle="--", alpha=0.7)
plt.legend()

OUTPUT_FILE = "kdd_scaling.png"
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=240)
plt.close()

print(f"\nGraphique sauvegardé → {os.path.abspath(OUTPUT_FILE)}\n")

spark.stop()
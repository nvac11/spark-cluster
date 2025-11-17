from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("DistributedTest") \
    .master("spark://alfa:7077") \
    .getOrCreate()

rdd = spark.sparkContext.parallelize(range(5_000_000_000), 12)

print("--- DEBUT DU CALCUL ---")
print("COUNT =", rdd.count())
print("--- FIN DU CALCUL ---")

spark.stop()
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

spark = SparkSession.builder \
    .master("local") \
    .appName("PySpark Installation Test") \
    .config("spark.hadoop.fs.permissions", "false") \
    .getOrCreate()

marvin_data = None
data_DF = spark.createDataFrame([marvin_data])
data_DF = data_DF.withColumn("shape", explode(col("shape")))

data_DF.show()

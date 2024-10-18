import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
from api.Marvin_data_exporter import MarvinDataExporter

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

spark = SparkSession.builder \
    .master("local") \
    .appName("PySpark Installation Test") \
    .config("spark.hadoop.fs.permissions", "false") \
    .getOrCreate()

map_list = [
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gflux', 'ha_6564'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gflux', 'hb_4862'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gvel', 'ha_6564'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gsigma', 'ha_6564'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gew', 'ha_6564'),
        ('12772-12705', 'SPX', 'MILESHC-MASTARSSP', 'emline_gew', 'hb_4862'),
    ]

for map_name, property_name, channel in map_list:
    marvin_exporter = MarvinDataExporter()
    marvin_exporter.fetch_and_store(map_list)
    path_base = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'landing')
    path_map_name = os.path.join(path_base, map_name)
    path = os.path.join(path_map_name, f"{map_name}-{property_name}_{channel}.json")
    data_DF = spark.read.json(path)
    data_DF.show()

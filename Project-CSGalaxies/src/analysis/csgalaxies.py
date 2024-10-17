from api.MarvinClient import Marvin
import pyspark
from pyspark.sql import SparkSession
import json

# Inicializa a SparkSession
spark = SparkSession.builder.master("local[*]").getOrCreate()

# Cria uma instância da classe Marvin
marvin = Marvin()

# Obtém os dados da API
marvin_map = marvin.get_api('8485-1901', 'SPX', 'MILESHC-MASTARSSP')

# Agora marvin_map deve conter os dados retornados pela API
# Se marvin_map for um dicionário ou lista, você pode criar um DataFrame assim:
if isinstance(marvin_map, dict):
    # Converte o dicionário para uma lista com um único item
    df = spark.read.json(spark.sparkContext.parallelize([json.dumps(marvin_map)]))
elif isinstance(marvin_map, list):
    # Se for uma lista, converta-a diretamente para DataFrame
    df = spark.read.json(spark.sparkContext.parallelize(marvin_map))

# Exibe o esquema e os dados
df.printSchema()
df.show()

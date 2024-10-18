import os
import sys
import shutil

from api.MarvinClient import Marvin
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

# Configurações do PySpark
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# Iniciando SparkSession
spark = SparkSession.builder \
    .master("local") \
    .appName("PySpark Installation Test") \
    .config("spark.hadoop.fs.permissions", "false") \
    .getOrCreate()

# Obtendo dados do Marvin API
marvin = Marvin()
map_name = '8485-1901'
marvin_data = marvin.get_api(map_name, 'SPX', 'MILESHC-MASTARSSP')

# Criando DataFrame e explodindo a coluna "shape"
data_DF = spark.createDataFrame([marvin_data])
data_DF = data_DF.withColumn("shape", explode(col("shape")))

# Mostrando os dados
data_DF.show()

# Salvando em um diretório temporário como uma única partição
temp_dir = f"../data/landing/temp_{map_name}"
data_DF.coalesce(1).write.csv(temp_dir, sep=';', mode='overwrite', header=True)

# Encontrando o arquivo CSV gerado e renomeando
for file_name in os.listdir(temp_dir):
    if file_name.endswith(".csv"):
        # Movendo o arquivo CSV para o destino final com o nome correto
        shutil.move(os.path.join(temp_dir, file_name), f"../data/landing/{map_name}.csv")
        break

# Remover o diretório temporário
shutil.rmtree(temp_dir)

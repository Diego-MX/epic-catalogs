# Databricks notebook source
# MAGIC %md
# MAGIC # Conexión de _SQL Azrue_ con _Databricks_
# MAGIC
# MAGIC Se realiza para dar estabilidad a la información proveniente de la fuente original (_excel_).
# MAGIC
# MAGIC Acciones necesarias para hacer uso de la base de datos:
# MAGIC
# MAGIC   - Creación de un scope llamado: **_sql-catallogs-feathers_**
# MAGIC       - Dicho _scope_ contiene las siguientes llaves con sus respectivos secretos:
# MAGIC           - _Key_=>**_dbcUsername_**, _Secret_=>**_admin-data_** 
# MAGIC           - _Key_=>**_dbcPasword_**, _Secret_=>**_ACCESS_**  
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ##Adquisición de ingredientes

# COMMAND ----------

import prueba_config as cfg 
from pyspark.dbutils import DBUtils
from pyspark.sql import SparkSession
import pandas as pd

# COMMAND ----------

# MAGIC %md
# MAGIC ## Preparación de ingredientes

# COMMAND ----------

spark=SparkSession.builder.getOrCreate()
dbutils=DBUtils(spark)

env=cfg.ENV
user=cfg.RESOURCES_AZURE[env]["sql-catallogs-feathers"]["user"]
key=cfg.RESOURCES_AZURE[env]["sql-catallogs-feathers"]["access"]

# COMMAND ----------

db_username=dbutils.secrets.get("sql-catallogs-feathers",user)
db_password=dbutils.secrets.get("sql-catallogs-feathers",key)
db_hostname="sql-lakehylia-dev.database.windows.net"
db_database="webapp_catalogs"
db_port=1433  # Puerto predeterminado para SQL Server

db_url = "jdbc:sqlserver://{0}:{1};database={2}".format(db_hostname, db_port, db_database)

# COMMAND ----------

connectionProperties = {
    "user" : db_username,
    "password" : db_password,
    "driver" : "com.microsoft.sqlserver.jdbc.SQLServerDriver"
}

# COMMAND ----------

def send_table_db(data_feather:pd, db_table: str, 
                  db_url: str, db_username: str, db_password: str):
    spark_df = spark.createDataFrame(data_feather)

    spark_df.write.format('jdbc')\
            .options(url=db_url, 
                    dbtable= f"{db_table}", 
                    user= db_username, 
                    password = db_password)\
            .mode('overwrite').save()

    return 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Preparación de los alimentos
# MAGIC **Se manda llamar una base de datos**

# COMMAND ----------

jdbcDF = spark.read \
    .format("jdbc") \
    .option("url", db_url) \
    .option("dbtable", "dbo.Pruebas") \
    .option("user", db_username) \
    .option("password", db_password) \
    .load()

jdbcDF.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **Envio de un dataframe a una base de datos**

# COMMAND ----------

databricks_user = "juan.v@bineo.com" 
rt_feather = f"file:/Workspace/Repos/{databricks_user}/data-prod-catalogs/refs/catalogs/"
rt_usr = dbutils.fs.ls(rt_feather)

l_files=["national-banks.feather","national-banks-bins.feather",
         "national-banks-acquiring.feather","codigos_drive_tipo_asentamientos.feather",
         "codigos_drive_ciudades.feather","codigos_drive_municipios.feather",
         "codigos_drive.feather","estados_claves.csv"]

for file in rt_usr:
    if file.name in l_files:
        if file.name.endswith(".csv"):
            file_name=file.name.split(".")[0]
            data_feather = pd.read_csv(file.path)
            send_table_db(data_feather,file_name,db_url,db_username,db_password)

        elif file.name.endswith(".feather"):
            file_name=file.name.split(".")[0].replace("-","_")
            data_feather=pd.read_feather(file.path)
            send_table_db(data_feather,file_name,db_url,db_username,db_password)

        else:
            print("Hay otro tipo de archivo que NO ES DE INTERES")

from pyspark.dbutils import DBUtils 
from pyspark.sql import (functions, GroupedData, DataFrame,SparkSession)

spark = SparkSession.builder.getOrCreate()
dbutils = DBUtils(spark)

a=dbutils.secrets.listScopes()

for i in a:
    print(i)

print("")

b=dbutils.secrets.list("sql-catallogs-feathers")

for i in b:
    print(i)

print("")

c=dbutils.secrets.get(scope="sql-catallogs-feathers",key="dbcPassword")
# aplica un for para sacar la información
d=dbutils.secrets.get(scope="sql-catallogs-feathers",key="dbcUsername")


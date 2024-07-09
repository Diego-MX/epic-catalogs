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

salva=""
for i in c:
    salva=salva+i+","

print(salva)

print("")

d=dbutils.secrets.get(scope="sql-catallogs-feathers",key="dbcUsername")

salve=""
for i in d:
    salve=salve+i+","

print(salve)

print("")

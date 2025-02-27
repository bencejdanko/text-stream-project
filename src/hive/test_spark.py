from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("KafkaToHive") \
    .config("hive.metastore.uris", "thrift://localhost:9083") \
    .config("spark.sql.catalogImplementation", "hive") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sql("SHOW TABLES").show()
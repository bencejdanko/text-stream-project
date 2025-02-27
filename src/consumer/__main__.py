from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, StructField
from pyhive import hive
from hive_utils.hive_writer import HiveWriter
import pandas as pd

from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import udf
from pyspark.ml.clustering import KMeans
from pyspark.sql.types import ArrayType, StringType
from pyspark.ml import Pipeline
from pyspark.sql.functions import when

from pyhive import hive

import json

import argparse

HIVE_PORT = None
HIVE_TABLE = None


def cluster_batch(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    batch_df = batch_df.filter(col("chunk").isNotNull())  # Filter out null chunks
    
    model = pipeline.fit(batch_df)
    clustered_df = model.transform(batch_df)
    with hive.Connection(host='localhost', port=HIVE_PORT) as conn:
            with conn.cursor() as cursor:
                for row in clustered_df.collect():
                    cursor.execute(f"""
                        INSERT INTO {HIVE_TABLE} VALUES 
                        ('{row.agent_id}', '{row.destination_uri}', '{row.event_time}', '{row.chunk}', '{row.cluster}')
                    """)

def load_schema_from_json(file_path):
    with open(file_path, 'r') as f:
        schema_json = json.load(f)
    fields = [StructField(field['name'], StringType(), True) for field in schema_json['fields']]
    return StructType(fields)

if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Consume the messages at a specified kafka broker in parquet, and either store them locally, or write to a HIVE table.")
    parser.add_argument("--schema-file", type=str, help="Path to the JSON schema file.", required=True)
    parser.add_argument("--kafka-broker-port", type=str, help="Kafka broker to write logs to.", required=True)
    parser.add_argument("--topic", type=str, help="Kafka topic to write to.", required=True)
    parser.add_argument("--hive-port", type=str, required=True, help="Hive metastore port.")
    parser.add_argument("--hive-table", type=str, required=True, help="Hive table name.")
    parser.add_argument("--logs-dir", type=str, help="Directory to store logs in parquet format.")

    args = parser.parse_args()

    SCHEMA_FILE = args.schema_file
    KAFKA_BROKER_PORT = args.kafka_broker_port
    KAFKA_TOPIC = args.topic

    HIVE_PORT = args.hive_port
    HIVE_TABLE = args.hive_table

    LOGS_DIR = args.logs_dir

    json_schema = load_schema_from_json(SCHEMA_FILE)
    
    spark = SparkSession.builder \
        .appName("KafkaJSONConsumer") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
        .getOrCreate()
    
    ###############################
    ### Spark ML Pipeline Setup ###
    ###############################

    # Tokenizer to split text into words, ensure that 
    tokenizer = Tokenizer(inputCol="chunk", outputCol="words")

    # HashingTF for feature extraction
    hashingTF = HashingTF(inputCol="words", outputCol="raw_features", numFeatures=1000)

    # IDF to scale TF values
    idf = IDF(inputCol="raw_features", outputCol="features")

    # KMeans clustering
    kmeans = KMeans(k=5, seed=42, featuresCol="features", predictionCol="cluster")

    pipeline = Pipeline(stages=[tokenizer, hashingTF, idf, kmeans])

    print(f"\033[92mSUBSCRIBING TO KAFKA TOPIC: {KAFKA_TOPIC} AT BROKER: {KAFKA_BROKER_PORT}\033[0m")
    # Read from Kafka topic
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", f"127.0.0.1:{KAFKA_BROKER_PORT}") \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON data, ensure that chunk is not null
    df_parsed = df.selectExpr("CAST(value AS STRING) as json_value") \
        .select(from_json(col("json_value"), json_schema).alias("data")) \
        .select("data.*") \
        .withColumn("chunk", when(col("chunk").isNotNull(), col("chunk")).otherwise(""))
    
    query = df_parsed.writeStream \
        .outputMode("append") \
        .foreachBatch(cluster_batch) \
        .start()

    query.awaitTermination()

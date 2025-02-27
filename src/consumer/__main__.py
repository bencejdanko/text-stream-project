from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, StructField
import json

import argparse

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
    
    parser.add_argument("--hive-metastore-port", type=str, required=True, help="Hive metastore port.")
    parser.add_argument("--hive-db", type=str, required=True, help="Hive database.")
    parser.add_argument("--hive-table", type=str, required=True, help="Hive table name.")
    
    parser.add_argument("--logs-dir", type=str, help="Directory to store logs in parquet format.")

    args = parser.parse_args()

    SCHEMA_FILE = args.schema_file
    KAFKA_BROKER_PORT = args.kafka_broker_port
    KAFKA_TOPIC = args.topic

    HIVE_PORT = args.hive_metastore_port
    HIVE_DB = args.hive_db
    HIVE_TABLE = args.hive_table

    LOGS_DIR = args.logs_dir

    json_schema = load_schema_from_json(SCHEMA_FILE)

    # Initialize Spark session
    if HIVE_PORT:
        spark = SparkSession.builder \
            .appName("KafkaToHive") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
            .config("hive.metastore.uris", f"thrift://localhost:{HIVE_PORT}") \
            .config("spark.sql.catalogImplementation", "hive") \
            .enableHiveSupport() \
            .getOrCreate()
    else:
        spark = SparkSession.builder \
            .appName("KafkaJSONConsumer") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
            .getOrCreate()

    print(f"\033[92mSUBSCRIBING TO KAFKA TOPIC: {KAFKA_TOPIC} AT BROKER: {KAFKA_BROKER_PORT}\033[0m")
    # Read from Kafka topic
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", f"127.0.0.1:{KAFKA_BROKER_PORT}") \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    df_parsed = df.selectExpr("CAST(value AS STRING) as json_value") \
        .select(from_json(col("json_value"), json_schema).alias("data")) \
        .select("data.*")  # This flattens the structure

    # If logs-dir is specified, write to parquet
    if LOGS_DIR:
        query = df_parsed.writeStream \
            .outputMode("append") \
            .format("parquet") \
            .option("path", LOGS_DIR) \
            .option("checkpointLocation", "chk-point-dir") \
            .start()
        
    if HIVE_DB and HIVE_TABLE:
        # Write to Hive table
        query = df_parsed.writeStream \
            .outputMode("append") \
            .format("hive") \
            .option("checkpointLocation", "chk-point-dir") \
            .toTable(f"{HIVE_DB}.{HIVE_TABLE}")

    #Write to console
    query = df_parsed.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    query.awaitTermination()

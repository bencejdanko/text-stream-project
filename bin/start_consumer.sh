#!/bin/bash

# Initialize variables
SCHEMA_FILE=""
KAFKA_BROKER_PORT=""
TOPIC=""
HIVE_PORT=""
HIVE_DB=""
HIVE_TABLE=""
LOGS_DIR=""

# Use `getopt` for multi-character options
OPTIONS=$(getopt -o s:k:t:l: --long schema-file:,kafka-broker-port:,topic:,hive-metastore-port:,hive-db:,hive-table:,logs-dir: -n "$0" -- "$@")

if [ $? -ne 0 ]; then
    echo "Failed to parse options." >&2
    exit 1
fi

eval set -- "$OPTIONS"

while true; do
    case "$1" in
        -s|--schema-file) SCHEMA_FILE="$2"; shift 2 ;;
        -k|--kafka-broker-port) KAFKA_BROKER_PORT="$2"; shift 2 ;;
        -t|--topic) TOPIC="$2"; shift 2 ;;
        -l|--logs-dir) LOGS_DIR="$2"; shift 2 ;;
        --hive-metastore-port) HIVE_PORT="$2"; shift 2 ;;
        --hive-db) HIVE_DB="$2"; shift 2 ;;
        --hive-table) HIVE_TABLE="$2"; shift 2 ;;
        --) shift; break ;;
        *) echo "Invalid option: $1" >&2; exit 1 ;;
    esac
done

# Ensure required options are provided
if [ -z "$SCHEMA_FILE" ] || [ -z "$KAFKA_BROKER_PORT" ] || [ -z "$TOPIC" ]; then
    echo "Usage: $0 --schema-file <schema-file> --kafka-broker-port <port> --topic <topic> --hive-metastore-port <port> --hive-db <db> --hive-table <table> --logs-dir <logs>"
    exit 1
fi

python3 src/consumer/ --schema-file "$SCHEMA_FILE" --kafka-broker-port "$KAFKA_BROKER_PORT" --topic "$TOPIC" --hive-metastore-port "$HIVE_PORT" --hive-db "$HIVE_DB" --hive-table "$HIVE_TABLE" --logs-dir "$LOGS_DIR"

#!/bin/bash

# Initialize variables
SCHEMA_FILE=""
KAFKA_BROKER_PORT=""
TOPIC=""
HIVE_PORT=""
HIVE_DB=""
HIVE_TABLE=""
LOGS_DIR=""

while getopts "s:k:t:hp:hd:ht:l:" opt; do
    case $opt in
        s) SCHEMA_FILE="$OPTARG"
        ;;
        k) KAFKA_BROKER_PORT="$OPTARG"
        ;;
        t) TOPIC="$OPTARG"
        ;;
        hp) HIVE_PORT="$OPTARG"
        ;;
        hd) HIVE_DB="$OPTARG"
        ;;
        ht) HIVE_TABLE="$OPTARG"
        ;;
        l) LOGS_DIR="$OPTARG"
        ;;
        \?) echo "Invalid option -$OPTARG" >&2
                echo "Usage: $0 -s <schema-file> -k <kafka-broker-port> -t <topic> -hp <hive-port> -hd <hive-db> -ht <hive-table> -l <logs-dir>"
                exit 1
        ;;
    esac
done

# Check if the required arguments are provided
if [ -z "$SCHEMA_FILE" ] || [ -z "$KAFKA_BROKER_PORT" ] || [ -z "$TOPIC" ]; then
        echo "Usage: $0 -s <schema-file> -k <kafka-broker-port> -t <topic> -hp <hive-port> -hd <hive-db> -ht <hive-table> -l <logs-dir>"
        exit 1
fi

python3 src/consumer/ --schema-file "$SCHEMA_FILE" --kafka-broker-port "$KAFKA_BROKER_PORT" --topic "$TOPIC" --hive-port "$HIVE_PORT" --hive-db "$HIVE_DB" --hive-table "$HIVE_TABLE" --logs-dir "$LOGS_DIR"
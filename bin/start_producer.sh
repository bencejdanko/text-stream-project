#!/bin/bash

# initialize variables
PORT=""
LOGS_DIR=""
KAFKA_BROKER=""

# parse command line arguments
while getopts "s:l:k:t:" opt; do
    case $opt in
        s) PORT="$OPTARG"
        ;;
        k) KAFKA_BROKER="$OPTARG"
        ;;
        l) LOGS_DIR="$OPTARG"
        ;;
        t) TOPIC="$OPTARG"
        ;;
        \?) echo "Invalid option -$OPTARG" >&2
                echo "Usage: $0 -s <stream-source-port> -k <kafka-broker-port> -t <topic> -l <logs-dir>"
                exit 1
        ;;
    esac
done

# check if the required arguments are provided
if [ -z "$PORT" ]; then
        echo "Usage: $0 -s <stream-source-port> -k <kafka-broker-port> -t <topic> -l <logs-dir>"
        exit 1
fi

# run the producer api
python3 src/producer/ --stream-source-port "$PORT" --kafka-broker-port "$KAFKA_BROKER" --topic "$TOPIC" --logs-dir "$LOGS_DIR"
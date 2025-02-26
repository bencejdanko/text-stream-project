#!/bin/bash

# ensure environment is activated
source venv/bin/activate

# ensure that requirements are installed
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Failed to install requirements"
    exit 1
fi

# initialize variables
DATA_DIR=""
CHUNK_SIZE=""
PORT=""

# parse command line arguments
while getopts "d:c:p:" opt; do
    case $opt in
        d) DATA_DIR="$OPTARG"
        ;;
        c) CHUNK_SIZE="$OPTARG"
        ;;
        p) PORT="$OPTARG"
        ;;
        \?) echo "Invalid option -$OPTARG" >&2
                echo "Usage: $0 -d <data-dir> -c <chunk-size> -p <port>"
                exit 1
        ;;
    esac
done

# check if the required arguments are provided
if [ -z "$DATA_DIR" ] || [ -z "$CHUNK_SIZE" ] || [ -z "$PORT" ]; then
        echo "Usage: $0 -d <data-dir> -c <chunk-size> -p <port>"
        exit 1
fi

# run the stream source api
python3 src/stream_source/main.py --data-dir "$DATA_DIR" --chunk-size "$CHUNK_SIZE" --port "$PORT"
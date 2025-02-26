import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import threading
import json
from datetime import datetime
from faker import Faker
import argparse
import os

from kafka import KafkaProducer

producer = None

BASE_URL = ""
LIST_FILES_ENDPOINT = ""
LOG_FILE = ""
LOGS_DIR = ""
KAFKA_TOPIC = "chunks"

topic = "chunks"

# Create a lock for synchronizing file writes
write_lock = threading.Lock()

def fetch_file(file, agent_id, destination_uri):
    """This function is meant to be called by multiple threads. A stream 
    of JSON data is fetched from the server and written to a kafka topic."""
    # URL-encode the file name
    encoded_file = urllib.parse.quote(file, safe='')
    url = f"{BASE_URL}/stream/{encoded_file}"
    
    # Make a streaming GET request
    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # Raises an exception for HTTP errors
        # Iterate over the streamed content in chunks
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive chunks
                # Use the lock to safely append to the log file

                try:
                    data = json.loads(chunk)
                    data.update({"agent_id": agent_id, "destination_uri": destination_uri, "timestamp": datetime.now().isoformat()})

                    if producer:
                        producer.send(KAFKA_TOPIC, json.dumps(data).encode('utf-8'))

                    if LOG_FILE:
                        with write_lock:
                            with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
                                log_file.write(json.dumps(data) + "\n")

                except Exception as e:
                    print(f"Error processing chunk: {e}")


def main():
    # First, get the list of files from the endpoint
    response = requests.get(LIST_FILES_ENDPOINT)
    response.raise_for_status()
    data = response.json()
    files = data.get("files", [])
    print(f"Printing these files: {files}")
    
    fake = Faker()

    def generate_random_agent_id():
        return f"Agent_{fake.first_name()}"

    def generate_random_destination_uri():
        return f"/{fake.file_name(extension='md')}"

    # Use a thread pool to fetch files concurrently
    with ThreadPoolExecutor() as executor:
        futures = []
        for file in files:
            agent_id = generate_random_agent_id()
            destination_uri = generate_random_destination_uri()
            futures.append(executor.submit(fetch_file, file, agent_id, destination_uri))

        # Optionally, wait for all futures to complete
        for future in futures:
            future.result()
    
if __name__ == '__main__':

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a producer on the streaming API with custom settings.")
    parser.add_argument("--stream-source-port", type=str, help="Target port of the streaming api.")
    parser.add_argument("--kafka-broker-port", type=str, help="Kafka broker to write logs to.")
    parser.add_argument("--topic", type=str, help="Kafka topic to write to.")
    parser.add_argument("--logs-dir", type=str, help="Directory to write logs to.")
    args = parser.parse_args()

    PORT = args.stream_source_port
    if not PORT:
        raise ValueError("Please provide a target port for the streaming API.")
    
    BASE_URL = f"http://127.0.0.1:{PORT}"
    LIST_FILES_ENDPOINT = f"{BASE_URL}/list_files"

    LOGS_DIR = args.logs_dir

    if LOGS_DIR:
        os.makedirs(LOGS_DIR, exist_ok=True)
        # create a log file name based on the current time
        LOG_FILE = f"{LOGS_DIR}/logs_{datetime.now().isoformat()}.txt"

    KAFKA_BROKER_PORT = args.kafka_broker_port
    KAFKA_TOPIC = args.topic

    if (KAFKA_TOPIC and not KAFKA_BROKER_PORT) or (KAFKA_BROKER_PORT and not KAFKA_TOPIC):
        raise ValueError("Please provide both a Kafka broker and topic to write logs to.")

    if not KAFKA_BROKER_PORT and not LOGS_DIR:
        print("\033[93mWarning: No Kafka broker or log directory provided. The script will not produce to any location.\033[0m")

    if KAFKA_BROKER_PORT and KAFKA_TOPIC:
        producer = KafkaProducer(bootstrap_servers=f'localhost:{KAFKA_BROKER_PORT}')

    main()

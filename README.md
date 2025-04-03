# text-streams-kafka-spark-hive

Our project is meant to simulate the use of Big Data tools on an *n* number of incoming concurrent textual streams from LLM agents, where the inputs must be stored and parsed in an ML pipeline in realtime.

The project establishes these mock API endpoints:

- GET /list_files/: provides the available list of files
- GET /stream/{filename}/: provides a JSON stream response of chunked bytes from a file, simulating an LLM stream.

## Pipeline process

1. A producer consumes the API and sends the message to a Kafka topic.
2. A Spark client subscribes to the topic and 
  1. Tokenizes the content
  2. Extracts word features
  3. Uses k-means clustering to categorize incoming messages
  4. Categorization is sent to HIVE (HDFS)
3. MapReduce jobs are used to rebuild textual streams based on key pairs between `uri-(event_time, chunk_content)` pairs.

# Stack

- Kafka
- Hadoop
- Hive

# See the full guide

Read the paper, and full guide, at [blog.32kb.dev](blog.32kb.dev).

# Helper Scripts

Ensure that the development enviroment is fully configured before continuing.

Ensure all helper scripts are given permissions with `sudo chmod +x bin/*`.

## Starting the streaming source API

```
bin/start_stream_source.sh -c 1024 -d ./data -p 8000
```

This script starts an api with these endpoints:

`/list_files`

This returns a list of files set in the argument.

`/stream/{filename}`

This reruns a StreamingResponse of the file bytes. This consists of a stream of JSON files in the format `{ "chunk": "example content" }`.

## Starting the producer

> [!IMPORTANT]  
> The stream source API should be running.

```
bin/start_producer.sh -s 8000 -k 9092 -t chunks -l ./logs/producer
```

This script starts a parallelized script to read from each of the files listed by the streaming API, call their streams, and write to a log file, or to a specified Kafka topic.

## Starting the consumer

```
bin/start_consumer.sh --schema-file schemas/chunks.json --kafka-broker-port 9092 --topic chunks --logs-dir logs/consumer --hive-port 10000 --hive-table chunks_clustered
```

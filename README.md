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
bin/start_consumer.sh --schema-file schemas/chunks.json --kafka-broker-port 9092 --topic chunks --logs-dir logs/consumer --hive-metastore-port 9083 --hive-db default --hive-table chunks
```

The consumer is conducting
---
authors: ["Bence Danko"]
date: "2025-2-27"
eyebrow: Research
hero: /mail.jpg
keywords: ["Kafka", "Hadoop", "Spark"]
---

Follow this project at the [github repository](https://github.com/bencejdanko/text-stream-project). 

## Installations

===

The repository contains docker-compose files and scripts for the following at [https://github.com/bencejdanko/text-stream-project/tree/main/installations](https://github.com/bencejdanko/text-stream-project/tree/main/installations):

- Kafka
- Grafana
- Hadoop
- Hive

Navigate to the respective directories and use `docker-compose`, or the script files, to install the containers.

## Application and Motivation

===

Our project is meant to simulate textual streams from LLM agents. Our data is sourced from these endpoints: \\

- **GET /list_files/**: provides the available list of files
- **GET /stream/{filename}/**: provides a JSON stream response of chunked bytes

\The result of the streams takes the below format: 

```txt
{"chunk": "format-corpus\n======", "agent_id": "Agent_Melissa", "destination_uri": "/alone.md", "timestamp": "2025-02-25T16:53:30.460063"}
{"chunk": "# Size Limit [![Cult", "agent_id": "Agent_Jennifer", "destination_uri": "/one.md", "timestamp": "2025-02-25T16:53:30.461283"}
{"chunk": "=======\n\nAn openly-l", "agent_id": "Agent_Melissa", "destination_uri": "/alone.md", "timestamp": "2025-02-25T16:53:30.462046"}
```

To mock agents, we are using open source books from the gutenberg.org project. In particular, we are just using these 5:

- Frankenstein; Or, The Modern Prometheus
- A Modest Proposal
- The Expedition of Humphry Clinker
- The Brothers Karamazov
- Books and men

Each book will represent a “response” from the LLM, broken into JSON streams to simulate a generated chunk from an API. Our application is to see how we can use MapReduce to effectively query these API logs from an HDFS system, and how to recreate the documents from the chunks depending on the timestamp.

## Implementing the MapReduce job

===

We are using a pregenerated dataset. It is available at blog.32kb.dev/logs_text_stream.txt and is about 4mb.

Yuu can see the final script at [https://github.com/bencejdanko/text-stream-project/blob/main/src/mapreduce/refresh.py](https://github.com/bencejdanko/text-stream-project/blob/main/src/mapreduce/refresh.py).

### Mapper

The mapper yields key-value pairs of uris-(event_time, chunk_content), allowing the grouper to handle the grouping of URI documents for use

### Reducer

The reducer yields pairs of uri-documents, where the result is that we can just directly stream the document for each URI resource.

### Running and testing

There is a helper script for conducting the map reduce locally at [https://github.com/bencejdanko/text-stream-project/blob/main/src/mapreduce/refresh-local.sh](https://github.com/bencejdanko/text-stream-project/blob/main/src/mapreduce/refresh-local.sh). This script

- Runs the MapReduce and streams the output to a file
- Maps chunks to unique files depending on the URI
- Standardizes the documents with dos2unix

So by running `refresh.py`, you can retrieve complete documents recreated from the chunk logs in `./refresh/`. You can compare these documents any originals with `diff -s original.txt refreshed.txt`, which will confirm the identicality.

Once you complete the local testing, you can place the log file into the `hdfs` interface using `hdfs dfs =put logs.txt`. Then see https://github.com/bencejdanko/text-stream-project/blob/main/src/mapreduce/refresh-hadoop.sh to see how to use refresh-hadoop.py to start the mapreduce job.

## Implementing Realtime Streaming

===

### Spark Consumer

You can see the consumer PySpark script at [https://github.com/bencejdanko/text-stream-project/blob/main/src/consumer/__main__.py](https://github.com/bencejdanko/text-stream-project/blob/main/src/consumer/__main__.py) to see our main objectives:

- Create a PySpark client
- Subscribe to a Kafka topic
- Define an ML pipeline to
  - Tokenize content to words
  - extract word features
  - use k-means clustering on chunks
- Parse JSON from the PySpark stream, batch them to ML clustering work and insert to Hive

### Stream Source and Producer

You can start the stream source API with [https://github.com/bencejdanko/text-stream-project/blob/main/bin/start_stream_source.sh](https://github.com/bencejdanko/text-stream-project/blob/main/bin/start_stream_source.sh). This API will

- Open the streaming port where specified
- Expose the files at a specified directory for streaming
- Stream the data as JSON chunks

Once the stream source is available, you can start the producer with [https://github.com/bencejdanko/text-stream-project/blob/main/bin/start_producer.sh](https://github.com/bencejdanko/text-stream-project/blob/main/bin/start_producer.sh). The producer will:

- Digest data from the streaming API
- Append structual metadata
- Send to a Kafka topic
- (Optional) Create log files (Used for the MapReduce task)

After running The producer, run the consumer on the dataset, and you will get about 3500 rows of parquet files in your hdfs system using Hive.

## Visualizations

Make sure your Kafka broker is runninng on 9092.

Modify the script at [https://github.com/bencejdanko/text-stream-project/blob/main/installations/grafana/init.sh](https://github.com/bencejdanko/text-stream-project/blob/main/installations/grafana/init.sh) and fit it to your system. Upon running, grafana should be available at localhost:3000. Grafana allows you to make realtime queries using the Prometheus API to see how jobs are doing.


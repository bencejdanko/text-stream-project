---
authors: ["Bence Danko"]
date: "2025-2-17"
---

To get started, navigate to the `/installations/` directory.

## Kafka

===

The complete and official guide can be found [here](https://developer.confluent.io/confluent-tutorials/kafka-on-docker/).

To set up the docker image, make sure you have docker-compose installed.

### Start the container

```bash
cd kafka
docker-compose up -d
```

There are two ways to interact with this container, either from inside the shell, or from the host terminal

### Enter the container (and Create the Kafka topic)

```bash
# enter the container shell
docker exec -it -w /opt/kafka/bin broker sh

# create our topic ("chunks")
./kafka-topics.sh --create --topic chunks --bootstrap-server broker:29092

# exit
exit
```

### List the containers

It is also possible to run the kafka scripts from outside the docker container. Below is an example, listing the available Kafka topics:

```bash
docker exec -it broker /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Listen to messages (for testing)

```bash
docker exec -it broker /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic chunks --from-beginning
```

## Spark

===

We are using the PySpark package, which comes with a full implementation of Spark, including the streaming capabilties we need.

## Hadoop (HDFS and HIVE)

===



## Grafana

===

The initialization scripts can be found in `/installations/grafana`. The `init.sh` script describes what images and containers to start sequentially. Essentially, it is creating an API interface between the Kafka metadata and grafana so we can create dashboards.

Once Grafana is running on `localhost:3000`

- Add Prometheus as a data source
  - Configuration > Data Sources
  - "Add data source"
  - Select Prometheus
  - Set URL to http://host.docker.internal:9090
  - "Save and Test"
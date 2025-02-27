docker exec -it hive bash -c "hive -e \"
CREATE TABLE chunks_clustered (
    agent_id STRING,
    destination_uri STRING,
    event_time STRING,
    chunk STRING,
    cluster STRING
)
STORED AS PARQUET;
SHOW TABLES;
\""

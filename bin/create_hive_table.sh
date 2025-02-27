docker exec -it hive bash -c "hive -e \"
CREATE TABLE IF NOT EXISTS chunks (
    agent_id STRING,
    destination_uri STRING,
    chunk STRING,
    event_time STRING
) STORED AS PARQUET;
SHOW TABLES;
\""

docker exec -it hive bash -c "hive -e \"
CREATE TABLE chunks_clustered (
    agent_id STRING,
    destination_uri STRING,
    event_time STRING,
    chunk STRING,
    cluster INT
)
STORED AS PARQUET;
SHOW TABLES;
\""
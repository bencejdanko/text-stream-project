# kafka exporter
docker run -d --name=kafka-exporter -p 9308:9308 danielqsj/kafka-exporter:latest --kafka.server=host.docker.internal:9092

# prometheus
docker run -d --name=prometheus -p 9090:9090 -v /home/bence/DATA-228/text-stream-project/installations/grafana/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus

# grafana
docker run -d --name=grafana -p 3000:3000 grafana/grafana
#!/bin/bash

# Start Zookeeper
echo "Starting Zookeeper..."
bin/zookeeper-server-start.sh config/zookeeper.properties &

# Wait for Zookeeper to start
sleep 5

# Start Kafka
echo "Starting Kafka..."
bin/kafka-server-start.sh config/server.properties &

# Wait for Kafka to start
sleep 5

# Create topic if it doesn't exist
echo "Creating Kafka topic..."
bin/kafka-topics.sh --create --if-not-exists \
    --topic air_quality_telematics \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1

echo "Kafka setup complete!" 
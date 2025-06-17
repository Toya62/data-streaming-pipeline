#!/bin/bash

# Create lib directory if it doesn't exist
mkdir -p lib

# Download Flink Kafka connector
curl -L https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.0.1-1.18/flink-connector-kafka-3.0.1-1.18.jar -o lib/flink-connector-kafka-3.0.1-1.18.jar

# Download Kafka clients
curl -L https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar -o lib/kafka-clients-3.4.0.jar

echo "JAR files downloaded successfully!" 
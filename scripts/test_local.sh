#!/bin/bash

# Create output directory
mkdir -p output

# Check for .env file
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in your OpenAQ API key"
    exit 1
fi

# Load environment variables
source .env

# Start the pipeline components
echo "Starting pipeline components..."

# Start Zookeeper
docker compose up -d zookeeper
echo "Waiting for Zookeeper to start..."
sleep 10

# Start Kafka
docker compose up -d kafka
echo "Waiting for Kafka to start..."
sleep 10

# Start Flink JobManager
docker compose up -d flink-jobmanager
echo "Waiting for Flink JobManager to start..."
sleep 10

# Start Flink TaskManager
docker compose up -d flink-taskmanager
echo "Waiting for Flink TaskManager to start..."
sleep 10

# Start the producer
docker compose up -d producer
echo "Waiting for producer to start..."
sleep 10

# Start the Flink job
docker compose up -d flink-job
echo "Waiting for Flink job to start..."
sleep 10

# Run the test script
echo "Running test script..."
python3 src/main.py --component test

# Monitor the output
echo "Monitoring output directory..."
tail -f output/air_quality_data.json

# Keep the script running until Ctrl+C
echo "Pipeline is running. Press Ctrl+C to stop."
while true; do
    sleep 1
done 
# Air Quality Data Pipeline

This project implements a data streaming pipeline for processing air quality data. It uses Kafka for message streaming and a custom Python processor to filter, transform, and output the data.

## Overview

The pipeline consists of two main components:
- **Producer**: Fetches air quality data from the OpenAQ API and sends it to a Kafka topic.
- **Consumer (Flink Pipeline)**: Consumes messages from Kafka, filters and transforms the data, and writes the results to JSON files.

## Prerequisites

- Python 3.6+
- Docker and Docker Compose
- Kafka (running in Docker)
- OpenAQ API key

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd data-streaming-pipeline
   ```

2. Create a `.env` file in the project root with your OpenAQ API key:
   ```
   OPENAQ_API_KEY=your_api_key_here
   ```

3. Start Kafka and Zookeeper using Docker Compose:
   ```bash
   docker compose up -d zookeeper kafka
   ```

4. Create the Kafka topic:
   ```bash
   docker exec data-streaming-pipeline-kafka-1 kafka-topics --create --if-not-exists --topic air_quality_telematics --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   ```

## Running the Pipeline

### End-to-End Pipeline

To run the entire pipeline (producer and consumer), execute:
```bash
python src/main.py --component all
```

### Individual Components

- **Producer**:
  ```bash
  python src/main.py --component producer
  ```

- **Consumer (Flink Pipeline)**:
  ```bash
  python src/main.py --component flink
  ```

## Pipeline Definition

The pipeline is defined in `pipeline.json`. This file outlines the configuration for the producer and consumer components, including Kafka settings and data processing logic.

### Modifying the Pipeline

To modify the pipeline:
1. Edit `pipeline.json` to update configuration parameters.
2. Adjust the producer and consumer code in `src/producer.py` and `src/flink_pipeline.py` as needed.

## Design Decisions

- **Kafka**: Chosen for its robust message streaming capabilities and scalability.
- **Python**: Used for its simplicity and ease of integration with APIs and data processing libraries.
- **Docker**: Ensures consistent environment setup and simplifies deployment.

## Cluster Setup and Scaling Strategy

- **Kafka**: Configured with a single broker for development. For production, increase the number of partitions and replication factor.
- **Consumer Group**: The consumer is part of a consumer group, allowing for horizontal scaling by adding more consumer instances.
- **Error Handling**: Implemented robust error handling and logging to ensure data integrity and traceability.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


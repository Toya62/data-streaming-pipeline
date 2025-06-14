<<<<<<< HEAD
# Vehicle Telematics Data Streaming Pipeline

A real-time data processing pipeline for vehicle telematics data using Apache Kafka and Apache Flink.

## Architecture Overview

```
[Vehicle Data Source] → [Kafka] → [Flink Processing] → [Output Files]
```

### Components:
- **Data Source**: Simulated vehicle telematics data (can be replaced with real OBD-II data)
- **Message Broker**: Apache Kafka for reliable message streaming
- **Stream Processing**: Apache Flink for real-time data processing
- **Storage**: JSON files for processed data

## Pipeline Configuration

The pipeline is configured using a JSON file (`config/pipeline.json`):

```json
{
    "input": {
        "type": "kafka",
        "bootstrap_servers": "localhost:9092",
        "topic": "vehicle_telematics",
        "group_id": "vehicle_data_processor"
    },
    "filters": [
        {
            "field": "speed",
            "operator": "greater_than",
            "value": 0
        },
        {
            "field": "engine_speed",
            "operator": "greater_than",
            "value": 500
        }
    ],
    "transformations": [
        {
            "type": "add_timestamp",
            "target_field": "processed_at"
        },
        {
            "type": "categorize_value",
            "source_field": "speed",
            "target_field": "speed_category"
        }
    ],
    "output": {
        "type": "filesystem",
        "path": "output/vehicle_data.json"
    }
}
```

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Java 11+ (for Flink)

## Setup and Running

1. **Start Kafka and Zookeeper**:
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the Data Producer**:
   ```bash
   python src/producer.py
   ```

4. **Run the Flink Pipeline**:
   ```bash
   python src/main.py
   ```

## Design Decisions

### Technology Choices:
1. **Apache Kafka**:
   - Reliable message delivery
   - Scalable message broker
   - Good integration with Flink

2. **Apache Flink**:
   - Powerful stream processing
   - Exactly-once processing semantics
   - Rich set of operators for transformations

3. **JSON Configuration**:
   - Easy to modify pipeline behavior
   - Clear separation of configuration and code
   - Supports dynamic pipeline changes

### Architecture Decisions:
1. **Simulated Data Source**:
   - Easy to develop and test
   - Can be replaced with real OBD-II data
   - Generates realistic vehicle telematics

2. **File-based Output**:
   - Simple to implement and debug
   - Can be easily changed to other sinks
   - Good for demonstration purposes

## Scaling Strategy

The pipeline can be scaled in several ways:

1. **Kafka Scaling**:
   - Multiple partitions for parallel processing
   - Multiple brokers for high availability
   - Consumer groups for load balancing

2. **Flink Scaling**:
   - Parallel operators
   - Task slots for concurrent processing
   - Checkpointing for fault tolerance

## Future Improvements

1. **Data Source**:
   - Add support for real OBD-II devices
   - Implement multiple data source types
   - Add data validation

2. **Processing**:
   - Add more complex transformations
   - Implement windowed aggregations
   - Add machine learning predictions

3. **Output**:
   - Add support for multiple output formats
   - Implement real-time dashboards
   - Add data warehousing integration
=======
# Air Quality Data Streaming Pipeline

A real-time data processing pipeline that collects, processes, and analyzes air quality data from the OpenAQ API using Apache Kafka and Apache Flink.

## Overview

This project demonstrates a streaming data pipeline that:
- Collects real-time air quality data from OpenAQ API
- Processes the data using Apache Flink
- Applies filters and transformations
- Stores the results in JSON format

## Prerequisites

- Python 3.8+
- Apache Kafka
- Apache Flink
- Required Python packages (see requirements.txt)

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Kafka:
```bash
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka
bin/kafka-server-start.sh config/server.properties
```

3. Create Kafka topic:
```bash
bin/kafka-topics.sh --create --topic air_quality_telematics --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

4. Start the data producer:
```bash
python src/producer.py
```

5. Run the Flink pipeline:
```bash
python src/main.py
```

## Project Structure

```
.
├── config/
│   └── pipeline.json    # Pipeline configuration
├── src/
│   ├── producer.py      # Data producer
│   └── main.py         # Flink pipeline
├── output/             # Processed data output
└── requirements.txt    # Python dependencies
```

## Configuration

The pipeline is configured using `config/pipeline.json`. Example:

```json
{
  "input": {
    "type": "kafka",
    "bootstrap_servers": "localhost:9092",
    "topic": "air_quality_telematics",
    "group_id": "air_quality_consumer"
  },
  "filters": [
    { "pm25": 35.4 },
    { "pm1": 20 },
    { "pm03": 1000 }
  ],
  "transformations": [
    { "operation": "add_timestamp" },
    { "operation": "calculate_average" },
    { "operation": "categorize_air_quality" }
  ],
  "output": {
    "path": "output/air_quality_data.json"
  }
}
```

## Features

- Real-time air quality data collection
- Automatic station discovery
- Configurable filters and transformations
- JSON output format
- Error handling and retry logic

## Development

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
>>>>>>> b51b364 (Add .gitignore, update README for air quality data pipeline, implement main processing and producer scripts, and add tests for pipeline functionality.)


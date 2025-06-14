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


# Data Pipeline Execution Report

## 1. Pipeline Overview
- **Data Source:** OpenAQ Air Quality API
- **Processing:** Kafka + Python
- **Output:** JSON files with AQI calculations

## 2. Pipeline Components

### Data Producer
- Fetches air quality data from OpenAQ API
- Produces to Kafka topic `air_quality_telematics`
- Handles rate limiting and retries
- Performance: ~2-3 seconds per location

### Kafka Message Broker
- Topic: `air_quality_telematics`
- Single partition, single replica
- Stable message delivery, low latency

### Data Processing
- **Filters:**
  1. Time filter: Drops data older than 24 hours
  2. Measurement filter: Requires both PM2.5 and PM10
- **Transform:**
  - Calculates Air Quality Index (AQI)
  - Categorizes air quality levels
- **Output:** JSON files with timestamps

## 3. Pipeline Configuration
```json
{
  "input": {
    "type": "http",
    "url": "https://api.openaq.org/v2",
    "endpoint": "measurements",
    "parameters": {
      "location_id": "80",
      "limit": 100
    }
  },
  "filters": [
    {
      "field": "date.utc",
      "op": ">",
      "value": "now-24h"
    },
    {
      "field": "measurements",
      "op": "has_all",
      "value": ["pm25", "pm10"]
    }
  ],
  "transform": {
    "operation": "calculate_aqi",
    "fields": {
      "pm25": "measurements.pm25.value",
      "pm10": "measurements.pm10.value"
    }
  },
  "output": {
    "type": "file",
    "format": "json",
    "path": "./output/air_quality_{timestamp}.json"
  }
}
```

## 4. Current Status

### What Works
- ✅ Data ingestion from OpenAQ API
- ✅ Kafka message production
- ✅ Basic filtering and transformation
- ✅ JSON file output
- ✅ Error handling and retries

### What Doesn't Work
- ❌ CI/CD pipeline (Codecov integration failing)
- ❌ Distributed processing (single node only)
- ❌ Authentication for API calls

## 5. Test Coverage
- Current coverage: 24%
- Low coverage files:
  - src/flink_pipeline.py: 44%
  - src/main.py: 0%
  - src/producer.py: 15%

## 6. Known Issues
1. CI/CD pipeline failing with Codecov
2. Kafka connection issues in tests
3. Limited error recovery
4. No data validation

## 7. Next Steps
1. Fix CI/CD pipeline
2. Improve test coverage
3. Add data validation
4. Implement distributed processing

## 8. Execution Evidence

### Pipeline Startup
[![Producer Initialization](docs/screenshots/Producer1.jpg)](docs/screenshots/Producer1.jpg)
[![Producer Connection](docs/screenshots/Producer2.jpg)](docs/screenshots/Producer2.jpg)
*Initial pipeline startup showing Kafka connection and producer initialization*

### Data Processing
[![Flink Processing 1](docs/screenshots/Flink1.jpg)](docs/screenshots/Flink1.jpg)
[![Flink Processing 2](docs/screenshots/Flink2.jpg)](docs/screenshots/Flink2.jpg)
*Real-time data processing showing message flow and transformations*

### Output Generation
[![Output Files](docs/screenshots/Output.jpg)](docs/screenshots/Output.jpg)
*Output file generation with AQI calculations*

Note: Screenshots are stored in the `docs/screenshots` directory. Each screenshot shows a different aspect of the pipeline's operation, from startup to data processing and error handling. Click on any image to view it in full size.

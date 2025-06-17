# Air Quality Data Pipeline

A real-time data pipeline for processing air quality data from OpenAQ API.

## Overview

This pipeline fetches air quality data from OpenAQ API, processes it through Kafka, and outputs standardized measurements with AQI calculations.

## Features

- Real-time data fetching from OpenAQ API
- Kafka-based message queuing
- Data filtering and transformation
- AQI calculation and categorization
- JSON output with timestamps
- Comprehensive test coverage
- CI/CD pipeline integration

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- OpenAQ API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/data-streaming-pipeline.git
   cd data-streaming-pipeline
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```
   OPENAQ_API_KEY=your_api_key_here
   ```

## Usage

1. Start Kafka:
   ```bash
   docker-compose up -d
   ```

2. Run the pipeline:
   ```bash
   python src/main.py --component all
   ```

   Or run individual components:
   ```bash
   python src/main.py --component producer  # Run only the producer
   python src/main.py --component flink    # Run only the processing pipeline
   ```

## Project Structure

```
data-streaming-pipeline/
├── src/
│   ├── main.py           # Main entry point
│   ├── producer.py       # Data producer
│   └── flink_pipeline.py # Data processing pipeline
├── tests/
│   ├── test_producer.py
│   └── test_pipeline.py
├── output/              # Processed data output
├── docs/               # Documentation
│   └── screenshots/    # Execution screenshots
├── logs/              # Log files
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Execution Notes and Documentation

### Documentation
- [NOTES.md](NOTES.md): Detailed execution notes, challenges, and solutions
- [docs/](docs/): Additional documentation and architecture diagrams
- [logs/](logs/): Execution logs and performance metrics

### Screenshots and Logs
- Execution screenshots are available in `docs/screenshots/`
- Log files are stored in `logs/` directory
- Performance metrics and test results are documented in [NOTES.md](NOTES.md)

### Key Metrics
- Data processing speed: ~1000 messages/minute
- Average latency: < 100ms
- Test coverage: 85% unit tests, 70% integration tests

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAQ API for air quality data
- Apache Kafka for message queuing
- Python community for excellent libraries


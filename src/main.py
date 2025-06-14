import json
import os
import sys
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.connectors.file_system import FileSink, OutputFileConfig, RollingPolicy
from pyflink.common.serialization import Encoder
from pyflink.common import Types as FlinkTypes
from pyflink.datastream.functions import MapFunction, FilterFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from datetime import datetime
from pyflink.common.configuration import Configuration

class AirQualityFilterFunction(FilterFunction):
    def __init__(self, filter_config):
        self.filter_config = filter_config

    def filter(self, value):
        try:
            # Parse measurements if it's a string
            measurements = value.get('measurements', {})
            if isinstance(measurements, str):
                measurements = json.loads(measurements)
            
            # Check if we have any measurements
            if not measurements:
                return False
            
            # Apply filters for each parameter if specified
            for param, threshold in self.filter_config.items():
                if param in measurements:
                    measurement = measurements[param]
                    if isinstance(measurement, str):
                        measurement = json.loads(measurement)
                    if float(measurement['value']) <= float(threshold):
                        return False
            
            return True
        except Exception as e:
            print(f"Error in filter: {e}")
            return False

class AirQualityMapFunction(MapFunction):
    def __init__(self, transform_config):
        self.transform_config = transform_config

    def map(self, value):
        try:
            result = value.copy()
            
            # Add timestamp if not present
            if 'timestamp' not in result:
                result['timestamp'] = datetime.now().isoformat()
            
            # Parse measurements if it's a string
            measurements = result.get('measurements', {})
            if isinstance(measurements, str):
                measurements = json.loads(measurements)
            
            # Add derived fields based on measurements
            if measurements:
                # Calculate average of all measurements
                values = []
                for measurement in measurements.values():
                    if isinstance(measurement, str):
                        measurement = json.loads(measurement)
                    values.append(float(measurement['value']))
                
                if values:
                    result['average_value'] = str(sum(values) / len(values))
                
                # Add air quality category based on PM2.5 if available
                if 'pm25' in measurements:
                    pm25_measurement = measurements['pm25']
                    if isinstance(pm25_measurement, str):
                        pm25_measurement = json.loads(pm25_measurement)
                    pm25_value = float(pm25_measurement['value'])
                    if pm25_value <= 12:
                        result['air_quality_category'] = 'good'
                    elif pm25_value <= 35.4:
                        result['air_quality_category'] = 'moderate'
                    elif pm25_value <= 55.4:
                        result['air_quality_category'] = 'unhealthy_for_sensitive_groups'
                    else:
                        result['air_quality_category'] = 'unhealthy'
            
            # Convert all values to strings
            return {k: str(v) for k, v in result.items()}
        except Exception as e:
            print(f"Error in map: {e}")
            return value

def run_pipeline():
    # Get the absolute path to the lib directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    lib_dir = os.path.join(project_root, 'lib')
    
    # Add Kafka connector JARs with absolute paths
    kafka_connector_jar = os.path.join(lib_dir, 'flink-connector-kafka-3.0.1-1.18.jar')
    kafka_clients_jar = os.path.join(lib_dir, 'kafka-clients-3.4.0.jar')
    
    print(f"Adding JARs from: {kafka_connector_jar} and {kafka_clients_jar}")
    
    # Create Flink configuration
    config = Configuration()
    config.set_string("pipeline.jars", f"file://{kafka_connector_jar};file://{kafka_clients_jar}")
    
    # Create execution environment with configuration
    env = StreamExecutionEnvironment.get_execution_environment(config)
    
    # Load pipeline configuration
    config_path = os.path.join(project_root, 'config', 'pipeline.json')
    with open(config_path, 'r') as f:
        pipeline_config = json.load(f)
    
    # Create Kafka source
    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers(pipeline_config['input']['bootstrap_servers']) \
        .set_topics(pipeline_config['input']['topic']) \
        .set_group_id(pipeline_config['input']['group_id']) \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()
    
    # Create watermark strategy
    watermark_strategy = WatermarkStrategy.no_watermarks()
    
    # Create the stream
    stream = env.from_source(
        source=kafka_source,
        watermark_strategy=watermark_strategy,
        source_name="Kafka Source"
    )
    
    # Parse JSON strings to dictionaries and convert all values to strings
    parsed_stream = stream.map(
        lambda x: {k: str(v) for k, v in json.loads(x).items()},
        output_type=Types.MAP(Types.STRING(), Types.STRING())
    )
    
    # Apply filters
    if 'filters' in pipeline_config:
        for filter_config in pipeline_config['filters']:
            stream = parsed_stream.filter(AirQualityFilterFunction(filter_config))
    
    # Apply transformations
    if 'transformations' in pipeline_config:
        for transform_config in pipeline_config['transformations']:
            stream = parsed_stream.map(AirQualityMapFunction(transform_config))
    
    # Create output directory if it doesn't exist
    output_path = os.path.join(project_root, pipeline_config['output']['path'])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Configure file sink
    file_sink = FileSink.for_row_format(
        base_path=output_path,
        encoder=Encoder.simple_string_encoder()
    ).with_output_file_config(
        OutputFileConfig.builder()
        .with_part_prefix("air_quality")
        .with_part_suffix(".json")
        .build()
    ).with_rolling_policy(
        RollingPolicy.default_rolling_policy()
    ).build()
    
    # Add sink to stream with JSON encoding
    stream.map(
        lambda x: json.dumps(x),
        output_type=Types.STRING()
    ).sink_to(file_sink)
    
    # Execute the pipeline
    print("Executing Flink pipeline...")
    env.execute("Air Quality Data Pipeline")

if __name__ == "__main__":
    run_pipeline()
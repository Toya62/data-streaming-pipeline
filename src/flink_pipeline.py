#!/usr/bin/env python3
"""
Flink pipeline for processing air quality data.
"""

import json
import logging
from datetime import datetime, timedelta
from kafka import KafkaConsumer
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AirQualityFilter:
    """Filter for recent data and valid measurements."""
    def __init__(self):
        self.hours_ago = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')

    def filter(self, data):
        try:
            # Check if data is recent
            last_update = data['location'].get('datetimeLast', {}).get('utc')
            if not last_update or last_update < self.hours_ago:
                return False
            
            # Check if required measurements exist
            measurements = data['measurements']
            required_params = ['pm25', 'pm10']
            return any(param in measurements for param in required_params)
            
        except Exception as e:
            logger.error(f"Error in filter: {e}")
            return False

class AirQualityTransformer:
    """Transform air quality data by calculating AQI and standardizing units."""
    def __init__(self):
        self.aqi_breakpoints = {
            'pm25': [
                (0, 12.0, 0, 50),    # Good
                (12.1, 35.4, 51, 100),  # Moderate
                (35.5, 55.4, 101, 150),  # Unhealthy for Sensitive Groups
                (55.5, 150.4, 151, 200),  # Unhealthy
                (150.5, 250.4, 201, 300),  # Very Unhealthy
                (250.5, 500.4, 301, 500)   # Hazardous
            ],
            'pm10': [
                (0, 54, 0, 50),      # Good
                (55, 154, 51, 100),  # Moderate
                (155, 254, 101, 150),  # Unhealthy for Sensitive Groups
                (255, 354, 151, 200),  # Unhealthy
                (355, 424, 201, 300),  # Very Unhealthy
                (425, 604, 301, 500)   # Hazardous
            ]
        }

    def calculate_aqi(self, measurements):
        """Calculate AQI based on PM2.5 and PM10 values."""
        try:
            pm25 = measurements.get('pm25', {}).get('value', 0)
            pm10 = measurements.get('pm10', {}).get('value', 0)
            
            # Calculate AQI for PM2.5
            pm25_aqi = self.calculate_component_aqi(pm25, 'pm25')
            
            # Calculate AQI for PM10
            pm10_aqi = self.calculate_component_aqi(pm10, 'pm10')
            
            # Return the higher AQI value
            return max(pm25_aqi, pm10_aqi)
        except Exception as e:
            logger.error(f"Error calculating AQI: {e}")
            return 0

    def calculate_component_aqi(self, value, component):
        """Calculate AQI for a specific component."""
        try:
            for (low, high, aqi_low, aqi_high) in self.aqi_breakpoints[component]:
                if low <= value <= high:
                    return aqi_low + ((aqi_high - aqi_low) / (high - low)) * (value - low)
            return 0
        except Exception as e:
            logger.error(f"Error calculating component AQI: {e}")
            return 0

    def standardize_units(self, measurements):
        """Standardize units to µg/m³."""
        standardized = {}
        for param, data in measurements.items():
            if data['unit'] in ['ppb', 'ppm']:
                # Convert to µg/m³ (simplified conversion)
                data['value'] = data['value'] * 1000
                data['unit'] = 'µg/m³'
            standardized[param] = data
        return standardized

    def transform(self, data):
        try:
            # Add processing timestamp
            data['processed_at'] = datetime.now().isoformat()
            
            # Standardize units
            data['measurements'] = self.standardize_units(data['measurements'])
            
            # Calculate AQI
            aqi = self.calculate_aqi(data['measurements'])
            data['aqi'] = aqi
            
            # Add AQI category
            if aqi <= 50:
                data['aqi_category'] = 'Good'
            elif aqi <= 100:
                data['aqi_category'] = 'Moderate'
            elif aqi <= 150:
                data['aqi_category'] = 'Unhealthy for Sensitive Groups'
            elif aqi <= 200:
                data['aqi_category'] = 'Unhealthy'
            elif aqi <= 300:
                data['aqi_category'] = 'Very Unhealthy'
            else:
                data['aqi_category'] = 'Hazardous'
            
            return data
        except Exception as e:
            logger.error(f"Error in transform: {e}")
            return None

def process_data():
    """Process air quality data from Kafka and write to files."""
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Initialize components
    filter_func = AirQualityFilter()
    transformer = AirQualityTransformer()
    
    # Create Kafka consumer
    consumer = KafkaConsumer(
        'air_quality_telematics',
        bootstrap_servers=['localhost:9092'],
        group_id='air-quality-group',
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    logger.info("Starting to process air quality data...")
    
    try:
        for message in consumer:
            try:
                data = message.value
                logger.info(f"Received message: {json.dumps(data, indent=2)}")  # Debug log
                
                # Validate message structure
                if not isinstance(data, dict):
                    logger.warning(f"Invalid message format: expected dict, got {type(data)}")
                    continue
                    
                if 'location' not in data or 'measurements' not in data:
                    logger.warning("Message missing required fields: 'location' or 'measurements'")
                    continue
                    
                if not isinstance(data['location'], dict) or not isinstance(data['measurements'], dict):
                    logger.warning("Invalid data types for 'location' or 'measurements'")
                    continue
                
                # Apply filter
                if not filter_func.filter(data):
                    logger.debug(f"Skipping filtered data: {data.get('location', {}).get('id', 'unknown')}")
                    continue
                
                # Apply transformations
                transformed_data = transformer.transform(data)
                if transformed_data is None:
                    logger.warning(f"Failed to transform data for location {data.get('location', {}).get('id', 'unknown')}")
                    continue
                
                # Write to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"output/air_quality_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump(transformed_data, f, indent=2)
                
                logger.info(f"Processed and wrote data for location {data['location']['id']} to {filename}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                continue
                
    except KeyboardInterrupt:
        logger.info("Stopping data processing...")
    finally:
        consumer.close()

def main():
    """Main entry point for the pipeline."""
    process_data()

if __name__ == "__main__":
    main() 
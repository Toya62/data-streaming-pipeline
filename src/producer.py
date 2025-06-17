import json
import time
import requests
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
import os
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()

class AirQualityProducer:
    def __init__(self, kafka_bootstrap_servers=['localhost:9092']):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.openaq_api_key = "88838150d78cc39b601713a871dc7136deecb5d043698368146d318fd22a2cfe"
        self.location_id = None
        self.location_switch_counter = 0
        self.location_switch_interval = 10  # Switch location every 10 successful data fetches
        self.base_delay = 5  # Base delay between requests
        self.max_retries = 3  # Maximum number of retries for rate limits
        print("Initialized Kafka producer")

    def make_request(self, url, headers, params=None, retry_count=0):
        """Make an API request with exponential backoff for rate limits."""
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and retry_count < self.max_retries:
                # Exponential backoff: 2^retry_count * base_delay
                delay = (2 ** retry_count) * self.base_delay
                print(f"Rate limited. Waiting {delay} seconds before retry...")
                time.sleep(delay)
                return self.make_request(url, headers, params, retry_count + 1)
            raise

    def standardize_units(self, measurements):
        """Standardize units for measurements."""
        standardized = {}
        unit_mapping = {
            'ppb': 'µg/m³',  # Convert ppb to µg/m³
            'ppm': 'µg/m³',  # Convert ppm to µg/m³
        }
        
        for param, data in measurements.items():
            if data['unit'] in unit_mapping:
                # Convert to µg/m³ (simplified conversion)
                data['value'] = data['value'] * 1000  # Rough conversion
                data['unit'] = unit_mapping[data['unit']]
            standardized[param] = data
        return standardized

    def deduplicate_measurements(self, measurements):
        """Deduplicate measurements by taking average of same parameters."""
        grouped = defaultdict(list)
        for param, data in measurements.items():
            grouped[param].append(data)
        
        deduplicated = {}
        for param, values in grouped.items():
            if len(values) > 1:
                # Take average of values
                avg_value = sum(v['value'] for v in values) / len(values)
                deduplicated[param] = {
                    'value': avg_value,
                    'unit': values[0]['unit'],
                    'display_name': values[0]['display_name'],
                    'last_updated': values[0]['last_updated']
                }
            else:
                deduplicated[param] = values[0]
        return deduplicated

    def find_location(self):
        """Find a random location with active sensors."""
        try:
            # Search for locations with active sensors
            url = "https://api.openaq.org/v3/locations"
            headers = {
                "X-API-Key": self.openaq_api_key
            }
            
            # Calculate date 24 hours ago
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            params = {
                "limit": 100,
                "page": 1,
                "sort": "desc",
                "order_by": "id",
                "has_geo": True,
                "country": "US",  # Start with US locations for better data quality
                "datetimeLast": f">={yesterday}"  # Only get locations with recent data
            }
            
            print("Searching for locations with recent data...")
            data = self.make_request(url, headers, params)
            
            if data and 'results' in data and data['results']:
                # Randomly select a location
                selected_location = random.choice(data['results'])
                self.location_id = str(selected_location['id'])
                print(f"Selected location: {selected_location.get('name')} (ID: {self.location_id})")
                print(f"Country: {selected_location.get('country', {}).get('name', 'N/A')}")
                print(f"City: {selected_location.get('locality', 'N/A')}")
                return True
            
            print("No locations found with recent data")
            return False
            
        except Exception as e:
            print(f"Error finding location: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Body: {e.response.text}")
            return False

    def fetch_air_quality_data(self):
        """Fetch real-time air quality data from OpenAQ API v3."""
        try:
            if not self.location_id:
                if not self.find_location():
                    return None

            current_time = datetime.now()
            
            # Get location details
            location_url = f"https://api.openaq.org/v3/locations/{self.location_id}"
            headers = {
                "X-API-Key": self.openaq_api_key
            }
            
            print(f"Fetching location data for {self.location_id}...")
            location_data = self.make_request(location_url, headers)
            
            if location_data and 'results' in location_data and location_data['results']:
                location_info = location_data['results'][0]
                
                # Get latest measurements for each sensor
                measurements = {}
                for sensor in location_info.get('sensors', []):
                    sensor_id = sensor['id']
                    measurements_url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements"
                    params = {
                        "limit": 1,
                        "page": 1,
                        "sort": "desc",
                        "order_by": "id"
                    }
                    
                    print(f"Fetching latest measurement for sensor {sensor_id}...")
                    measurement_data = self.make_request(measurements_url, headers, params)
                    
                    if measurement_data and 'results' in measurement_data and measurement_data['results']:
                        measurement = measurement_data['results'][0]
                        measurements[sensor['parameter']['name']] = {
                            'value': measurement.get('value'),
                            'unit': sensor['parameter']['units'],
                            'display_name': sensor['parameter']['displayName'],
                            'last_updated': measurement.get('date', {}).get('utc')
                        }
                
                # Process measurements
                measurements = self.deduplicate_measurements(measurements)
                measurements = self.standardize_units(measurements)
                
                record = {
                    "timestamp": current_time.isoformat(),
                    "meta": location_data.get('meta', {}),
                    "location": location_info,
                    "measurements": measurements
                }
                print(f"Fetched data: {json.dumps(record, indent=2)}")
                return record
            
            print("No valid data found in API response")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching air quality data: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Body: {e.response.text}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def produce_data(self):
        """Continuously produce air quality data to Kafka."""
        print("Starting to produce air quality data to Kafka...")
        
        try:
            while True:
                data = self.fetch_air_quality_data()
                if data:
                    self.producer.send('air_quality_telematics', value=data)
                    location = data['location']
                    sensors_str = ", ".join([f"{m['display_name']} ({m['unit']})" for m in data['measurements'].values()])
                    print(f"Sent data for Location='{location.get('name', 'N/A')}' (ID: {location.get('id', 'N/A')}): {sensors_str}")
                    
                    # Increment counter and check if we should switch locations
                    self.location_switch_counter += 1
                    if self.location_switch_counter >= self.location_switch_interval:
                        print(f"Switching location after {self.location_switch_interval} successful fetches...")
                        self.location_id = None
                        self.location_switch_counter = 0
                else:
                    print("No data fetched from OpenAQ API. Retrying...")
                    # If we failed to fetch data, try a new location
                    self.location_id = None
                
                time.sleep(self.base_delay)  # Wait between requests to avoid rate limits
                
        except KeyboardInterrupt:
            print("\nStopping producer...")
        finally:
            self.producer.close()

def main():
    producer = AirQualityProducer()
    producer.produce_data()

if __name__ == "__main__":
    main()
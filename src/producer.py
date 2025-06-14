import json
import time
import requests
from datetime import datetime
from kafka import KafkaProducer
import os

class AirQualityProducer:
    def __init__(self, kafka_bootstrap_servers=['localhost:9092']):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.openaq_api_key = "88838150d78cc39b601713a871dc7136deecb5d043698368146d318fd22a2cfe"
        self.location_id = None  # Will be set after finding a valid location
        print("Initialized Kafka producer")

    def find_active_location(self):
        """Find an active location in Kathmandu."""
        try:
            url = "https://api.openaq.org/v3/locations"
            headers = {
                "X-API-Key": self.openaq_api_key
            }
            params = {
                "city": "Kathmandu",
                "country": "NP",
                "limit": 10,
                "order_by": "lastUpdated",
                "sort": "desc"
            }
            
            print("Searching for active locations in Kathmandu...")
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data and 'results' in data and data['results']:
                # Find the first location with recent data
                for location in data['results']:
                    if location.get('lastUpdated'):
                        self.location_id = str(location['id'])
                        print(f"Found active location: {location.get('name')} (ID: {self.location_id})")
                        return True
            
            print("No active locations found in Kathmandu")
            return False
            
        except Exception as e:
            print(f"Error searching for locations: {e}")
            return False

    def fetch_air_quality_data(self):
        """Fetch real-time air quality data from OpenAQ API v3."""
        try:
            if not self.location_id:
                if not self.find_active_location():
                    return None

            current_time = datetime.now()
            
            # Fetch the latest measurements
            measurements_url = "https://api.openaq.org/v3/measurements"
            params = {
                "location_id": self.location_id,
                "limit": 10,
                "order_by": "datetime",
                "sort": "desc"
            }
            headers = {
                "X-API-Key": self.openaq_api_key
            }
            
            print(f"Fetching latest measurements for location {self.location_id}...")
            response = requests.get(measurements_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data and 'results' in data and data['results']:
                # Group measurements by parameter
                measurements = {}
                for measurement in data['results']:
                    param = measurement.get('parameter')
                    if param:
                        measurements[param] = {
                            'value': measurement.get('value'),
                            'unit': measurement.get('unit'),
                            'lastUpdated': measurement.get('date', {}).get('utc')
                        }
                
                if measurements:
                    # Get location details
                    location_url = f"https://api.openaq.org/v3/locations/{self.location_id}"
                    location_response = requests.get(location_url, headers=headers)
                    location_response.raise_for_status()
                    location_data = location_response.json()
                    
                    if location_data and 'results' in location_data and location_data['results']:
                        location_info = location_data['results'][0]
                        record = {
                            "timestamp": current_time.isoformat(),
                            "location_id": self.location_id,
                            "location_name": location_info.get('name', 'Unknown Location'),
                            "city": location_info.get('city', 'Unknown City'),
                            "country": location_info.get('country', 'Unknown Country'),
                            "coordinates": location_info.get('coordinates', {}),
                            "measurements": measurements
                        }
                        return record
            
            print("No valid measurements found in API response")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching air quality data: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response Body: {e.response.text}")
                if e.response.status_code == 401:
                    print("Authentication failed. Please check your API key.")
                elif e.response.status_code == 404:
                    print(f"Location ID {self.location_id} not found or has no recent data.")
                    self.location_id = None  # Reset location ID to trigger a new search
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
                    measurements_str = ", ".join([f"{p}: {v['value']} {v['unit']}" for p, v in data['measurements'].items()])
                    print(f"Sent data for Location='{data.get('location_name', 'N/A')}' (ID: {data.get('location_id', 'N/A')}): {measurements_str}")
                else:
                    print("No data fetched from OpenAQ API. Retrying...")
                
                time.sleep(5)  # Wait 5 seconds between requests to avoid rate limits
                
        except KeyboardInterrupt:
            print("\nStopping producer...")
        finally:
            self.producer.close()

def main():
    producer = AirQualityProducer()
    producer.produce_data()

if __name__ == "__main__":
    main()
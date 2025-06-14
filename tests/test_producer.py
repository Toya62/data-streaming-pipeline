import unittest
from unittest.mock import patch, MagicMock
import json
from src.producer import AirQualityProducer

class TestAirQualityProducer(unittest.TestCase):
    def setUp(self):
        self.producer = AirQualityProducer(['localhost:9092'])

    @patch('requests.get')
    def test_find_active_location(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {
                    'id': 123,
                    'name': 'Test Location',
                    'lastUpdated': '2024-03-15T12:00:00Z'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test finding active location
        result = self.producer.find_active_location()
        self.assertTrue(result)
        self.assertEqual(self.producer.location_id, '123')

    @patch('requests.get')
    def test_fetch_air_quality_data(self, mock_get):
        # Mock location data response
        location_response = MagicMock()
        location_response.json.return_value = {
            'results': [{
                'name': 'Test Location',
                'city': 'Test City',
                'country': 'Test Country',
                'coordinates': {'latitude': 0, 'longitude': 0}
            }]
        }
        location_response.raise_for_status.return_value = None

        # Mock measurements response
        measurements_response = MagicMock()
        measurements_response.json.return_value = {
            'results': [
                {
                    'parameter': 'pm25',
                    'value': 25.5,
                    'unit': 'µg/m³',
                    'date': {'utc': '2024-03-15T12:00:00Z'}
                }
            ]
        }
        measurements_response.raise_for_status.return_value = None

        # Set up mock to return different responses
        mock_get.side_effect = [location_response, measurements_response]

        # Test fetching air quality data
        self.producer.location_id = '123'
        result = self.producer.fetch_air_quality_data()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['location_id'], '123')
        self.assertIn('measurements', result)
        self.assertIn('pm25', result['measurements'])

    @patch('kafka.KafkaProducer')
    def test_producer_initialization(self, mock_kafka):
        # Test producer initialization
        producer = AirQualityProducer(['localhost:9092'])
        self.assertIsNotNone(producer)
        mock_kafka.assert_called_once()

if __name__ == '__main__':
    unittest.main() 
import unittest
from unittest.mock import patch, MagicMock, ANY
import json
import pytest
from src.producer import AirQualityProducer

class TestAirQualityProducer(unittest.TestCase):
    @patch('src.producer.KafkaProducer')
    def setUp(self, mock_kafka):
        # Create a mock instance for KafkaProducer
        self.mock_kafka_instance = MagicMock()
        mock_kafka.return_value = self.mock_kafka_instance
        
        # Initialize producer with mocked Kafka
        self.producer = AirQualityProducer(['localhost:9092'])
        
        # Verify KafkaProducer was called with correct arguments
        mock_kafka.assert_called_once_with(
            bootstrap_servers=['localhost:9092'],
            value_serializer=ANY
        )

    @patch('requests.get')
    def test_fetch_air_quality_data(self, mock_get):
        # Mock location response
        location_response = MagicMock()
        location_response.json.return_value = {
            'results': [{
                'id': '80',
                'name': 'Test Location',
                'sensors': [
                    {
                        'id': '1',
                        'parameter': {
                            'name': 'pm25',
                            'units': 'µg/m³',
                            'displayName': 'PM2.5'
                        }
                    },
                    {
                        'id': '2',
                        'parameter': {
                            'name': 'pm10',
                            'units': 'µg/m³',
                            'displayName': 'PM10'
                        }
                    }
                ]
            }]
        }
        location_response.raise_for_status.return_value = None

        # Mock measurements response
        measurements_response = MagicMock()
        measurements_response.json.return_value = {
            'results': [
                {
                    'value': 25.5,
                    'date': {'utc': '2024-03-15T12:00:00Z'}
                }
            ]
        }
        measurements_response.raise_for_status.return_value = None

        # Configure mock to return different responses for different URLs
        def mock_get_side_effect(url, *args, **kwargs):
            if 'locations' in url:
                return location_response
            elif 'sensors' in url:
                return measurements_response
            return MagicMock()

        mock_get.side_effect = mock_get_side_effect

        # Test fetching air quality data
        self.producer.location_id = '80'
        result = self.producer.fetch_air_quality_data()

        # Verify the result
        self.assertIsNotNone(result)
        self.assertIn('measurements', result)
        self.assertIn('pm25', result['measurements'])
        self.assertIn('pm10', result['measurements'])
        
        # Verify measurement values
        self.assertEqual(result['measurements']['pm25']['value'], 25.5)
        self.assertEqual(result['measurements']['pm10']['value'], 25.5)
        self.assertEqual(result['measurements']['pm25']['unit'], 'µg/m³')
        self.assertEqual(result['measurements']['pm10']['unit'], 'µg/m³')

    @patch('requests.get')
    def test_find_location(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {
                    'id': 80,
                    'name': 'Amsterdam-Van Diemenstraat',
                    'locality': 'Amsterdam',
                    'country': {
                        'code': 'NL',
                        'name': 'Netherlands'
                    },
                    'coordinates': {
                        'latitude': 52.389983,
                        'longitude': 4.887810
                    },
                    'sensors': [
                        {
                            'parameter': {
                                'name': 'pm25'
                            }
                        },
                        {
                            'parameter': {
                                'name': 'pm10'
                            }
                        }
                    ]
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test finding active location
        result = self.producer.find_location()

        self.assertTrue(result)
        self.assertIsNotNone(self.producer.location_id)
        self.assertEqual(self.producer.location_id, '80')

    def test_producer_initialization(self):
        # Test producer initialization
        self.assertIsNotNone(self.producer)
        self.assertIsNotNone(self.producer.producer)
        self.assertIsNotNone(self.producer.openaq_api_key)
        self.assertIsNone(self.producer.location_id)
        self.assertEqual(self.producer.location_switch_counter, 0)
        self.assertEqual(self.producer.location_switch_interval, 10)

if __name__ == '__main__':
    unittest.main() 
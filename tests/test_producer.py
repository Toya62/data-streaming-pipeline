import unittest
from unittest.mock import patch, MagicMock
import json
import pytest
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
        result = self.producer.find_active_location()
        self.assertTrue(result)
        self.assertEqual(self.producer.location_id, '80')

    @patch('requests.get')
    def test_fetch_air_quality_data(self, mock_get):
        # Mock measurements response
        measurements_response = MagicMock()
        measurements_response.json.return_value = {
            'results': [
                {
                    'parameter': 'pm25',
                    'value': 25.5,
                    'unit': 'µg/m³',
                    'date': {'utc': '2024-03-15T12:00:00Z'}
                },
                {
                    'parameter': 'pm10',
                    'value': 35.5,
                    'unit': 'µg/m³',
                    'date': {'utc': '2024-03-15T12:00:00Z'}
                }
            ]
        }
        measurements_response.raise_for_status.return_value = None
        mock_get.return_value = measurements_response

        # Test fetching air quality data
        self.producer.location_id = '80'
        result = self.producer.fetch_air_quality_data()
        
        self.assertIsNotNone(result)
        self.assertIn('measurements', result)
        self.assertIn('pm25', result['measurements'])
        self.assertIn('pm10', result['measurements'])

    @patch('kafka.KafkaProducer')
    def test_producer_initialization(self, mock_kafka):
        # Test producer initialization
        mock_kafka.return_value = MagicMock()
        producer = AirQualityProducer(['localhost:9092'])
        self.assertIsNotNone(producer)
        mock_kafka.assert_called_once()

if __name__ == '__main__':
    unittest.main() 
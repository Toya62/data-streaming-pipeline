import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta
import pytest
from src.flink_pipeline import AirQualityFilter, AirQualityTransformer

class TestAirQualityPipeline(unittest.TestCase):
    def setUp(self):
        self.filter = AirQualityFilter()
        self.transformer = AirQualityTransformer()

    def test_filter_function(self):
        # Test data with valid measurements
        valid_data = {
            "location": {
                "datetimeLast": {
                    "utc": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
                }
            },
            "measurements": {
                "pm25": {"value": 40.0, "unit": "µg/m³"},
                "pm10": {"value": 25.0, "unit": "µg/m³"}
            }
        }
        self.assertTrue(self.filter.filter(valid_data))

        # Test data with invalid measurements
        invalid_data = {
            "location": {
                "datetimeLast": {
                    "utc": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
                }
            },
            "measurements": {
                "co": {"value": 30.0, "unit": "µg/m³"}
            }
        }
        self.assertFalse(self.filter.filter(invalid_data))

    def test_transform_function(self):
        # Test data transformation
        input_data = {
            "location": {
                "name": "Test Location",
                "coordinates": {
                    "latitude": 52.389983,
                    "longitude": 4.887810
                }
            },
            "measurements": {
                "pm25": {"value": 40.0, "unit": "µg/m³"},
                "pm10": {"value": 60.0, "unit": "µg/m³"}
            }
        }
        
        result = self.transformer.transform(input_data)
        
        self.assertIsNotNone(result)
        self.assertIn("location", result)
        self.assertIn("measurements", result)
        self.assertIn("aqi", result)
        self.assertIn("processed_at", result)
        self.assertIn("aqi_category", result)
        
        # Verify AQI calculation
        self.assertGreater(result["aqi"], 0)
        self.assertIsInstance(result["aqi_category"], str)

if __name__ == '__main__':
    unittest.main() 
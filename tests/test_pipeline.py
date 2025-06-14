import unittest
from unittest.mock import patch, MagicMock
import json
from src.main import AirQualityFilterFunction, AirQualityMapFunction

class TestAirQualityPipeline(unittest.TestCase):
    def setUp(self):
        self.filter_config = {"pm25": 35.4, "pm1": 20}
        self.transform_config = {"operation": "add_timestamp"}
        self.filter_function = AirQualityFilterFunction(self.filter_config)
        self.map_function = AirQualityMapFunction(self.transform_config)

    def test_filter_function(self):
        # Test data with valid measurements
        valid_data = {
            "measurements": {
                "pm25": {"value": 40.0, "unit": "µg/m³"},
                "pm1": {"value": 25.0, "unit": "µg/m³"}
            }
        }
        self.assertTrue(self.filter_function.filter(valid_data))

        # Test data with invalid measurements
        invalid_data = {
            "measurements": {
                "pm25": {"value": 30.0, "unit": "µg/m³"},
                "pm1": {"value": 15.0, "unit": "µg/m³"}
            }
        }
        self.assertFalse(self.filter_function.filter(invalid_data))

    def test_map_function(self):
        # Test data transformation
        input_data = {
            "location_id": "123",
            "measurements": {
                "pm25": {"value": 40.0, "unit": "µg/m³"}
            }
        }
        
        result = self.map_function.map(input_data)
        
        self.assertIsNotNone(result)
        self.assertIn("timestamp", result)
        self.assertIn("measurements", result)
        self.assertIn("average_value", result)
        self.assertIn("air_quality_category", result)

    def test_map_function_with_string_measurements(self):
        # Test handling string measurements
        input_data = {
            "location_id": "123",
            "measurements": json.dumps({
                "pm25": {"value": 40.0, "unit": "µg/m³"}
            })
        }
        
        result = self.map_function.map(input_data)
        
        self.assertIsNotNone(result)
        self.assertIn("timestamp", result)
        self.assertIn("measurements", result)
        self.assertIn("average_value", result)

    def test_filter_function_with_string_measurements(self):
        # Test handling string measurements in filter
        valid_data = {
            "measurements": json.dumps({
                "pm25": {"value": 40.0, "unit": "µg/m³"},
                "pm1": {"value": 25.0, "unit": "µg/m³"}
            })
        }
        self.assertTrue(self.filter_function.filter(valid_data))

if __name__ == '__main__':
    unittest.main() 
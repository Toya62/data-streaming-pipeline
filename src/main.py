#!/usr/bin/env python3
"""
Main entry point for the Air Quality Data Pipeline.
This script can run the entire pipeline or individual components.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment variables and directories."""
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Check for required environment variables
    required_vars = ['OPENAQ_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        sys.exit(1)

def run_producer():
    """Run the data producer component."""
    from producer import main as producer_main
    logger.info("Starting producer...")
    producer_main()

def run_flink_pipeline():
    """Run the Flink pipeline component."""
    from flink_pipeline import main as flink_main
    logger.info("Starting Flink pipeline...")
    flink_main()

def run_tests():
    """Run the test suite."""
    from test_pipeline import main as test_main
    logger.info("Running tests...")
    test_main()

def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(description='Air Quality Data Pipeline')
    parser.add_argument('--component', choices=['producer', 'flink', 'test', 'all'],
                      default='all', help='Component to run')
    parser.add_argument('--env-file', default='.env',
                      help='Path to .env file')
    
    args = parser.parse_args()
    
    # Load environment variables
    if os.path.exists(args.env_file):
        from dotenv import load_dotenv
        load_dotenv(args.env_file)
    
    # Set up environment
    setup_environment()
    
    # Run selected component(s)
    if args.component == 'all':
        logger.info("Running full pipeline...")
        run_producer()
        run_flink_pipeline()
    elif args.component == 'producer':
        run_producer()
    elif args.component == 'flink':
        run_flink_pipeline()
    elif args.component == 'test':
        run_tests()

if __name__ == "__main__":
    main()
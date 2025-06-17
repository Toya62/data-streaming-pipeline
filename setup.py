from setuptools import setup, find_packages

setup(
    name="data-streaming-pipeline",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "kafka-python",
        "requests",
        "python-dotenv",
        "apache-flink",
        "pytest",
        "pytest-cov"
    ],
    python_requires=">=3.8",
) 
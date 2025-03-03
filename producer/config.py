"""
Configuration for the producer service.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RabbitMQConfig:
    """
    RabbitMQ configuration.
    """
    HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    PORT: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    USER: str = os.getenv("RABBITMQ_USER", "guest")
    PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    QUEUE: str = os.getenv("RABBITMQ_QUEUE", "financial_data_queue")
    EXCHANGE: str = os.getenv("RABBITMQ_EXCHANGE", "financial_data_exchange")
    ROUTING_KEY: str = os.getenv("RABBITMQ_ROUTING_KEY", "financial_data")


class APIConfig:
    """
    API configuration.
    """
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    TITLE: str = "Financial Data Processing API"
    DESCRIPTION: str = "API for submitting financial data for processing"
    VERSION: str = "1.0.0"


class Config:
    """
    Main configuration.
    """
    RABBITMQ: RabbitMQConfig = RabbitMQConfig()
    API: APIConfig = APIConfig()


# Create a singleton instance
config = Config()

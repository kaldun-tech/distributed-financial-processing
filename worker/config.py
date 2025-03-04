"""
Configuration for the worker service.
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


class MongoDBConfig:
    """
    MongoDB configuration.
    """
    URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DB: str = os.getenv("MONGODB_DB", "financial_data")
    COLLECTION: str = os.getenv("MONGODB_COLLECTION", "financial_data")


class OpenAIConfig:
    """
    OpenAI configuration.
    """
    API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL: str = "gpt-4o"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.0


class Config:
    """
    Main configuration.
    """
    RABBITMQ: RabbitMQConfig = RabbitMQConfig()
    MONGODB: MongoDBConfig = MongoDBConfig()
    OPENAI: OpenAIConfig = OpenAIConfig()


# Create a singleton instance
config = Config()

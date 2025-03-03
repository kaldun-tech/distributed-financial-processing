"""
RabbitMQ client for the producer service.
"""
import json
import logging
import pika
from typing import Dict, Any, Optional
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from producer.config import config
from common.utils import serialize_to_json

# Configure logging
logger = logging.getLogger(__name__)


class RabbitMQClient:
    """
    Client for interacting with RabbitMQ.
    """

    def __init__(self) -> None:
        """
        Initialize the RabbitMQ client.
        """
        self.host = config.RABBITMQ.HOST
        self.port = config.RABBITMQ.PORT
        self.user = config.RABBITMQ.USER
        self.password = config.RABBITMQ.PASSWORD
        self.queue = config.RABBITMQ.QUEUE
        self.exchange = config.RABBITMQ.EXCHANGE
        self.routing_key = config.RABBITMQ.ROUTING_KEY
        self.connection = None
        self.channel = None

    def connect(self) -> None:
        """
        Connect to RabbitMQ.
        
        Raises:
            AMQPConnectionError: If connection to RabbitMQ fails
        """
        try:
            # Create connection parameters
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )

            # Connect to RabbitMQ
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare exchange and queue
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='direct',
                durable=True
            )

            self.channel.queue_declare(
                queue=self.queue,
                durable=True
            )

            self.channel.queue_bind(
                queue=self.queue,
                exchange=self.exchange,
                routing_key=self.routing_key
            )

            logger.info("Connected to RabbitMQ at %s:%s", self.host, self.port)
        except AMQPConnectionError as e:
            logger.error("Failed to connect to RabbitMQ: %s", e)
            raise

    def publish(self, message: Dict[str, Any]) -> None:
        """
        Publish a message to RabbitMQ.
        
        Args:
            message: Message to publish
            
        Raises:
            AMQPConnectionError: If connection to RabbitMQ fails
        """
        if not self.connection or self.connection.is_closed:
            self.connect()

        try:
            # Serialize message to JSON
            message_body = serialize_to_json(message)

            # Publish message
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )

            logger.info("Published message to RabbitMQ: %s", message)
        except AMQPConnectionError as e:
            logger.error("Failed to connect to RabbitMQ: %s", e)
            raise
        except AMQPChannelError as e:
            logger.error("Channel error when publishing to RabbitMQ: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error when publishing to RabbitMQ: %s", e)
            raise

    def close(self) -> None:
        """
        Close the connection to RabbitMQ.
        """
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed connection to RabbitMQ")


# Create a singleton instance
rabbitmq_client = RabbitMQClient()

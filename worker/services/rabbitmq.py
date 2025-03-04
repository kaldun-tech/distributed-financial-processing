"""
RabbitMQ client for the worker service.
"""
import json
import logging
import pika
from typing import Dict, Any, Callable, Optional
from pika.exceptions import AMQPConnectionError, AMQPChannelError
from pymongo.errors import ConnectionFailure
from openai.error import APIError, Timeout, RateLimitError, APIConnectionError, InvalidRequestError

from worker.config import config
from common.utils import deserialize_from_json

# Configure logging
logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    Consumer for RabbitMQ messages.
    """

    def __init__(self) -> None:
        """
        Initialize the RabbitMQ consumer.
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

            # Set QoS prefetch count
            self.channel.basic_qos(prefetch_count=1)

            logger.info("Connected to RabbitMQ at %s:%s", self.host, self.port)
        except AMQPConnectionError as e:
            logger.error("Failed to connect to RabbitMQ: %s", e)
            raise

    def consume(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Consume messages from RabbitMQ.
        
        Args:
            callback: Callback function to process messages
            
        Raises:
            AMQPConnectionError: If connection to RabbitMQ fails
        """
        if not self.connection or self.connection.is_closed:
            self.connect()

        def on_message(ch: pika.channel.Channel, method: pika.spec.Basic.Deliver, 
                       properties: pika.spec.BasicProperties, body: bytes) -> None:
            """
            Process a message from RabbitMQ.
            
            Args:
                ch: Channel
                method: Method
                properties: Properties
                body: Message body
            """
            try:
                # Deserialize message from JSON
                message = deserialize_from_json(body.decode('utf-8'))

                # Process message
                callback(message)

                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)

                logger.info("Processed message: %s", message)
            except json.JSONDecodeError as e:
                logger.error("Failed to decode message JSON: %s", e)
                # Negative acknowledgement without requeue for malformed messages
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except (APIError, Timeout, RateLimitError, APIConnectionError, InvalidRequestError) as e:
                logger.error("OpenAI API error while processing message: %s", e)
                # Negative acknowledgement with requeue for OpenAI API errors
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            except ConnectionFailure as e:
                logger.error("MongoDB connection error while processing message: %s", e)
                # Negative acknowledgement with requeue for MongoDB connection errors
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            except ValueError as e:
                logger.error("Value error while processing message: %s", e)
                # Negative acknowledgement without requeue for value errors
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except (AMQPConnectionError, AMQPChannelError) as e:
                logger.error("RabbitMQ error while processing message: %s", e)
                # Let RabbitMQ connection errors propagate
                raise

        # Start consuming
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=on_message
        )

        logger.info("Started consuming messages from queue %s", self.queue)

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.close()
        except AMQPConnectionError as e:
            logger.error("Connection error while consuming messages: %s", e)
            self.close()
            raise
        except AMQPChannelError as e:
            logger.error("Channel error while consuming messages: %s", e)
            self.close()
            raise
        except Exception as e:
            logger.error("Unexpected error while consuming messages: %s", e)
            self.close()
            raise

    def close(self) -> None:
        """
        Close the connection to RabbitMQ.
        """
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed connection to RabbitMQ")


# Create a singleton instance
rabbitmq_consumer = RabbitMQConsumer()

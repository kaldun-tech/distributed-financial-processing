"""
Worker service for processing financial data.
"""
import logging
import signal
import sys
import json
from typing import Dict, Any
from pymongo.errors import ConnectionFailure
from openai.error import APIError, Timeout, RateLimitError, APIConnectionError, InvalidRequestError
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from worker.services.rabbitmq import rabbitmq_consumer
from worker.services.openai_client import openai_client
from worker.services.mongodb import mongodb_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_message(message: Dict[str, Any]) -> None:
    """
    Process a message from RabbitMQ.
    
    Args:
        message: Message from RabbitMQ
    """
    try:
        # Extract raw text from message
        raw_text = message.get('raw_text')
        request_id = message.get('request_id', 'unknown')

        if not raw_text:
            logger.warning("Received message with no raw_text, skipping. Request ID: %s", request_id)
            return

        logger.info("Processing message with request ID: %s", request_id)

        # Extract structured data using OpenAI
        structured_data = openai_client.extract_financial_data(raw_text)

        # Add request ID to metadata
        if structured_data.metadata is None:
            structured_data.metadata = {}
        structured_data.metadata['request_id'] = request_id

        # Store data in MongoDB
        document = structured_data.dict()
        document_id = mongodb_client.insert_one(document)

        logger.info("Successfully processed and stored financial data. MongoDB ID: %s", document_id)
    except (APIError, Timeout, RateLimitError, APIConnectionError, InvalidRequestError) as e:
        logger.error("OpenAI API error while processing message: %s", e)
        # Let the exception propagate to the consumer for proper handling
        raise
    except ConnectionFailure as e:
        logger.error("MongoDB error while processing message: %s", e)
        # Let the exception propagate to the consumer for proper handling
        raise
    except json.JSONDecodeError as e:
        logger.error("JSON parsing error while processing message: %s", e)
        # Let the exception propagate to the consumer for proper handling
        raise
    except ValueError as e:
        logger.error("Value error while processing message: %s", e)
        # Let the exception propagate to the consumer for proper handling
        raise
    except Exception as e:
        logger.error("Unexpected error while processing message: %s", e)
        # Let the exception propagate to the consumer for proper handling
        raise


def setup_signal_handlers() -> None:
    """
    Set up signal handlers for graceful shutdown.
    """
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal, closing connections...")
        rabbitmq_consumer.close()
        mongodb_client.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """
    Main entry point for the worker service.
    """
    try:
        # Connect to services
        logger.info("Starting worker service...")

        # Connect to MongoDB
        logger.info("Connecting to MongoDB...")
        mongodb_client.connect()

        # Set up signal handlers
        setup_signal_handlers()

        # Start consuming messages
        logger.info("Starting to consume messages from RabbitMQ...")
        rabbitmq_consumer.consume(process_message)
    except KeyboardInterrupt:
        logger.info("Worker service stopped by user")
    except ConnectionFailure as e:
        logger.error("Failed to connect to MongoDB: %s", e)
        sys.exit(1)
    except (APIError, Timeout, RateLimitError, APIConnectionError, InvalidRequestError) as e:
        logger.error("OpenAI API error in worker service: %s", e)
        sys.exit(1)
    except AMQPConnectionError as e:
        logger.error("Failed to connect to RabbitMQ: %s", e)
        sys.exit(1)
    except AMQPChannelError as e:
        logger.error("RabbitMQ channel error: %s", e)
        sys.exit(1)
    finally:
        # Close connections
        rabbitmq_consumer.close()
        mongodb_client.close()


if __name__ == "__main__":
    main()

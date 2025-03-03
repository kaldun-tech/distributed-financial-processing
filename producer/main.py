"""
FastAPI application for the producer service.
"""
import uuid
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from producer.config import config
from producer.models import RawFinancialData, FinancialDataSubmissionResponse
from producer.services.rabbitmq import rabbitmq_client
import pika

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=config.API.TITLE,
    description=config.API.DESCRIPTION,
    version=config.API.VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """
    Connect to RabbitMQ on startup.
    """
    try:
        rabbitmq_client.connect()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error("Failed to connect to RabbitMQ on startup: %s", e)
    except Exception as e:
        logger.error("Unexpected error when connecting to RabbitMQ: %s", e)
        # Re-raise unexpected exceptions
        raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Close RabbitMQ connection on shutdown.
    """
    rabbitmq_client.close()


@app.post(
    "/api/v1/financial-data/submit",
    response_model=FinancialDataSubmissionResponse,
    summary="Submit financial data for processing",
    description="Submit raw financial data for processing. The data will be sent to a RabbitMQ queue for processing by a worker service."
)
async def submit_financial_data(data: RawFinancialData) -> FinancialDataSubmissionResponse:
    """
    Submit financial data for processing.
    
    Args:
        data: Raw financial data
        
    Returns:
        Response with status and request ID
        
    Raises:
        HTTPException: If submission fails
    """
    try:
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Prepare message for RabbitMQ
        message = {
            "request_id": request_id,
            "raw_text": data.raw_text,
            "metadata": data.metadata
        }

        # Publish message to RabbitMQ
        rabbitmq_client.publish(message)

        # Return response
        return FinancialDataSubmissionResponse(
            message="Financial data submitted for processing",
            status="success",
            request_id=request_id,
            metadata={"raw_text_length": len(data.raw_text)}
        )
    except pika.exceptions.AMQPConnectionError as e:
        logger.error("Failed to connect to RabbitMQ: %s", e)
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to message broker. Please try again later."
        ) from e
    except Exception as e:
        logger.error("Failed to submit financial data: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit financial data: {str(e)}"
        ) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "producer.main:app",
        host=config.API.HOST,
        port=config.API.PORT,
        reload=True
    )

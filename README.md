# Distributed Financial Data Processing

A distributed system for processing financial data using RabbitMQ, OpenAI's ChatGPT API, and MongoDB.

## System Components

1. **Producer Service** - A FastAPI service that accepts raw financial data and sends it to a RabbitMQ queue.
2. **Worker Service** - Consumes messages from the queue, extracts structured financial data using the ChatGPT API, normalizes it, and stores it in MongoDB.
3. **Database Storage** - MongoDB for storing the extracted and normalized financial data.

## Technical Stack

- Python 3.9+
- RabbitMQ as the message broker
- FastAPI for the producer service
- Pika for interacting with RabbitMQ
- OpenAI's ChatGPT API for financial data extraction
- Pymongo for MongoDB interaction
- Docker for containerization

## Setup and Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Start RabbitMQ and MongoDB (using Docker Compose): `docker-compose up -d`
5. Start the producer service: `python -m producer.main`
6. Start the worker service: `python -m worker.main`

## API Endpoints

- `POST /api/v1/financial-data/submit` - Submit raw financial data for processing

## Data Flow

1. Raw financial data is submitted to the producer service
2. Producer service sends the data to a RabbitMQ queue
3. Worker service consumes messages from the queue
4. Worker extracts structured data using OpenAI's ChatGPT API
5. Worker normalizes the data and stores it in MongoDB

## Project Structure

```
.
├── docker-compose.yml        # Docker Compose configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── producer/                 # Producer service
│   ├── __init__.py
│   ├── main.py               # FastAPI application
│   ├── config.py             # Configuration
│   ├── models.py             # Data models
│   └── services/
│       └── rabbitmq.py       # RabbitMQ client
├── worker/                   # Worker service
│   ├── __init__.py
│   ├── main.py               # Worker entry point
│   ├── config.py             # Configuration
│   ├── models.py             # Data models
│   └── services/
│       ├── rabbitmq.py       # RabbitMQ client
│       ├── openai_client.py  # OpenAI API client
│       └── mongodb.py        # MongoDB client
└── common/                   # Shared code
    ├── __init__.py
    ├── models.py             # Shared data models
    └── utils.py              # Utility functions

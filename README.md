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

## Test Client

The repository includes a test client for interacting with the API:

```bash
# Submit default sample text
python test_client.py

# Submit custom text
python test_client.py --text "Apple Inc. reported revenue of $89.5 billion for Q4 2023."

# Use sample data from a CSV file
python test_client.py --file data/sample_data.csv

# Use a specific row from the CSV file
python test_client.py --file data/sample_data.csv --row 3
```

When running the test client without arguments, it will look for the default sample file (`data/sample_data.csv`) and prompt you to:
- Select a row by number
- Choose a random row
- Process all rows (not implemented yet)

## Sample Data

The `data` directory contains sample financial data for testing:

- `sample_data.csv` - Contains various financial statements for testing the system

The CSV file has a simple format with a header row and one column containing the raw financial text:

```csv
raw_text
"Acme Inc reported a operating profit of 30.5 million AUD for Q3 2024."
"Omicron Solutions reported a total assets of 20.8 million USD for Q4 2024."
...
```

You can add your own sample data by following this format or creating a new CSV file.

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
├── data/                     # Sample data for testing
│   └── sample_data.csv       # CSV file with sample financial statements
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
├── common/                   # Shared code
│   ├── __init__.py
│   ├── models.py             # Shared data models
│   └── utils.py              # Utility functions
└── test_client.py            # Test client for the API

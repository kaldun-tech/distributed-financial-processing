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

1. Clone the repository:
   ```bash
   git clone https://github.com/kaldun-tech/distributed-financial-processing.git
   cd distributed-financial-processing
   ```

2. Set up a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (see `.env.example`):
   ```bash
   # Copy the example file and edit with your values
   cp .env.example .env
   ```

5. Start RabbitMQ and MongoDB (using Docker Compose):
   ```bash
   docker-compose up -d
   ```

6. Start the producer service:
   ```bash
   python -m producer.main
   ```

7. Start the worker service:
   ```bash
   python -m worker.main
   ```

## API Endpoints

- `POST /api/v1/financial-data/submit` - Submit raw financial data for processing

## Test Client

The repository includes a test client for interacting with the API:

```bash
# Submit default sample text
python test_client.py

# Submit custom text
python test_client.py --text "Apple Inc. reported revenue of $89.5 billion for Q4 2023."

# Use sample data from a CSV file (processes all rows by default)
python test_client.py --file data/sample_data.csv

# Use a specific row from the CSV file
python test_client.py --file data/sample_data.csv --row 3

# Select a random row from the CSV file
python test_client.py --file data/sample_data.csv --random
```

When running the test client without arguments, it will look for the default sample file (`data/sample_data.csv`) and process all rows. If the file doesn't exist, it will use a default sample text.

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
```

## Development Best Practices

1. **Recommend to use a virtual environment**: This isolates your project dependencies from other Python projects and system packages.

2. **Keep dependencies up to date**: Regularly update your dependencies to get security fixes and new features.

3. **Follow type annotations**: Use type hints throughout the codebase to improve code quality and enable better IDE support.

4. **Handle exceptions properly**: Use specific exception types and proper error handling to make debugging easier.

5. **Write tests**: Ensure your code is tested thoroughly to catch bugs early.

6. **Document your code**: Keep documentation up-to-date, including docstrings and this README.

7. **Use environment variables for configuration**: Never hardcode sensitive information like API keys or database credentials.

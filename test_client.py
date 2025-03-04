"""
Test client for the financial data processing API.
"""
import argparse
import csv
import json
import os
import random
import sys
import time
from typing import Optional, List, Union, Dict, Any

import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from worker.config import config


def submit_financial_data(api_url: str, raw_text: Union[str, List[str]]) -> Dict[str, Any]:
    """
    Submit financial data to the API.
    
    Args:
        api_url: URL of the API
        raw_text: Raw financial text to submit (string or list of strings)
        
    Returns:
        The response from the API as a dictionary
    """
    # Handle single string or list of strings
    if isinstance(raw_text, list):
        for i, text in enumerate(raw_text):
            print(f"\nSubmitting item {i+1} of {len(raw_text)}:")
            _submit_single_item(api_url, text)
    elif isinstance(raw_text, str):
        return _submit_single_item(api_url, raw_text)
    else:
        print("Invalid input type for raw_text. It should be a string or a list of strings.")
        sys.exit(1)


def _submit_single_item(api_url: str, raw_text: str) -> Dict[str, Any]:
    """
    Submit a single financial data item to the API.
    
    Args:
        api_url: URL of the API
        raw_text: Raw financial text to submit
        
    Returns:
        The response from the API as a dictionary
    """
    # Create request payload
    payload = {
        "raw_text": raw_text
    }

    # Make request
    try:
        response = requests.post(
            f"{api_url}/api/v1/financial-data/submit",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10  # Add timeout to prevent hanging indefinitely
        )

        # Check response
        if response.status_code == 200:
            result = response.json()
            print("Financial data submitted successfully:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"Error submitting financial data: {response.status_code}")
            print(response.text)
            sys.exit(1)
    except requests.exceptions.Timeout:
        print("Request timed out. The server may be down or overloaded.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Connection error. Please check if the API server is running.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def get_processed_data(request_id: str, wait_time: int = 0) -> None:
    """
    Retrieve processed financial data from MongoDB for a specific request ID.
    
    Args:
        request_id: The request ID to retrieve data for
        wait_time: Time to wait in seconds before retrieving data (to allow processing)
    """
    try:
        # Wait for processing to complete if specified
        if wait_time > 0:
            print(f"Waiting {wait_time} seconds for processing to complete...")
            time.sleep(wait_time)
        
        # Connect to MongoDB
        client = MongoClient(config.MONGODB.URI)
        db = client[config.MONGODB.DB]
        collection = db[config.MONGODB.COLLECTION]
        
        # Query for the document
        document = collection.find_one({"metadata.request_id": request_id})
        
        # Close MongoDB connection
        client.close()
        
        # Display results
        if document:
            # Remove MongoDB _id field for cleaner output
            if "_id" in document:
                del document["_id"]
                
            print("\nProcessed Financial Data:")
            print(json.dumps(document, indent=2))
        else:
            print(f"\nNo processed data found for request ID: {request_id}")
            print("The data may still be processing or there was an error.")
            
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error retrieving processed data: {e}")
        sys.exit(1)


def load_csv_data(file_path: str, row_index: Optional[int] = None, random_row: bool = False) -> Union[str, List[str]]:
    """
    Load financial data from a CSV file.
    
    Args:
        file_path: Path to the CSV file containing data
        row_index: Index of the row to load (if provided)
        random_row: Whether to select a random row
        
    Returns:
        Raw financial text from the selected row(s) - either a single string or a list of strings
    """
    try:
        with open(file_path, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            rows = list(reader)

        if not rows:
            print(f"No data found in {file_path}")
            sys.exit(1)

        # Case 1: Specific row requested
        if row_index is not None:
            if 0 <= row_index < len(rows):
                return rows[row_index][0]  # Assuming raw_text is in the first column
            else:
                print(f"Invalid row index: {row_index}. Must be between 0 and {len(rows)-1}")
                sys.exit(1)
                
        # Case 2: Random row requested
        if random_row:
            selected_row = random.choice(rows)
            print(f"Randomly selected row: {selected_row[0][:50]}...")
            return selected_row[0]
            
        # Case 3: Default - return all rows
        return [row[0] for row in rows]

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)
    except csv.Error as e:
        print(f"CSV parsing error: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"I/O error while reading file: {e}")
        sys.exit(1)
    except IndexError as e:
        print(f"Index error while processing CSV data: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main entry point.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test client for the financial data processing API")
    parser.add_argument("--api-url", default="http://localhost:8000", help="URL of the API")

    # Create a mutually exclusive group for operation modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--submit", action="store_true", help="Submit financial data for processing (default)")
    mode_group.add_argument("--retrieve", metavar="REQUEST_ID", help="Retrieve processed data for a specific request ID")

    # Create a mutually exclusive group for text input options (only for submit mode)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--text", help="Raw financial text to submit")
    input_group.add_argument("--file", help="Path to a CSV file containing financial data")

    # Selection options for CSV file (only for submit mode)
    selection_group = parser.add_argument_group("Row selection options (only used with --file)")
    selection_group.add_argument("--row", type=int, help="Specific row index to use from the CSV file")
    selection_group.add_argument("--random", action="store_true", help="Select a random row from the CSV file")

    # Options for retrieve mode
    parser.add_argument("--wait", type=int, default=0, help="Wait time in seconds before retrieving data (default: 0)")

    args = parser.parse_args()

    # Retrieve mode
    if args.retrieve:
        get_processed_data(args.retrieve, args.wait)
        return
        
    # Default to submit mode
    # Get the raw text to submit
    raw_text = None

    if args.text:
        raw_text = args.text
    elif args.file:
        raw_text = load_csv_data(args.file, args.row, args.random)
    else:
        # Default sample file
        default_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'sample_data.csv')
        if os.path.exists(default_sample_file):
            raw_text = load_csv_data(default_sample_file, args.row, args.random)
        else:
            # Use default text if no file is provided
            raw_text = "Company XYZ reported a net income of $5.3 million for Q1 2024."
            print("Using default sample text. For more options, use --text, --file, or create a data/sample_data.csv file.")

    # Submit financial data
    result = submit_financial_data(args.api_url, raw_text)
    
    # If wait time is specified, automatically retrieve the processed data after submission
    if isinstance(raw_text, str) and args.wait > 0:
        request_id = result.get("request_id")
        if request_id:
            get_processed_data(request_id, args.wait)


if __name__ == "__main__":
    main()

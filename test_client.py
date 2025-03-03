"""
Test client for the financial data processing API.
"""
import requests
import json
import argparse
import sys


def submit_financial_data(api_url: str, raw_text: str) -> None:
    """
    Submit financial data to the API.
    
    Args:
        api_url: URL of the API
        raw_text: Raw financial text to submit
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
        else:
            print(f"Error submitting financial data: {response.status_code}")
            print(response.text)
    except requests.exceptions.Timeout:
        print("Request timed out. The server may be down or overloaded.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Connection error. Please check if the API server is running.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main entry point.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test client for the financial data processing API")
    parser.add_argument("--api-url", default="http://localhost:8000", help="URL of the API")
    parser.add_argument("--text", default="Company XYZ reported a net income of $5.3 million for Q1 2024.", 
                        help="Raw financial text to submit")
    args = parser.parse_args()

    # Submit financial data
    submit_financial_data(args.api_url, args.text)


if __name__ == "__main__":
    main()

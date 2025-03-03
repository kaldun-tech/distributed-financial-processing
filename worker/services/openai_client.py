"""
OpenAI client for the worker service.
"""
import json
import logging
from typing import Dict, Any, Optional
import openai
from openai.error import APIError, Timeout, RateLimitError, APIConnectionError, InvalidRequestError

from worker.config import config
from common.models import StructuredFinancialData
from common.utils import normalize_financial_value, extract_quarter

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Client for interacting with OpenAI's ChatGPT API.
    """

    def __init__(self) -> None:
        """
        Initialize the OpenAI client.
        """
        self.api_key = config.OPENAI.API_KEY
        self.model = config.OPENAI.MODEL
        self.max_tokens = config.OPENAI.MAX_TOKENS
        self.temperature = config.OPENAI.TEMPERATURE

        # Set API key
        openai.api_key = self.api_key

    def extract_financial_data(self, raw_text: str) -> StructuredFinancialData:
        """
        Extract structured financial data from raw text using OpenAI's ChatGPT API.
        
        Args:
            raw_text: Raw financial text
            
        Returns:
            Structured financial data
            
        Raises:
            APIError: If the OpenAI API returns an error
            Timeout: If the request times out
            RateLimitError: If the API rate limit is exceeded
            APIConnectionError: If there is a connection error
            InvalidRequestError: If the request is invalid
        """
        try:
            # Create prompt for OpenAI
            prompt = self._create_extraction_prompt(raw_text)

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial data extraction assistant. Extract structured financial data from the given text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract response
            response_text = response.choices[0].message.content.strip()

            # Parse JSON response
            try:
                extracted_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If response is not valid JSON, try to extract it from the text
                extracted_data = self._extract_json_from_text(response_text)

            # Normalize data
            structured_data = self._normalize_extracted_data(extracted_data, raw_text)

            logger.info("Successfully extracted financial data from raw text")
            return structured_data
        except (APIError, Timeout, RateLimitError, APIConnectionError, InvalidRequestError) as e:
            logger.error("OpenAI API error: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error when extracting financial data: %s", e)
            raise

    def _create_extraction_prompt(self, raw_text: str) -> str:
        """
        Create a prompt for extracting financial data.
        
        Args:
            raw_text: Raw financial text
            
        Returns:
            Prompt for OpenAI
        """
        return f"""
        Extract the following financial information from the text below:
        - Company name
        - Financial metric (e.g., revenue, net income, profit)
        - Numerical value
        - Currency
        - Time period (quarter/year)

        Text: "{raw_text}"

        Return the extracted information as a JSON object with the following structure:
        {{
            "company": "Company name",
            "metric": "Financial metric",
            "value": "Raw numerical value as string (e.g., '5.3 million')",
            "currency": "Currency code (e.g., 'USD')",
            "quarter": "Financial quarter (e.g., 'Q1 2024')"
        }}

        Only return the JSON object, nothing else.
        """

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Extracted JSON
            
        Raises:
            ValueError: If JSON cannot be extracted
        """
        # Find JSON-like structure in the text
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
            raise ValueError("Could not extract JSON from OpenAI response")

        json_str = text[start_idx:end_idx + 1]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse extracted JSON: {e}")

    def _normalize_extracted_data(self, extracted_data: Dict[str, Any], raw_text: str) -> StructuredFinancialData:
        """
        Normalize extracted data.
        
        Args:
            extracted_data: Extracted data from OpenAI
            raw_text: Original raw text
            
        Returns:
            Normalized structured financial data
            
        Raises:
            ValueError: If required fields are missing
        """
        # Check required fields
        required_fields = ['company', 'metric', 'value', 'currency', 'quarter']
        for field in required_fields:
            if field not in extracted_data:
                raise ValueError(f"Missing required field '{field}' in extracted data")

        # Normalize value
        value_str = extracted_data['value']
        normalized_value = normalize_financial_value(value_str)

        # Normalize quarter if needed
        quarter = extracted_data['quarter']
        if not quarter:
            # Try to extract quarter from raw text
            quarter = extract_quarter(raw_text) or "Unknown"

        # Create structured data
        return StructuredFinancialData(
            company=extracted_data['company'],
            metric=extracted_data['metric'],
            value=normalized_value,
            currency=extracted_data['currency'],
            quarter=quarter,
            raw_text=raw_text,
            metadata={"original_value": value_str}
        )


# Create a singleton instance
openai_client = OpenAIClient()

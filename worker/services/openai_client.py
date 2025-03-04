"""
OpenAI client for the worker service.
"""
import json
import logging
from typing import Dict, Any

from openai import OpenAI

from worker.config import config
from common.models import StructuredFinancialData
from common.utils import normalize_financial_value, extract_quarter

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Client for interacting with OpenAI's ChatGPT API.
    """

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize the OpenAI client with minimal configuration
        self.client = OpenAI(api_key=self.api_key)

        logger.info("Initialized OpenAI client with model %s", self.model)

    def extract_financial_data(self, raw_text: str) -> StructuredFinancialData:
        """
        Extract structured financial data from raw text.
        
        Args:
            raw_text: Raw financial text
            
        Returns:
            Structured financial data
            
        Raises:
            ValueError: If extraction fails
        """
        try:
            # Create system prompt
            system_prompt = """
            You are a financial data extraction assistant. Extract the following information from the given financial text:
            1. Company name
            2. Financial metric (e.g., revenue, net income, EBITDA)
            3. Value (numerical value only)
            4. Currency (e.g., USD, EUR)
            5. Quarter (e.g., Q1 2023)
            
            Return the extracted information as a JSON object with the following structure:
            {
                "company": "Company name",
                "metric": "Financial metric",
                "value": "Numerical value (as a string)",
                "currency": "Currency code",
                "quarter": "Quarter"
            }
            
            Only include the JSON object in your response, nothing else.
            """

            # Create user prompt
            user_prompt = f"Extract financial data from the following text: {raw_text}"

            # Create messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract response text
            response_text = response.choices[0].message.content.strip()

            # Parse JSON from response
            extracted_data = self._extract_json_from_text(response_text)

            # Normalize extracted data
            structured_data = self._normalize_extracted_data(extracted_data, raw_text)

            logger.info("Successfully extracted financial data: %s", structured_data)

            return structured_data

        except Exception as e:
            logger.error("Failed to extract financial data: %s", e)
            raise

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Extracted JSON
            
        Raises:
            ValueError: If JSON extraction fails
        """
        # Check if the text is already valid JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from text
        start_idx = text.find('{')
        end_idx = text.rfind('}')

        if start_idx == -1 or end_idx == -1:
            raise ValueError("Could not find JSON in response")

        json_str = text[start_idx:end_idx + 1]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse extracted JSON: {e}") from e

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
                raise ValueError(f"Missing required field: {field}")

        # Normalize value
        value_str = str(extracted_data['value'])
        value = normalize_financial_value(value_str)

        # Normalize quarter
        quarter = extract_quarter(extracted_data['quarter'])

        # Create structured data
        structured_data = StructuredFinancialData(
            company=extracted_data['company'],
            metric=extracted_data['metric'].lower(),
            value=value,
            currency=extracted_data['currency'].upper(),
            quarter=quarter,
            raw_text=raw_text
        )

        return structured_data


# Create a singleton instance
openai_client = OpenAIClient(
    api_key=config.OPENAI.API_KEY,
    model=config.OPENAI.MODEL,
    max_tokens=config.OPENAI.MAX_TOKENS,
    temperature=config.OPENAI.TEMPERATURE
)

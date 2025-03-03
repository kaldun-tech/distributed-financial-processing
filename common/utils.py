"""
Utility functions shared between producer and worker services.
"""
import json
import re
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def serialize_to_json(data: Dict[str, Any]) -> str:
    """
    Serialize a dictionary to a JSON string.
    
    Args:
        data: Dictionary to serialize
        
    Returns:
        JSON string
    """
    return json.dumps(data)


def deserialize_from_json(json_str: str) -> Dict[str, Any]:
    """
    Deserialize a JSON string to a dictionary.
    
    Args:
        json_str: JSON string to deserialize
        
    Returns:
        Dictionary
    """
    return json.loads(json_str)


def normalize_financial_value(value_str: str) -> float:
    """
    Normalize financial values from text to numeric values.
    
    Examples:
        "$5.3 million" -> 5300000
        "5.3M" -> 5300000
        "1.2 billion" -> 1200000000
        
    Args:
        value_str: String representation of a financial value
        
    Returns:
        Normalized numeric value
    """
    # Remove currency symbols and whitespace
    cleaned_value = re.sub(r'[$£€¥]', '', value_str).strip()

    # Extract the numeric part and the multiplier
    match = re.search(r'([-+]?\d*\.?\d+)\s*(thousand|million|billion|trillion|[kmbt])?', cleaned_value, re.IGNORECASE)

    if not match:
        logger.warning("Could not parse financial value: %s", value_str)
        return 0.0

    numeric_value = float(match.group(1))
    multiplier = match.group(2)

    # Apply multiplier
    if multiplier:
        multiplier = multiplier.lower()
        if multiplier in ['thousand', 'k']:
            numeric_value *= 1_000
        elif multiplier in ['million', 'm']:
            numeric_value *= 1_000_000
        elif multiplier in ['billion', 'b']:
            numeric_value *= 1_000_000_000
        elif multiplier in ['trillion', 't']:
            numeric_value *= 1_000_000_000_000

    return numeric_value


def extract_quarter(text: str) -> Optional[str]:
    """
    Extract quarter information from text.
    
    Examples:
        "Q1 2024" -> "Q1 2024"
        "first quarter of 2024" -> "Q1 2024"
        "2024 Q1" -> "Q1 2024"
        
    Args:
        text: Text containing quarter information
        
    Returns:
        Normalized quarter string or None if not found
    """
    # Direct quarter notation (e.g., "Q1 2024")
    direct_match = re.search(r'Q([1-4])\s*(\d{4})', text, re.IGNORECASE)
    if direct_match:
        return f"Q{direct_match.group(1)} {direct_match.group(2)}"

    # Year first notation (e.g., "2024 Q1")
    year_first_match = re.search(r'(\d{4})\s*Q([1-4])', text, re.IGNORECASE)
    if year_first_match:
        return f"Q{year_first_match.group(2)} {year_first_match.group(1)}"

    # Written format (e.g., "first quarter of 2024")
    quarters = {
        'first': '1',
        'second': '2',
        'third': '3',
        'fourth': '4'
    }

    for quarter_name, quarter_num in quarters.items():
        pattern = rf'{quarter_name}\s+quarter\s+of\s+(\d{{4}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"Q{quarter_num} {match.group(1)}"

    return None

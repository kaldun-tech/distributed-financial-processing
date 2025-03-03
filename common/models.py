"""
Common data models shared between producer and worker services.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RawFinancialData(BaseModel):
    """
    Model representing raw, unstructured financial data.
    """
    raw_text: str = Field(..., description="Raw financial text to be processed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata about the financial data")


class StructuredFinancialData(BaseModel):
    """
    Model representing structured, normalized financial data.
    """
    company: str = Field(..., description="Company name")
    metric: str = Field(..., description="Financial metric (e.g., 'net income', 'revenue')")
    value: float = Field(..., description="Numerical value of the metric")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")
    quarter: str = Field(..., description="Financial quarter (e.g., 'Q1 2024')")
    raw_text: str = Field(..., description="Original raw text that was processed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata about the financial data")

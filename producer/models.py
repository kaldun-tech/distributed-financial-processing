"""
Data models for the producer service.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Re-export common models
from common.models import RawFinancialData


class FinancialDataSubmissionResponse(BaseModel):
    """
    Response model for financial data submission.
    """
    message: str = Field(..., description="Response message")
    status: str = Field(..., description="Status of the submission")
    request_id: str = Field(..., description="Unique identifier for the request")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata about the submission")

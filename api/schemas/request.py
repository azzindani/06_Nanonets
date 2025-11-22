"""
Request schemas for API endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class OCRRequest(BaseModel):
    """Request schema for OCR processing."""
    max_tokens: int = Field(default=2048, ge=100, le=8000)
    max_image_size: int = Field(default=1536, ge=256, le=4096)
    output_format: str = Field(default="json", pattern="^(json|xml|csv)$")
    extract_fields: bool = Field(default=True)
    enabled_fields: Optional[List[str]] = None
    custom_fields: Optional[List[str]] = None
    webhook_url: Optional[str] = None
    confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)


class WebhookRequest(BaseModel):
    """Request schema for webhook registration."""
    url: str
    events: List[str] = Field(default=["document.processed"])
    secret: Optional[str] = None

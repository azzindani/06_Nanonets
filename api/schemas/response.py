"""
Response schemas for API endpoints.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    model_loaded: bool
    gpu_available: bool
    version: str
    timestamp: str


class OCRPageResult(BaseModel):
    """Result for a single page."""
    page_number: int
    text: str
    processing_time_seconds: float
    success: bool


class DocumentMetadata(BaseModel):
    """Document metadata."""
    filename: str
    file_size_mb: float
    file_type: str
    total_pages: int


class OCRResponse(BaseModel):
    """Response schema for OCR processing."""
    job_id: str
    status: str
    processing_time_ms: int
    document: DocumentMetadata
    result: Dict[str, Any]
    extracted_fields: Optional[Dict[str, str]] = None
    confidence_scores: Optional[Dict[str, float]] = None


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str
    detail: Optional[str] = None
    timestamp: str


class ModelInfo(BaseModel):
    """Model information response."""
    name: str
    device: str
    quantization: str
    memory_used_gb: float
    is_loaded: bool

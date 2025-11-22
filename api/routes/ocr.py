"""
OCR processing endpoints.
"""
import os
import time
import uuid
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from api.schemas.response import OCRResponse, DocumentMetadata, ErrorResponse
from core.ocr_engine import get_ocr_engine
from core.output_parser import OutputParser
from core.field_extractor import FieldExtractor
from core.format_converter import FormatConverter
from config import PREDEFINED_FIELDS

router = APIRouter()


@router.post("/ocr", response_model=OCRResponse)
async def process_document(
    file: UploadFile = File(...),
    max_tokens: int = Form(default=2048),
    max_image_size: int = Form(default=1536),
    output_format: str = Form(default="json"),
    extract_fields: bool = Form(default=True),
    webhook_url: Optional[str] = Form(default=None),
    confidence_threshold: float = Form(default=0.75)
):
    """
    Process a document with OCR.

    Args:
        file: Document file (PDF or image).
        max_tokens: Maximum tokens for generation.
        max_image_size: Maximum image dimension.
        output_format: Output format (json, xml, csv).
        extract_fields: Whether to extract predefined fields.
        webhook_url: URL for webhook callback.
        confidence_threshold: Minimum confidence for field extraction.

    Returns:
        OCRResponse with extracted data.
    """
    job_id = str(uuid.uuid4())
    start_time = time.time()

    # Validate file type
    filename = file.filename or "document"
    extension = os.path.splitext(filename)[1].lower()

    supported = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.pdf']
    if extension not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Get OCR engine
        engine = get_ocr_engine()

        # Process document
        result = engine.process_document(
            tmp_path,
            max_tokens=max_tokens
        )

        # Parse output
        parser = OutputParser()
        parsed = parser.parse(result.total_text)

        # Convert to requested format
        converter = FormatConverter()

        if output_format == "json":
            formatted_output = converter.to_json(parsed)
        elif output_format == "xml":
            formatted_output = converter.to_xml(parsed)
        else:
            formatted_output = converter.to_json(parsed)

        # Extract fields if requested
        extracted_fields = None
        confidence_scores = None

        if extract_fields:
            extractor = FieldExtractor()
            field_results = extractor.extract(
                result.total_text,
                enabled_fields=PREDEFINED_FIELDS
            )
            extracted_fields = extractor.to_dict(field_results)
            confidence_scores = extractor.get_confidence_scores(field_results)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = OCRResponse(
            job_id=job_id,
            status="completed",
            processing_time_ms=processing_time_ms,
            document=DocumentMetadata(
                filename=filename,
                file_size_mb=len(content) / (1024 * 1024),
                file_type=extension.upper().replace('.', ''),
                total_pages=result.metadata.total_pages
            ),
            result={
                "text": result.total_text,
                "pages": [
                    {
                        "page_number": page.page_number,
                        "text": page.text,
                        "success": page.success
                    }
                    for page in result.pages
                ],
                "tables_count": sum(len(p.tables_html) for p in parsed.pages),
                "equations_count": sum(len(p.latex_equations) for p in parsed.pages),
                "formatted_output": formatted_output
            },
            extracted_fields=extracted_fields,
            confidence_scores=confidence_scores
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/ocr/{job_id}")
async def get_job_status(job_id: str):
    """
    Get status of an OCR job.

    For synchronous processing, this always returns completed.
    For async processing (future), this would check job queue.
    """
    return {
        "job_id": job_id,
        "status": "completed",
        "message": "Synchronous processing - job completed immediately"
    }

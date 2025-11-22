"""
Health check endpoints.
"""
from datetime import datetime
import torch
from fastapi import APIRouter

from api.schemas.response import HealthResponse, ModelInfo
from models.model_manager import get_model_manager

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check API health status.
    """
    model_manager = get_model_manager()
    model_info = model_manager.get_model_info()

    return HealthResponse(
        status="healthy",
        model_loaded=model_info.is_loaded,
        gpu_available=torch.cuda.is_available(),
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@router.get("/models", response_model=ModelInfo)
async def get_model_info():
    """
    Get information about the loaded model.
    """
    model_manager = get_model_manager()
    info = model_manager.get_model_info()

    return ModelInfo(
        name=info.name,
        device=info.device,
        quantization=info.quantization,
        memory_used_gb=info.memory_used_gb,
        is_loaded=info.is_loaded
    )

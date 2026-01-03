"""
FastAPI application server with API versioning.
"""
# Suppress known compatibility warnings
import warnings
warnings.filterwarnings("ignore", message=".*MessageFactory.*")
warnings.filterwarnings("ignore", message=".*bcrypt.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime


from config import settings
from api.routes import health, ocr, webhook, auth
from api.middleware.auth import verify_api_key
from api.middleware.rate_limit import rate_limit_middleware
from utils.logger import api_logger, generate_request_id, set_request_context, clear_request_context

# Create FastAPI app
app = FastAPI(
    title="Nanonets VL OCR API",
    description="Enterprise-grade Vision-Language OCR API for document processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
if settings.api.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Add request context middleware for logging
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_context(request_id=request_id)

    api_logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown"
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    api_logger.info(
        "Request completed",
        status_code=response.status_code
    )

    clear_request_context()
    return response


# Add rate limiting middleware
@app.middleware("http")
async def add_rate_limiting(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# Include routers
app.include_router(health.router, prefix=settings.api.api_prefix, tags=["Health"])
app.include_router(auth.router, prefix=settings.api.api_prefix, tags=["Authentication"])
app.include_router(ocr.router, prefix=settings.api.api_prefix, tags=["OCR"])
app.include_router(webhook.router, prefix=settings.api.api_prefix, tags=["Webhooks"])


# Startup event to pre-load models
@app.on_event("startup")
async def startup_event():
    """Initialize OCR engine and pre-load model on startup."""
    print("=" * 60)
    print("INITIALIZING OCR ENGINE")
    print("=" * 60)
    
    try:
        from core.ocr_engine import get_ocr_engine
        engine = get_ocr_engine()
        engine.initialize()
        
        model_info = engine.get_model_info()
        print(f"  ✓ Model loaded: {model_info['name']}")
        print(f"  ✓ Device: {model_info['device']}")
        print(f"  ✓ Quantization: {model_info['quantization']}")
        print(f"  ✓ Memory used: {model_info['memory_used_gb']:.2f} GB")
        print("=" * 60)
        print("OCR ENGINE READY")
        print("=" * 60)
    except Exception as e:
        print(f"  ✗ Failed to initialize OCR engine: {e}")
        print("  OCR will initialize on first request (cold start)")
        print("=" * 60)


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Nanonets VL OCR API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.api.api_prefix}/health"
    }


@app.get("/status")
async def status():
    """Get detailed server status including model loading state."""
    try:
        from core.ocr_engine import get_ocr_engine
        engine = get_ocr_engine()
        model_info = engine.get_model_info()
        
        return {
            "status": "ready" if model_info["is_loaded"] else "initializing",
            "model": {
                "name": model_info["name"],
                "loaded": model_info["is_loaded"],
                "device": model_info["device"],
                "quantization": model_info["quantization"],
                "memory_used_gb": model_info["memory_used_gb"]
            },
            "api_version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "api_version": "1.0.0"
        }



def run_server():
    """Run the API server."""
    import uvicorn
    uvicorn.run(
        "api.server:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=False
    )


if __name__ == "__main__":
    print("=" * 60)
    print("API SERVER")
    print("=" * 60)
    print(f"  Starting server on {settings.api.host}:{settings.api.port}")
    print(f"  API prefix: {settings.api.api_prefix}")
    print(f"  Docs: http://{settings.api.host}:{settings.api.port}/docs")
    print("=" * 60)

    run_server()

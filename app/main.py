"""Main FastAPI application for the Language Translator API."""

import time
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.models import (
    TranslateRequest,
    TranslateResponse,
    LanguagesResponse,
    LanguageInfo,
    ErrorResponse
)
from app.translator import translator_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print(f"🚀 Starting {settings.API_TITLE} v{settings.API_VERSION}")
    print(f"📝 Supported languages: {len(translator_service.get_supported_languages())}")
    print(f"⚡ Rate limit: {settings.RATE_LIMIT} requests/minute")
    print(f"🌐 Server will run on http://{settings.HOST}:{settings.PORT}")
    yield
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": errors,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": None,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": None,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        )


# Rate limiting middleware (simple implementation)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting middleware."""
    # Skip rate limiting for docs and static files
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Simple rate limiting using time-based window
    # In production, use Redis or a proper rate limiter
    from collections import defaultdict
    from datetime import datetime, timedelta
    
    # Store request counts (in memory - for demo only)
    if not hasattr(app.state, "rate_limit_data"):
        app.state.rate_limit_data = defaultdict(list)
    
    now = datetime.now()
    window_start = now - timedelta(minutes=1)
    
    # Clean old requests
    app.state.rate_limit_data[client_ip] = [
        t for t in app.state.rate_limit_data[client_ip] 
        if t > window_start
    ]
    
    # Check rate limit
    if len(app.state.rate_limit_data[client_ip]) >= settings.RATE_LIMIT:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Maximum {settings.RATE_LIMIT} requests per minute",
                "status_code": status.HTTP_429_TOO_MANY_REQUESTS
            }
        )
    
    # Add current request
    app.state.rate_limit_data[client_ip].append(now)
    
    return await call_next(request)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "languages": len(translator_service.get_supported_languages())
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.API_TITLE}",
        "version": settings.API_VERSION,
        "documentation": "/docs",
        "endpoints": {
            "translate": "/translate",
            "languages": "/languages",
            "detect": "/detect",
            "health": "/health"
        }
    }


# Translation endpoint
@app.post(
    "/translate",
    response_model=TranslateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Translation"]
)
async def translate(request: TranslateRequest) -> Dict[str, Any]:
    """
    Translate text from one language to another.
    
    - **text**: The text to translate (max 5000 characters)
    - **target_lang**: Target language code (e.g., 'es' for Spanish)
    - **source_lang**: Source language code (auto-detect if not provided)
    
    Returns translated text with language detection info.
    """
    try:
        result = translator_service.translate(
            text=request.text,
            target_lang=request.target_lang,
            source_lang=request.source_lang
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


# Languages endpoint
@app.get(
    "/languages",
    response_model=LanguagesResponse,
    status_code=status.HTTP_200_OK,
    tags=["Languages"]
)
async def get_languages() -> Dict[str, Any]:
    """
    Get all supported languages.
    
    Returns a list of language codes and their names.
    """
    languages = translator_service.get_supported_languages()
    language_list = [
        LanguageInfo(code=code, name=name)
        for code, name in languages.items()
    ]
    return {
        "languages": language_list,
        "total": len(language_list)
    }


# Language detection endpoint
@app.post(
    "/detect",
    status_code=status.HTTP_200_OK,
    tags=["Languages"]
)
async def detect_language(request: Dict[str, str]) -> Dict[str, Any]:
    """
    Detect the language of a given text.
    
    - **text**: The text to detect language for
    
    Returns detected language code, name, and confidence.
    """
    text = request.get("text")
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text is required for language detection"
        )
    
    try:
        result = translator_service.detect_language(text)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language detection failed: {str(e)}"
        )


# Run the application (if executed directly)
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

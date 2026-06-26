"""Pydantic models for request and response validation."""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class TranslateRequest(BaseModel):
    """Request model for translation endpoint."""
    
    text: str = Field(..., description="Text to translate", min_length=1, max_length=5000)
    target_lang: str = Field(..., description="Target language code (ISO 639-1)", min_length=2, max_length=5)
    source_lang: Optional[str] = Field(None, description="Source language code (auto-detect if not provided)", min_length=2, max_length=5)
    
    @validator('text')
    def validate_text(cls, v):
        """Validate that text is not empty."""
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()
    
    @validator('target_lang')
    def validate_target_lang(cls, v):
        """Validate target language code format."""
        v = v.lower().strip()
        if len(v) < 2 or len(v) > 5:
            raise ValueError('Language code must be 2-5 characters')
        return v


class TranslateResponse(BaseModel):
    """Response model for translation endpoint."""
    
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: Optional[float] = None


class LanguageInfo(BaseModel):
    """Model for language information."""
    
    code: str
    name: str


class LanguagesResponse(BaseModel):
    """Response model for languages endpoint."""
    
    languages: List[LanguageInfo]
    total: int


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    error: str
    detail: Optional[str] = None
    status_code: int

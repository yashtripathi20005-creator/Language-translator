"""Configuration management for the translator API."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API settings
    API_TITLE: str = "Language Translator API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Free language translation API using Google Translate"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Rate limiting
    RATE_LIMIT: int = 30  # requests per minute
    
    # Supported languages (ISO 639-1 codes)
    SUPPORTED_LANGUAGES: dict = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh-cn": "Chinese (Simplified)",
        "zh-tw": "Chinese (Traditional)",
        "ar": "Arabic",
        "hi": "Hindi",
        "bn": "Bengali",
        "ur": "Urdu",
        "te": "Telugu",
        "ta": "Tamil",
        "mr": "Marathi",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "or": "Odia",
        "pa": "Punjabi",
        "as": "Assamese",
        "mai": "Maithili",
        "sat": "Santali",
        "ne": "Nepali",
        "si": "Sinhala",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "ms": "Malay",
        "fil": "Filipino",
        "nl": "Dutch",
        "sv": "Swedish",
        "no": "Norwegian",
        "da": "Danish",
        "fi": "Finnish",
        "pl": "Polish",
        "tr": "Turkish",
        "el": "Greek",
        "cs": "Czech",
        "hu": "Hungarian",
        "ro": "Romanian",
        "uk": "Ukrainian",
        "bg": "Bulgarian",
        "sr": "Serbian",
        "hr": "Croatian",
        "sk": "Slovak",
        "sl": "Slovenian",
        "et": "Estonian",
        "lv": "Latvian",
        "lt": "Lithuanian",
        "is": "Icelandic",
        "he": "Hebrew",
        "fa": "Persian",
        "am": "Amharic",
        "my": "Burmese",
        "km": "Khmer",
        "lo": "Lao",
        "mn": "Mongolian",
        "az": "Azerbaijani",
        "ka": "Georgian",
        "hy": "Armenian",
        "af": "Afrikaans",
        "sw": "Swahili",
        "ha": "Hausa",
        "ig": "Igbo",
        "yo": "Yoruba",
        "zu": "Zulu"
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

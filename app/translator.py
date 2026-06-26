"""Translation service using Google Translate API."""

import logging
from typing import Dict, Any, Optional
from googletrans import Translator, LANGUAGES

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslationService:
    """Service class for handling translation operations."""
    
    def __init__(self):
        """Initialize the translator service."""
        self.translator = Translator()
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        logger.info("Translation service initialized with %d languages", len(self.supported_languages))
    
    def translate(self, text: str, target_lang: str, source_lang: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code (auto-detect if None)
            
        Returns:
            Dictionary with translation results
            
        Raises:
            ValueError: If language is not supported or translation fails
        """
        try:
            # Validate target language
            if target_lang not in self.supported_languages:
                raise ValueError(f"Target language '{target_lang}' is not supported")
            
            # Validate source language if provided
            if source_lang and source_lang not in self.supported_languages:
                raise ValueError(f"Source language '{source_lang}' is not supported")
            
            # Perform translation
            logger.info(f"Translating from {source_lang or 'auto'} to {target_lang}")
            
            result = self.translator.translate(
                text=text,
                dest=target_lang,
                src=source_lang or 'auto'
            )
            
            # Build response
            response = {
                'original_text': text,
                'translated_text': result.text,
                'source_lang': result.src,
                'target_lang': target_lang,
                'confidence': getattr(result, 'confidence', None)
            }
            
            logger.info(f"Translation successful: {len(text)} chars -> {len(result.text)} chars")
            return response
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise ValueError(f"Translation failed: {str(e)}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get all supported languages.
        
        Returns:
            Dictionary of language codes and names
        """
        return self.supported_languages
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to detect language for
            
        Returns:
            Dictionary with detected language info
            
        Raises:
            ValueError: If language detection fails
        """
        try:
            detection = self.translator.detect(text)
            return {
                'language_code': detection.lang,
                'language_name': LANGUAGES.get(detection.lang, 'Unknown'),
                'confidence': detection.confidence
            }
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            raise ValueError(f"Language detection failed: {str(e)}")


# Singleton instance
translator_service = TranslationService()

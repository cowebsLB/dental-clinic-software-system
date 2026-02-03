"""Internationalization (i18n) support for the application."""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import pytz
from config.settings import settings


class Translator:
    """Translation manager for multi-language support."""
    
    def __init__(self, language: Optional[str] = None):
        self.language = language or settings.default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.translations_dir = Path(__file__).parent.parent / "translations"
        self.translations_dir.mkdir(exist_ok=True)
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files."""
        translation_file = self.translations_dir / f"{self.language}.json"
        
        if translation_file.exists():
            try:
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations[self.language] = json.load(f)
            except Exception as e:
                print(f"Error loading translations: {e}")
                self.translations[self.language] = {}
        else:
            # Load English as fallback
            en_file = self.translations_dir / "en.json"
            if en_file.exists():
                try:
                    with open(en_file, 'r', encoding='utf-8') as f:
                        self.translations[self.language] = json.load(f)
                except Exception:
                    self.translations[self.language] = {}
            else:
                self.translations[self.language] = {}
    
    def translate(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """Translate a key to the current language.
        
        Supports nested keys with dot notation, e.g., "auth.login" -> translations["auth"]["login"]
        """
        translations_dict = self.translations.get(self.language, {})
        
        # Handle nested keys with dot notation
        if '.' in key:
            keys = key.split('.')
            translation = translations_dict
            try:
                for k in keys:
                    translation = translation[k]
            except (KeyError, TypeError):
                translation = default or key
        else:
            # Simple key lookup
            translation = translations_dict.get(key, default or key)
        
        # Ensure translation is a string
        if not isinstance(translation, str):
            translation = default or key
        
        # Replace placeholders if kwargs provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return translation
    
    def set_language(self, language: str):
        """Change the current language."""
        self.language = language
        self._load_translations()
    
    def format_date(self, date: datetime, format_type: str = "short") -> str:
        """Format a date according to locale."""
        # Default formats
        formats = {
            "short": "%m/%d/%Y",
            "medium": "%B %d, %Y",
            "long": "%A, %B %d, %Y",
            "time": "%I:%M %p",
            "datetime": "%m/%d/%Y %I:%M %p"
        }
        
        format_str = formats.get(format_type, formats["short"])
        return date.strftime(format_str)
    
    def format_currency(self, amount: float, currency: str = "USD") -> str:
        """Format currency according to locale."""
        # Simple currency formatting
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"


# Global translator instance
translator = Translator()


def tr(key: str, default: Optional[str] = None, **kwargs) -> str:
    """Convenience function for translation."""
    return translator.translate(key, default, **kwargs)


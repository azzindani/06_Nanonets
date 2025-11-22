"""
Multi-language support for OCR processing.
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    THAI = "th"
    VIETNAMESE = "vi"
    INDONESIAN = "id"
    MALAY = "ms"
    TURKISH = "tr"
    POLISH = "pl"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"
    GREEK = "el"
    HEBREW = "he"
    CZECH = "cs"
    ROMANIAN = "ro"
    HUNGARIAN = "hu"
    UKRAINIAN = "uk"
    UNKNOWN = "unknown"


@dataclass
class LanguageDetectionResult:
    """Result of language detection."""
    primary_language: Language
    confidence: float
    all_scores: Dict[str, float]
    script_detected: str
    is_multilingual: bool
    secondary_languages: List[Language]


class LanguageDetector:
    """Detect language of text content."""

    def __init__(self):
        """Initialize language detector with patterns."""
        self._patterns = self._build_language_patterns()
        self._script_ranges = self._build_script_ranges()

    def _build_language_patterns(self) -> Dict[Language, Dict]:
        """Build characteristic patterns for each language."""
        return {
            Language.ENGLISH: {
                "common_words": ["the", "and", "is", "in", "to", "of", "a", "for", "that", "with"],
                "patterns": [r"\bthe\b", r"\band\b", r"\bis\b"],
                "script": "latin"
            },
            Language.SPANISH: {
                "common_words": ["de", "la", "que", "el", "en", "y", "los", "se", "del", "las"],
                "patterns": [r"\bque\b", r"\bdel\b", r"ñ", r"¿", r"¡"],
                "script": "latin"
            },
            Language.FRENCH: {
                "common_words": ["de", "la", "le", "et", "les", "des", "en", "un", "du", "une"],
                "patterns": [r"\bqu['e]", r"\bc'est\b", r"œ", r"ç"],
                "script": "latin"
            },
            Language.GERMAN: {
                "common_words": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"],
                "patterns": [r"\bder\b", r"\bdie\b", r"\bund\b", r"ß", r"ü", r"ö", r"ä"],
                "script": "latin"
            },
            Language.ITALIAN: {
                "common_words": ["di", "che", "la", "il", "un", "per", "con", "non", "una", "sono"],
                "patterns": [r"\bche\b", r"\bnon\b", r"\bper\b"],
                "script": "latin"
            },
            Language.PORTUGUESE: {
                "common_words": ["de", "que", "e", "do", "da", "em", "um", "para", "com", "não"],
                "patterns": [r"\bnão\b", r"\bpara\b", r"ã", r"õ"],
                "script": "latin"
            },
            Language.DUTCH: {
                "common_words": ["de", "het", "een", "van", "en", "in", "is", "dat", "op", "te"],
                "patterns": [r"\bhet\b", r"\been\b", r"\bvan\b", r"ij"],
                "script": "latin"
            },
            Language.RUSSIAN: {
                "common_words": ["и", "в", "не", "на", "я", "что", "он", "с", "это", "как"],
                "patterns": [r"[а-яА-Я]"],
                "script": "cyrillic"
            },
            Language.CHINESE: {
                "common_words": ["的", "一", "是", "不", "了", "在", "人", "有", "我", "他"],
                "patterns": [r"[\u4e00-\u9fff]"],
                "script": "cjk"
            },
            Language.JAPANESE: {
                "common_words": ["の", "に", "は", "を", "た", "が", "で", "て", "と", "し"],
                "patterns": [r"[\u3040-\u309f]", r"[\u30a0-\u30ff]"],
                "script": "japanese"
            },
            Language.KOREAN: {
                "common_words": ["이", "그", "저", "것", "수", "하다", "있다", "되다", "없다"],
                "patterns": [r"[\uac00-\ud7af]"],
                "script": "hangul"
            },
            Language.ARABIC: {
                "common_words": ["من", "في", "على", "إلى", "عن", "مع", "هذا", "أن", "كان", "لا"],
                "patterns": [r"[\u0600-\u06ff]"],
                "script": "arabic"
            },
            Language.HINDI: {
                "common_words": ["का", "की", "को", "में", "है", "और", "से", "के", "एक", "यह"],
                "patterns": [r"[\u0900-\u097f]"],
                "script": "devanagari"
            },
            Language.THAI: {
                "common_words": ["ที่", "และ", "ใน", "ของ", "มี", "เป็น", "ได้", "จะ", "นี้", "ไม่"],
                "patterns": [r"[\u0e00-\u0e7f]"],
                "script": "thai"
            },
        }

    def _build_script_ranges(self) -> Dict[str, Tuple[int, int]]:
        """Build Unicode ranges for different scripts."""
        return {
            "latin": (0x0000, 0x024F),
            "cyrillic": (0x0400, 0x04FF),
            "arabic": (0x0600, 0x06FF),
            "devanagari": (0x0900, 0x097F),
            "thai": (0x0E00, 0x0E7F),
            "cjk": (0x4E00, 0x9FFF),
            "hangul": (0xAC00, 0xD7AF),
            "japanese_hiragana": (0x3040, 0x309F),
            "japanese_katakana": (0x30A0, 0x30FF),
            "hebrew": (0x0590, 0x05FF),
            "greek": (0x0370, 0x03FF),
        }

    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Detect the language of the given text.

        Args:
            text: The text to analyze.

        Returns:
            LanguageDetectionResult with detected language and confidence.
        """
        if not text or len(text.strip()) == 0:
            return LanguageDetectionResult(
                primary_language=Language.UNKNOWN,
                confidence=0.0,
                all_scores={},
                script_detected="unknown",
                is_multilingual=False,
                secondary_languages=[]
            )

        text_lower = text.lower()
        scores: Dict[str, float] = {}

        # Detect script first
        script = self._detect_script(text)

        # Score each language
        for lang, config in self._patterns.items():
            score = 0.0

            # Check common words
            for word in config["common_words"]:
                if re.search(rf"\b{re.escape(word)}\b", text_lower):
                    score += 1.0

            # Check patterns
            for pattern in config["patterns"]:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches) * 0.5

            # Boost if script matches
            if config["script"] == script:
                score *= 1.5

            # Normalize
            max_possible = len(config["common_words"]) + len(config["patterns"]) * 5
            scores[lang.value] = score / max_possible if max_possible > 0 else 0

        # Find best matches
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if sorted_scores and sorted_scores[0][1] > 0:
            primary = Language(sorted_scores[0][0])
            confidence = min(sorted_scores[0][1] * 2, 1.0)

            # Check for multilingual content
            secondary = []
            for lang_code, score in sorted_scores[1:4]:
                if score > 0.1:
                    secondary.append(Language(lang_code))

            return LanguageDetectionResult(
                primary_language=primary,
                confidence=confidence,
                all_scores=scores,
                script_detected=script,
                is_multilingual=len(secondary) > 0,
                secondary_languages=secondary
            )

        return LanguageDetectionResult(
            primary_language=Language.UNKNOWN,
            confidence=0.0,
            all_scores=scores,
            script_detected=script,
            is_multilingual=False,
            secondary_languages=[]
        )

    def _detect_script(self, text: str) -> str:
        """Detect the primary script used in text."""
        script_counts = {
            "latin": 0,
            "cyrillic": 0,
            "arabic": 0,
            "cjk": 0,
            "hangul": 0,
            "devanagari": 0,
            "thai": 0,
            "japanese": 0,
            "hebrew": 0,
            "greek": 0,
        }

        for char in text:
            code = ord(char)

            if 0x0000 <= code <= 0x024F:
                script_counts["latin"] += 1
            elif 0x0400 <= code <= 0x04FF:
                script_counts["cyrillic"] += 1
            elif 0x0600 <= code <= 0x06FF:
                script_counts["arabic"] += 1
            elif 0x4E00 <= code <= 0x9FFF:
                script_counts["cjk"] += 1
            elif 0xAC00 <= code <= 0xD7AF:
                script_counts["hangul"] += 1
            elif 0x0900 <= code <= 0x097F:
                script_counts["devanagari"] += 1
            elif 0x0E00 <= code <= 0x0E7F:
                script_counts["thai"] += 1
            elif 0x3040 <= code <= 0x30FF:
                script_counts["japanese"] += 1
            elif 0x0590 <= code <= 0x05FF:
                script_counts["hebrew"] += 1
            elif 0x0370 <= code <= 0x03FF:
                script_counts["greek"] += 1

        if script_counts:
            return max(script_counts, key=script_counts.get)
        return "unknown"

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return [lang.value for lang in Language if lang != Language.UNKNOWN]


class MultiLanguageProcessor:
    """Process documents in multiple languages."""

    def __init__(self):
        """Initialize the multi-language processor."""
        self.detector = LanguageDetector()
        self._field_translations = self._load_field_translations()

    def _load_field_translations(self) -> Dict[str, Dict[str, str]]:
        """Load field name translations for different languages."""
        return {
            "invoice_number": {
                "en": "invoice number",
                "es": "número de factura",
                "fr": "numéro de facture",
                "de": "rechnungsnummer",
                "it": "numero fattura",
                "pt": "número da fatura",
            },
            "date": {
                "en": "date",
                "es": "fecha",
                "fr": "date",
                "de": "datum",
                "it": "data",
                "pt": "data",
            },
            "total": {
                "en": "total",
                "es": "total",
                "fr": "total",
                "de": "gesamt",
                "it": "totale",
                "pt": "total",
            },
            "tax": {
                "en": "tax",
                "es": "impuesto",
                "fr": "taxe",
                "de": "steuer",
                "it": "tassa",
                "pt": "imposto",
            },
        }

    def get_field_pattern(self, field_name: str, language: Language) -> Optional[str]:
        """
        Get the localized pattern for a field.

        Args:
            field_name: The field to get pattern for.
            language: The target language.

        Returns:
            Localized field label or None.
        """
        if field_name in self._field_translations:
            return self._field_translations[field_name].get(language.value)
        return None

    def process_multilingual(
        self,
        text: str,
        fields: List[str]
    ) -> Dict[str, Dict]:
        """
        Process document extracting fields in detected language.

        Args:
            text: The document text.
            fields: List of field names to extract.

        Returns:
            Dictionary with extracted values and language info.
        """
        # Detect language
        detection = self.detector.detect(text)

        results = {
            "language": detection.primary_language.value,
            "confidence": detection.confidence,
            "fields": {}
        }

        # Extract fields using localized patterns
        for field in fields:
            pattern = self.get_field_pattern(field, detection.primary_language)
            if pattern:
                regex = rf"{pattern}\s*:?\s*(.+?)(?:\n|$)"
                match = re.search(regex, text, re.IGNORECASE)
                if match:
                    results["fields"][field] = match.group(1).strip()

        return results


# Singleton instances
_language_detector = None
_multi_language_processor = None


def get_language_detector() -> LanguageDetector:
    """Get the language detector singleton."""
    global _language_detector
    if _language_detector is None:
        _language_detector = LanguageDetector()
    return _language_detector


def get_multi_language_processor() -> MultiLanguageProcessor:
    """Get the multi-language processor singleton."""
    global _multi_language_processor
    if _multi_language_processor is None:
        _multi_language_processor = MultiLanguageProcessor()
    return _multi_language_processor

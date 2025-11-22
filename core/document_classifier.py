"""
Document classification service for auto-detecting document types.
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DocumentType(Enum):
    """Supported document types."""
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    FORM = "form"
    LETTER = "letter"
    REPORT = "report"
    ID_DOCUMENT = "id_document"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    MEDICAL = "medical"
    UNKNOWN = "unknown"


@dataclass
class ClassificationResult:
    """Result of document classification."""
    document_type: DocumentType
    confidence: float
    all_scores: Dict[str, float]
    keywords_found: List[str]


class DocumentClassifier:
    """Classify documents into predefined categories."""

    def __init__(self):
        """Initialize the document classifier with keyword patterns."""
        self._patterns = self._build_patterns()

    def _build_patterns(self) -> Dict[DocumentType, Dict]:
        """Build keyword patterns for each document type."""
        return {
            DocumentType.INVOICE: {
                "keywords": [
                    "invoice", "bill to", "ship to", "invoice number", "invoice date",
                    "due date", "payment terms", "subtotal", "tax", "total due",
                    "remit to", "purchase order", "qty", "unit price", "amount due"
                ],
                "patterns": [
                    r"invoice\s*#?\s*:?\s*\w+",
                    r"inv\s*-?\s*\d+",
                    r"bill\s+to\s*:",
                    r"payment\s+due",
                    r"total\s+amount\s*:?\s*\$?"
                ],
                "weight": 1.0
            },
            DocumentType.RECEIPT: {
                "keywords": [
                    "receipt", "transaction", "paid", "cash", "credit card",
                    "change", "subtotal", "tax", "total", "thank you",
                    "store", "cashier", "items"
                ],
                "patterns": [
                    r"receipt\s*#?\s*:?\s*\w+",
                    r"transaction\s*id",
                    r"paid\s+by",
                    r"change\s*:?\s*\$?\d+"
                ],
                "weight": 1.0
            },
            DocumentType.CONTRACT: {
                "keywords": [
                    "agreement", "contract", "terms and conditions", "party",
                    "whereas", "hereby", "witnesseth", "covenant", "binding",
                    "executed", "signature", "effective date", "termination"
                ],
                "patterns": [
                    r"this\s+agreement",
                    r"parties\s+agree",
                    r"terms\s+and\s+conditions",
                    r"binding\s+agreement"
                ],
                "weight": 1.0
            },
            DocumentType.FORM: {
                "keywords": [
                    "form", "application", "please fill", "required fields",
                    "checkbox", "select", "signature required", "date of birth",
                    "applicant", "submit"
                ],
                "patterns": [
                    r"form\s*#?\s*:?\s*\w+",
                    r"please\s+(fill|complete)",
                    r"\[\s*\]",  # Empty checkboxes
                    r"_+\s*\(.*?\)"  # Blank lines with labels
                ],
                "weight": 1.0
            },
            DocumentType.LETTER: {
                "keywords": [
                    "dear", "sincerely", "regards", "yours truly", "to whom",
                    "attention", "re:", "subject:", "enclosed"
                ],
                "patterns": [
                    r"dear\s+\w+",
                    r"sincerely\s*,",
                    r"regards\s*,",
                    r"to\s+whom\s+it\s+may\s+concern"
                ],
                "weight": 0.9
            },
            DocumentType.REPORT: {
                "keywords": [
                    "report", "summary", "analysis", "findings", "conclusion",
                    "executive summary", "methodology", "results", "recommendations"
                ],
                "patterns": [
                    r"executive\s+summary",
                    r"table\s+of\s+contents",
                    r"section\s+\d+",
                    r"figure\s+\d+"
                ],
                "weight": 0.9
            },
            DocumentType.ID_DOCUMENT: {
                "keywords": [
                    "passport", "driver license", "identification", "id card",
                    "date of birth", "expiry", "nationality", "sex", "height"
                ],
                "patterns": [
                    r"passport\s*no",
                    r"license\s*#",
                    r"date\s+of\s+birth",
                    r"expir(y|ation)\s+date"
                ],
                "weight": 1.0
            },
            DocumentType.BANK_STATEMENT: {
                "keywords": [
                    "statement", "account", "balance", "deposit", "withdrawal",
                    "transaction", "opening balance", "closing balance", "interest"
                ],
                "patterns": [
                    r"account\s*(number|#)",
                    r"statement\s+period",
                    r"opening\s+balance",
                    r"closing\s+balance"
                ],
                "weight": 1.0
            },
            DocumentType.TAX_DOCUMENT: {
                "keywords": [
                    "tax", "w-2", "1099", "irs", "income", "deduction",
                    "federal", "state", "employer", "wages", "withholding"
                ],
                "patterns": [
                    r"form\s+w-?2",
                    r"form\s+1099",
                    r"tax\s+year",
                    r"taxable\s+income"
                ],
                "weight": 1.0
            },
            DocumentType.MEDICAL: {
                "keywords": [
                    "patient", "diagnosis", "prescription", "medication",
                    "doctor", "physician", "hospital", "clinic", "medical",
                    "treatment", "dosage", "symptoms"
                ],
                "patterns": [
                    r"patient\s+(name|id)",
                    r"date\s+of\s+service",
                    r"diagnosis\s*:",
                    r"rx\s*:"
                ],
                "weight": 1.0
            }
        }

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify a document based on its text content.

        Args:
            text: The extracted text from the document.

        Returns:
            ClassificationResult with document type and confidence.
        """
        text_lower = text.lower()
        scores: Dict[str, float] = {}
        keywords_found: Dict[str, List[str]] = {}

        for doc_type, config in self._patterns.items():
            score = 0.0
            found_keywords = []

            # Score keywords
            for keyword in config["keywords"]:
                if keyword.lower() in text_lower:
                    score += 1.0
                    found_keywords.append(keyword)

            # Score regex patterns
            for pattern in config["patterns"]:
                if re.search(pattern, text_lower):
                    score += 2.0  # Patterns are more specific

            # Apply weight
            score *= config["weight"]

            # Normalize by number of patterns
            max_score = len(config["keywords"]) + len(config["patterns"]) * 2
            normalized_score = score / max_score if max_score > 0 else 0

            scores[doc_type.value] = normalized_score
            keywords_found[doc_type.value] = found_keywords

        # Find best match
        if scores:
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]

            # Require minimum confidence
            if best_score < 0.1:
                return ClassificationResult(
                    document_type=DocumentType.UNKNOWN,
                    confidence=0.0,
                    all_scores=scores,
                    keywords_found=[]
                )

            return ClassificationResult(
                document_type=DocumentType(best_type),
                confidence=min(best_score * 2, 1.0),  # Scale up but cap at 1.0
                all_scores=scores,
                keywords_found=keywords_found.get(best_type, [])
            )

        return ClassificationResult(
            document_type=DocumentType.UNKNOWN,
            confidence=0.0,
            all_scores={},
            keywords_found=[]
        )

    def classify_with_routing(self, text: str) -> Tuple[ClassificationResult, str]:
        """
        Classify document and suggest processing route.

        Args:
            text: The extracted text from the document.

        Returns:
            Tuple of (ClassificationResult, suggested_schema)
        """
        result = self.classify(text)

        # Map document types to schemas
        schema_mapping = {
            DocumentType.INVOICE: "invoice",
            DocumentType.RECEIPT: "receipt",
            DocumentType.CONTRACT: "contract",
            DocumentType.BANK_STATEMENT: "bank_statement",
            DocumentType.TAX_DOCUMENT: "tax_document",
            DocumentType.MEDICAL: "medical",
        }

        suggested_schema = schema_mapping.get(result.document_type, "general")

        return result, suggested_schema

    def get_supported_types(self) -> List[str]:
        """Get list of supported document types."""
        return [dt.value for dt in DocumentType if dt != DocumentType.UNKNOWN]


# Singleton instance
_classifier = None


def get_document_classifier() -> DocumentClassifier:
    """Get the document classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = DocumentClassifier()
    return _classifier

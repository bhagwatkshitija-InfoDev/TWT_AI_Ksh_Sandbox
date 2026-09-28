"""Custom exceptions for the Document QA Agent."""


class DocumentQAException(Exception):
    """Base exception for all Document QA Agent errors."""

    pass


class DocumentProcessingError(DocumentQAException):
    """Raised when document processing fails."""

    pass


class PDFExtractionError(DocumentProcessingError):
    """Raised when PDF extraction fails."""

    pass


class DOCXParsingError(DocumentProcessingError):
    """Raised when DOCX parsing fails."""

    pass


class LanguageDetectionError(DocumentQAException):
    """Raised when language detection fails."""

    pass


class FormattingAnalysisError(DocumentQAException):
    """Raised when formatting analysis fails."""

    pass


class InvalidDocumentError(DocumentQAException):
    """Raised when document format is invalid."""

    pass


class DatabaseError(DocumentQAException):
    """Raised when database operation fails."""

    pass


class ConfigurationError(DocumentQAException):
    """Raised when configuration is invalid."""

    pass


class ReportGenerationError(DocumentQAException):
    """Raised when report generation fails."""

    pass

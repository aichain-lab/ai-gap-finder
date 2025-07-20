"""Custom exceptions for AI Gap Finder"""


class GapFinderException(Exception):
    """Base exception for Gap Finder errors"""
    pass


class LLMServiceException(GapFinderException):
    """Exception for LLM service errors"""
    pass


class PDFExtractionException(GapFinderException):
    """Exception for PDF extraction errors"""
    pass


class ArXivServiceException(GapFinderException):
    """Exception for arXiv service errors"""
    pass


class ConfigurationException(GapFinderException):
    """Exception for configuration errors"""
    pass


class ValidationException(GapFinderException):
    """Exception for validation errors"""
    pass

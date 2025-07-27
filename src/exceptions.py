"""
Custom exceptions for the Salesforce AI Bridge application.
Provides specific error types with appropriate HTTP status codes.
"""

class SalesforceAIBridgeException(Exception):
    """Base exception for all Salesforce AI Bridge errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationError(SalesforceAIBridgeException):
    """Raised when input validation fails."""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, status_code=400)


class ProcessingError(SalesforceAIBridgeException):
    """Raised when asset processing fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class SalesforceConnectionError(SalesforceAIBridgeException):
    """Raised when Salesforce connection fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class AIServiceError(SalesforceAIBridgeException):
    """Raised when AI service processing fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=502)


class CacheError(SalesforceAIBridgeException):
    """Raised when cache operations fail."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class RateLimitError(SalesforceAIBridgeException):
    """Raised when rate limits are exceeded."""
    def __init__(self, message: str):
        super().__init__(message, status_code=429)
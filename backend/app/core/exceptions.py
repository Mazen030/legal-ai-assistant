class LegalAIException(Exception):
    """Base exception for Legal AI Assistant."""
    pass


class DocumentProcessingError(LegalAIException):
    """Raised when document parsing or processing fails."""
    pass


class UnsupportedFileTypeError(LegalAIException):
    """Raised when the uploaded file type is not supported."""
    pass


class FileTooLargeError(LegalAIException):
    """Raised when the uploaded file exceeds the size limit."""
    pass


class SessionNotFoundError(LegalAIException):
    """Raised when a requested session ID does not exist."""
    pass


class VectorStoreError(LegalAIException):
    """Raised when vector store operations fail."""
    pass

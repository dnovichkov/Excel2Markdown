"""Custom exceptions for Excel2Markdown service."""


class Excel2MarkdownError(Exception):
    """Base exception for all Excel2Markdown errors."""

    pass


class InvalidFileFormatError(Excel2MarkdownError):
    """Raised when the uploaded file is not a valid Excel format."""

    pass


class FileTooLargeError(Excel2MarkdownError):
    """Raised when the uploaded file exceeds the maximum allowed size."""

    pass


class EmptyFileError(Excel2MarkdownError):
    """Raised when the uploaded file contains no data."""

    pass


class EmptySheetError(Excel2MarkdownError):
    """Raised when a sheet contains no data."""

    pass


class ConversionError(Excel2MarkdownError):
    """Raised when conversion fails for any reason."""

    pass


class TaskNotFoundError(Excel2MarkdownError):
    """Raised when a requested task does not exist."""

    pass


class StorageError(Excel2MarkdownError):
    """Raised when file storage operations fail."""

    pass

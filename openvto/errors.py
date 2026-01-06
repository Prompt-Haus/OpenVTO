"""Custom exceptions for OpenVTO."""


class OpenVTOError(Exception):
    """Base exception for all OpenVTO errors."""

    pass


class ValidationError(OpenVTOError):
    """Raised when input validation fails.

    Examples:
        - Invalid image format
        - Missing required parameters
        - Invalid aspect ratio
    """

    pass


class ProviderError(OpenVTOError):
    """Raised when a provider API call fails.

    Attributes:
        provider: Name of the provider that failed.
        status_code: HTTP status code if applicable.
        response: Raw response from the provider if available.
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        status_code: int | None = None,
        response: str | None = None,
    ):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.response = response


class ProviderAuthError(ProviderError):
    """Raised when provider authentication fails.

    Examples:
        - Invalid API key
        - Expired credentials
        - Missing authentication
    """

    pass


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""

    pass


class ProviderQuotaError(ProviderError):
    """Raised when provider quota is exhausted."""

    pass


class ModelNotFoundError(ProviderError):
    """Raised when the requested model is not available."""

    pass


class CacheError(OpenVTOError):
    """Raised when cache operations fail.

    Examples:
        - Cache read/write errors
        - Invalid cache key
        - Storage backend unavailable
    """

    pass


class ImageProcessingError(OpenVTOError):
    """Raised when image processing fails.

    Examples:
        - Invalid image format
        - Resize/crop failures
        - Encoding errors
    """

    pass


class PromptError(OpenVTOError):
    """Raised when prompt template rendering fails.

    Examples:
        - Missing template file
        - Invalid template syntax
        - Missing required variables
    """

    pass


class PipelineError(OpenVTOError):
    """Raised when a pipeline step fails.

    Attributes:
        step: Name of the pipeline step that failed.
        cause: The underlying exception if available.
    """

    def __init__(
        self,
        message: str,
        step: str | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.step = step
        self.cause = cause


class ConfigurationError(OpenVTOError):
    """Raised when client configuration is invalid.

    Examples:
        - Invalid provider name
        - Missing required configuration
        - Incompatible options
    """

    pass

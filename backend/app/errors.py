class ServiceError(Exception):
    """Base exception for backend service failures."""


class ResourceNotFound(ServiceError):
    """Requested resource does not exist."""


class ServiceUnavailable(ServiceError):
    """A dependent service is unavailable."""


class ValidationServiceError(ServiceError):
    """Service-level validation failure."""

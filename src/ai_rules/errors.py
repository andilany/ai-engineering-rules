class AirulesError(Exception):
    """Base class for expected user-facing airules errors."""


class ConfigurationError(AirulesError):
    """Raised when canonical/project configuration is invalid."""


class SafetyError(AirulesError):
    """Raised when a requested file operation is outside airules-owned paths."""

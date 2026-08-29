from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProviderState(str, Enum):
    NOT_CONFIGURED = "NOT_CONFIGURED"
    CONFIGURED = "CONFIGURED"
    DISABLED = "DISABLED"
    UNAVAILABLE = "UNAVAILABLE"


class ProviderError(Exception):
    def __init__(self, message, state=ProviderState.UNAVAILABLE):
        super().__init__(message)
        self.state = state


@dataclass
class ProviderResult:
    success: bool
    provider: str
    reference: str | None = None
    status: str | None = None
    data: dict[str, Any] | None = None
    error: str | None = None

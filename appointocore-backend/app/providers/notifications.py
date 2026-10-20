import logging
import secrets
from abc import ABC, abstractmethod

from flask import current_app

from .base import ProviderError, ProviderResult, ProviderState

logger = logging.getLogger(__name__)


class NotificationProvider(ABC):
    name = "notification"

    @property
    @abstractmethod
    def state(self):
        pass

    @abstractmethod
    def send(self, recipient, subject, body, html=None, template=None, data=None):
        pass


class MockNotificationProvider(NotificationProvider):
    def __init__(self, channel):
        self.name = f"mock_{channel}"

    @property
    def state(self):
        return ProviderState.CONFIGURED

    def send(self, recipient, subject, body, html=None, template=None, data=None):
        reference = f"mock_{secrets.token_hex(8)}"
        logger.info("Mock notification sent", extra={"provider": self.name, "reference": reference})
        return ProviderResult(True, self.name, reference, "sent", {"recipient": recipient})


class ConfiguredNotificationProvider(NotificationProvider):
    def __init__(self, channel):
        self.name = channel
        self.channel = channel

    @property
    def state(self):
        config = current_app.config
        enabled = config.get(f"{self.channel.upper()}_ENABLED", False)
        provider = config.get(f"{self.channel.upper()}_PROVIDER", "")
        if not enabled:
            return ProviderState.DISABLED
        if not provider or not config.get(f"{self.channel.upper()}_API_KEY"):
            return ProviderState.NOT_CONFIGURED
        return ProviderState.UNAVAILABLE

    def send(self, recipient, subject, body, html=None, template=None, data=None):
        raise ProviderError(f"{self.channel.title()} provider adapter is not available for the configured vendor.", self.state)


def get_notification_provider(channel):
    channel = channel.lower()
    config = current_app.config
    provider_name = config.get(f"{channel.upper()}_PROVIDER", "mock").lower()
    if provider_name == "mock" and config.get("APP_ENV") != "production":
        return MockNotificationProvider(channel)
    return ConfiguredNotificationProvider(channel)

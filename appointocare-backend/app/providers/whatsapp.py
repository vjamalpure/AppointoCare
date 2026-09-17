import hashlib
import hmac
import json
import logging
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

from flask import current_app

from .base import ProviderError, ProviderResult, ProviderState
from .notifications import MockNotificationProvider

logger = logging.getLogger(__name__)


class WhatsAppProvider(ABC):
    @property
    @abstractmethod
    def state(self):
        pass

    @abstractmethod
    def send_text(self, recipient, message):
        pass

    def verify_signature(self, raw_body, signature):
        return True


class MockWhatsAppProvider(MockNotificationProvider, WhatsAppProvider):
    def __init__(self):
        super().__init__("whatsapp")

    def send_text(self, recipient, message):
        return self.send(recipient, None, message)


class MetaWhatsAppProvider(WhatsAppProvider):
    @property
    def state(self):
        config = current_app.config
        if not config.get("WHATSAPP_ENABLED"):
            return ProviderState.DISABLED
        if not config.get("WHATSAPP_ACCESS_TOKEN") or not config.get("WHATSAPP_PHONE_NUMBER_ID"):
            return ProviderState.NOT_CONFIGURED
        return ProviderState.CONFIGURED

    def send_text(self, recipient, message):
        if self.state != ProviderState.CONFIGURED:
            raise ProviderError("WhatsApp provider is not configured.", self.state)
        payload = {"messaging_product": "whatsapp", "to": recipient, "type": "text", "text": {"body": message}}
        request = urllib.request.Request(
            f"https://graph.facebook.com/v20.0/{current_app.config['WHATSAPP_PHONE_NUMBER_ID']}/messages",
            data=json.dumps(payload).encode(), method="POST",
            headers={"Authorization": f"Bearer {current_app.config['WHATSAPP_ACCESS_TOKEN']}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            logger.warning("Meta WhatsApp request failed", extra={"error_type": type(exc).__name__})
            raise ProviderError("WhatsApp provider is temporarily unavailable.") from exc
        message_id = (data.get("messages") or [{}])[0].get("id")
        return ProviderResult(True, "meta_whatsapp", message_id, "sent", data)

    def verify_signature(self, raw_body, signature):
        secret = current_app.config.get("WHATSAPP_APP_SECRET", "")
        if not secret:
            return False
        expected = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature or "")


def get_whatsapp_provider():
    if current_app.config.get("WHATSAPP_PROVIDER", "mock").lower() == "meta":
        return MetaWhatsAppProvider()
    if current_app.config.get("WHATSAPP_PROVIDER", "mock").lower() == "mock" and current_app.config.get("APP_ENV") != "production":
        return MockWhatsAppProvider()
    return MetaWhatsAppProvider()

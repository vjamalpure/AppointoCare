import hashlib
import hmac
import json
import logging
import secrets
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

from flask import current_app

from .base import ProviderError, ProviderResult, ProviderState

logger = logging.getLogger(__name__)


class PaymentProvider(ABC):
    name = "payment"

    @property
    @abstractmethod
    def state(self):
        pass

    @abstractmethod
    def create_order(self, amount, currency, receipt, notes=None):
        pass

    @abstractmethod
    def fetch_order(self, provider_order_id):
        pass

    @abstractmethod
    def verify_payment(self, order_id, payment_id, signature):
        pass


class MockPaymentProvider(PaymentProvider):
    name = "mock"

    @property
    def state(self):
        return ProviderState.CONFIGURED

    def create_order(self, amount, currency, receipt, notes=None):
        order_id = f"mock_order_{secrets.token_hex(10)}"
        return ProviderResult(True, self.name, order_id, "created", {"amount": amount, "currency": currency, "receipt": receipt, "notes": notes or {}})

    def fetch_order(self, provider_order_id):
        return ProviderResult(True, self.name, provider_order_id, "created", {})

    def verify_payment(self, order_id, payment_id, signature):
        return ProviderResult(True, self.name, payment_id, "captured", {"order_id": order_id})


class UnconfiguredPaymentProvider(PaymentProvider):
    name = "none"

    @property
    def state(self):
        return ProviderState.NOT_CONFIGURED

    def _raise(self):
        raise ProviderError("Payment provider is not configured.", self.state)

    create_order = lambda self, *args, **kwargs: self._raise()
    fetch_order = lambda self, *args, **kwargs: self._raise()
    verify_payment = lambda self, *args, **kwargs: self._raise()


class RazorpayProvider(PaymentProvider):
    name = "razorpay"

    @property
    def state(self):
        if not current_app.config.get("RAZORPAY_ENABLED"):
            return ProviderState.DISABLED
        if not current_app.config.get("RAZORPAY_KEY_ID") or not current_app.config.get("RAZORPAY_KEY_SECRET"):
            return ProviderState.NOT_CONFIGURED
        return ProviderState.CONFIGURED

    def _request(self, method, path, body=None):
        if self.state != ProviderState.CONFIGURED:
            raise ProviderError("Payment provider is not configured.", self.state)
        credentials = f"{current_app.config['RAZORPAY_KEY_ID']}:{current_app.config['RAZORPAY_KEY_SECRET']}".encode()
        request = urllib.request.Request(
            f"https://api.razorpay.com/v1/{path}",
            data=json.dumps(body).encode() if body else None,
            method=method,
            headers={"Authorization": "Basic " + __import__('base64').b64encode(credentials).decode(), "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            logger.warning("Razorpay request failed", extra={"path": path, "error_type": type(exc).__name__})
            raise ProviderError("Payment provider is temporarily unavailable.") from exc

    def create_order(self, amount, currency, receipt, notes=None):
        data = self._request("POST", "orders", {"amount": int(round(amount * 100)), "currency": currency, "receipt": receipt, "notes": notes or {}})
        return ProviderResult(True, self.name, data.get("id"), data.get("status"), data)

    def fetch_order(self, provider_order_id):
        data = self._request("GET", f"orders/{provider_order_id}")
        return ProviderResult(True, self.name, provider_order_id, data.get("status"), data)

    def verify_payment(self, order_id, payment_id, signature):
        secret = current_app.config["RAZORPAY_KEY_SECRET"].encode()
        expected = hmac.new(secret, f"{order_id}|{payment_id}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature or ""):
            raise ProviderError("Invalid payment signature.", ProviderState.UNAVAILABLE)
        return ProviderResult(True, self.name, payment_id, "verified", {"order_id": order_id})


def get_payment_provider():
    provider = current_app.config.get("PAYMENT_PROVIDER", "mock").lower()
    if provider == "razorpay":
        return RazorpayProvider()
    if provider == "mock" and current_app.config.get("APP_ENV") != "production":
        return MockPaymentProvider()
    return UnconfiguredPaymentProvider()

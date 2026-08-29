import logging
from datetime import datetime

from app.models import MessageLog, Notification, db
from app.providers.base import ProviderError
from app.providers.notifications import get_notification_provider
from app.providers.whatsapp import get_whatsapp_provider

logger = logging.getLogger(__name__)


def send_notification(channel, organization_id, recipient, message, subject=None, html=None, template=None, data=None):
    channel = channel.lower()
    provider = get_whatsapp_provider() if channel == "whatsapp" else get_notification_provider(channel)
    if provider.state.value in ("DISABLED", "NOT_CONFIGURED"):
        raise ProviderError(f"{channel.title()} provider is not configured.", provider.state)
    if channel == "whatsapp":
        result = provider.send_text(recipient, message)
        log = MessageLog(organization_id=organization_id, recipient_number=recipient, message_type="WhatsApp", message_content=message, status=result.status or "Sent", sent_at=datetime.utcnow())
    else:
        result = provider.send(recipient, subject, message, html, template, data)
        log = MessageLog(organization_id=organization_id, recipient_number=recipient, message_type=channel.title(), message_content=message, status=result.status or "Sent", sent_at=datetime.utcnow())
    db.session.add(log)
    db.session.commit()
    return result

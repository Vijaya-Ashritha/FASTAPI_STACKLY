
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings


logger = logging.getLogger(__name__)


def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    message = EmailMessage()
    message["From"] = settings.sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=15,
        ) as server:
            server.starttls()
            server.login(
                settings.smtp_username,
                settings.smtp_password,
            )
            server.send_message(message)

        logger.info("Email sent successfully to %s", recipient)

    except (smtplib.SMTPException, OSError) as exc:
        logger.exception("Email delivery failed to %s", recipient)
        raise RuntimeError("Email delivery failed") from exc

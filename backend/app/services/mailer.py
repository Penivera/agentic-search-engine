from __future__ import annotations

import asyncio
import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings


logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


def _validate_smtp_config() -> None:
    missing: list[str] = []
    if not settings.SMTP_HOST:
        missing.append("SMTP_HOST")
    if not settings.SMTP_USERNAME:
        missing.append("SMTP_USERNAME")
    if not settings.SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")
    if not settings.SMTP_SEND_FROM_MAIL:
        missing.append("SMTP_SEND_FROM_MAIL")

    if missing:
        raise EmailDeliveryError(
            f"SMTP is not fully configured. Missing: {', '.join(missing)}"
        )


def _send_email_sync(to_email: str, subject: str, body: str) -> None:
    _validate_smtp_config()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_SEND_FROM_MAIL
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=settings.SMTP_TIMEOUT_SECONDS,
        ) as server:
            server.ehlo()
            if settings.SMTP_USE_STARTTLS:
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as exc:
        raise EmailDeliveryError(str(exc)) from exc


async def send_verification_otp_email(to_email: str, otp_code: str) -> None:
    subject = "Your ASE verification code"
    body = (
        "Use the code below to verify your account.\n\n"
        f"OTP: {otp_code}\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.\n"
    )

    await asyncio.to_thread(_send_email_sync, to_email, subject, body)
    logger.info("Sent OTP email to %s", to_email)

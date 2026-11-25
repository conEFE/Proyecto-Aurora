"""Envío de emails transaccionales (activación de cuenta).

Proveedores (EMAIL_PROVIDER):
- console: no envía; registra el email en el log y lo deja en `outbox` (desarrollo y pruebas).
- smtp: envía por SMTP_HOST con STARTTLS. Las credenciales se leen de .env.

El envío nunca debe romper la operación que lo origina: los errores se registran y se informan como False.
"""

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger("aurora.email")


@dataclass
class OutgoingEmail:
    to: str
    subject: str
    text: str
    html: str | None = None


# Emails "enviados" por el proveedor console (las pruebas leen el link desde aquí)
outbox: list[OutgoingEmail] = []


def _send_smtp(mail: OutgoingEmail) -> None:
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = mail.to
    msg["Subject"] = mail.subject
    msg.set_content(mail.text)
    if mail.html:
        msg.add_alternative(mail.html, subtype="html")
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
        if settings.SMTP_STARTTLS:
            smtp.starttls()
        if settings.SMTP_USER:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)


def send(mail: OutgoingEmail) -> bool:
    provider = (settings.EMAIL_PROVIDER or "console").lower()
    try:
        if provider == "smtp":
            if not settings.SMTP_HOST:
                raise RuntimeError("EMAIL_PROVIDER=smtp pero SMTP_HOST está vacío")
            _send_smtp(mail)
        else:
            outbox.append(mail)
            if len(outbox) > 100:
                del outbox[:-100]
            logger.info("Email (console) para %s: %s\n%s", mail.to, mail.subject, mail.text)
        return True
    except Exception:  # noqa: BLE001 - el envío no debe tumbar la request
        logger.exception("No se pudo enviar el email '%s'", mail.subject)
        return False


def activation_link(token: str) -> str:
    return f"{settings.PUBLIC_APP_URL.rstrip('/')}/activar?token={token}"


def activation_email(to: str, first_name: str, token: str) -> OutgoingEmail:
    link = activation_link(token)
    hours = settings.ACTIVATION_TOKEN_HOURS
    text = (
        f"Hola {first_name}:\n\n"
        "Se creó su cuenta en Aurora, la plataforma de apoyo al triage de casos sospechosos de cáncer de mama.\n"
        "Para confirmar su email y definir su contraseña, abra este link:\n\n"
        f"{link}\n\n"
        f"El link vence en {hours} horas y sirve una sola vez. Si usted no esperaba este email, ignórelo.\n\n"
        "Equipo Aurora"
    )
    html = (
        f"<p>Hola {_esc(first_name)}:</p>"
        "<p>Se creó su cuenta en <strong>Aurora</strong>, la plataforma de apoyo al triage de casos sospechosos "
        "de cáncer de mama.</p>"
        "<p>Para confirmar su email y definir su contraseña, use este botón:</p>"
        f'<p><a href="{_esc(link)}" style="background:#be185d;color:#fff;padding:10px 18px;border-radius:8px;'
        'text-decoration:none;display:inline-block">Activar mi cuenta</a></p>'
        f'<p style="color:#666;font-size:13px">O copie este link: {_esc(link)}<br>'
        f"Vence en {hours} horas y sirve una sola vez. Si no esperaba este email, ignórelo.</p>"
    )
    return OutgoingEmail(to=to, subject="Active su cuenta de Aurora", text=text, html=html)


def _esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

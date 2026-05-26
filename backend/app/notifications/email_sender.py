import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@rastreador.com")

async def send_email_notification(to_email: str, subject: str, message: str):
    if not SENDGRID_API_KEY:
        logger.warning("SendGrid não configurado. Email não enviado.")
        return
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        mail = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=f"<p>{message}</p>"
        )
        response = sg.send(mail)
        logger.info(f"Email enviado para {to_email}, status {response.status_code}")
    except Exception as e:
        logger.error(f"Falha ao enviar email: {e}")
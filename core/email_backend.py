import logging

from anymail.backends.mailgun import EmailBackend as MailgunBackend

logger = logging.getLogger(__name__)


class LoggingMailgunBackend(MailgunBackend):
    """Mailgun backend with detailed logging."""

    def send_messages(self, email_messages):
        """Send messages with logging."""
        if not email_messages:
            return 0

        sent_count = 0

        for message in email_messages:
            try:
                # Log the attempt
                recipients = ", ".join(message.to)
                logger.info(f"📧 Sending email to {recipients}: {message.subject}")

                # Send the email
                result = super().send_messages([message])

                if result:
                    logger.info(f"✅ Email sent successfully to {recipients}")
                    sent_count += result
                else:
                    logger.error(f"❌ Email failed to send to {recipients}")

            except Exception as e:
                logger.error(f"❌ Email sending error to {recipients}: {str(e)}")

        return sent_count

"""
Email services for the projects app.
"""

import logging
from typing import Any, Dict, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Mailgun API."""

    def __init__(self):
        self.api_key = settings.MAILGUN_API_KEY
        self.domain = settings.MAILGUN_DOMAIN
        self.default_from_email = settings.DEFAULT_FROM_EMAIL

        # Validate settings
        self._validate_settings()

    def _validate_settings(self) -> None:
        """Validate that all required email settings are configured."""
        if not self.api_key:
            logger.warning("MAILGUN_API_KEY is not set - email functionality will be disabled")
            return
        if not self.domain:
            logger.warning("MAILGUN_DOMAIN is not set - email functionality will be disabled")
            return
        if not self.default_from_email:
            logger.warning("DEFAULT_FROM_EMAIL is not set - email functionality will be disabled")
            return

    def _send_email(self, subject: str, html_content: str, recipient_email: str) -> Dict[str, Any]:
        """
        Send email via Mailgun API.

        Args:
            subject: Email subject
            html_content: HTML email content
            recipient_email: Recipient email address

        Returns:
            Dictionary with send status
        """
        try:
            # Check if email settings are configured
            if not all([self.api_key, self.domain, self.default_from_email]):
                logger.warning("Email settings not configured - skipping email send")
                return {
                    'status': 'skipped',
                    'message': 'Email settings not configured'
                }

            # Prepare Mailgun API request
            url = f"https://api.mailgun.net/v3/{self.domain}/messages"
            logger.info(f"Sending email to {recipient_email}: {subject}")

            auth = ('api', self.api_key)

            data = {
                'from': self.default_from_email,
                'to': recipient_email,
                'subject': subject,
                'html': html_content
            }

            # Send the email
            response = requests.post(url, auth=auth, data=data, timeout=30)
            response.raise_for_status()

            logger.info(f"Email sent successfully via Mailgun to {recipient_email}")
            return {
                'status': 'success',
                'message': 'Email sent successfully',
                'mailgun_response': response.json()
            }

        except requests.exceptions.HTTPError as e:
            logger.error(f"Mailgun API error: {e.response.status_code} - {e.response.text}")
            return {
                'status': 'error',
                'message': f'Mailgun API error: {e.response.status_code}',
                'details': e.response.text
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending email: {str(e)}")
            return {
                'status': 'error',
                'message': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }

    def send_invitation_email(
        self,
        email: str,
        project_name: str,
        invitation_url: str,
        invited_by_email: str
    ) -> Dict[str, Any]:
        """
        Send project invitation email via Mailgun API.

        Args:
            email: Recipient email address
            project_name: Name of the project
            invitation_url: URL to accept invitation
            invited_by_email: Email of the person sending invitation

        Returns:
            Dictionary with send status
        """
        try:
            subject = f"Invitation to collaborate on {project_name}"

            html_content = f"""
            <html>
            <body>
                <h2>Project Collaboration Invitation</h2>
                <p>Hello!</p>
                <p><strong>{invited_by_email}</strong> has invited you to collaborate on the housing evaluation project "<strong>{project_name}</strong>".</p>
                <p>Click the link below to accept the invitation:</p>
                <p><a href="{invitation_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accept Invitation</a></p>
                <p>Or copy and paste this URL into your browser:</p>
                <p>{invitation_url}</p>
                <p>Best regards,<br>The Checklist Casa Team</p>
            </body>
            </html>
            """

            return self._send_email(
                subject=subject,
                html_content=html_content,
                recipient_email=email
            )

        except Exception as e:
            logger.error(f"Error sending invitation email: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error sending invitation email: {str(e)}'
            }

    def send_home_upload_confirmation(self, user, home_name: str) -> Dict[str, Any]:
        """
        Send confirmation email after home upload if user has opted in.

        Args:
            user: User object
            home_name: Name/address of the uploaded home

        Returns:
            Dictionary with send status
        """
        try:
            # Check if user wants to receive confirmation emails
            if not hasattr(user, 'profile') or not user.profile.receive_confirmation_emails:
                logger.info(f"Skipping confirmation email for user {user.email} - opted out")
                return {
                    'status': 'skipped',
                    'message': 'User has opted out of confirmation emails'
                }

            subject = f"Home Information Uploaded: {home_name}"

            html_content = f"""
            <html>
            <body>
                <h2>Home Upload Confirmation</h2>
                <p>Hello!</p>
                <p>Your home information has been successfully uploaded to Checklist Casa.</p>
                <p><strong>Home:</strong> {home_name}</p>
                <p>You can now view and manage this home in your dashboard.</p>
                <p>Best regards,<br>The Checklist Casa Team</p>
            </body>
            </html>
            """

            return self._send_email(
                subject=subject,
                html_content=html_content,
                recipient_email=user.email
            )

        except Exception as e:
            logger.error(f"Error sending home upload confirmation: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error sending confirmation email: {str(e)}'
            }

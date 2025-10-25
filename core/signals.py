import logging

from allauth.account.signals import (
    email_added,
    email_confirmation_sent,
    email_confirmed,
    password_changed,
    password_reset,
    user_logged_in,
    user_logged_out,
    user_signed_up,
)
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(user_signed_up)
def log_user_signup(sender, request, user, **kwargs):
    """Log when a user signs up."""
    ip = get_client_ip(request)
    logger.info(f"🎉 User signup: {user.email} from IP {ip}")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    ip = get_client_ip(request)
    logger.info(f"🔐 User login: {user.email} from IP {ip}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    ip = get_client_ip(request)
    user_email = user.email if user else "unknown"
    logger.info(f"👋 User logout: {user_email} from IP {ip}")


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempts."""
    ip = get_client_ip(request)
    email = credentials.get("email", "unknown")
    logger.warning(f"🚫 Login failed: {email} from IP {ip}")


@receiver(email_confirmation_sent)
def log_email_confirmation_sent(sender, request, confirmation, signup, **kwargs):
    """Log when email confirmation is sent."""
    ip = get_client_ip(request)
    user_email = confirmation.email_address.email
    action = "signup" if signup else "resend"
    logger.info(f"📧 Email confirmation sent ({action}): {user_email} from IP {ip}")


@receiver(email_confirmed)
def log_email_confirmed(sender, request, email_address, **kwargs):
    """Log when email is confirmed."""
    ip = get_client_ip(request)
    logger.info(f"✅ Email confirmed: {email_address.email} from IP {ip}")


@receiver(email_added)
def log_email_added(sender, request, user, email_address, **kwargs):
    """Log when email is added to account."""
    ip = get_client_ip(request)
    logger.info(
        f"📬 Email added: {email_address.email} for user {user.email} from IP {ip}"
    )


@receiver(password_reset)
def log_password_reset(sender, request, user, **kwargs):
    """Log password reset requests."""
    ip = get_client_ip(request)
    logger.info(f"🔑 Password reset requested: {user.email} from IP {ip}")


@receiver(password_changed)
def log_password_changed(sender, request, user, **kwargs):
    """Log password changes."""
    ip = get_client_ip(request)
    logger.info(f"🔐 Password changed: {user.email} from IP {ip}")


def get_client_ip(request):
    """Get client IP from request."""
    if not request:
        return "unknown"

    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")

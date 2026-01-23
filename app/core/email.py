import smtplib
from email.message import EmailMessage
from app.core.config import settings


def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP Verification Code"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    msg.set_content(
        f"""
Your OTP code is: {otp}

This code is valid for 10 minutes.
Do not share this code with anyone.
        """
    )

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_password_reset_email(to_email: str, reset_token: str):
    """Send password reset email with reset link"""
    # Construct reset link - update with your frontend URL
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    
    msg = EmailMessage()
    msg["Subject"] = "Reset Your Password"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    msg.set_content(
        f"""
You requested to reset your password.

Click the link below to reset your password:
{reset_link}

This link is valid for 15 minutes.

If you didn't request this, please ignore this email.
        """
    )

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
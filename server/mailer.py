"""
mailer.py - sends enquiry notification emails.

Uses smtplib with Gmail SMTP. Reads MAIL_USER, MAIL_PASSWORD, MAIL_TO from
environment variables. If any variable is missing or sending fails, the error
is logged but NOT raised - the enquiry is still saved and the visitor still
sees a success message.
"""
import os
import smtplib
from email.message import EmailMessage


def send_enquiry_email(name, email, message, property_title=None):
    """
    Send an enquiry notification email to MAIL_TO.

    Returns True if the email was sent, False otherwise (missing config or
    SMTP failure). Never raises an exception.
    """
    mail_user = os.environ.get("MAIL_USER")
    mail_password = os.environ.get("MAIL_PASSWORD")
    mail_to = os.environ.get("MAIL_TO")

    if not mail_user or not mail_password or not mail_to:
        print("mailer: MAIL_USER/MAIL_PASSWORD/MAIL_TO not set, skipping email")
        return False

    subject = f"New property enquiry from {name}"
    body = f"""\
New enquiry received on LOK Property Solutions website.

Name: {name}
Email: {email}
Property: {property_title or "General enquiry"}

Message:
{message}
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = mail_user
    msg["To"] = mail_to
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(mail_user, mail_password)
            server.send_message(msg)
        print(f"mailer: enquiry email sent to {mail_to}")
        return True
    except Exception as exc:
        print(f"mailer: failed to send email: {exc}")
        return False
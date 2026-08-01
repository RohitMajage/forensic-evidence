import random
import requests
import os
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_custom_email(subject, message, recipient_list):
    brevo_key = os.environ.get('BREVO_API_KEY')
    if brevo_key:
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {"name": "ForensicEvidence", "email": settings.DEFAULT_FROM_EMAIL},
            "to": [{"email": email} for email in recipient_list],
            "subject": subject,
            "htmlContent": f"<html><body><p>{message.replace(chr(10), '<br>')}</p></body></html>",
            "textContent": message
        }
        headers = {
            "accept": "application/json",
            "api-key": brevo_key,
            "content-type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Brevo API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Brevo API response: {e.response.text}")
            return False
    else:
        # Fallback to standard Django send_mail
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        return True
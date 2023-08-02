from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django_otp.plugins.otp_email.models import EmailDevice

User = get_user_model()


class EmailOTPBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

from django.core.mail import send_mail
from django_otp import devices_for_user

def send_otp_email(user):
    # Generate a one-time code
    device = devices_for_user(user, confirmed=True).get()
    otp_code = device.generate_challenge()

    # Send the one-time code via email
    subject = 'Your One-Time Code for 2FA'
    message = f'Your one-time code is: {otp_code}'
    from_email = 'your_email@example.com'  # Replace with your email
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
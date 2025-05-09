from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.cache import cache

from celery import shared_task 

from django.utils.timezone import now
from bookapp.models import Subscription

@shared_task
def send_otp_email_task(email):
    otp = generate_otp()
    cache.set(f"otp_{email}", otp, timeout=600)
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
 
def generate_otp():
    return random.randint(100000, 999999)

@shared_task
def send_otp_email_task_beat():
    subject = 'Welcome message'
    message = 'Hello from Celery!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['classicgamer622@gmail.com']
    send_mail(subject, message, email_from,recipient_list,fail_silently=False)


@shared_task
def deactivate_expired_subscriptions():
    expired = Subscription.objects.filter(expiry_date__lt=now(), is_active=True)
    count = expired.update(is_active=False)
    return f"Deactivated {count} expired subscriptions"
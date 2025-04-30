from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.cache import cache
from .mixins import*


from functools import wraps
 
def send_otp_email(email):
    otp = generate_otp()
    cache.set(f"otp_{email}", otp, timeout=600)
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
 
def generate_otp():
    return random.randint(100000, 999999)


def redis_cache(timeout=300):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            user = request.user
            # If pk exists (detail view), use it; else use 'all' (list view)
            pk = kwargs.get('pk')
            cache_key = (
                self.get_cache_key(user.id, pk) if hasattr(self, 'get_cache_key')
                else f"user_books_{user.id}"
            )

            cached_data = cache.get(cache_key)
            if cached_data is not None:
                print("data listed from cache")
                return Response({
                    "message": "Successfully listed from cache",
                    "data": cached_data
                })

            # Fetch fresh data
            response = func(self, request, *args, **kwargs)
            # Cache only if it's a 200 OK
            if response.status_code == 200:
                cache.set(cache_key, response.data["data"], timeout=timeout)
                print("data listed from database and cached")
            return response
        return wrapper
    return decorator

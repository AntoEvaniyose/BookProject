# worker Celery


# import os
# from celery import Celery
 
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookproject.settings')
 
# app = Celery('bookproject')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()



# beat Celery


from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
 
# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookproject.settings')
 
app = Celery('bookproject')
app.conf.enable_utc=False
app.conf.update(timezone='Asia/Kolkata')
 
 
app.config_from_object('django.conf:settings', namespace='CELERY')
 

 
 
app.conf.beat_schedule = {
    # Task 1: Send email reminders one hour before the appointment
    'send_otp_email_task_beat': {
        'task': 'bookapp.tasks.send_otp_email_task_beat',
        # 'schedule': 30.0,  # Run every minute'
        # 'schedule' : crontab(minute='*/5'),   #every 5 minute
        # 'schedule': crontab(minute='*/10'),     #every 10 minute
        # 'schedule': crontab(minute='0,30'),    #every 30 minute
        'schedule': crontab(hour=10, minute=30),  # Every day at 10:30 AM
    },
    'deactivate_expired_juice_subscriptions': {
        'task': 'bookapp.tasks.deactivate_expired_subscriptions',
        'schedule': crontab(hour=10, minute=30),  # Runs daily at 10:30 AM
    },  
}
 
 
app.autodiscover_tasks()
 
# app.conf.timezone = 'Asia/Kolkata'
 
 
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone        
from .manager import *

from django.utils.timezone import now
from datetime import timedelta



class Bookuser(AbstractUser):
  
    username = None
    email = models.EmailField(unique=True,null=True,blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
 
    REQUIRED_FIELDS = []
 
    objects = UserManager()
    
    def __str__(self):
        return self.email
    

    
class Book(models.Model):
    name=models.CharField(max_length=20)
    author=models.CharField(max_length=20)
    price=models.IntegerField()
    image=models.ImageField(upload_to="book_image")
    bookuser=models.ForeignKey(Bookuser, on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.name
    

class Subscription(models.Model):
    JUICE_CHOICES = [
        ('orange', 'Orange Juice'),
        ('apple', 'Apple Juice'),
        ('mango', 'Mango Juice'),
    ]

    juice_type = models.CharField(max_length=50, choices=JUICE_CHOICES)
    package_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)  # Allow blank/null
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.expiry_date and self.package_date:
            self.expiry_date = self.package_date + timedelta(days=5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.juice_type} subscription (expires {self.expiry_date})"
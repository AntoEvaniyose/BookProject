from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone        
from .manager import *



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

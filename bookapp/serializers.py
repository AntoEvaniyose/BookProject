from rest_framework import serializers
from . models import *
from django.contrib.auth import authenticate



class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookuser
        fields = [ 'email', 'password','first_name','last_name','otp']
 
    def create(self, validated_data):
 
        user = Bookuser.objects.create_user(**validated_data)
        return user
    
       
class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
 
 
 
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
 
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
       
        # Use the custom authentication backend
        user = authenticate(email=email, password=password)
        # print(f'Authenticating user: {email}') 
       
        if not user:
            print('Invalid credentials')
            raise serializers.ValidationError('Invalid credentials')
 
        if not user.is_active:
            print('User account is not active')
            raise serializers.ValidationError('User account is not active')
 
        data['user'] = user
        return data
   
class BookuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookuser
        fields = ['id','email','first_name','last_name']
        read_only_fields=['id']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id','name','author','image','bookuser','price']
        read_only_fields=['id','bookuser']

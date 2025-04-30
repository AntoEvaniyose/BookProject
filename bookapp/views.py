from django.shortcuts import render
from rest_framework import generics,status,permissions


from . models import *
from . serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response

import random
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import *

from django.shortcuts import get_object_or_404

from .mixins import *

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache


from .task import *



class UserRegistrationView(APIView):
    def post(self, request):

        email = request.data.get('email')

        try:
            user = Bookuser.objects.get(email=email)

            if user.is_active:
                    return custom200( "Email is already verified. Please log in.")

            send_otp_email_task.delay(email=email)

            return custom200("OTP resent. Please verify your email.")

        except Bookuser.DoesNotExist:
                # New user — register and send OTP
                serializer = UserRegistrationSerializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save(is_active = False)
                    send_otp_email_task.delay(email=email)

                    return custom200("OTP sent successfully. Please verify your email.")
                return custom404("Not Found",serializer.errors)



class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = str(serializer.validated_data['otp'])

            try:
                user = Bookuser.objects.get(email=email, is_active=False)

                # Get OTP from Redis
                cached_otp = cache.get(f"otp_{email}")

                if cached_otp:
                    if str(cached_otp) == otp:
                        # Success: Activate user
                        user.is_active = True
                        user.otp = None  # Clear OTP from DB
                        user.save()

                        cache.delete(f"otp_{email}")  # Remove from Redis
                        return custom200("Email verified successfully. Account activated.")
                    else:
                        return custom404("Invalid OTP.")
                else:
                    return custom404( "OTP has expired. Please request a new one.")

            except Bookuser.DoesNotExist:
                return custom404("No user found with this email or already activated.")

        return custom404("Not Found",serializer.errors)



class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
 
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
       
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = authenticate(email=email, password=password)
       
        if not user:
            raise serializers.ValidationError('Invalid credentials')
 
        if not user.is_active:
            raise serializers.ValidationError('User account is not active')
 
        refresh = RefreshToken.for_user(user)
        return custom200("Successfully Login",{
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    
    


    

class BookUserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can view

    def get(self, request):
        bookusers = Bookuser.objects.all()
        serializer = BookuserSerializer(bookusers, many=True)
        return custom200("Successfully lists",serializer.data)



# class BookListCreateView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         cache_key = f"user_books_{user.id}"

#         # Check cache first
#         data = cache.get(cache_key)
        
#         if data is None:
#             books = Book.objects.filter(bookuser=user)
#             serializer = BookSerializer(books, many=True)
#             data = serializer.data
#             print("data listed from database")
#             cache.set(cache_key, data, timeout=300)  # 5 minutes
#         print("data listed from cache")
#         return custom200("Successfully lists", data)

#     def post(self, request):
#         user = request.user
#         serializer = BookSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(bookuser=user)

#             # Invalidate the user's cache so new GET shows updated list
#             cache_key = f"user_books_{user.id}"
#             cache.delete(cache_key)

#             return custom200("Successfully Created", serializer.data)
#         return custom404("Not Found", serializer.errors)


class BookListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_cache_key(self, user_id, book_id=None):
        return f"user_books_{user_id}"

    @redis_cache(timeout=300)
    def get(self, request):
        user = request.user
        books = Book.objects.filter(bookuser=user)
        serializer = BookSerializer(books, many=True)
        return custom200("Successfully lists", serializer.data)

    def post(self, request):
        user = request.user
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(bookuser=user)

            # Invalidate user's book list cache
            cache_key = self.get_cache_key(user.id)
            cache.delete(cache_key)

            return custom200("Successfully Created", serializer.data)
        return custom404("Not Found", serializer.errors)


# class BookDetailView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get_cache_key(self, user_id, book_id):
#         return f"book_{user_id}_{book_id}"

#     def get(self, request, pk):
#         user = request.user
#         cache_key = self.get_cache_key(user.id, pk)

#         # Try to get from cache
#         data = cache.get(cache_key)
#         if data is None:
#             book = get_object_or_404(Book, pk=pk, bookuser=user)
#             serializer = BookSerializer(book)
#             data = serializer.data
#             print("data listed from database")
#             cache.set(cache_key, data, timeout=300)  # 5 minutes
#         print("data listed from cache")
#         return custom200("Successfully list", data)

#     def put(self, request, pk):
#         user = request.user
#         book = get_object_or_404(Book, pk=pk, bookuser=user)
#         serializer = BookSerializer(book, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             data = serializer.data

#             # Update book cache
#             cache_key = self.get_cache_key(user.id, pk)
#             cache.set(cache_key, data, timeout=300)

#             # Invalidate list cache
#             cache.delete(f"user_books_{user.id}")
#             return custom200("Successfully Updated", data)
#         return custom404("Not Found", serializer.errors)

#     def patch(self, request, pk):
#         user = request.user
#         book = get_object_or_404(Book, pk=pk, bookuser=user)
#         serializer = BookSerializer(book, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             data = serializer.data

#             # Update book cache
#             cache_key = self.get_cache_key(user.id, pk)
#             cache.set(cache_key, data, timeout=300)

#             # Invalidate list cache
#             cache.delete(f"user_books_{user.id}")
#             return custom200("Successfully Updated", data)
#         return custom404("Not Found", serializer.errors)

#     def delete(self, request, pk):
#         user = request.user
#         book = get_object_or_404(Book, pk=pk, bookuser=user)
#         book.delete()

#         # Remove this book from cache
#         cache_key = self.get_cache_key(user.id, pk)
#         cache.delete(cache_key)

#         # Invalidate the book list cache too
#         cache.delete(f"user_books_{user.id}")
#         return custom200("Successfully Deleted")



class BookDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_cache_key(self, user_id, book_id=None):
        if book_id:
            return f"book_{user_id}_{book_id}"
        return f"user_books_{user_id}"

    @redis_cache(timeout=300)
    def get(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk, bookuser=user)
        serializer = BookSerializer(book)
        return custom200("Successfully list", serializer.data)

    def put(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk, bookuser=user)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data

            # Update book cache
            cache_key = self.get_cache_key(user.id, pk)
            cache.set(cache_key, data, timeout=300)

            # Invalidate list cache
            cache.delete(self.get_cache_key(user.id))
            return custom200("Successfully Updated", data)
        return custom404("Not Found", serializer.errors)

    def patch(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk, bookuser=user)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data

            # Update book cache
            cache_key = self.get_cache_key(user.id, pk)
            cache.set(cache_key, data, timeout=300)

            # Invalidate list cache
            cache.delete(self.get_cache_key(user.id))
            return custom200("Successfully Updated", data)
        return custom404("Not Found", serializer.errors)

    def delete(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk, bookuser=user)
        book.delete()

        # Invalidate caches
        cache.delete(self.get_cache_key(user.id, pk))
        cache.delete(self.get_cache_key(user.id))
        return custom200("Successfully Deleted")
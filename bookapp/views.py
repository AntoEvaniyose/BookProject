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




class UserRegistrationView(APIView):
    def post(self, request):

        email = request.data.get('email')

        try:
            user = Bookuser.objects.get(email=email)

            if user.is_email_verified:
                    return Response({"message": "Email is already verified. Please log in."}, status=status.HTTP_200_OK)

            send_otp_email(email=email)

            return Response({"message": "OTP resent. Please verify your email."}, status=status.HTTP_200_OK)

        except Bookuser.DoesNotExist:
                # New user — register and send OTP
                serializer = UserRegistrationSerializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save(is_active = False)
                    send_otp_email(email=email)

                    return Response({"message": "OTP sent successfully. Please verify your email."}, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = str(serializer.validated_data['otp'])

            try:
                user = Bookuser.objects.get(email=email, is_email_verified=False)

                # Get OTP from Redis
                cached_otp = cache.get(f"otp_{email}")

                if cached_otp:
                    if str(cached_otp) == otp:
                        # Success: Activate user
                        user.is_active = True
                        user.is_email_verified = True
                        user.otp = None  # Clear OTP from DB
                        user.save()

                        cache.delete(f"otp_{email}")  # Remove from Redis
                        return Response({"message": "Email verified successfully. Account activated."}, status=status.HTTP_200_OK)
                    else:
                        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            except Bookuser.DoesNotExist:
                return Response({"error": "No user found with this email or already activated."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            # 'user': UserLoginSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    


    

class BookUserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can view

    def get(self, request):
        bookusers = Bookuser.objects.all()
        serializer = BookuserSerializer(bookusers, many=True)
        return Response(serializer.data)




class BookListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can access

    # GET all books
    def get(self, request):
        user = request.user
        books = Book.objects.filter(bookuser=user)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    # POST create a new book
    def post(self, request):
        user = request.user
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(bookuser=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BookDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # GET book by ID
    def get(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk,bookuser=user)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    # PUT update the entire book record
    def put(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk,bookuser=user)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH update part of the book record
    def patch(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk,bookuser=user)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE book by ID
    def delete(self, request, pk):
        user = request.user
        book = get_object_or_404(Book, pk=pk,bookuser=user)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
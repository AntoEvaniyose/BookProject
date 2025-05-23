from django.urls import path
from . views import *

urlpatterns = [
    path('register/',UserRegistrationView.as_view()),
    path('OTP_valid/',OTPVerificationView.as_view()),
    path('login/',UserLoginView.as_view()),
    path('bookusers/', BookUserListView.as_view(), name='bookuser-list'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
]
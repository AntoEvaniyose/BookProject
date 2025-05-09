from django.urls import path
from . views import *

urlpatterns = [
    path('register/',UserRegistrationView.as_view()),
    path('OTP_valid/',OTPVerificationView.as_view()),
    path('login/',UserLoginView.as_view()),
    path('bookusers/', BookUserListView.as_view(), name='bookuser-list'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/pdf/<int:book_id>/', BookPDFView.as_view(), name='book_pdf'),
    path('books/pdf/', BookListPDFView.as_view(), name='user_book_pdf'),


    path('generate_qr/<int:book_id>/', GenerateQRCodeWithDataView.as_view(), name='generate_qr'),

]
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.cache import cache
from .mixins import*


from functools import wraps

from reportlab.pdfgen import canvas
from io import BytesIO
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


import qrcode
from django.core.files.base import ContentFile

 
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



class BookPDFGenerator:
    def __init__(self, book):
        self.book = book

    def generate_pdf(self):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, "Book Details")

        # Book Information
        p.setFont("Helvetica", 12)
        p.drawString(100, 770, f"Book ID: {self.book.id}")
        p.drawString(100, 750, f"Name: {self.book.name}")
        p.drawString(100, 730, f"Author: {self.book.author}")
        p.drawString(100, 710, f"Price: ₹{self.book.price}")

        # Finish PDF
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer
    


class BookListPDFGenerator:
    def __init__(self, user, books):
        self.user = user
        self.books = books

    def generate_pdf(self):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = Paragraph(f"Book List for User: {self.user.email}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Table data
        data = [['ID', 'Name', 'Author', 'Price']]
        for book in self.books:
            data.append([book.id, book.name, book.author, f'₹{book.price}'])

        # Table style
        table = Table(data, colWidths=[50, 150, 150, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer



def generate_qr_code_from_data(data_dict):
    # Raw format as string (using pipe "|" as separator)
    data_string = f"Book Id:{data_dict['id']}|Book Name:{data_dict['name']}|Book price:{data_dict['price']}"

    # Format data in clean column style
    data_string = (
        f"ID     : {data_dict['id']}\n"
        f"Name   : {data_dict['name']}\n"
        f"Price  : {data_dict['price']}"
        # f"Image  : {data_dict['image']}"
    )

    # Create QR code
    qr = qrcode.QRCode(
        version=1,  # Use smaller version for smaller QR code
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Lower error correction for smaller QR
        box_size=10,  # Small boxes
        border=4,  # Small border
    )
    
    qr.add_data(data_string)
    qr.make(fit=True)
    
    # Generate QR code image and save to buffer
    buffer = BytesIO()
    img = qr.make_image(fill='black', back_color='white')
    img.save(buffer, format="PNG")
    
    return buffer.getvalue()
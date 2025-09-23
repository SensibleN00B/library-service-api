from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from library.models import Book, Borrowing
from payment.models import Payment

User = get_user_model()

book = Book.objects.create(title="Test", author="Test_author", daily_fee=0.2)
borrowing = Borrowing.objects.create(expected_return_date=timezone.now() + timedelta(days=5), book=book, user=User.objects.get(id=1))
payment = Payment.objects.create(borrowing=borrowing, money_to_pay=25.02)

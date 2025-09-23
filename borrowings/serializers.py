from django.utils import timezone
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentBorrowingSerializer
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    payments = PaymentBorrowingSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    payments = PaymentBorrowingSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = ("borrow_date", "expected_return_date", "book", "payments")
        extra_kwargs = {"borrow_date": {"required": False}}

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]

        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(user=user, **validated_data)
        return borrowing

    def validate(self, data):
        borrow_date = data.get("borrow_date") or timezone.now().date()
        expected_return_date = data["expected_return_date"]
        request = self.context["request"]
        user = request.user

        if borrow_date > expected_return_date:
            raise serializers.ValidationError(
                {
                    "expected_return_date": (
                        "Expected return date must be after borrow date."
                    )
                }
            )

        if data["book"].inventory < 1:
            raise serializers.ValidationError(
                {"book": "This book is out of stock."}
            )

        pending_payments = Payment.objects.filter(
            borrowing__user=user, status="pending"
        )
        if pending_payments.exists():
            raise serializers.ValidationError(
                {
                    "detail": [
                        "You have pending payments."
                        " You cannot borrow new books until they are resolved."
                    ]
                }
            )

        return data


class BorrowingReturnSerializer(serializers.Serializer):
    pass

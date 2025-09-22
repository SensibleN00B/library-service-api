from django.utils import timezone
from rest_framework import serializers

from library.models import Book, Borrowing
from user.serializers import UserSerializer


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "daily_fee")


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("borrow_date", "expected_return_date", "book")
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

        return data


class BorrowingReturnSerializer(serializers.Serializer):
    pass

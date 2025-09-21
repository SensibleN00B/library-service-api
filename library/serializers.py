from rest_framework import serializers

from library.models import Book, Borrowing


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "daily_fee")


class BorrowingSerializer(serializers.ModelSerializer):
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


class BorrowingListSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

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

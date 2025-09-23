from rest_framework import serializers

from books.models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")

    @staticmethod
    def validate_inventory(value):
        if value < 0:
            raise serializers.ValidationError("Inventory cannot be negative.")
        return value

    @staticmethod
    def validate_daily_fee(value):
        if value < 0:
            raise serializers.ValidationError("Daily fee cannot be negative.")
        return value


class BookListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "daily_fee")

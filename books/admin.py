from django.contrib import admin

from books.models import Book
from borrowings.models import Borrowing


class BorrowingInline(admin.TabularInline):
    model = Borrowing
    extra = 0
    fields = (
        "book",
        "user",
        "expected_return_date",
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "inventory", "daily_fee")
    search_fields = ("title", "author")
    list_filter = ("inventory",)
    inlines = [BorrowingInline]

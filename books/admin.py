from django.contrib import admin

from library.models import Book, Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Borrowing.objects.select_related("user", "book")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass

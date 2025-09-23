from django.contrib import admin

from borrowings.models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Borrowing.objects.select_related("user", "book")

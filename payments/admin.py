from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "borrowing",
        "user",
        "book",
        "type",
        "status",
        "money_to_pay",
        "session_url",
    )
    list_filter = ("status", "type")
    search_fields = ("borrowing__book__title", "borrowing__user__username")
    actions = ["mark_as_paid"]

    def user(self, obj):
        return obj.borrowing.user

    user.admin_order_field = "borrowing__user"
    user.short_description = "User"

    def book(self, obj):
        return obj.borrowing.book.title

    book.admin_order_field = "borrowing__book"
    book.short_description = "Book"

    def get_queryset(self, request):
        return Payment.objects.select_related("borrowing__user", "borrowing")

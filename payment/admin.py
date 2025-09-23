from django.contrib import admin

from payment.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Payment.objects.select_related("borrowing__user", "borrowing")

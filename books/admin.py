from django.contrib import admin

from library.models import Borrowing, Book


@admin.register(Borrowing)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class PaymentAdmin(admin.ModelAdmin):
    pass
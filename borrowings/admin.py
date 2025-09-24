from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from borrowings.forms import BorrowingAdminForm
from borrowings.models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    form = BorrowingAdminForm
    list_display = (
        "book",
        "user",
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "return_button",
    )
    readonly_fields = ("actual_return_date",)
    list_filter = (
        "user",
        "book",
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<path:object_id>/return/",
                self.admin_site.admin_view(self.process_return),
                name="borrowing_return",
            ),
        ]
        return custom + urls

    def process_return(self, request, object_id):
        borrowing = self.get_object(request, object_id)
        borrowing.return_book()
        return redirect(request.META.get("HTTP_REFERER"))

    def return_button(self, obj):
        if obj.actual_return_date:
            return "Already returned!"
        url = reverse("admin:borrowing_return", args=[obj.pk])
        return format_html('<a class="button" href="{}">Return</a>', url)

    return_button.short_description = "Return"

    def delete_model(self, request, obj):
        if not obj.actual_return_date:
            obj.book.inventory += 1
            obj.book.save()
        super().delete_model(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.book.inventory -= 1
            obj.book.save()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return Borrowing.objects.select_related("user", "book")

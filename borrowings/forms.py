from django import forms
from django.core.exceptions import ValidationError

from .models import Borrowing


class BorrowingAdminForm(forms.ModelForm):
    class Meta:
        model = Borrowing
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get("book")

        if book and book.inventory <= 0:
            raise ValidationError("No copies available for borrowing")

        return cleaned_data

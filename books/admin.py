from django.contrib import admin

from borrowings.models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass

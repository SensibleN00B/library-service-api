import django_filters

from borrowings.models import Borrowing


class BorrowingFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(method="filter_is_active")
    user_id = django_filters.NumberFilter(field_name="user__id")

    class Meta:
        model = Borrowing
        fields = ["user_id", "is_active"]

    @staticmethod
    def filter_is_active(queryset, value):
        if value:
            return queryset.filter(actual_return_date__isnull=True)
        else:
            return queryset.filter(actual_return_date__isnull=False)

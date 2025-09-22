from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from library.models import Book, Borrowing
from library.serializers import (
    BookListSerializer,
    BookSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
    BorrowingSerializer,
)
from utils.mixins import BaseViewSetMethodMixin
from payment.models import Payment
from payment.payment_service.stripe_service import StripePayment


class BookViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer

    action_serializers = {
        "list": BookListSerializer,
    }

    action_permissions = {
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "partial_update": [IsAdminUser],
        "destroy": [IsAdminUser],
    }


class BorrowingViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        user_id = self.request.query_params.get("user_id")
        if user.is_staff and user_id:
            queryset = queryset.filter(user__id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "return_book_action":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        borrowing = serializer.save()

        book_title = f"{borrowing.book.title} by {borrowing.book.author}"
        days_of_use = (borrowing.expected_return_date - borrowing.borrow_date).days
        money_to_pay = borrowing.book.daily_fee * days_of_use

        with transaction.atomic():
            payment = Payment.objects.create(
                borrowing=borrowing,
                money_to_pay=money_to_pay,
            )

            stripe_payment = StripePayment()
            session = stripe_payment.create_session(self.request, {
                "book_title": book_title,
                "money_to_pay": money_to_pay,
                "payment": payment.id,
            })

            payment.session_id = session.id
            payment.session_url = session.url
            payment.save()

    @action(methods=["POST"], url_path="return", detail=True)
    def return_book_action(self, request, pk=None):
        borrowing = self.get_object()

        try:
            borrowing.return_book()
        except ValidationError as error:
            return Response(
                {"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"status": "book_returned"}, status=status.HTTP_200_OK)

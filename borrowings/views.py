from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.filters import BorrowingFilter
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
    BorrowingSerializer,
)
from payments.models import Payment
from payments.payment_service.stripe_service import StripePayment


@extend_schema_view(
    list=extend_schema(
        summary="List borrowings",
        description="Get a list of all borrowings. "
        "For a regular user, only their own borrowings are returned. "
        "Staff can filter by user_id and is_active.",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="User ID (available for staff only).",
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter borrowings by activity status "
                "(true/false).",
            ),
        ],
        responses={200: BorrowingSerializer},
    ),
    retrieve=extend_schema(
        summary="Retrieve borrowing",
        description="Get detailed information about a specific"
        "borrowing by its ID.",
        responses={200: BorrowingSerializer},
    ),
    create=extend_schema(
        summary="Create borrowing",
        description="Create a new borrowing. "
        "A user can borrow a book if it is available.",
        request=BorrowingCreateSerializer,
        responses={
            201: BorrowingSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    ),
)
class BorrowingViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = BorrowingFilter

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "return_book_action":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        borrowing = serializer.save()
        days_of_use = (
            borrowing.expected_return_date - borrowing.borrow_date
        ).days
        money_to_pay = borrowing.book.daily_fee * days_of_use

        stripe_payment = StripePayment()

        with transaction.atomic():
            stripe_payment.create_payment(
                request=self.request,
                borrowing=borrowing,
                money_to_pay=money_to_pay,
                payment_type=Payment.Type.payment,
            )

    @extend_schema(
        summary="Return a book",
        description="Marks a borrowing as returned. "
        "If the book has already been returned or other business "
        "constraints apply - an error is raised.",
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Successful return",
                        value={"status": "book_returned"},
                    ),
                ],
                description="The book was successfully returned.",
            ),
            400: OpenApiResponse(
                description="Error: the book is already returned or "
                "another business rule was violated.",
                examples=[
                    OpenApiExample(
                        "Return error",
                        value={
                            "detail": "This book has already been returned."
                        },
                    ),
                ],
            ),
        },
    )
    @action(methods=["POST"], url_path="return", detail=True)
    def return_book_action(self, request, pk=None):
        borrowing = self.get_object()

        try:
            overdue = borrowing.return_book()
        except ValidationError as error:
            return Response(
                {"detail": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        if overdue > 0:
            stripe_payment = StripePayment()
            money_to_pay = (
                overdue
                * borrowing.book.daily_fee
                * Decimal(str(settings.FINE_MULTIPLIER))
            )

            with transaction.atomic():
                payment = stripe_payment.create_payment(
                    request=self.request,
                    borrowing=borrowing,
                    money_to_pay=money_to_pay,
                    payment_type=Payment.Type.fine,
                )

                return Response(
                    {
                        "detail": "Book overdue, fine payments required",
                        "type": payment.type,
                        "status": payment.status,
                        "days_of_overdue": overdue,
                        "money_to_pay": payment.money_to_pay,
                        "session_url": payment.session_url,
                    },
                    status=status.HTTP_200_OK,
                )

        return Response({"status": "book_returned"}, status=status.HTTP_200_OK)

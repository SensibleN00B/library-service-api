from rest_framework import serializers

from payment.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "borrowing",
            "money_to_pay",
            "status",
            "session_url",
            "session_id"
    )


class PaymentBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "type",
            "money_to_pay",
            "status",
            "session_url",
    )



class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "borrowing",
            "money_to_pay",
            "status",
            "session_url",
            "session_id"
    )

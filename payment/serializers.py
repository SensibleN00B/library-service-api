from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "borrowing",
            "fine_days",
            "money_to_pay",
            "session_url",
            "session_id"
    )


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "borrowing",
            "fine_days",
            "session_url",
            "session_id"
    )

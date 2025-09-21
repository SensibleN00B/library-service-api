from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "status",
            "borrowing",
            "money_to_pay",
            "session_url",
            "session_id"
    )


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "status",
            "borrowing",
            "money_to_pay",
            "session_url",
            "session_id"
    )

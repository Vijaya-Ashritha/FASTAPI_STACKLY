from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(
    serializers.ModelSerializer
):

    card_last_four = serializers.CharField(
        source="card.last_four",
        read_only=True,
    )

    class Meta:

        model = Transaction

        fields = [
            "id",
            "reference",
            "card",
            "card_last_four",
            "amount",
            "status",
            "description",
            "created_at",
            "updated_at",
        ]
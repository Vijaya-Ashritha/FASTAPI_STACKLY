from rest_framework import serializers

from .models import Card


class CardCreateSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(
        write_only=True,
        min_length=13,
        max_length=19,
    )

    class Meta:
        model = Card
        fields = [
            "id",
            "card_type",
            "card_holder_name",
            "card_number",
            "masked_card",
            "last_four",
            "created_at",
        ]
        read_only_fields = [
            "masked_card",
            "last_four",
            "created_at",
        ]

    def validate_card_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Card number must contain digits only."
            )

        if len(value) < 13 or len(value) > 19:
            raise serializers.ValidationError(
                "Card number must contain 13 to 19 digits."
            )

        return value

    def create(self, validated_data):
        card_number = validated_data.pop("card_number")

        last_four = card_number[-4:]

        masked_card = "*" * (len(card_number) - 4) + last_four

        card = Card.objects.create(
            user=self.context["request"].user,
            masked_card=masked_card,
            last_four=last_four,
            **validated_data,
        )

        return card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            "id",
            "card_type",
            "card_holder_name",
            "masked_card",
            "last_four",
            "created_at",
        ]
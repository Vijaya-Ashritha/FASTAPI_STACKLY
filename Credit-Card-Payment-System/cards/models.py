from django.conf import settings
from django.db import models

class Card(models.Model):

    CARD_TYPES = [
        ("CREDIT", "credit"),
        ("DEBIT", "debit")
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cards"
    )

    card_type = models.CharField(
        max_length=10,
        choices=CARD_TYPES,
    )

    card_holder_name = models.CharField(
        max_length=25
    )

    masked_card = models.CharField(
        max_length=25
    )

    last_four = models.CharField(
        max_length=4
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):

        return(
            f"{self.card_type}"
            f"****{self.last_four}"
        )
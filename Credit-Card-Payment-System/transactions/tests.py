from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework.test import APITestCase

from cards.models import Card

from .models import Transaction


class AuthenticationTests(APITestCase):

    def test_register(self):

        response = self.client.post(
            reverse("register"),
            {
                "username": "vijaya",
                "email": "vijaya@gmail.com",
                "password": "StrongPass123!",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertTrue(
            User.objects.filter(
                username="vijaya"
            ).exists()
        )


class CardTests(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="user1",
            password="StrongPass123!",
        )

        self.client.force_authenticate(
            user=self.user
        )

    def test_card_is_masked(self):

        response = self.client.post(
            "/api/cards/",
            {
                "card_type": "CREDIT",
                "card_holder_name": (
                    "Vijaya Ashritha"
                ),
                "card_number": (
                    "4111111111111111"
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            response.data["last_four"],
            "1111",
        )

        self.assertNotIn(
            "4111111111111111",
            str(response.data),
        )


class PaymentTransactionTests(
    APITestCase
):

    def setUp(self):

        self.user = User.objects.create_user(
            username="user2",
            password="StrongPass123!",
        )

        self.card = Card.objects.create(
            user=self.user,
            card_type="DEBIT",
            card_holder_name="Test User",
            masked_card="************1111",
            last_four="1111",
        )

    def test_pending_transaction(self):

        transaction = (
            Transaction.objects.create(
                user=self.user,
                card=self.card,
                amount=Decimal("100.00"),
                reference="TEST-001",
            )
        )

        self.assertEqual(
            transaction.status,
            "PENDING",
        )
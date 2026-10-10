from rest_framework import generics

from .models import Card
from .serializers import CardCreateSerializer, CardSerializer


class CardListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        return Card.objects.filter(
            user=self.request.user
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CardCreateSerializer

        return CardSerializer


class CardDeleteView(generics.DestroyAPIView):
    serializer_class = CardSerializer

    def get_queryset(self):
        return Card.objects.filter(
            user=self.request.user
        )
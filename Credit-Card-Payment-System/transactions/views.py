from django.utils.dateparse import parse_date

from rest_framework import generics

from .models import Transaction

from .serializers import TransactionSerializer


class TransactionListView(
    generics.ListAPIView
):

    serializer_class = TransactionSerializer

    def get_queryset(self):

        queryset = Transaction.objects.filter(
            user=self.request.user
        )

        status = self.request.query_params.get(
            "status"
        )

        min_amount = (
            self.request.query_params.get(
                "min_amount"
            )
        )

        max_amount = (
            self.request.query_params.get(
                "max_amount"
            )
        )

        from_date = (
            self.request.query_params.get(
                "from_date"
            )
        )

        to_date = (
            self.request.query_params.get(
                "to_date"
            )
        )

        if status:

            queryset = queryset.filter(
                status=status.upper()
            )

        if min_amount:

            queryset = queryset.filter(
                amount__gte=min_amount
            )

        if max_amount:

            queryset = queryset.filter(
                amount__lte=max_amount
            )

        if from_date:

            parsed_from_date = parse_date(
                from_date
            )

            if parsed_from_date:

                queryset = queryset.filter(
                    created_at__date__gte=(
                        parsed_from_date
                    )
                )

        if to_date:

            parsed_to_date = parse_date(
                to_date
            )

            if parsed_to_date:

                queryset = queryset.filter(
                    created_at__date__lte=(
                        parsed_to_date
                    )
                )

        return queryset


class TransactionDetailView(
    generics.RetrieveAPIView
):

    serializer_class = TransactionSerializer

    def get_queryset(self):

        return Transaction.objects.filter(
            user=self.request.user
        )
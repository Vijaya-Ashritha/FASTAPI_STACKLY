import csv

from django.contrib import admin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils import timezone

from .models import AdminLog, Transaction


@admin.action(
    description="Export selected transactions to CSV"
)
def export_transactions_csv(
    modeladmin,
    request,
    queryset,
):

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = (
        'attachment; '
        'filename="transactions.csv"'
    )

    writer = csv.writer(response)

    writer.writerow(
        [
            "Reference",
            "User",
            "Amount",
            "Status",
            "Card",
            "Created At",
        ]
    )

    transactions = queryset.select_related(
        "user",
        "card",
    )

    for transaction in transactions:

        writer.writerow(
            [
                transaction.reference,
                transaction.user.username,
                transaction.amount,
                transaction.status,
                f"****{transaction.card.last_four}",
                transaction.created_at,
            ]
        )

    return response


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = [
        "reference",
        "user",
        "amount",
        "status",
        "card",
        "created_at",
    ]

    list_filter = [
        "status",
        "created_at",
    ]

    search_fields = [
        "reference",
        "user__username",
    ]

    actions = [
        export_transactions_csv
    ]

    change_list_template = (
        "admin/transactions/"
        "transaction/change_list.html"
    )

    def changelist_view(
        self,
        request,
        extra_context=None,
    ):

        today = timezone.localdate()

        summary = (
            Transaction.objects
            .filter(
                created_at__date=today
            )
            .aggregate(
                count=Count("id"),
                total=Sum("amount"),
            )
        )

        extra_context = extra_context or {}

        extra_context[
            "daily_payment_summary"
        ] = summary

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):

    list_display = [
        "admin",
        "action",
        "created_at",
    ]

    search_fields = [
        "admin__username",
        "action",
        "details",
    ]

    readonly_fields = [
        "created_at"
    ]

import logging

from app.services.notification_service import (
    send_registration_confirmation,
    send_low_stock_alert,
    send_inventory_operation_notification,
)


logger = logging.getLogger(__name__)


def run_registration_email(username: str, email: str) -> None:
    try:
        send_registration_confirmation(username, email)
    except Exception:
        logger.exception(
            "Registration email failed for user %s",
            email,
        )


def run_low_stock_email(
    product_name: str,
    stock_quantity: int,
    reorder_level: int,
) -> None:
    try:
        send_low_stock_alert(
            product_name,
            stock_quantity,
            reorder_level,
        )
    except Exception:
        logger.exception(
            "Low-stock email failed for product %s",
            product_name,
        )


def run_inventory_operation_email(
    operation: str,
    product_name: str,
    stock_quantity: int,
) -> None:
    try:
        send_inventory_operation_notification(
            operation,
            product_name,
            stock_quantity,
        )
    except Exception:
        logger.exception(
            "Inventory operation email failed for %s",
            product_name,
        )

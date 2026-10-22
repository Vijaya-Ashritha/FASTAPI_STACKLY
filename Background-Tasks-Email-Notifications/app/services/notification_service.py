
from app.core.config import settings
from app.services.email_service import send_email


def send_registration_confirmation(
    username: str,
    email: str,
) -> None:
    subject = "Registration Successful"

    body = (
        f"Hello {username},\n\n"
        "Your registration was successful.\n"
        "Thank you for registering with our application.\n\n"
        "You can now use your registered account.\n"
    )

    send_email(email, subject, body)


def send_low_stock_alert(
    product_name: str,
    stock_quantity: int,
    reorder_level: int,
) -> None:
    subject = f"Low Stock Alert: {product_name}"

    body = (
        "Inventory Stock Alert\n\n"
        f"Product: {product_name}\n"
        f"Current stock quantity: {stock_quantity}\n"
        f"Reorder level: {reorder_level}\n\n"
        "Please review the stock and arrange replenishment "
        "if necessary."
    )

    send_email(settings.admin_email, subject, body)


def send_inventory_operation_notification(
    operation: str,
    product_name: str,
    stock_quantity: int,
) -> None:
    subject = f"Inventory Operation: {operation}"

    body = (
        "An inventory operation was completed.\n\n"
        f"Operation: {operation}\n"
        f"Product: {product_name}\n"
        f"Current stock quantity: {stock_quantity}\n"
    )

    send_email(settings.admin_email, subject, body)

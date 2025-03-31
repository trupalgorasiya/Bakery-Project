# your_app/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_status_update_email(custom_order):
    """Send an email notification when order status changes."""
    subject = f"Order #{custom_order.id} Status Update"
    message = generate_status_message(custom_order)  # Get a structured message with status and pickup time

    send_mail(
        subject,
        "Your email client does not support HTML emails.",  # Fallback for non-HTML clients
        settings.DEFAULT_FROM_EMAIL,
        [custom_order.user.email_id],
        html_message=message  # Send well-formatted HTML email
    )

def generate_status_message(custom_order):
    """Generate an email with only the status and pickup time."""
    status_messages = {
        "ordered": "Your order has been successfully placed!",
        "accepted": "Great news! Your order has been accepted by our team.",
        "declined": "Unfortunately, your order has been declined. Please contact support for more details.",
        "processing": "Your cake is being prepared with love! We’ll notify you when it’s ready.",
        "ready": "Your order is ready for pickup! Please visit our store at your scheduled time.",
        "completed": "Your order has been successfully completed. We hope you enjoy your cake! 🎂",
        "cancelled": "Your order has been cancelled. If you have any concerns, feel free to reach out.",
    }

    status_message = status_messages.get(custom_order.status, "Your order status has been updated.")

    # Email body in HTML format with only status and pickup time
    message = f"""
    <html>
        <body>
            <h2 style="color: #d63384;">Hello {custom_order.user.first_name},</h2>
            <p>{status_message}</p>

            <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th style="background-color: #d63384; color: white;">Order Number</th>
                    <td>{custom_order.id}</td>
                </tr>
                <tr>
                    <th style="background-color: #d63384; color: white;">Pickup Time</th>
                    <td>{custom_order.pickup_time}</td>
                </tr>
            </table>

            <p>If you have any questions, feel free to contact us.</p>
            <p style="color: #d63384;"><strong>🎉 Thank you for choosing us! 🎂</strong></p>
        </body>
    </html>
    """
    return message

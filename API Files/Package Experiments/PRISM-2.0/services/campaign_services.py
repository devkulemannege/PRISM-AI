from services.whatsapp_api import send_template
from db.connection import get_db_connection
import time

def send_template_cli(phone, template_name, parameters):
    """Send a template to a single phone via CLI."""
    print(f"Sending template '{template_name}' to {phone} with params: {parameters}")
    send_template(phone, template_name, parameters)


def send_template_to_all(business_id):
    """Send a template message to all customers linked to a specific business."""
    connection = get_db_connection()
    if connection is None:
        print("DB connection failed.")
        return

    cursor = connection.cursor()
    try:
        # Get business details
        cursor.execute("SELECT name FROM business WHERE businessId = %s", (business_id,))
        business = cursor.fetchone()
        if not business:
            print(f"No business found with ID {business_id}")
            return
        business_name = business[0]

        # Get customers linked to the business
        cursor.execute("""
            SELECT c.fName, c.mobileNo
            FROM customer c
            JOIN customer_business cb ON c.customerId = cb.customerId
            WHERE cb.businessId = %s
        """, (business_id,))
        customers = cursor.fetchall()

        if not customers:
            print(f"No customers found for business ID {business_id}")
            return

        # Send template to each customer
        for name, number in customers:
            if not number.startswith('+'):
                if number.startswith('0'):
                    number = number[1:]
                number = f"+94{number}"
            print(f"Sending to {name} ({number})")

            params = [
                {"type": "text", "text": name},
                {"type": "text", "text": business_name},
                {"type": "text", "text": "Special offer just for you!"},
                {"type": "text", "text": "Visit us today"}
            ]
            send_template(number, "promo_offer", params)
            time.sleep(1)  # avoid rate limits

    except Exception as e:
        print(f"Error during campaign send: {e}")
    finally:
        cursor.close()
        connection.close()

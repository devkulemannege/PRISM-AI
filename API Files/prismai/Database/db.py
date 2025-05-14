import mysql.connector
from mysql.connector import Error

def get_db_connection(config):
    """Create a connection to the MariaDB database."""
    try:
        connection = mysql.connector.connect(
            host=config["DB_HOST"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
            database=config["DB_NAME"]
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def save_conversation(config, phone, user_msg, ai_reply):
    """Save the conversation to the database."""
    connection = get_db_connection(config)
    if connection is None:
        return
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO chats (phone, user_msg, ai_reply) VALUES (%s, %s, %s)",
            (phone, user_msg, ai_reply)
        )
        connection.commit()
    except Error as e:
        print(f"Error saving conversation: {e}")
    finally:
        cursor.close()
        connection.close()

def fetch_customer_data(config, template_name, customer_id=1, business_id=1):
    """Fetch customer, business, and product data for sending templates."""
    connection = get_db_connection(config)
    if connection is None:
        return None

    cursor = connection.cursor()
    try:
        # Fetch customer
        cursor.execute("SELECT fName, mobileNo FROM customer WHERE customerId = %s", (customer_id,))
        customer_row = cursor.fetchone()
        if not customer_row:
            print(f"No customer found with customerId = {customer_id}, aborting...")
            return None

        customer_name, customer_phone = customer_row
        if not customer_phone:
            print(f"Customer with customerId = {customer_id} has no phone number, aborting...")
            return None

        # Format phone number
        if not customer_phone.startswith('+'):
            if customer_phone.startswith('0'):
                customer_phone = customer_phone[1:]
            customer_phone = f"+94{customer_phone}"

        # Fetch business
        cursor.execute("SELECT businessId, name FROM business WHERE businessId = %s", (business_id,))
        business_row = cursor.fetchone()
        if not business_row:
            print(f"No business found with businessId = {business_id}, aborting...")
            return None

        business_id, business_name = business_row

        # Fetch products
        cursor.execute("SELECT name, description FROM product WHERE businessId = %s", (business_id,))
        product_rows = cursor.fetchall()
        if not product_rows:
            print(f"No products found for businessId={business_id}, aborting...")
            return None

        # Prepare template data
        template_data = []
        for product_row in product_rows:
            product_name, product_description = product_row
            parameters = [
                {"type": "text", "text": customer_name},
                {"type": "text", "text": business_name},
                {"type": "text", "text": product_description},
                {"type": "text", "text": product_name}
            ]
            template_data.append({
                "phone": customer_phone,
                "template_name": template_name,
                "parameters": parameters
            })

        return template_data
    except Error as e:
        print(f"Error querying database: {e}")
        return None
    finally:
        cursor.close()
        connection.close()
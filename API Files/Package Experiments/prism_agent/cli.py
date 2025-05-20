# Contents of prism_agent/cli.py
import argparse
import sys
import time
from prism_agent.config import Config  # Import Config
from mysql.connector import Error
from prism_agent.whatsapp.whatsapp_api import send_template  # Import send_template
from prism_agent.db.database import get_db_connection #Import get_db_connection

def send_template_cli(phone, template_name, parameters):
    """CLI to Send Template Message"""
    print(f"CLI ACCESS_TOKEN: {Config.ACCESS_TOKEN}") # Import Config
    send_template(phone, template_name, parameters)
    return None

def send_template_to_all(business_id):
    """This funtion is to send template massage to all the customers in a business"""
    connection = get_db_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    try:
        # Check if the business exists and fetch its details
        cursor.execute("SELECT name, template, prompt, template_parameters FROM business WHERE businessId = %s", (business_id,))
        business_row = cursor.fetchone()
        if not business_row:
            print(f"No business found with businessId = {business_id}, aborting...")
            return

        business_name = business_row[0]
        template_name = business_row[1]
        prompt = business_row[2]
        template_params = business_row[3].split(',') if business_row[3] else ['customer_name', 'business_name']
        print(f"Business details: businessId={business_id}, name={business_name}, template={template_name}, prompt={prompt}, params={template_params}")

        if not template_name:
            print(f"No template specified for businessId = {business_id}, aborting...")
            return

        # Fetch all customers associated with the business
        cursor.execute("""
            SELECT c.customerId, c.fName, c.mobileNo
            FROM customer c
            JOIN customer_business cb ON c.customerId = cb.customerId
            WHERE cb.businessId = %s
        """, (business_id,))
        customers = cursor.fetchall()
        print(f"Found {len(customers)} customers associated with businessId={business_id}")

        if not customers:
            print(f"No customers found for businessId = {business_id}, aborting...")
            return

        # For each customer, send the template message
        for customer_row in customers:
            customer_id = customer_row[0]
            customer_name = customer_row[1]
            customer_phone = customer_row[2]
            print(f"Processing customer: customerId={customer_id}, name={customer_name}, phone={customer_phone}")

            if not customer_phone:
                print(f"Customer with customerId = {customer_id} has no phone number, skipping...")
                continue

            # Format the customer's phone number
            if not customer_phone.startswith('+'):
                if customer_phone.startswith('0'):
                    customer_phone = customer_phone[1:]
                customer_phone = f"+94{customer_phone}"
            print(f"Formatted customer phone: {customer_phone}")

            # Prepare dynamic parameters based on template_parameters
            parameters = []
            if 'customer_name' in template_params:
                parameters.append({"type": "text", "text": customer_name})
            if 'business_name' in template_params:
                parameters.append({"type": "text", "text": business_name})
            if 'description' in template_params or 'product_name' in template_params:
                cursor.execute("SELECT description, name FROM product WHERE businessId = %s LIMIT 1", (business_id,))
                product_row = cursor.fetchone()
                if product_row and 'description' in template_params:
                    parameters.append({"type": "text", "text": product_row[0]})
                if product_row and 'product_name' in template_params:
                    parameters.append({"type": "text", "text": product_row[1]})

            print(f"Sending template {template_name} to {customer_phone} with parameters {parameters}")
            send_template(customer_phone, template_name, parameters)
            time.sleep(1)
    except Error as e:
        print(f"Error querying database: {e}")
        raise
    finally:
        cursor.close()
        connection.close()
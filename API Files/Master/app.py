#Imports neccessary libraries for online dashnoard
from flask import Flask, render_template, request, redirect, url_for, session
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database')))
from connect_db import get_db_connection
from werkzeug.utils import secure_filename

#Imports to run the agent
from dotenv import load_dotenv
import os
import requests
import mysql.connector
from mysql.connector import Error
from chatlog_table import addRow
from connect_db import get_db_connection
import time
import argparse
import sys
import threading
from flask import Flask, request
from llm_chain import initialize_llm_chain, call_llm_with_chain

# Load environment variables
load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "credentials.env")))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
print(f"Loaded ACCESS_TOKEN: {ACCESS_TOKEN}")
print(f"Loaded PHONE_NUMBER_ID: {PHONE_NUMBER_ID}")

##################################################################################################################33
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database get_db_connection
# (No need to redefine get_db_connection if imported)

# Home redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        business_type = request.form['type']
        password = request.form['password']

        conn, cur = get_db_connection()

        business_id = random.randint(1000000, 9999999)
        cur.execute("SELECT businessId FROM business")
        existing_ids = [row[0] for row in cur.fetchall()]
        while business_id in existing_ids:
            business_id = random.randint(1000000, 9999999)

        agent_status = 0

        cur.execute(
            "INSERT INTO business (businessId, name, contact, type, agentStatus, password) VALUES (%s, %s, %s, %s, %s, %s)",
            (business_id, name, contact, business_type, agent_status, password)
        )

        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        conn, cur = get_db_connection()
        cur.execute("SELECT * FROM business WHERE name=%s AND password=%s", (name, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['name'] = user[1]  # user[1] is name
            return redirect(url_for('dashboard'))
        else:
            return "Login Failed. Invalid credentials."

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('name', None)
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'name' in session:
        conn, cur = get_db_connection()
        # Get businessId for the logged-in user
        cur.execute("SELECT businessId FROM business WHERE name=%s", (session['name'],))
        business_id_row = cur.fetchone()
        campaigns = []
        if business_id_row:
            business_id = business_id_row[0]
            # Fetch all campaigns for this business
            cur.execute("SELECT * FROM campaign WHERE businessId=%s ORDER BY campaignId DESC", (business_id,))
            columns = [desc[0] for desc in cur.description]
            for row in cur.fetchall():
                campaigns.append(dict(zip(columns, row)))
        cur.close()  # <-- Fix: close the cursor, not the connection
        conn.close()
        return render_template('dashboard.html', name=session['name'], campaigns=campaigns)
    else:
        return redirect(url_for('login'))

# === PRODUCT GENERATION FUNCTIONALITY ===

# Show product input form
@app.route('/product')
def product_form():
    if 'name' not in session:
        return redirect(url_for('login'))
    return render_template('product.html')

# Handle form submission and generate the marketing prompt
@app.route('/generate', methods=['POST'])
def generate_prompt():
    if 'name' not in session:
        return redirect(url_for('login'))

    # Get all form fields
    product_name = request.form['product_name']
    target_problem = request.form['target_problem']
    target_audience = request.form['target_audience']
    unique_solution = request.form['unique_solution']
    reason_why_needed = request.form['reason_why_needed']
    main_benefits = request.form['main_benefits']
    social_proof = request.form['social_proof']
    price = request.form['price']
    offer = request.form['offer']
    urgency = request.form['urgency']
    cta = request.form['cta']
    product_type = request.form['product_type']

    # Prompt templates for each product type
    recurrent_prompt = f"""Hey, PRISM AI here! {target_problem} is a challenge every {target_audience} faces, day in and day out. That's why we created {product_name}—a solution designed for ongoing value. With {unique_solution}, you'll never have to worry about {target_problem} again. Now is the perfect time: {reason_why_needed}. Enjoy continuous benefits like {main_benefits}. See what others say: {social_proof}. Normally {price}, but now {offer}. {urgency} Don't miss out on a better future—{cta}"""

    one_time_prompt = f"""PRISM AI presents: {product_name}! If you've ever struggled with {target_problem}, you're not alone. {product_name} is a one-time breakthrough for {target_audience}, offering {unique_solution}. Why now? {reason_why_needed}. Key benefits: {main_benefits}. Hear from our users: {social_proof}. Usual price: {price}, special offer: {offer}. {urgency} Act fast—{cta}"""

    # Choose prompt based on product type
    if product_type == "Recurrent Selling Product":
        prompt = recurrent_prompt
    else:
        prompt = one_time_prompt

    # Save campaign to database (add ProductType column)
    conn, cur = get_db_connection()
    cur.execute("SELECT businessId FROM business WHERE name=%s", (session['name'],))
    business_id_row = cur.fetchone()
    if business_id_row:
        business_id = business_id_row[0]
        cur.execute("""
            INSERT INTO campaign (businessId, campaignName, prompt, template, parameters, targetProblem, targetAudience, uniqueSolution, whyNeeded, mainBenefits, socialProof, price, offer, urgency, cta, ProductType)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            business_id,
            product_name,
            prompt,
            '', '',
            target_problem,
            target_audience,
            unique_solution,
            reason_why_needed,
            main_benefits,
            social_proof,
            price,
            offer,
            urgency,
            cta,
            product_type
        ))
        conn.commit()
    conn.close()

    # Redirect to customer upload page after product submission
    return redirect(url_for('customer_upload'))

# === CUSTOMER UPLOAD FUNCTIONALITY ===

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'CustomerUpload')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Customer CSV upload
@app.route('/customer-upload', methods=['GET', 'POST'])
def customer_upload():
    if 'name' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if file and file.filename.endswith('.csv'):
            # Get business name and latest campaignId
            conn, cur = get_db_connection()
            cur.execute("SELECT businessId FROM business WHERE name=%s", (session['name'],))
            business_id_row = cur.fetchone()
            business_id = business_id_row[0] if business_id_row else 'unknown'
            cur.execute("SELECT campaignId FROM campaign WHERE businessId=%s ORDER BY campaignId DESC LIMIT 1", (business_id,))
            campaign_id_row = cur.fetchone()
            campaign_id = campaign_id_row[0] if campaign_id_row else 'unknown'
            # Create filename: businessname_campaignid.csv
            safe_business = secure_filename(session['name'])
            filename = f"{safe_business}_{campaign_id}.csv"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            conn.close()
            # Render upload page with continue button
            return render_template('CustomerUpload.html', uploaded_file=save_path, campaign_id=campaign_id)
        else:
            return "Invalid file type. Please upload a CSV file."
    return render_template('CustomerUpload.html', uploaded_file=None, campaign_id=None)

# Route to process the uploaded CSV and link customers to campaign
@app.route('/process-customer-upload', methods=['POST'])
def process_customer_upload():
    import importlib.util
    import sys
    ml_dir = os.path.join(os.path.dirname(__file__), 'File Reader', 'File Reader with ML')
    if ml_dir not in sys.path:
        sys.path.insert(0, ml_dir)
    ml_path = os.path.join(ml_dir, 'read_file.py')
    spec = importlib.util.spec_from_file_location('ml_read_file', ml_path)
    ml_read_file = importlib.util.module_from_spec(spec)
    sys.modules['ml_read_file'] = ml_read_file
    spec.loader.exec_module(ml_read_file)
    file_path = request.form.get('file_path')
    campaign_id = request.form.get('campaign_id')
    if file_path and campaign_id:
        ml_read_file.readData.campaignId = int(campaign_id)
        ml_read_file.readData(file_path)
        return render_template('success.html')
    return "Missing file path or campaign ID."

# Profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'name' not in session:
        return redirect(url_for('login'))
    conn, cur = get_db_connection()
    # Fetch businessId for the logged-in user
    cur.execute("SELECT businessId FROM business WHERE name=%s", (session['name'],))
    business_id_row = cur.fetchone()
    business_id = business_id_row[0] if business_id_row else None
    # Fetch customer row for this business (assuming 1:1 business-customer for profile)
    cur.execute("SELECT * FROM customer WHERE campaignId IN (SELECT campaignId FROM campaign WHERE businessId=%s) ORDER BY customerId DESC LIMIT 1", (business_id,))
    customer = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    customer_dict = dict(zip(columns, customer)) if customer else None
    profile_pic_url = url_for('static', filename='profile.png')
    if customer_dict and customer_dict.get('profile_pic'):
        profile_pic_url = url_for('static', filename='profile_pics/' + customer_dict['profile_pic'])
    if request.method == 'POST':
        file = request.files.get('profile_pic')
        if file and file.filename:
            filename = secure_filename(file.filename)
            pic_folder = os.path.join(app.static_folder, 'profile_pics')
            if not os.path.exists(pic_folder):
                os.makedirs(pic_folder)
            file.save(os.path.join(pic_folder, filename))
            # Save filename in DB
            cur.execute("UPDATE customer SET profile_pic=%s WHERE customerId=%s", (filename, customer_dict['customerId']))
            conn.commit()
            profile_pic_url = url_for('static', filename='profile_pics/' + filename)
    conn.close()
    return render_template('profile.html', profile_pic_url=profile_pic_url, customer=customer_dict)

@app.route('/campaign')
def campaign():
    if 'name' not in session:
        return redirect(url_for('login'))
    conn, cur = get_db_connection()
    # Get businessId for the logged-in user
    cur.execute("SELECT businessId FROM business WHERE name=%s", (session['name'],))
    business_id_row = cur.fetchone()
    campaigns = []
    if business_id_row:
        business_id = business_id_row[0]
        # Fetch all campaigns for this business
        cur.execute("SELECT * FROM campaign WHERE businessId=%s ORDER BY campaignId DESC", (business_id,))
        columns = [desc[0] for desc in cur.description]
        for row in cur.fetchall():
            campaigns.append(dict(zip(columns, row)))
    conn.close()
    return render_template('campaign.html', name=session['name'], campaigns=campaigns)

@app.route('/leads')
def leads():
    if 'name' not in session:
        return redirect(url_for('login'))
    return render_template('leads.html')

@app.route('/sales')
def sales():
    if 'name' not in session:
        return redirect(url_for('login'))
    return render_template('sales.html')

@app.route('/agent')
def agent():
    if 'name' not in session:
        return redirect(url_for('login'))
    return render_template('agent.html')

def send_whatsapp_message(phone, msg):
    """Send a free-form message to a WhatsApp number."""
    if not isinstance(msg, str):
        raise ValueError(f"Expected string for msg, got {type(msg)}: {msg}")
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": msg}
    }
    res = requests.post(url, headers=headers, json=payload)
    print(f"WhatsApp API Response (free-form): {res.json()}")
    return res.json()

# WhatsApp - Send Template Message
def send_template(phone, template_name, parameters=None):
    """Send a template message to a WhatsApp number."""
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    if parameters is None:
        parameters = []
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": parameters
                }
            ]
        }
    }
    print(f"Sending request with headers: {headers}")
    print(f"Sending request with payload: {payload}")
    res = requests.post(url, headers=headers, json=payload)
    print(f"WhatsApp API Response for {phone}: {res.json()}")
    return res.json()

def send_template_to_all(campaign_id):
    """This function is to send template messages to all the customers in a campaign"""
    connection, cursor = get_db_connection()
    if connection is None:
        print("Failed to connect to database")
        return

    try:
        # Check if the campaign exists and fetch its details
        cursor.execute("SELECT * FROM campaign WHERE campaignId = %s", (campaign_id,))
        business_row = cursor.fetchone()
        if not business_row:
            print(f"No campaign found with campaignId = {campaign_id}, aborting...")
            return

        campaign_name = business_row[2]
        template_name = business_row[4]
        prompt = business_row[3]
        template_params = business_row[5].split(',') if business_row[5] else ['customer_name', 'campaign_name']
        print(f"Campaign details: campaignId={campaign_id}, name={campaign_name}, template={template_name}, prompt={prompt}, params={template_params}")

        if not template_name:
            print(f"No template specified for campaignId = {campaign_id}, aborting...")
            return

        # Fetch all customers associated with the campaign
        cursor.execute("""
            SELECT customerId, fName, mobileNo
            FROM customer 
            WHERE campaignId = %s
        """, (campaign_id,))
        customers = cursor.fetchall()
        print(f"Found {len(customers)} customers associated with campaignId={campaign_id}")

        if not customers:
            print(f"No customers found for campaignId = {campaign_id}, aborting...")
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
            if customer_phone.startswith('0'):
                customer_phone = customer_phone[1:]
            customer_phone = f"+94{customer_phone}"
            print(f"Formatted customer phone: {customer_phone}")

            # Prepare dynamic parameters based on template_parameters
            parameters = []
            if 'customer_name' in template_params:
                parameters.append({"type": "text", "text": customer_name})
            if 'business_name' in template_params:
                parameters.append({"type": "text", "text": campaign_name})
            if 'description' in template_params or 'product_name' in template_params:
                cursor.execute("SELECT offer, campaignName FROM campaign WHERE campaignId = %s LIMIT 1", (campaign_id,))
                product_row = cursor.fetchone()
                if product_row and 'description' in template_params:
                    parameters.append({"type": "text", "text": product_row[0]})
                if product_row and 'product_name' in template_params:
                    parameters.append({"type": "text", "text": product_row[1]})

            print(f"Sending template {template_name} to {customer_phone} with parameters {parameters}")
            print(f"Template expects {len(parameters)} parameters: {parameters}")
            response = send_template(customer_phone, template_name, parameters)
            if 'error' in response:
                print(f"Failed to send template to {customer_phone}: {response['error']}")
            time.sleep(1)
    except Error as e:
        print(f"Error querying database: {e}")
        raise
    finally:
        cursor.close()
        connection.close()
    
# CLI to Send Template Message
def send_template_cli(phone, template_name, parameters):
    print(f"CLI ACCESS_TOKEN: {ACCESS_TOKEN}")
    send_template(phone, template_name, parameters)
    return None

# Webhook Routes
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    print(f"Webhook verification: mode={request.args.get('hub.mode')}, token={token}, challenge={challenge}")
    if token == VERIFY_TOKEN:
        print("Webhook verified successfully")
        return challenge, 200
    else:
        print("Webhook verification failed")
        return "Verification token mismatch", 403
    
@app.route("/webhook", methods=["POST"])
def webhook():
    # Handle incoming messages from WhatsApp
    data = request.json
    print(f"Incoming webhook data: {data}")
    try:
        if "entry" in data and len(data["entry"]) > 0:
            entry = data["entry"][0]
            if "changes" in entry and len(entry["changes"]) > 0:
                change = entry["changes"][0]
                if "value" in change and "messages" in change["value"]:
                    message = change["value"]["messages"][0]
                    sender = message["from"]
                    text = message.get("text", {}).get("body", "No text")
                    print(f"Received message from {sender}: {text}")

                    # Keep original sender for WhatsApp API, format for database
                    db_sender = sender
                    if db_sender.startswith('94') and len(db_sender) == 11:
                        db_sender = '0' + db_sender[2:]
                    print(f"Formatted sender for database: {db_sender}")

                    # Fetch customerId and campaign details
                    connection, cursor = get_db_connection()
                    customer_id = None
                    campaign_id = None
                    if connection and cursor:
                        try:
                            cursor.execute("SELECT customerId FROM customer WHERE mobileNo = %s", (db_sender,))
                            customer_row = cursor.fetchone()
                            if customer_row:
                                customer_id = customer_row[0]
                                # Try to get campaign from customer_campaign, fallback to latest campaign for customer
                                cursor.execute("""
                                    SELECT b.campaignId
                                    FROM campaign b
                                    JOIN customer_campaign cb ON b.campaignId = cb.campaignId
                                    WHERE cb.customerId = %s LIMIT 1
                                """, (customer_id,))
                                campaign_row = cursor.fetchone()
                                if campaign_row:
                                    campaign_id = campaign_row[0]
                                else:
                                    # Fallback: get latest campaign for this customer
                                    cursor.execute("SELECT campaignId FROM customer WHERE customerId = %s ORDER BY campaignId DESC LIMIT 1", (customer_id,))
                                    fallback_row = cursor.fetchone()
                                    if fallback_row:
                                        campaign_id = fallback_row[0]
                        except Error as e:
                            print(f"Database error fetching customer/campaign: {e}")
                        finally:
                            cursor.close()
                            connection.close()

                    # Initialize LangChain conversation
                    print(f"Initialized LangChain conversation for customerId={customer_id}, sender={db_sender}")
                    runnable, customer_name, campaign_name = initialize_llm_chain(customer_id, db_sender)

                    # Generate AI reply using LangChain
                    ai_reply = call_llm_with_chain(runnable, text, customer_name, campaign_name, session_id=customer_id)
                    print(f"AI reply before sending: {repr(ai_reply)}, type: {type(ai_reply)}")  # Debug the reply
                    if not isinstance(ai_reply, str):
                        raise ValueError(f"Expected string for ai_reply, got {type(ai_reply)}: {ai_reply}")
                    send_whatsapp_message(sender, ai_reply)

                    # Save conversation
                    if customer_id and campaign_id:
                        addRow(db_sender, campaign_id, ai_reply, text)
                    else:
                        print("Skipping saving conversation due to missing customer_id or campaign_id")
        else:
            print("Webhook payload missing 'entry' or 'changes' or 'messages'. Data:", data)
    except Exception as e:
        print(f"Webhook Error: {e}")
        import traceback
        traceback.print_exc()  # Print full stack trace
    return "OK", 200

# API Endpoints
@app.route("/send-template", methods=["POST"])
def send_template_route():
    """Send a template message to a WhatsApp number."""
    data = request.json
    phone = data.get("phone")
    template_name = data.get("template_name", "test_template")
    parameters = data.get("parameters", [])
    send_template(phone, template_name, parameters)
    return "Template sent", 200

@app.route("/send-to-all", methods=["POST"])
def send_to_all_route():
    data = request.json
    campaign_id = data.get("campaign_id", 1)
    send_template_to_all(campaign_id)
    return "Templates sent to customers", 200

def run_flask():
    print("Starting Flask app for inbound messaging on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prism AI WhatsApp Bot")
    parser.add_argument(
        "--send-template",
        nargs=2,
        metavar=("PHONE", "TEMPLATE_NAME"),
        help="Send a template message to a phone number (e.g., --send-template +94787555063 retail_template Janith AdoguaLtd '20% off deals in weekends' Bread)"
    )
    parser.add_argument(
        "params",
        nargs='*',
        help="Parameters for the template (e.g., Janith AdoguaLtd '20% off deals in weekends' Bread)"
    )
    parser.add_argument(
        "--send-to-all",
        nargs=1,
        metavar=("BUSINESS_ID"),
        help="Send a template to all customers associated with a campaign (e.g., --send-to-all 1 or --send-to-all 2)"
    )
    args = parser.parse_args()

    if args.send_template:
        phone, template_name = args.send_template
        params = args.params
        if template_name == "retail_template" and len(params) != 4:
            print("Error: retail_template requires exactly 4 parameters (e.g., Janith AdoguaLtd '20% off deals in weekends' Bread)")
            sys.exit(1)
        parameters = [{"type": "text", "text": param} for param in params]
        send_template_cli(phone, template_name, parameters)
    elif args.send_to_all:
        campaign_id = int(args.send_to_all[0])
        send_template_to_all(campaign_id)
    else:
        # Start Flask server in a separate thread
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")


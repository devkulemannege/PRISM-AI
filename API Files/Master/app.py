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
from cluster_visualization import fetch_all_chatlog_msgs, cluster_and_reduce, save_cluster_plot

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

# Home shows index.html
@app.route('/')
def home():
    return render_template('index.html')

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
        business_id = business_id_row[0] if business_id_row else None

        # Default values for all analytics
        total_sales = 0
        total_leads = 0
        total_campaigns = 0
        total_customers = 0
        total_uploads = 0
        active_campaigns = 0
        recent_upload = None
        top_campaign = None
        recent_sale = None
        chart_labels = []
        chart_data = []

        if business_id:
            # Total campaigns
            cur.execute("SELECT COUNT(*) FROM campaign WHERE businessId=%s", (business_id,))
            total_campaigns = cur.fetchone()[0] or 0

            # Total leads (messages from customers)
            cur.execute("SELECT COUNT(*) FROM chatlog WHERE businessId=%s", (business_id,))
            total_leads = cur.fetchone()[0] or 0

            # Total sales (simulate as number of unique customers with a sale, or sum of sales table if exists)
            try:
                cur.execute("SELECT COUNT(DISTINCT customerId) FROM chatlog WHERE businessId=%s AND LLM_msg LIKE '%purchase%'", (business_id,))
                total_sales = cur.fetchone()[0] or 0
            except:
                total_sales = 0

            # Total customers (count distinct customers linked to this business via campaign)
            cur.execute("""
                SELECT COUNT(DISTINCT cu.customerId)
                FROM customer cu
                JOIN campaign ca ON cu.campaignId = ca.campaignId
                WHERE ca.businessId=%s
            """, (business_id,))
            total_customers = cur.fetchone()[0] or 0

            # Total uploads (CSV files in CustomerUpload/)
            upload_dir = os.path.join(os.path.dirname(__file__), 'CustomerUpload')
            if os.path.exists(upload_dir):
                files = [f for f in os.listdir(upload_dir) if f.endswith('.csv')]
                total_uploads = len(files)
                # Recent upload
                if files:
                    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(upload_dir, f)))
                    with open(os.path.join(upload_dir, latest_file), 'r', encoding='utf-8', errors='ignore') as f:
                        row_count = sum(1 for _ in f) - 1  # minus header
                    recent_upload = {'filename': latest_file, 'rows': row_count}
            else:
                total_uploads = 0
                recent_upload = None

            # Active campaigns (now just total campaigns for this business)
            cur.execute("SELECT COUNT(*) FROM campaign WHERE businessId=%s", (business_id,))
            active_campaigns = cur.fetchone()[0] or 0

            # Top campaign (by number of leads)
            cur.execute("""
                SELECT c.campaignName, COUNT(ch.msgId) as leads
                FROM campaign c LEFT JOIN chatlog ch ON c.campaignId = ch.CampaignId
                WHERE c.businessId=%s
                GROUP BY c.campaignId
                ORDER BY leads DESC LIMIT 1
            """, (business_id,))
            row = cur.fetchone()
            if row:
                top_campaign = {'name': row[0], 'leads': row[1]}

            # Recent sale (simulate as latest chatlog with 'purchase' in LLM_msg)
            cur.execute("""
                SELECT ch.LLM_msg, cu.fName FROM chatlog ch
                LEFT JOIN customer cu ON ch.customerId = cu.customerId
                WHERE ch.businessId=%s AND ch.LLM_msg LIKE '%purchase%'
                ORDER BY ch.timestamp DESC LIMIT 1
            """, (business_id,))
            row = cur.fetchone()
            if row:
                recent_sale = {'amount': 'Success', 'customer': row[1] or 'Unknown'}

            # Chart data: sales per campaign (or per month)
            cur.execute("""
                SELECT DATE_FORMAT(ch.timestamp, '%b %Y') as month, COUNT(*) as sales
                FROM chatlog ch
                WHERE ch.businessId=%s AND ch.LLM_msg LIKE '%purchase%'
                GROUP BY month
                ORDER BY MIN(ch.timestamp) ASC
            """, (business_id,))
            chart_rows = cur.fetchall()
            chart_labels = [row[0] for row in chart_rows] if chart_rows else []
            chart_data = [row[1] for row in chart_rows] if chart_rows else []

        # Always return lists for chart_labels and chart_data
        if not chart_labels:
            chart_labels = ["No Data"]
        if not chart_data:
            chart_data = [0]

        cur.close()
        conn.close()
        return render_template(
            'dashboard.html',
            name=session['name'],
            total_sales=total_sales,
            total_leads=total_leads,
            total_campaigns=total_campaigns,
            recent_upload=recent_upload,
            top_campaign=top_campaign,
            recent_sale=recent_sale,
            total_customers=total_customers,
            total_uploads=total_uploads,
            active_campaigns=active_campaigns,
            chart_labels=chart_labels,
            chart_data=chart_data
        )
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
    recurrent_prompt = f"""Act as the world's best AI salesperson to solve the problem  of {target_problem} for {target_audience} by providing {product_name} and specifically {unique_solution} s the unfair advantage and the reason why it needs is {reason_why_needed} also giving high benifits such as {main_benefits} while {social_proof}. So the price selling is {price} but as a special offer giving for {offer}, so {urgency} and {cta}  , using simple, friendly messages (100 words or in 3 sentences) to build trust like a friend. Indirectly promote the product by addressing the target problem and unique solution. If the customer asks about the product directly, provide clear details to drive a sale and share the business contact (website/social). Use paragraphs only when needed. Dont put the thinking process or do not analyse just simple massage output like a sales person would."""

    one_time_prompt = f"""Act as the world's best AI salesperson to solve the problem  of {target_problem} for {target_audience} by providing {product_name} and specifically {unique_solution} s the unfair advantage and the reason why it needs is {reason_why_needed} also giving high benifits such as {main_benefits} while {social_proof}. So the price selling is {price} but as a special offer giving for {offer}, so {urgency} and {cta}  , using simple, friendly messages (100 words or in 3 sentences) to build trust like a friend. Indirectly promote the product by addressing the target problem and unique solution. If the customer asks about the product directly, provide clear details to drive a sale and share the business contact (website/social). Use paragraphs only when needed. Dont put the thinking process or do not analyse just simple massage output like a sales person would"""

    #Choose the massage template and the mass based on user input
    Massage_template="test" #for now
    if Massage_template == "retail":
        template= "retail_template"
        template_parameters="customer_name,business_name,description,product_name"
    elif Massage_template == "PC":
        template = "PC_template"
        template_parameters="customer_name,business_name"
    elif Massage_template == "test":
        template = "test_template"
        template_parameters="customer_name"
    else:
        template = "test_template"
        template_parameters="customer_name"

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
            template, 
            template_parameters,
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

        STORE = "faiss"  # for now, fix typo from 'fiass'
        # Save the campaign details and sales into a vector database

        if STORE == 'faiss':
            # === Add campaign details to vector store FAISS LOCALLY ===
            from faiss_store import add_campaign_to_vector_store
            add_campaign_to_vector_store(
            campaign_id=cur.lastrowid,
            campaign_name=product_name,
            product_type=product_type,
            target_audience=target_audience,
            target_problem=target_problem,
            unique_solution=unique_solution,
            reason_why_needed=reason_why_needed,
            main_benefits=main_benefits,
            social_proof=social_proof,
            price=price,
            offer=offer,
            urgency=urgency,
            cta=cta
       )
        elif STORE == 'qdrant':
            # === Add campaign details to vector store Qdrant ===
            from Qdrant_store import add_campaign_to_vector_store
            add_campaign_to_vector_store(
                campaign_id=cur.lastrowid,
                campaign_name=product_name,
                product_type=product_type,
                target_audience=target_audience,
                target_problem=target_problem,
                unique_solution=unique_solution,
                reason_why_needed=reason_why_needed,
                main_benefits=main_benefits,
                social_proof=social_proof,
                price=price,
                offer=offer,
                urgency=urgency,
                cta=cta
            )
        else:
            print("Invalid vector store option. Please choose 'faiss' or 'qdrant'.")

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
    # Fix: If file_path is None, use the last uploaded file from CustomerUpload
    if not file_path:
        upload_folder = app.config['UPLOAD_FOLDER']
        files = [os.path.join(upload_folder, f) for f in os.listdir(upload_folder) if f.endswith('.csv')]
        if files:
            file_path = max(files, key=os.path.getctime)
    if file_path and campaign_id:
        ml_read_file.readData.campaignId = int(campaign_id)
        # Get businessId for the campaign
        conn, cur = get_db_connection()
        cur.execute("SELECT businessId FROM campaign WHERE campaignId=%s", (campaign_id,))
        business_id_row = cur.fetchone()
        business_id = business_id_row[0] if business_id_row else None
        conn.close()
        ml_read_file.readData(file_path, businessId=business_id)
        send_template_to_all(int(campaign_id))  # Automatically send outbound messages after upload
        return render_template('success.html')
    return "Missing file path or campaign ID."

# Profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'name' not in session:
        return redirect(url_for('login'))
    conn, cur = get_db_connection()
    # Fetch business row for the logged-in user
    cur.execute("SELECT * FROM business WHERE name=%s", (session['name'],))
    business = cur.fetchone()
    columns = [desc[0] for desc in cur.description]
    business_dict = dict(zip(columns, business)) if business else None
    print('DEBUG: business_dict =', business_dict)  # Debug print
    profile_pic_url = url_for('static', filename='profile.png')
    if business_dict and business_dict.get('profile_pic'):
        profile_pic_url = url_for('static', filename='profile_pics/' + business_dict['profile_pic'])
    if request.method == 'POST':
        file = request.files.get('profile_pic')
        if file and file.filename:
            filename = secure_filename(file.filename)
            pic_folder = os.path.join(app.static_folder, 'profile_pics')
            if not os.path.exists(pic_folder):
                os.makedirs(pic_folder)
            file.save(os.path.join(pic_folder, filename))
            cur.execute("UPDATE business SET profile_pic=%s WHERE businessId=%s", (filename, business_dict['businessId']))
            conn.commit()
            profile_pic_url = url_for('static', filename='profile_pics/' + filename)
        # Refresh business_dict after update
        cur.execute("SELECT * FROM business WHERE name=%s", (session['name'],))
        business = cur.fetchone()
        business_dict = dict(zip(columns, business)) if business else None
    conn.close()
    return render_template('profile.html', profile_pic_url=profile_pic_url, business=business_dict)

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
    conn, cur = get_db_connection()
    leads_data = []
    # Get businessId for the logged-in user
    cur.execute("SELECT businessId FROM business WHERE name=%s", (session['name'],))
    row = cur.fetchone()
    business_id = row[0] if row else None
    if business_id:
        cur.execute('''
            SELECT ch.msgId, ch.customerId, ch.businessId, ch.LLM_msg, ch.customer_msg, ch.timestamp, ch.CampaignId, cu.fName, ca.campaignName
            FROM chatlog ch
            JOIN campaign ca ON ch.CampaignId = ca.campaignId
            LEFT JOIN customer cu ON ch.customerId = cu.customerId
            WHERE ca.businessId = %s
            ORDER BY ch.msgId DESC
        ''', (business_id,))
        rows = cur.fetchall()
        for row in rows:
            leads_data.append({
                'msg_id': row[0],
                'customer_id': row[1],
                'business_id': row[2],
                'llm_msg': row[3],
                'customer_msg': row[4],
                'timestamp': row[5],
                'campaign_id': row[6],
                'customer_name': row[7] or 'Unknown',
                'campaign_name': row[8] or 'Unknown'
            })
    cur.close()
    conn.close()
    return render_template('leads.html', leads_data=leads_data)

@app.route('/sales')
def sales():
    if 'name' not in session:
        return redirect(url_for('login'))
    img_path = None
    cluster_msg = None
    df = fetch_all_chatlog_msgs()
    if not df.empty:
        static_dir = os.path.join(app.root_path, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        img_path = os.path.join(static_dir, 'sales_clusters.png')
        clustered_df = cluster_and_reduce(df, n_clusters=5)
        if clustered_df is not None:
            save_cluster_plot(clustered_df, img_path)
        else:
            img_path = None
            cluster_msg = "Not enough customer messages to perform clustering."
    else:
        cluster_msg = "No customer messages found."
    img_url = url_for('static', filename='sales_clusters.png') if img_path and os.path.exists(img_path) else None
    return render_template('sales.html', cluster_img=img_url, cluster_msg=cluster_msg)

@app.route('/agent')
def agent():
    if 'name' not in session:
        return redirect(url_for('login'))
    return render_template('agent.html')

import ratelimit

@ratelimit.sleep_and_retry
@ratelimit.limits(calls=60, period=60)

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
    # Essential: Log every POST request
    print("Webhook POST hit!")
    data = request.json
    try:
        if "entry" in data and len(data["entry"]) > 0:
            entry = data["entry"][0]
            if "changes" in entry and len(entry["changes"]) > 0:
                change = entry["changes"][0]
                if "value" in change and "messages" in change["value"]:
                    message = change["value"]["messages"][0]
                    sender = message["from"]
                    text = message.get("text", {}).get("body", "No text")
                    print(f"Received WhatsApp message from {sender}: {text}")

                    # Keep original sender for WhatsApp API, format for database
                    db_sender = sender
                    if db_sender.startswith('94') and len(db_sender) == 11:
                        db_sender = '0' + db_sender[2:]
                    print(f"Formatted sender for database: {db_sender}")

                    # Fetch customerId and campaign details using separate cursors
                    connection, cursor = get_db_connection()
                    customer_id = None
                    campaign_id = None
                    try:
                        cursor.execute("SELECT customerId FROM customer WHERE mobileNo = %s", (db_sender,))
                        customer_row = cursor.fetchone()
                        print(f"Fetched customer row: {customer_row}")
                        customer_id= customer_row[0] if customer_row else None
                    except Error as e:
                        print(f"Database error fetching customer: {e}")
                    finally:
                        cursor.close()
                        connection.close()

                    #To send the massage to the ML model to identify the campaign
                    from faiss_store import find_relevant_campaign
                    print(f"text: {text}")
                    campaign_id = find_relevant_campaign(text, "Master/campaign_vector.index", "Master/campaign_vector_meta.pkl") 
                    print(f"Most relevant campaign found: {campaign_id}")
                    

                    
                    # Initialize LangChain conversation
                    print(f"Initialized LangChain conversation for customerId={customer_id}, sender={db_sender}, campaign_id={campaign_id}")
                    (
                        runnable, customer_name, campaign_name, offer, main_benefits, product_type, target_audience, target_problem,
                        unique_solution, reason_why_needed, social_proof, price, urgency, cta, db_prompt, history_data
                    ) = initialize_llm_chain(customer_id, db_sender, campaign_id)

                    # Generate AI reply using LangChain
                    ai_reply = call_llm_with_chain(
                        runnable, text, customer_name, campaign_name, session_id=customer_id,
                        offer=offer, main_benefits=main_benefits, product_type=product_type, target_audience=target_audience,
                        target_problem=target_problem, unique_solution=unique_solution, reason_why_needed=reason_why_needed,
                        social_proof=social_proof, price=price, urgency=urgency, cta=cta, db_prompt=db_prompt, history=history_data
                    )
                    print(f"AI reply before sending: {repr(ai_reply)}, type: {type(ai_reply)}")  # Debug the reply
                    if not isinstance(ai_reply, str):
                        raise ValueError(f"Expected string for ai_reply, got {type(ai_reply)}: {ai_reply}")
                    send_whatsapp_message(sender, ai_reply)

                    # Save conversation
                    if campaign_id:
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


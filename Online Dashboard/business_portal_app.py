from flask import Flask, render_template, request, redirect, url_for, session
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Database')))
from connect_db import connection
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn, cur = connection()
    return conn, cur

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
            "INSERT INTO business (businessId, name, contact, type, agentStatus, password) VALUES (?, ?, ?, ?, ?, ?)",
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
        cur.execute("SELECT * FROM business WHERE name=? AND password=?", (name, password))
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
        cur.execute("SELECT businessId FROM business WHERE name=?", (session['name'],))
        business_id_row = cur.fetchone()
        campaigns = []
        if business_id_row:
            business_id = business_id_row[0]
            # Fetch all campaigns for this business
            cur.execute("SELECT * FROM campaign WHERE businessId=? ORDER BY campaignId DESC", (business_id,))
            columns = [desc[0] for desc in cur.description]
            for row in cur.fetchall():
                campaigns.append(dict(zip(columns, row)))
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
    cur.execute("SELECT businessId FROM business WHERE name=?", (session['name'],))
    business_id_row = cur.fetchone()
    if business_id_row:
        business_id = business_id_row[0]
        cur.execute("""
            INSERT INTO campaign (businessId, campaignName, prompt, template, parameters, targetProblem, targetAudience, uniqueSolution, whyNeeded, mainBenefits, socialProof, price, offer, urgency, cta, ProductType)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            cur.execute("SELECT businessId FROM business WHERE name=?", (session['name'],))
            business_id_row = cur.fetchone()
            business_id = business_id_row[0] if business_id_row else 'unknown'
            cur.execute("SELECT campaignId FROM campaign WHERE businessId=? ORDER BY campaignId DESC LIMIT 1", (business_id,))
            campaign_id_row = cur.fetchone()
            campaign_id = campaign_id_row[0] if campaign_id_row else 'unknown'
            # Create filename: businessname_campaignid.csv
            safe_business = secure_filename(session['name'])
            filename = f"{safe_business}_{campaign_id}.csv"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            conn.close()
            return render_template('success.html')
        else:
            return "Invalid file type. Please upload a CSV file."
    return render_template('CustomerUpload.html')

# Profile page
@app.route('/profile')
def profile():
    if 'name' not in session:
        return redirect(url_for('login'))
    # Optionally, fetch more user info from DB here
    return render_template('profile.html')

@app.route('/campaign')
def campaign():
    if 'name' not in session:
        return redirect(url_for('login'))
    conn, cur = get_db_connection()
    # Get businessId for the logged-in user
    cur.execute("SELECT businessId FROM business WHERE name=?", (session['name'],))
    business_id_row = cur.fetchone()
    campaigns = []
    if business_id_row:
        business_id = business_id_row[0]
        # Fetch all campaigns for this business
        cur.execute("SELECT * FROM campaign WHERE businessId=? ORDER BY campaignId DESC", (business_id,))
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

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)

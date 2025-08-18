from flask import Flask, render_template, request, redirect, url_for, session
import mariadb
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    return mariadb.connect(
        host='localhost',
        user='root',
        password='',
        database='prism_ai_database'
    )

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

        conn = get_db_connection()
        cur = conn.cursor()

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

        conn = get_db_connection()
        cur = conn.cursor()
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
        return render_template('dashboard.html', name=session['name'])
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

    # Prompt paragraph template
    prompt = f"""Hey I'm PRISM AI!. See this, {target_problem}. Every {target_audience} has felt it — the constant struggle, the wasted hours, the missed opportunities. That’s when we decided enough was enough. We created {product_name}, not just as another tool, but as a complete transformation.

Unlike anything you’ve tried before, {product_name} offers {unique_solution}, finally giving you control over {target_problem}. And now more than ever, {reason_why_needed} — the timing couldn’t be more perfect.

With {main_benefits}, it’s not just powerful, it’s also incredibly easy to use. People are already seeing amazing results — just look at this: {social_proof}.

Normally, you’d pay {price} for this kind of breakthrough. But for a short time, you get {offer}. {urgency} — so if you’re serious about changing your life, this is your moment.

{cta}"""

    return render_template('result.html', prompt=prompt)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)

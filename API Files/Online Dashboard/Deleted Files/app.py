# app.py
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/product')
def product_form():
    return render_template('product.html')

@app.route('/generate', methods=['POST'])
def generate_prompt():
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
    prompt = f"""Hey im PRISM AI!. See this, {target_problem}. Every {target_audience} has felt it — the constant struggle, the wasted hours, the missed opportunities. That’s when we decided enough was enough. We created {product_name}, not just as another tool, but as a complete transformation.

Unlike anything you’ve tried before, {product_name} offers {unique_solution}, finally giving you control over {target_problem}. And now more than ever, {reason_why_needed} — the timing couldn’t be more perfect.

With {main_benefits}, it’s not just powerful, it’s also incredibly easy to use. People are already seeing amazing results — just look at this: {social_proof}.

Normally, you’d pay {price} for this kind of breakthrough. But for a short time, you get {offer}. {urgency} — so if you’re serious about changing your life, this is your moment.

{cta}"""

    return render_template('result.html', prompt=prompt)

if __name__ == '__main__':
    app.run(debug=True)

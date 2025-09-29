import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from reportlab.lib.units import inch

app = Flask(__name__)

# Configure the SQLite database with the name "database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Generate a secret key using os.urandom()
app.secret_key = os.urandom(24)  # Generates a random 24-byte key

db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    business_name = db.Column(db.String(120), nullable=False)
    gst_number = db.Column(db.String(15), unique=True, nullable=False)
    contact_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed password in production
    business_type = db.Column(db.String(50))

# Define other models as needed (e.g., Invoice, Product, Customer)
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)  # Added customer_name
    items = db.Column(db.String(1000), nullable=False)  # JSON of items
    quantities = db.Column(db.String(1000), nullable=False)  # JSON of quantities
    prices = db.Column(db.String(1000), nullable=False)  # JSON of prices
    discount = db.Column(db.Float, default=0.0)
    tax = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    contact_number = db.Column(db.String(15), nullable=True)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('login.html')  # Render the login page

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database to find the user
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # Replace with password hashing in production
            session['user_id'] = user.id  # Store user ID in session
            return jsonify({'success': True, 'redirect': url_for('home')})  # Redirect to home page
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})

    return render_template('login.html')  # Show login page


@app.route('/check_username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})


@app.route('/check_gst_number', methods=['POST'])
def check_gst_number():
    data = request.get_json()
    gst_number = data.get('gst_number')
    user = User.query.filter_by(gst_number=gst_number).first()
    if user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})


@app.route('/check_contact_number', methods=['POST'])
def check_contact_number():
    data = request.get_json()
    contact_number = data.get('contact_number')
    user = User.query.filter_by(contact_number=contact_number).first()
    if user:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        business_name = request.form['business_name']
        gst_number = request.form['gst_number']
        contact_number = request.form['contact_number']
        email = request.form['email']
        password = request.form['password']
        business_type = request.form['business_type']

        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email address already exists. Please use a different email.', 'error')
            return render_template('signup.html')

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template('signup.html')

        existing_gst = User.query.filter_by(gst_number=gst_number).first()
        if existing_gst:
            flash('GST number already exists. Please choose a different GST number.', 'error')
            return render_template('signup.html')

        existing_contact = User.query.filter_by(contact_number=contact_number).first()
        if existing_contact:
            flash('Contact Number already exists. Please use a different Contact Number.', 'error')
            return render_template('signup.html')

        # Create a new user instance
        new_user = User(username=username,
                        business_name=business_name,
                        gst_number=gst_number,
                        contact_number=contact_number,
                        email=email,
                        password=password,
                        business_type=business_type)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    return jsonify({'exists': bool(user)})


@app.route('/new_invoices')
def new_invoices():
    return render_template('new_invoices.html')


@app.route('/invoices')
def invoices():
    # Fetch invoices for the current user
    if 'user_id' in session:
        user_id = session['user_id']
        invoices = Invoice.query.filter_by(user_id=user_id).all()
        return render_template('invoices.html', invoices=invoices)
    else:
        return redirect(url_for('login'))

@app.route('/invoice/<int:invoice_id>')
def invoice_detail(invoice_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    invoice = Invoice.query.get_or_404(invoice_id)
    items = json.loads(invoice.items)
    quantities = json.loads(invoice.quantities)
    prices = json.loads(invoice.prices)
    rows = []
    for i in range(len(items)):
        quantity = int(quantities[i])
        price = float(prices[i])
        rows.append({'item': items[i], 'quantity': quantity, 'price': price, 'amount': quantity * price})
    return render_template('invoice_detail.html', invoice=invoice, rows=rows)

@app.route('/inventory')
def inventory():
    products = Product.query.all()
    return render_template('inventory.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    price = request.form['price']
    stock_quantity = request.form['stock_quantity']

    new_product = Product(name=name, price=price, stock_quantity=stock_quantity)
    db.session.add(new_product)
    db.session.commit()

    return redirect(url_for('products'))

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if product:
        product.name = request.form['name']
        product.price = request.form['price']
        product.stock_quantity = request.form['stock_quantity']
        db.session.commit()
    return redirect(url_for('products'))

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('products'))

@app.route('/customers')
def customers():
    invoices = Invoice.query.all()  # Fetch all invoices

    # Calculate monthly spending for each customer
    monthly_spending = {}
    months = []
    customers = set()  # Use a set to store unique customer names

    for invoice in invoices:
        customer_name = invoice.customer_name  # Get customer name from invoice
        customers.add(customer_name)  # Add customer name to the set

        month = invoice.date.strftime('%B')  # Month name
        if month not in months:
            months.append(month)

        if customer_name not in monthly_spending:
            monthly_spending[customer_name] = {}

        if month not in monthly_spending[customer_name]:
            monthly_spending[customer_name][month] = 0

        monthly_spending[customer_name][month] += invoice.total_amount

    customer_list = list(customers)  # Convert set to list for the template

    return render_template(
        'customers.html',
        customers=customer_list,
        monthly_spending=monthly_spending,
        months=months
    )

@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)


@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))  # Redirect to login after logout

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    if user is None:
        return "User not found", 404

    # Get form data
    customer_name = request.form['customer_name']
    invoice_date_str = request.form['invoice_date']
    invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').date()  # Convert to date

    invoice_items = json.loads(request.form['item_names']) #request.form.getlist('item[]')
    invoice_quantities = json.loads(request.form['item_quantities']) #request.form.getlist('quantity[]')
    invoice_prices = json.loads(request.form['item_prices']) #request.form.getlist('price[]')
    discount = float(request.form['discount']) if request.form['discount'] else 0.0
    tax = float(request.form['tax']) if request.form['tax'] else 0.0  # Get tax amount from form

    # Calculate total amount
    total_amount = 0.0
    for i in range(len(invoice_items)):
        quantity = int(invoice_quantities[i])
        price = float(invoice_prices[i])
        total_amount += quantity * price

    # Apply discount and tax
    total_amount -= discount
    total_amount += tax

    # Generate unique invoice number
    invoice_number = f"INV-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Create new invoice
    new_invoice = Invoice(
        user_id=user_id,
        invoice_number=invoice_number,
        date=invoice_date,
        customer_name=customer_name,
        items=json.dumps(invoice_items),  # Store as JSON
        quantities=json.dumps(invoice_quantities),  # Store as JSON
        prices=json.dumps(invoice_prices),  # Store as JSON
        discount=discount,
        tax=tax,
        total_amount=total_amount
    )
    db.session.add(new_invoice)
    db.session.commit()

    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Centering the business name and GSTIN
    centered_style = ParagraphStyle(
        name='Center',
        parent=styles['Normal'],
        alignment=1,  # 0: left, 1: center, 2: right, 4: justify
    )
    styles.add(centered_style)
    
    # Centering the Heading1
    centered_heading1 = ParagraphStyle(
        name='CenterHeading1',
        parent=styles['Heading1'],
        alignment=1,  # 0: left, 1: center, 2: right, 4: justify
    )
    styles.add(centered_heading1)

    story = []

    # Add a logo or header image (replace 'logo.png' with your logo file)
    logo_path = os.path.join(app.static_folder, 'logo.png')
    if os.path.exists(logo_path):
        from reportlab.platypus import Image
        logo = Image(logo_path, width=2*inch, height=inch)
        story.append(logo)
    else:
        #Use center_heading1
        story.append(Paragraph(user.business_name, styles['CenterHeading1']))

    #Use centered_style
    story.append(Paragraph(f"GSTIN: {user.gst_number}", centered_style))
    story.append(Spacer(1, 12))

    # Invoice Details Table
    invoice_details = [
        ["Invoice Number:", invoice_number],
        ["Invoice Date:", invoice_date.strftime('%Y-%m-%d')],
        ["Customer Name:", customer_name]
    ]
    invoice_table = Table(invoice_details)
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (1, -1), 6),
        ('TOPPADDING', (0, 0), (1, -1), 6),
    ]))
    story.append(invoice_table)
    story.append(Spacer(1, 12))

    # Invoice Items Table
    data = [["Item", "Quantity", "Price", "Amount"]]
    for i in range(len(invoice_items)):
        item = invoice_items[i]
        quantity = int(invoice_quantities[i])
        price = float(invoice_prices[i])
        amount = quantity * price
        data.append([item, quantity, price, amount])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Discount and Tax
    totals_data = [
        ["Discount:", discount],
        ["Tax:", tax],
        ["Total Amount:", total_amount]
    ]
    totals_table = Table(totals_data)
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (1, -1), 6),
        ('TOPPADDING', (0, 0), (1, -1), 6),
    ]))
    story.append(totals_table)

    # Build the PDF
    doc.build(story)
    buffer.seek(0)

    # Return PDF
    return send_file(buffer, as_attachment=True, download_name='invoice.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)

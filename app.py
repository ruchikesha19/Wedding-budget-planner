from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/weddingbudget'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://username:password@localhost/weddingplanner')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Mail ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

db = SQLAlchemy(app)
mail = Mail(app)

# --------------- Models ---------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    weddings = db.relationship('Wedding', backref='owner', lazy=True)

class Wedding(db.Model):
    __tablename__ = 'weddings'
    title = db.Column(db.String(120), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wedding_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(255))
    total_budget = db.Column(db.Float, nullable=False, default=0.0)
    categories = db.relationship('Category', backref='wedding_ref', lazy=True, cascade="all, delete")
    
    __table_args__ = (
        db.UniqueConstraint('title', 'user_id', name='_user_wedding_uc'),
    )

    @property
    def total_allocated(self):
        return sum(c.default_amount for c in self.categories)

    @property
    def total_spent(self):
        return sum(item.actual for c in self.categories for item in c.items)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    wedding_title = db.Column(db.String(120), db.ForeignKey('weddings.title'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    default_amount = db.Column(db.Float, default=0.0)
    items = db.relationship('Item', backref='category', lazy=True, cascade="all, delete")

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    allocated = db.Column(db.Float, default=0.0)
    actual = db.Column(db.Float, default=0.0)
    payments = db.relationship('Payment', backref='item', lazy=True, cascade="all, delete")

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_date = db.Column(db.Date, default=datetime.utcnow)
    notes = db.Column(db.String(255))

# -------- Helper functions ----------
def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def send_email(to, subject, body):
    if not app.config['MAIL_USERNAME']:
        app.logger.warning('MAIL_USERNAME not configured; email not sent.')
        return
    try:
        msg = Message(subject, recipients=[to], body=body)
        mail.send(msg)
    except Exception as e:
        app.logger.error(f"Email send error: {e}")

# --------------- Routes ---------------
@app.route('/')
def index():
    return render_template('index.html')

# --- Auth ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Account created, please log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out', 'info')
    return redirect(url_for('index'))

# --- Dashboard / Weddings ---
@app.route('/dashboard')
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    weddings = Wedding.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html', weddings=weddings, user=user)

@app.route('/wedding/new', methods=['GET', 'POST'])
def new_wedding():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        wedding_date = request.form['wedding_date']
        location = request.form['location']
        total_budget = request.form['total_budget']
        try:
            wedding = Wedding(user_id=user.id, title=title, wedding_date=wedding_date,
                            location=location, total_budget=total_budget)
            db.session.add(wedding)
            db.session.commit()
            flash('Wedding created!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            if 'Duplicate entry' in str(e) and 'title' in str(e):
                flash('A wedding with this title already exists. Please choose a different title.', 'danger')
            else:
                flash('An error occurred while creating the wedding.', 'danger')
            return render_template('new_wedding.html')
    return render_template('new_wedding.html')

@app.route('/wedding/<wedding_title>')
def wedding_detail(wedding_title):
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    wedding = Wedding.query.get_or_404(wedding_title)
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('wedding_detail.html', wedding=wedding)

# --- Category ---
@app.route('/wedding/<wedding_title>/add_category', methods=['GET', 'POST'])
def add_category(wedding_title):
    user = current_user()
    wedding = Wedding.query.get_or_404(wedding_title)
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        default_amount = request.form['default_amount']
        cat = Category(wedding_title=wedding.title, name=name, default_amount=default_amount)
        db.session.add(cat)
        db.session.commit()
        flash('Category added!', 'success')
        return redirect(url_for('wedding_detail', wedding_title=wedding.title))
    return render_template('add_category.html', wedding=wedding)

# --- Item ---
@app.route('/category/<int:category_id>/add_item', methods=['GET', 'POST'])
def add_item(category_id):
    user = current_user()
    category = Category.query.get_or_404(category_id)
    wedding = category.wedding_ref
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form['name']
        allocated = request.form['allocated']
        item = Item(category_id=category.id, name=name, allocated=allocated)
        db.session.add(item)
        db.session.commit()
        flash('Item added!', 'success')
        return redirect(url_for('wedding_detail', wedding_id=wedding.id))
    return render_template('add_item.html', category=category, wedding=wedding)

# --- Payment ---
@app.route('/item/<int:item_id>/add_payment', methods=['GET', 'POST'])
def add_payment(item_id):
    user = current_user()
    item = Item.query.get_or_404(item_id)
    category = item.category
    wedding = category.wedding_ref
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        notes = request.form['notes']
        payment = Payment(item_id=item.id, amount=amount, notes=notes)
        db.session.add(payment)
        # Update actual spent for item
        item.actual += amount
        db.session.commit()
        flash('Payment recorded!', 'success')
        # Email reminder / confirmation
        send_email(user.email, 'Payment Recorded', f'You recorded a payment of ₹{amount:.2f} for {item.name}.')
        return redirect(url_for('wedding_detail', wedding_id=wedding.id))
    return render_template('add_payment.html', item=item, wedding=wedding)

@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    user = current_user()
    category = Category.query.get_or_404(category_id)
    wedding = category.wedding
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        category.name = request.form['name']
        category.default_amount = float(request.form['default_amount'])
        db.session.commit()
        flash('Category updated!', 'success')
        return redirect(url_for('wedding_detail', wedding_id=wedding.id))
    
    return render_template('edit_category.html', category=category)

@app.route('/category/<int:category_id>/delete')
def delete_category(category_id):
    user = current_user()
    category = Category.query.get_or_404(category_id)
    wedding = category.wedding
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted!', 'success')
    return redirect(url_for('wedding_detail', wedding_id=wedding.id))
@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    user = current_user()
    item = Item.query.get_or_404(item_id)
    category = item.category
    wedding = category.wedding
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        item.name = request.form['name']
        item.allocated = float(request.form['allocated'])
        db.session.commit()
        flash('Item updated!', 'success')
        return redirect(url_for('wedding_detail', wedding_id=wedding.id))
    
    return render_template('edit_item.html', item=item)

@app.route('/item/<int:item_id>/delete')
def delete_item(item_id):
    user = current_user()
    item = Item.query.get_or_404(item_id)
    category = item.category
    wedding = category.wedding
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted!', 'success')
    return redirect(url_for('wedding_detail', wedding_id=wedding.id))

@app.route('/payment/<int:payment_id>/edit', methods=['GET', 'POST'])
def edit_payment(payment_id):
    user = current_user()
    payment = Payment.query.get_or_404(payment_id)
    item = payment.item
    category = item.category
    wedding = category.wedding
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        old_amount = payment.amount
        payment.amount = float(request.form['amount'])
        payment.notes = request.form['notes']
        # Update item's actual spent
        item.actual = item.actual - old_amount + payment.amount
        db.session.commit()
        flash('Payment updated!', 'success')
        return redirect(url_for('wedding_detail', wedding_id=wedding.id))
    
    return render_template('edit_payment.html', payment=payment, item=item)

@app.route('/payment/<int:payment_id>/delete')
def delete_payment(payment_id):
    user = current_user()
    payment = Payment.query.get_or_404(payment_id)
    item = payment.item
    category = item.category
    wedding = category.wedding
    if wedding.user_id != user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    
    # Update item's actual spent
    item.actual -= payment.amount
    db.session.delete(payment)
    db.session.commit()
    flash('Payment deleted!', 'success')
    return redirect(url_for('wedding_detail', wedding_id=wedding.id))
# ------------- Run --------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

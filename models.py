# backend/models.py
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# --- MODEL BUKU ---
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    price = db.Column(db.Float, default=0.0, nullable=False)
    synopsis = db.Column(db.Text, nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    cover_image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'stock': self.stock,
            'price': self.price,
            'synopsis': self.synopsis,
            'publication_year': self.publication_year,
            'cover_image_url': self.cover_image_url
        }

# --- MODEL RESERVATION ---
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Pastikan ini ada
    user_name = db.Column(db.String(255), nullable=False)
    user_contact = db.Column(db.String(255), nullable=False)
    reservation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending', nullable=False)
    pickup_date = db.Column(db.Date, nullable=True)
    return_date = db.Column(db.Date, nullable=True)

    book = db.relationship('Book', backref='reservations', lazy=True)
    user = db.relationship('User', backref='reservations', lazy=True) # Pastikan ini ada

    def __repr__(self):
        return f'<Reservation {self.id} for Book {self.book.title} by User {self.user.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_contact': self.user_contact,
            'reservation_date': self.reservation_date.isoformat(),
            'status': self.status,
            'pickup_date': self.pickup_date.isoformat() if self.pickup_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'book_title': self.book.title,
            'book_author': self.book.author,
            'book_isbn': self.book.isbn,
            'username': self.user.username, # Pastikan ini ada
            'user_email': self.user.email,   # Pastikan ini ada
        }

# --- MODEL USER ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    is_librarian = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'is_librarian': self.is_librarian
        }

# --- MODEL ORDER ---
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Pastikan ini ada
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending_payment', nullable=False)
    shipping_address = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(100), nullable=True)

    book = db.relationship('Book', backref='orders', lazy=True)
    user = db.relationship('User', backref='orders', lazy=True) # Pastikan ini ada

    def __repr__(self):
        return f'<Order {self.id} for Book {self.book.title} by User {self.user.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'order_date': self.order_date.isoformat(),
            'quantity': self.quantity,
            'total_price': self.total_price,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'payment_method': self.payment_method,
            'book_title': self.book.title,
            'book_author': self.book.author,
            'username': self.user.username, # Pastikan ini ada
            'user_email': self.user.email # Pastikan ini ada
        }

# --- MODEL NEWS/ARTICLE ---
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    publication_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_url = db.Column(db.String(255), nullable=True) # <--- PASTIKAN INI ADA

    author = db.relationship('User', backref='articles', lazy=True)

    def __repr__(self):
        return f'<Article {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'author_username': self.author.username if self.author else 'Anonim',
            'publication_date': self.publication_date.isoformat(),
            'image_url': self.image_url # <--- PASTIKAN INI ADA
        }
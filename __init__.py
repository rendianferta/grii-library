# backend/__init__.py
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from werkzeug.utils import secure_filename # Import ini untuk allowed_file

db = SQLAlchemy()
cors = CORS()
login_manager = LoginManager()

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    from .config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    # --- PENTING: PASTIKAN BARIS INI ADA DI SINI ---
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
    # --- AKHIR BAGIAN PENTING ---

    cors.init_app(app, supports_credentials=True)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.session_protection = "strong"

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"message": "Autentikasi diperlukan. Silakan login."}), 401

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    from . import models
    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return "Halo dari Backend Flask Perpustakaan!"

    from .routes import api_bp
    app.register_blueprint(api_bp)

    return app

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
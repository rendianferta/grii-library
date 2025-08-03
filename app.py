# backend/app.py
import os
from flask import Flask, jsonify # jsonify mungkin tidak lagi dibutuhkan di sini, tapi tidak masalah
from flask_cors import CORS # CORS mungkin tidak lagi dibutuhkan di sini
from flask_sqlalchemy import SQLAlchemy # SQLAlchemy mungkin tidak lagi dibutuhkan di sini
from config import Config # Config mungkin tidak lagi dibutuhkan di sini

from __init__ import create_app, db
from models import Book # Book mungkin tidak lagi dibutuhkan di sini

app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

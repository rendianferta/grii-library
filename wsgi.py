import sys
import os

# Tambahkan ROOT folder ke sys.path agar bisa import backend
sys.path.insert(0, os.path.dirname(__file__))

from backend import create_app

application = create_app()
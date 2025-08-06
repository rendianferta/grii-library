# backend/config.py
import os

class Config:
    # --- PENTING: PASTIKAN INI ADA DAN UNIK! ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci-rahasia-yang-sangat-sulit-ditebak-dan-unik-sekali'
    # Jika Anda belum menyetel SECRET_KEY sebagai environment variable,
    # gunakan string yang sangat panjang dan acak seperti di atas untuk pengembangan.
    # Untuk produksi, ini harus disetel sebagai environment variable yang sebenarnya.

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usergrii:Wwinter060906@172.18.9.212/griiLibrarydb'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- PENTING: KONFIGURASI COOKIE SESI UNTUK PENGEMBANGAN CROSS-ORIGIN ---
    # Mengizinkan cookie dikirim dalam permintaan cross-site
    # 'None' berarti browser akan mengirim cookie dalam konteks cross-site.
    # Ini diperlukan untuk pengembangan dengan frontend di port berbeda.
    SESSION_COOKIE_SAMESITE = None

    # Karena kita menggunakan HTTP (bukan HTTPS) di localhost,
    # kita harus menyetel SESSION_COOKIE_SECURE ke False.
    # Jika Anda menggunakan HTTPS, set ini ke True.
    SESSION_COOKIE_SECURE = False

    # Opsional: Jika Anda ingin cookie berlaku lebih lama (misal 30 hari)
    # PERMANENT_SESSION_LIFETIME = timedelta(days=30)
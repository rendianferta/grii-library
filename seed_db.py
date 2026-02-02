# backend/seed_db.py
import os
from backend import create_app, db
from backend.models import User, Book, Reservation, Order, Article # Import Article
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        print("Menghapus semua tabel yang ada...")
        db.drop_all()
        print("Membuat ulang semua tabel...")
        db.create_all()
        print("Tabel berhasil dibuat ulang.")

        # --- Tambah User Admin & Biasa (Sudah Ada) ---
        print("\nMenambahkan user admin...")
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user is None:
            admin_user = User(username='admin', email='admin@perpustakaan.com', full_name='Admin Perpustakaan', is_librarian=True)
            admin_user.set_password('adminpassword')
            db.session.add(admin_user)
            db.session.commit()
            print(f"User Admin '{admin_user.username}' berhasil dibuat.")
        else:
            print(f"User Admin '{admin_user.username}' sudah ada.")
            if not admin_user.is_librarian:
                admin_user.is_librarian = True
                db.session.commit()
                print(f"User Admin '{admin_user.username}' diubah menjadi pustakawan.")
        
        print("\nMenambahkan user biasa...")
        user1 = User.query.filter_by(username='pengguna1').first()
        if user1 is None:
            user1 = User(username='pengguna1', email='user1@example.com', full_name='Pengguna Biasa', is_librarian=False)
            user1.set_password('userpassword')
            db.session.add(user1)
            db.session.commit()
            print(f"User '{user1.username}' berhasil dibuat.")
        else:
            print(f"User '{user1.username}' sudah ada.")

        # --- Tambah Buku-buku (Sudah Ada) ---
        print("\nMenambahkan buku-buku...")
        if not Book.query.first():
            book1 = Book(title='Atomic Habits', author='James Clear', isbn='978-0735211299', stock=10, price=150000, synopsis='Sebuah buku tentang kebiasaan kecil tentang bagaimana kebiasaan kecil membentuk hasil besar.', publication_year=2018, cover_image_url='https://cdn.gramedia.com/uploads/items/9786020619931_filosofi_teras_cov.jpg')
            book2 = Book(title='Filosofi Teras', author='Henry Manampiring', isbn='978-6020619931', stock=7, price=95000, synopsis='Pengantar Stoisisme sebagai filosofi praktis untuk kehidupan modern yang lebih tenang dan bahagia.', publication_year=2018, cover_image_url='https://cdn.gramedia.com/uploads/items/9786020619931_filosofi_teras_cov.jpg')
            book3 = Book(title='Sapiens: A Brief History of Humankind', author='Yuval Noah Harari', isbn='978-0062316097', stock=5, price=200000, synopsis='Sebuah sejarah singkat manusia dari awal mula hingga masa kini, menjelaskan bagaimana Homo sapiens mendominasi bumi.', publication_year=2014, cover_image_url='https://cdn.gramedia.com/uploads/items/9786020619931_filosofi_teras_cov.jpg')
            book4 = Book(title='Dune', author='Frank Herbert', isbn='978-0441013593', stock=12, price=180000, synopsis='Sebuah epik fiksi ilmiah yang berlatar di planet gurun Arrakis, tempat produksi rempah berharga.', publication_year=1965, cover_image_url='https://cdn.gramedia.com/uploads/items/9786020619931_filosofi_teras_cov.jpg')
            book5 = Book(title='The Great Gatsby', author='F. Scott Fitzgerald', isbn='978-0743273565', stock=8, price=110000, synopsis='Kisah klasik tentang impian Amerika, kekayaan, dan tragedi di era Roaring Twenties.', publication_year=1925, cover_image_url='https://cdn.gramedia.com/uploads/items/9786020619931_filosofi_teras_cov.jpg')
            
            db.session.add_all([book1, book2, book3, book4, book5])
            db.session.commit()
            print("Buku-buku berhasil ditambahkan.")
        else:
            print("Buku sudah ada di database.")
        
        # --- Tambah Data Reservasi Contoh (Sudah Ada) ---
        print("\nMenambahkan reservasi contoh...")
        # Pastikan user1 dan buku sudah ada
        if user1 and book1 and not Reservation.query.filter_by(user_id=user1.id, book_id=book1.id).first():
            res1 = Reservation(
                book_id=book1.id, user_id=user1.id, # Penting: gunakan user_id
                user_name=user1.full_name, user_contact=user1.email,
                reservation_date=datetime.utcnow(), status='pending',
                pickup_date=date.today() + timedelta(days=3)
            )
            db.session.add(res1)
            db.session.commit()
            print("Reservasi 1 berhasil ditambahkan.")
        
        if user1 and book2 and not Reservation.query.filter_by(user_id=user1.id, book_id=book2.id).first():
             res2 = Reservation(
                book_id=book2.id, user_id=user1.id, # Penting: gunakan user_id
                user_name=user1.full_name, user_contact=user1.email,
                reservation_date=datetime.utcnow() - timedelta(days=7),
                status='borrowed', # Contoh status sudah dipinjam
                pickup_date=date.today() - timedelta(days=5)
            )
             db.session.add(res2)
             db.session.commit()
             print("Reservasi 2 berhasil ditambahkan.")

        # --- Tambah Data Pesanan Contoh (Sudah Ada) ---
        print("\nMenambahkan pesanan contoh...")
        if user1 and book3 and not Order.query.filter_by(user_id=user1.id, book_id=book3.id).first():
            order1 = Order(
                book_id=book3.id, user_id=user1.id, quantity=1,
                total_price=book3.price * 1, shipping_address="Jl. Contoh No. 10, Kota Dummy",
                payment_method="QRIS", status="pending_payment"
            )
            db.session.add(order1)
            db.session.commit()
            print("Pesanan 1 berhasil ditambahkan.")

        # --- Tambah Data Berita/Artikel Contoh BARU ---
        print("\nMenambahkan berita/artikel contoh...")
        if not Article.query.first(): # Hanya tambah jika belum ada artikel
            news1 = Article(
                title='Perpustakaan Kami Merayakan Ulang Tahun ke-10!',
                content='Kami dengan bangga mengumumkan bahwa perpustakaan tercinta kita telah berusia 10 tahun. Rayakan bersama kami dengan berbagai acara dan diskon buku!',
                author_id=admin_user.id,
                publication_date=datetime.utcnow() - timedelta(days=10)
            )
            news2 = Article(
                title='Koleksi Buku Terbaru di Bulan Ini',
                content='Temukan berbagai judul menarik dari penulis-penulis terkemuka di rak-rak baru kami. Mulai dari fiksi hingga non-fiksi, ada sesuatu untuk semua orang.',
                author_id=admin_user.id,
                publication_date=datetime.utcnow() - timedelta(days=5)
            )
            news3 = Article(
                title='Workshop Menulis Kreatif untuk Remaja',
                content='Bergabunglah dalam workshop menulis kreatif kami yang dirancang khusus untuk remaja. Pelajari tips dan trik dari penulis profesional. Daftar sekarang!',
                author_id=admin_user.id,
                publication_date=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add_all([news1, news2, news3])
            db.session.commit()
            print("Berita/artikel berhasil ditambahkan.")
        else:
            print("Berita/artikel sudah ada di database.")

        print("\nSeed database selesai!")

if __name__ == '__main__':
    seed_database()
# backend/routes.py
import os # Pastikan ini diimpor
from flask import Blueprint, jsonify, request, url_for, current_app, Response # Pastikan ini lengkap
from urllib.parse import urljoin
from werkzeug.utils import secure_filename # Pastikan ini diimpor
from . import db
from . import models
from .models import Book, Reservation, User, Order, Article # Pastikan Article diimpor
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime # Pastikan datetime juga diimpor
from io import StringIO
import io
import csv
from .__init__ import allowed_file # Pastikan ini diimpor

api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Fungsi Pembantu untuk Memeriksa Admin ---
def is_librarian_required():
    if not current_user.is_authenticated or not current_user.is_librarian:
        return jsonify({"message": "Akses ditolak: Hanya pustakawan yang diizinkan."}), 403 # Forbidden
    return None # Lanjutkan jika pustakawan

# --- API BUKU ---
@api_bp.route('/status', methods=['GET'])
def api_status():
    return jsonify({"message": "Backend Flask berjalan dengan baik dari Blueprint!", "status": "ok"})

@api_bp.route('/books', methods=['GET'])
def get_all_books():
    search_query = request.args.get('q', type=str)
    author_query = request.args.get('author', type=str)
    title_query = request.args.get('title', type=str)
    isbn_query = request.args.get('isbn', type=str)
    books_query = models.Book.query
    if search_query:
        search_pattern = f"%{search_query}%"
        books_query = books_query.filter(
            (models.Book.title.ilike(search_pattern)) |
            (models.Book.author.ilike(search_pattern))
        )
    if author_query: books_query = books_query.filter(models.Book.author.ilike(f"%{author_query}%"))
    if title_query: books_query = books_query.filter(models.Book.title.ilike(f"%{title_query}%"))
    if isbn_query: books_query = books_query.filter(models.Book.isbn.ilike(f"%{isbn_query}%"))
    books = books_query.all()
    books_data = [book.to_dict() for book in books]
    return jsonify(books_data)

@api_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book_detail(book_id):
    book = models.Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@api_bp.route('/books', methods=['POST'])
@login_required
def add_book():
    auth_check = is_librarian_required()
    if auth_check: return auth_check
    data = request.get_json()
    if not data: return jsonify({"message": "Permintaan harus berupa JSON"}), 400
    if not data.get('title') or not data.get('author') or not data.get('isbn'):
        return jsonify({"message": "Judul, penulis, dan ISBN harus diisi."}), 400
    if models.Book.query.filter_by(isbn=data.get('isbn')).first():
        return jsonify({"message": "Buku dengan ISBN ini sudah ada."}), 409
    new_book = models.Book(
        title=data.get('title'), author=data.get('author'), isbn=data.get('isbn'),
        stock=data.get('stock', 0), price=data.get('price', 0.0), synopsis=data.get('synopsis'),
        publication_year=data.get('publication_year'), cover_image_url=data.get('cover_image_url')
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Buku berhasil ditambahkan", "book": new_book.to_dict()}), 201

@api_bp.route('/books/<int:book_id>', methods=['PUT'])
@login_required
def edit_book(book_id):
    auth_check = is_librarian_required()
    if auth_check: return auth_check
    book = models.Book.query.get_or_404(book_id)
    data = request.get_json()
    if not data: return jsonify({"message": "Permintaan harus berupa JSON"}), 400
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.isbn = data.get('isbn', book.isbn)
    book.stock = data.get('stock', book.stock)
    book.price = data.get('price', book.price)
    book.synopsis = data.get('synopsis', book.synopsis)
    book.publication_year = data.get('publication_year', book.publication_year)
    book.cover_image_url = data.get('cover_image_url', book.cover_image_url)
    db.session.commit()
    return jsonify({"message": "Buku berhasil diperbarui", "book": book.to_dict()}), 200

@api_bp.route('/books/<int:book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    auth_check = is_librarian_required()
    if auth_check: return auth_check
    book = models.Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Buku berhasil dihapus"}), 200


# --- API BARU: EKSPOR BUKU KE CSV ---
@api_bp.route('/admin/books/export', methods=['GET'])
@login_required # Membutuhkan user yang login
def export_books():
    # 1. Periksa otorisasi: Hanya pustakawan yang diizinkan mengakses rute ini
    if not current_user.is_librarian:
        return jsonify({"message": "Akses ditolak: Hanya pustakawan yang diizinkan."}), 403 # HTTP 403 Forbidden

    # 2. Ambil semua data buku dari database
    # Gunakan models.Book.query.all() untuk mendapatkan list objek Book
    all_books = models.Book.query.all()
    
    # 3. Ubah list objek Book menjadi list dictionary menggunakan metode to_dict()
    # Frontend mengharapkan data dalam format yang bisa di-JSON-kan, jadi kita panggil to_dict()
    # di sini untuk memastikan data yang diakses di langkah selanjutnya adalah dictionary.
    books_data_dicts = [book.to_dict() for book in all_books]
    # 4. Siapkan StringIO untuk menulis data CSV ke memori (bukan ke file fisik)
    si = StringIO()
    # Buat objek writer CSV
    writer = csv.writer(si)

    # 5. Tulis baris header CSV
    # Pastikan header cocok dengan key di dictionary objek buku Anda
    writer.writerow(['id', 'title', 'author', 'isbn', 'stock', 'price', 'synopsis', 'publication_year', 'cover_image_url'])

    # 6. Iterasi setiap buku dan tulis ke baris CSV
    for book_dict in books_data_dicts:
        writer.writerow([
            book_dict['id'],
            book_dict['title'],
            book_dict['author'],
            book_dict['isbn'],
            book_dict['stock'],
            book_dict['price'],
            book_dict['synopsis'] or '', # Gunakan '' jika null untuk menghindari 'None' di CSV
            book_dict['publication_year'] or '',
            book_dict['cover_image_url'] or ''
        ])

    # 7. Ambil seluruh konten CSV sebagai string
    output = si.getvalue()

    # 8. Buat dan kembalikan Respons HTTP untuk unduhan file CSV
    return Response(
        output, # Konten CSV
        mimetype='text/csv', # Tipe MIME untuk file CSV
        headers={"Content-Disposition": "attachment;filename=buku_perpustakaan.csv"} # Header untuk mengunduh file
    )

@api_bp.route('/admin/books/import', methods=['POST'])
@login_required
def import_books_csv():
    auth_check = is_librarian_required()
    if auth_check:
        return auth_check

    if 'file' not in request.files:
        return jsonify({'message': 'Tidak ada file CSV yang diunggah.'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'Nama file kosong.'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'message': 'Format file tidak valid. Harus berupa .csv'}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)

        imported = 0
        for row in csv_input:
            title = row.get("title")
            author = row.get("author")
            isbn = row.get("isbn")
            stock = row.get("stock")
            price = row.get("price")
            synopsis = row.get("synopsis")
            publication_year = row.get("publication year")

            
            if not (title and author and isbn and stock and price and synopsis and publication_year):
                continue  # lewati baris tak lengkap

            # Cek apakah buku dengan ISBN yang sama sudah ada
            existing_book = Book.query.filter_by(isbn=isbn).first()
            if existing_book:
                continue  # Lewati duplikat

            new_book = Book(
                title=title,
                author=author,
                isbn=isbn,
                stock=int(stock),
                price=float(price),
                synopsis=synopsis,
                publication_year=int(publication_year)
            )
            db.session.add(new_book)
            imported += 1

        db.session.commit()
        return jsonify({'message': f'Berhasil mengimpor {imported} buku.'}), 200

    except Exception as e:
        print("Import error:", e)
        return jsonify({'message': 'Terjadi kesalahan saat mengimpor file CSV.'}), 500

# --- API UPLOAD GAMBAR ---
@api_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    auth_check = is_librarian_required()
    if auth_check: return auth_check

    if 'file' not in request.files:
        return jsonify({"message": "Tidak ada bagian file dalam permintaan."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "Tidak ada file yang dipilih."}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename)
        
        file.save(file_path)       
        
        file_url = url_for('static', filename=f'uploads/{filename}', _external=False)
       
        return jsonify({"message": "File berhasil diupload.", "file_url": file_url}), 200
    else:
        return jsonify({"message": "Tipe file tidak diizinkan. Hanya gambar (png, jpg, jpeg, gif).", "file_name": file.filename}), 400


# --- API RESERVASI BUKU ---
@api_bp.route('/reservations', methods=['POST'])
@login_required
def create_reservation():
    data = request.get_json()
    if not data: return jsonify({"message": "Permintaan harus berupa JSON"}), 400
    book_id = data.get('book_id')
    user_name = current_user.full_name if current_user.full_name else current_user.username
    user_contact = current_user.email if current_user.email else current_user.phone_number
    pickup_date = data.get('pickup_date')
    if not book_id: return jsonify({"message": "ID buku harus diisi."}), 400
    book = models.Book.query.get(book_id)
    if not book: return jsonify({"message": "Buku tidak ditemukan."}), 404
    if book.stock <= 0: return jsonify({"message": "Maaf, stok buku tidak tersedia untuk dipinjam."}), 400
    book.stock -= 1
    try:
        from datetime import date # Pastikan ini sudah ada di atas
        parsed_pickup_date = None
        if pickup_date:
            parsed_pickup_date = date.fromisoformat(pickup_date)
        new_reservation = Reservation(
            book_id=book_id, user_name=user_name, user_id=current_user.id, user_contact=user_contact,
            status='pending', pickup_date=parsed_pickup_date
        )
        db.session.add(new_reservation)
        db.session.commit()
        return jsonify({"message": "Reservasi berhasil diajukan!", "reservation": new_reservation.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating reservation: {e}")
        return jsonify({"message": "Gagal membuat reservasi. Silakan coba lagi.", "error": str(e)}), 500

# --- API MANAJEMEN RESERVASI (Untuk Pustakawan) ---
@api_bp.route('/admin/reservations', methods=['GET'])
@login_required
def get_all_reservations_admin():
    auth_check = is_librarian_required()
    if auth_check:
        return auth_check

    q = request.args.get('q', '').strip().lower()

    query = models.Reservation.query.join(models.User).join(models.Book)

    if q:
        query = query.filter(
            db.or_(
                models.User.full_name.ilike(f'%{q}%'),
                models.Book.title.ilike(f'%{q}%'),
                models.Reservation.status.ilike(f'%{q}%')
            )
        )

    reservations = query.all()
    reservations_data = [r.to_dict() for r in reservations]
    return jsonify(reservations_data)

@api_bp.route('/admin/reservations/<int:res_id>', methods=['PUT'])
@login_required
def update_reservation_status_admin(res_id):
    auth_check = is_librarian_required()
    if auth_check: return auth_check
    reservation = models.Reservation.query.get_or_404(res_id)
    data = request.get_json()
    new_status = data.get('status')
    new_pickup_date_str = data.get('pickup_date')
    new_return_date_str = data.get('return_date')

    if not new_status: return jsonify({"message": "Status baru harus diisi."}), 400
    
    valid_statuses = ['pending', 'confirmed', 'borrowed', 'returned', 'cancelled']
    if new_status not in valid_statuses: return jsonify({"message": "Status tidak valid."}), 400

    old_status = reservation.status

    if new_status == 'returned':
        if old_status == 'borrowed':
            if reservation.book:
                reservation.book.stock += 1
                print(f"Stok buku '{reservation.book.title}' (ID: {reservation.book.id}) bertambah +1. Stok baru: {reservation.book.stock} (dari borrowed ke returned)")
        
    elif old_status == 'returned' and new_status == 'borrowed':
        if reservation.book:
            if reservation.book.stock > 0:
                reservation.book.stock -= 1
                print(f"Stok buku '{reservation.book.title}' (ID: {reservation.book.id}) berkurang -1. Stok baru: {reservation.book.stock} (dari returned ke borrowed)")
            else:
                print(f"Peringatan: Tidak bisa mengurangi stok buku '{reservation.book.title}' (ID: {reservation.book.id}) karena stok sudah 0. Sesuaikan manual jika perlu.")

    elif new_status == 'cancelled':
        if old_status in ['pending', 'confirmed', 'borrowed']:
            if reservation.book:
                reservation.book.stock += 1
                print(f"Stok buku '{reservation.book.title}' (ID: {reservation.book.id}) bertambah +1. Stok baru: {reservation.book.stock} (karena dibatalkan dari {old_status})")
        
    elif old_status == 'cancelled' and new_status in ['pending', 'confirmed', 'borrowed']:
        if reservation.book:
            if reservation.book.stock > 0:
                reservation.book.stock -= 1
                print(f"Stok buku '{reservation.book.title}' (ID: {reservation.book.id}) berkurang -1. Stok baru: {reservation.book.stock} (dari cancelled ke {new_status})")
            else:
                print(f"Peringatan: Tidak bisa mengurangi stok buku '{reservation.book.title}' (ID: {reservation.book.id}) karena stok sudah 0. Sesuaikan manual jika perlu.")

    reservation.status = new_status

    if new_pickup_date_str:
        try: reservation.pickup_date = date.fromisoformat(new_pickup_date_str)
        except ValueError: return jsonify({"message": "Format tanggal pengambilan tidak valid (YYYY-MM-DD)."}), 400
    if new_return_date_str:
        try: reservation.return_date = date.fromisoformat(new_return_date_str)
        except ValueError: return jsonify({"message": "Format tanggal pengembalian tidak valid (YYYY-MM-DD)."}), 400

    db.session.commit()
    return jsonify({"message": f"Status reservasi {res_id} berhasil diperbarui menjadi {new_status}.", "reservation": reservation.to_dict()}), 200

# --- API PEMBELIAN/ORDER ---
@api_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    if not data: return jsonify({"message": "Permintaan harus berupa JSON"}), 400
    book_id = data.get('book_id')
    quantity = data.get('quantity', 1)
    shipping_address = data.get('shipping_address')
    payment_method = data.get('payment_method')
    if not book_id or not quantity or quantity <= 0: return jsonify({"message": "ID buku dan kuantitas valid harus diisi."}), 400
    if not shipping_address: return jsonify({"message": "Alamat pengiriman harus diisi."}), 400
    book = models.Book.query.get(book_id)
    if not book: return jsonify({"message": "Buku tidak ditemukan."}), 404
    if book.stock < quantity: return jsonify({"message": f"Maaf, stok {book.title} tidak cukup. Tersedia: {book.stock}."}), 400
    book.stock -= quantity
    total_price = book.price * quantity
    try:
        new_order = Order(
            book_id=book_id, user_id=current_user.id, quantity=quantity,
            total_price=total_price, shipping_address=shipping_address,
            payment_method=payment_method, status='pending_payment'
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"message": "Pesanan berhasil dibuat! Silakan lakukan pembayaran.", "order": new_order.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating order: {e}")
        return jsonify({"message": "Gagal membuat pesanan. Silakan coba lagi.", "error": str(e)}), 500

# --- API MANAJEMEN PESANAN (Untuk Pustakawan) ---
@api_bp.route('/admin/orders', methods=['GET'])
@login_required
def get_all_orders_admin():
    auth_check = is_librarian_required()
    if auth_check:
        return auth_check

    q = request.args.get('q', '').strip().lower()

    query = models.Order.query.join(models.User).join(models.Book)

    if q:
        query = query.filter(
            db.or_(
                models.User.full_name.ilike(f'%{q}%'),
                models.Book.title.ilike(f'%{q}%'),
                models.Order.status.ilike(f'%{q}%')
            )
        )

    orders = query.all()
    orders_data = [o.to_dict() for o in orders]
    return jsonify(orders_data)

@api_bp.route('/admin/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order_status_admin(order_id):
  auth_check = is_librarian_required()
  if auth_check: return auth_check
  order = models.Order.query.get_or_404(order_id)
  data = request.get_json()
  new_status = data.get('status')
  if not new_status: return jsonify({"message": "Status baru harus diisi."}), 400
  valid_statuses = ['pending_payment', 'paid', 'shipped', 'completed', 'cancelled']
  if new_status not in valid_statuses: return jsonify({"message": "Status tidak valid."}), 400

  old_status = order.status # Dapatkan status lama sebelum update
  order.status = new_status

  # --- LOGIKA STOK UNTUK PEMBATALAN PESANAN (Tambahan) ---
  if old_status in ['pending_payment', 'paid'] and new_status == 'cancelled':
    # Jika pesanan dibatalkan setelah stok dikurangi, kembalikan stoknya
    if order.book:
      order.book.stock += order.quantity # Tambahkan kembali stok sejumlah yang dipesan
      print(f"Stok buku '{order.book.title}' (ID: {order.book.id}) bertambah +{order.quantity} karena pesanan dibatalkan. Stok baru: {order.book.stock}")
    else:
      print(f"Peringatan: Buku tidak ditemukan untuk pesanan ID {order_id} saat pembatalan stok.")
  # --- AKHIR LOGIKA STOK TAMBAHAN ---

  db.session.commit()
  return jsonify({"message": f"Status pesanan {order_id} berhasil diperbarui menjadi {new_status}.", "order": order.to_dict()}), 200

# --- API AUTENTIKASI ---
@api_bp.route('/register', methods=['POST'])
def register_user():
  data = request.get_json()
  if not data: return jsonify({"message": "Permintaan harus berupa JSON"}), 400
  username = data.get('username')
  email = data.get('email')
  password = data.get('password')
  full_name = data.get('full_name')
  phone_number = data.get('phone_number')
  if not username or not email or not password: return jsonify({"message": "Username, email, dan password harus diisi."}), 400
  if User.query.filter_by(username=username).first(): return jsonify({"message": "Username sudah ada."}), 409
  if User.query.filter_by(email=email).first(): return jsonify({"message": "Email sudah terdaftar."}), 409
  new_user = User(username=username, email=email, full_name=full_name, phone_number=phone_number)
  new_user.set_password(password)
  db.session.add(new_user)
  db.session.commit()
  return jsonify({"message": "Registrasi berhasil!", "user": new_user.to_dict()}), 201

@api_bp.route('/login', methods=['POST'])
def login():
  data = request.get_json()
  if not data: return jsonify({"message": "Permintaan harus berupa JSON"}), 400
  username = data.get('username')
  password = data.get('password')
  remember_me = data.get('remember_me', False)
  user = models.User.query.filter_by(username=username).first()
  if user is None or not user.check_password(password): # <--- PERBAIKAN DI SINI
    return jsonify({"message": "Username atau password salah."}), 401
  login_user(user, remember=remember_me)
  return jsonify({"message": "Login berhasil!", "user": user.to_dict()}), 200

@api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
  logout_user()
  return jsonify({"message": "Logout berhasil!"}), 200

@api_bp.route('/current_user', methods=['GET'])
@login_required
def get_current_user():
  return jsonify({"message": "User sedang login", "user": current_user.to_dict()}), 200


# --- API BARU: RIWAYAT RESERVASI PENGGUNA ---
@api_bp.route('/user/reservations', methods=['GET'])
@login_required
def get_user_reservations():
    # Mengambil reservasi berdasarkan user_id dari current_user yang sedang login
    reservations = models.Reservation.query.filter_by(user_id=current_user.id).all()
    reservations_data = [r.to_dict() for r in reservations]
    return jsonify(reservations_data)

# --- API BARU: RIWAYAT PESANAN PENGGUNA ---
@api_bp.route('/user/orders', methods=['GET'])
@login_required
def get_user_orders():
    # Mengambil pesanan berdasarkan user_id dari current_user yang sedang login
    orders = models.Order.query.filter_by(user_id=current_user.id).all()
    orders_data = [o.to_dict() for o in orders]
    return jsonify(orders_data)


# --- API BARU: MANAJEMEN PENGGUNA (untuk Pustakawan) ---
@api_bp.route('/admin/users', methods=['GET'])
@login_required
def get_all_users_admin():
    auth_check = is_librarian_required()
    if auth_check:
          return auth_check

    q = request.args.get('q', '').strip().lower()

    query = models.User.query

    if q:
          query = query.filter(
              db.or_(
                  models.User.full_name.ilike(f'%{q}%'),
                  models.User.username.ilike(f'%{q}%'),
                  models.User.email.ilike(f'%{q}%')
              )
          )

    users = query.all()
    users_data = [u.to_dict() for u in users]
    return jsonify(users_data)

@api_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user_admin(user_id):
  auth_check = is_librarian_required()
  if auth_check: return auth_check
  user = models.User.query.get_or_404(user_id)
  data = request.get_json()
  if not data:
    return jsonify({"message": "Permintaan harus berupa JSON"}), 400

  user.username = data.get('username', user.username)
  user.email = data.get('email', user.email)
  user.full_name = data.get('full_name', user.full_name)
  user.phone_number = data.get('phone_number', user.phone_number)
  user.is_librarian = data.get('is_librarian', user.is_librarian) # Bisa mengubah status pustakawan

  # Jika password diubah, pastikan di-hash
  if 'password' in data and data['password']:
    user.set_password(data['password'])

  db.session.commit()
  return jsonify({"message": f"Pengguna {user_id} berhasil diperbarui.", "user": user.to_dict()}), 200

@api_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user_admin(user_id):
  auth_check = is_librarian_required()
  if auth_check: return auth_check

  if current_user.id == user_id: # Admin tidak bisa menghapus dirinya sendiri
    return jsonify({"message": "Anda tidak bisa menghapus akun Anda sendiri."}), 400

  user = models.User.query.get_or_404(user_id)
  db.session.delete(user)
  db.session.commit()
  return jsonify({"message": "Pengguna berhasil dihapus."}), 200

# --- API BARU: MANAJEMEN BERITA/ARTIKEL ---

@api_bp.route('/news', methods=['GET'])
def get_all_news():

    q = request.args.get('q', '').strip().lower()

    query = models.Article.query

    if q:
        query = query.filter(
            db.or_(
                models.Article.title.ilike(f'%{q}%')
            )
        )

    newsArticle = query.all()
    newsArticle_data = [na.to_dict() for na in newsArticle]
    return jsonify(newsArticle_data)

@api_bp.route('/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
  news_article = models.Article.query.get_or_404(news_id)
  return jsonify(news_article.to_dict())

@api_bp.route('/admin/news', methods=['POST'])
@login_required
def add_news_admin():
    auth_check = is_librarian_required()
    if auth_check: return auth_check
    data = request.get_json()
    if not data: return jsonify({"message": "Permintaan harus berupa JSON"}), 400

    title = data.get('title')
    content = data.get('content')
    image_url = data.get('image_url')
    
    if not title or not content:
      return jsonify({"message": "Judul dan konten berita harus diisi."}), 400

    new_article = Article(
      title=title,
      content=content,
      author_id=current_user.id, # Penulis adalah user admin yang login
      image_url=image_url
    )
    db.session.add(new_article)
    db.session.commit()
    return jsonify({"message": "Berita berhasil ditambahkan", "article": new_article.to_dict()}), 201

@api_bp.route('/admin/news/<int:news_id>', methods=['PUT'])
@login_required
def edit_news_admin(news_id):
  auth_check = is_librarian_required()
  if auth_check: return auth_check
  news_article = models.Article.query.get_or_404(news_id)
  data = request.get_json()
  if not data: return jsonify({"message": "Permintaan harus berupa JSON"}), 400

  news_article.title = data.get('title', news_article.title)
  news_article.content = data.get('content', news_article.content)
  news_article.image_url = data.get('image_url', news_article.image_url)
  # publication_date bisa diupdate, atau biarkan default (creation date)
  # news_article.publication_date = datetime.utcnow() # Atau dari data.get('publication_date')

  db.session.commit()
  return jsonify({"message": "Berita berhasil diperbarui", "article": news_article.to_dict()}), 200

@api_bp.route('/admin/news/<int:news_id>', methods=['DELETE'])
@login_required
def delete_news_admin(news_id):
  auth_check = is_librarian_required()
  if auth_check: return auth_check
  news_article = models.Article.query.get_or_404(news_id)
  db.session.delete(news_article)
  db.session.commit()
  return jsonify({"message": "Berita berhasil dihapus"}), 200
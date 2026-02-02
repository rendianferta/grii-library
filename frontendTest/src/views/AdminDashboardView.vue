<template>
  <div class="admin-dashboard-container">
    <h1>Dashboard Admin</h1>
    <p v-if="currentUser">Selamat datang, Pustakawan {{ currentUser.full_name || currentUser.username }}!</p>
    <p v-else>Memuat informasi admin...</p>

    <div class="admin-nav">
      <button :class="{ active: currentSection === 'books' }" @click="currentSection = 'books'">Manajemen Buku</button>
      <button :class="{ active: currentSection === 'reservations' }" @click="currentSection = 'reservations'">Manajemen Reservasi</button>
      <button :class="{ active: currentSection === 'orders' }" @click="currentSection = 'orders'">Manajemen Pesanan</button>
      <button :class="{ active: currentSection === 'users' }" @click="currentSection = 'users'">Manajemen Pengguna</button>
      <button :class="{ active: currentSection === 'news' }" @click="currentSection = 'news'">Manajemen Berita</button>
    </div>

    <div v-if="currentSection === 'books'" class="admin-section">
      <h2>Manajemen Buku</h2>
      <div class="book-admin-actions">
        <button @click="showAddBookForm = true" class="add-button">Tambah Buku Baru</button>
        <button @click="exportCSV" class="export-btn">Ekspor Buku (CSV)</button>
        <input type="file" ref="csvFile" @change="importCSV" accept=".csv" style="display: none;">
        <button @click="csvFile.click()" class="import-btn">Impor Buku (CSV)</button>
      </div>

      <div class="search-bar">
        <input 
          type="text" 
          v-model="booksearchQuery" 
          @keyup.enter="fetchBooks" 
          placeholder="Cari judul atau penulis buku..."
        >
        <button @click="fetchBooks">Cari</button>
      </div>

      <table class="admin-table book-admin-table">
        <thead>
          <tr>
            <th>No</th>
            <th>Judul</th>
            <th>Penulis</th>
            <th>ISBN</th>
            <th>Stok</th>
            <th>Harga</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingBooks">
            <td colspan="7">Memuat buku...</td>
          </tr>
          <tr v-else-if="errorBooks">
            <td colspan="7" class="error-message">{{ errorBooks }}</td>
          </tr>
          <tr v-else-if="books.length === 0">
            <td colspan="7">Tidak ada buku.</td>
          </tr>
          <tr v-for="(book, index) in books" :key="book.id">
            <td>{{ index + 1 }}</td>
            <td>{{ book.title }}</td>
            <td>{{ book.author }}</td>
            <td>{{ book.isbn }}</td>
            <td>{{ book.stock }}</td>
            <td>Rp {{ formatPrice(book.price) }}</td>
            <td>
              <button @click="editBook(book)" class="edit-button">Edit</button>
              <button @click="deleteBook(book.id)" class="delete-button">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="currentSection === 'reservations'" class="admin-section">
      <h2>Manajemen Reservasi</h2>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="reservationsearchQuery" 
          @keyup.enter="fetchReservations" 
          placeholder="Cari peminjam, buku, atau status..."
        >
        <button @click="fetchReservations">Cari</button>
      </div>
      <table class="admin-table reservation-admin-table">
        <thead>
          <tr>
            <th>No</th>
            <th>Buku</th>
            <th>Peminjam</th>
            <th>Kontak</th>
            <th>Tgl. Res.</th>
            <th>Tgl. Ambil</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingReservations">
            <td colspan="8">Memuat reservasi...</td>
          </tr>
          <tr v-else-if="errorReservations">
            <td colspan="8" class="error-message">{{ errorReservations }}</td>
          </tr>
          <tr v-else-if="reservations.length === 0">
            <td colspan="8">Tidak ada reservasi.</td>
          </tr>
          <tr v-for="(reservation, index) in reservations" :key="reservation.id">
            <td>{{ index + 1 }}</td>
            <td>{{ reservation.book_title }} ({{ reservation.book_author }})</td>
            <td>{{ reservation.user_name }}</td>
            <td>{{ reservation.user_contact }}</td>
            <td>{{ formatDate(reservation.reservation_date) }}</td>
            <td>{{ reservation.pickup_date ? formatDate(reservation.pickup_date) : '-' }}</td>
            <td>
              <select v-model="reservation.status" @change="updateReservationStatus(reservation)">
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="borrowed">Borrowed</option>
                <option value="returned">Returned</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </td>
            <td>
              <button @click="updateReservationStatus(reservation)" class="save-button">Simpan</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="currentSection === 'orders'" class="admin-section">
      <h2>Manajemen Pesanan</h2>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="ordersearchQuery" 
          @keyup.enter="fetchOrders" 
          placeholder="Cari pembeli, buku, atau status..."
        >
        <button @click="fetchOrders">Cari</button>
      </div>
      <table class="admin-table order-admin-table">
        <thead>
          <tr>
            <th>No</th>
            <th>Buku</th>
            <th>Pembeli</th>
            <th>Qty</th>
            <th>Total Harga</th>
            <th>Tgl. Pes.</th>
            <th>Alamat</th>
            <th>Metode Bayar</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingOrders">
            <td colspan="10">Memuat pesanan...</td>
          </tr>
          <tr v-else-if="errorOrders">
            <td colspan="10" class="error-message">{{ errorOrders }}</td>
          </tr>
          <tr v-else-if="orders.length === 0">
            <td colspan="10">Tidak ada pesanan.</td>
          </tr>
          <tr v-for="(order, index) in orders" :key="order.id">
            <td>{{ index + 1 }}</td>
            <td>{{ order.book_title }} ({{ order.book_author }})</td>
            <td>{{ order.username }} ({{ order.user_email }})</td>
            <td>{{ order.quantity }}</td>
            <td>Rp {{ formatPrice(order.total_price) }}</td>
            <td>{{ formatDate(order.order_date) }}</td>
            <td>{{ order.shipping_address }}</td>
            <td>{{ order.payment_method }}</td>
            <td>
              <select v-model="order.status" @change="updateOrderStatus(order)">
                <option value="pending_payment">Pending Payment</option>
                <option value="paid">Paid</option>
                <option value="shipped">Shipped</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </td>
            <td>
              <button @click="updateOrderStatus(order)" class="save-button">Simpan</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="currentSection === 'users'" class="admin-section">
      <h2>Manajemen Pengguna</h2>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="usersearchQuery" 
          @keyup.enter="fetchUsers" 
          placeholder="Cari username, email, atau nama lengkap..."
        >
        <button @click="fetchUsers">Cari</button>
      </div>
      <table class="admin-table user-admin-table">
        <thead>
          <tr>
            <th>No</th>
            <th>Username</th>
            <th>Email</th>
            <th>Nama Lengkap</th>
            <th>No. Telepon</th>
            <th>Pustakawan?</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingUsers">
            <td colspan="7">Memuat pengguna...</td>
          </tr>
          <tr v-else-if="errorUsers">
            <td colspan="7" class="error-message">{{ errorUsers }}</td>
          </tr>
          <tr v-else-if="users.length === 0">
            <td colspan="7">Tidak ada pengguna.</td>
          </tr>
          <tr v-for="(user, index) in users" :key="user.id">
            <td>{{ index + 1 }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.full_name || '-' }}</td>
            <td>{{ user.phone_number || '-' }}</td>
            <td>
              <input type="checkbox" v-model="user.is_librarian" @change="updateUser(user)">
            </td>
            <td>
              <button @click="showEditUserForm(user)" class="edit-button">Edit</button>
              <button @click="deleteUser(user.id)" class="delete-button" :disabled="user.id === currentUser.id">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="currentSection === 'news'" class="admin-section">
      <h2>Manajemen Berita & Artikel</h2>
      <button @click="showAddNewsForm = true" class="add-button">Tambah Berita Baru</button>

      <div class="search-bar">
        <input 
          type="text" 
          v-model="newssearchQuery" 
          @keyup.enter="fetchNewsArticles" 
          placeholder="Cari judul berita..."
        >
        <button @click="fetchNewsArticles">Cari</button>
      </div>

      <table class="admin-table news-admin-table">
        <thead>
          <tr>
            <th>No</th>
            <th>Judul</th>
            <th>Penulis</th>
            <th>Tanggal Publikasi</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingNews">
            <td colspan="5">Memuat berita...</td>
          </tr>
          <tr v-else-if="errorNews">
            <td colspan="5" class="error-message">{{ errorNews }}</td>
          </tr>
          <tr v-else-if="newsArticles.length === 0">
            <td colspan="5">Tidak ada berita.</td>
          </tr>
          <tr v-for="(news, index) in newsArticles" :key="news.id">
            <td>{{ index + 1 }}</td>
            <td>{{ news.title }}</td>
            <td>{{ news.author_username }}</td>
            <td>{{ formatDate(news.publication_date) }}</td>
            <td>
              <button @click="editNews(news)" class="edit-button">Edit</button>
              <button @click="deleteNews(news.id)" class="delete-button">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>


    <div v-if="showAddBookForm || showEditBookForm" class="form-overlay">
      <div class="form-modal">
        <h2>{{ isEditMode ? 'Edit Buku' : 'Tambah Buku Baru' }}</h2>
        <form @submit.prevent="submitBookForm">
          <div class="form-group">
            <label for="title">Judul:</label>
            <input type="text" id="title" v-model="bookForm.title" required>
          </div>
          <div class="form-group">
            <label for="author">Penulis:</label>
            <input type="text" id="author" v-model="bookForm.author" required>
          </div>
          <div class="form-group">
            <label for="isbn">ISBN:</label>
            <input type="text" id="isbn" v-model="bookForm.isbn" required>
          </div>
          <div class="form-group">
            <label for="stock">Stok:</label>
            <input type="number" id="stock" v-model.number="bookForm.stock" min="0" required>
          </div>
          <div class="form-group">
            <label for="price">Harga:</label>
            <input type="number" id="price" v-model.number="bookForm.price" min="0" step="0.01" required>
          </div>
          <div class="form-group">
            <label for="synopsis">Sinopsis:</label>
            <textarea id="synopsis" v-model="bookForm.synopsis"></textarea>
          </div>
          <div class="form-group">
            <label for="publicationYear">Tahun Terbit:</label>
            <input type="number" id="publicationYear" v-model.number="bookForm.publication_year" min="1000" max="9999">
          </div>
          <div class="form-group">
            <label for="coverImageFile">Upload Gambar Sampul:</label>
            <input type="file" id="coverImageFile" ref="bookImageFileInput" @change="handleBookImageFileChange">
            <img v-if="bookForm.cover_image_url" :src="bookForm.cover_image_url" alt="Preview Sampul" class="image-preview">
          </div>
          <p v-if="formMessage" :class="{'success-message': formSuccess, 'error-message': !formSuccess}">
            {{ formMessage }}
          </p>
          
          <div class="form-actions">
            <button type="submit" :disabled="submittingForm">
              {{ submittingForm ? 'Memproses...' : (isEditMode ? 'Perbarui Buku' : 'Tambah Buku') }}
            </button>
            <button type="button" @click="closeBookForm" class="cancel-button">Batal</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showEditUserFormModal" class="form-overlay">
      <div class="form-modal">
        <h2>Edit Pengguna: {{ userForm.username }}</h2>
        <form @submit.prevent="submitUserForm">
          <div class="form-group">
            <label for="editUsername">Username:</label>
            <input type="text" id="editUsername" v-model="userForm.username" required>
          </div>
          <div class="form-group">
            <label for="editEmail">Email:</label>
            <input type="email" id="editEmail" v-model="userForm.email" required>
          </div>
          <div class="form-group">
            <label for="editFullName">Nama Lengkap:</label>
            <input type="text" id="editFullName" v-model="userForm.full_name">
          </div>
          <div class="form-group">
            <label for="editPhoneNumber">No. Telepon:</label>
            <input type="text" id="editPhoneNumber" v-model="userForm.phone_number">
          </div>
          <div class="form-group">
            <input type="checkbox" id="isLibrarian" v-model="userForm.is_librarian">
            <label for="isLibrarian">Adalah Pustakawan?</label>
          </div>
          <div class="form-group">
            <label for="editPassword">Password Baru (kosongkan jika tidak diubah):</label>
            <input type="password" id="editPassword" v-model="userForm.password">
          </div>
          
          <p v-if="userFormMessage" :class="{'success-message': userFormSuccess, 'error-message': !userFormSuccess}">
            {{ userFormMessage }}
          </p>
          
          <div class="form-actions">
            <button type="submit" :disabled="submittingUserForm">
              {{ submittingUserForm ? 'Memproses...' : 'Perbarui Pengguna' }}
            </button>
            <button type="button" @click="closeUserForm" class="cancel-button">Batal</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showAddNewsForm || showEditNewsForm" class="form-overlay">
      <div class="form-modal">
        <h2>{{ isEditNewsMode ? 'Edit Berita' : 'Tambah Berita Baru' }}</h2>
        <form @submit.prevent="submitNewsForm">
          <div class="form-group">
            <label for="newsTitle">Judul:</label>
            <input type="text" id="newsTitle" v-model="newsForm.title" required>
          </div>
          <div class="form-group">
            <label for="newsContent">Konten:</label>
            <textarea id="newsContent" v-model="newsForm.content" rows="10" required></textarea>
          </div>
          <div class="form-group">
            <label for="newsImageFile">Upload Gambar:</label>
            <input type="file" id="newsImageFile" ref="newsImageFileInput" @change="handleNewsImageFileChange">
            <img v-if="newsForm.image_url" :src="newsForm.image_url" alt="Preview Gambar" class="image-preview">
          </div>
          <p v-if="newsFormMessage" :class="{'success-message': newsFormSuccess, 'error-message': !newsFormSuccess}">
            {{ newsFormMessage }}
          </p>
          
          <div class="form-actions">
            <button type="submit" :disabled="submittingNewsForm">
              {{ submittingNewsForm ? 'Memproses...' : (isEditNewsMode ? 'Perbarui Berita' : 'Tambah Berita') }}
            </button>
            <button type="button" @click="closeNewsForm" class="cancel-button">Batal</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
// Bagian <script setup> dan <style> tidak diubah
import { ref, onMounted, watchEffect } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from '../composables/useToast'; // Pastikan ini diimpor
// Hapus useLoading jika tidak ingin global loading
// import { useLoading } from '../composables/useLoading';
const router = useRouter();
const { showToast } = useToast(); // Ambil fungsi showToast
// Hapus inisialisasi useLoading jika tidak diimpor
// const { startLoading, stopLoading } = useLoading();
const booksearchQuery = ref('');
const books = ref([]);
const loadingBooks = ref(true);
const errorBooks = ref(null);

const reservationsearchQuery = ref('');
const reservations = ref([]);
const loadingReservations = ref(true);
const errorReservations = ref(null);

const ordersearchQuery = ref('');const orders = ref([]);
const loadingOrders = ref(true);
const errorOrders = ref(null);

const usersearchQuery = ref('');
const users = ref([]);
const loadingUsers = ref(true);
const errorUsers = ref(null);

const newssearchQuery = ref('');
const newsArticles = ref([]);
const loadingNews = ref(true);
const errorNews = ref(null);

const currentUser = ref(null);
const currentSection = ref('books'); // default section yang aktif

const showAddBookForm = ref(false);
const showEditBookForm = ref(false);
const isEditMode = ref(false); // Untuk mode edit buku
const bookForm = ref({
 id: null, title: '', author: '', isbn: '', stock: 0, price: 0.0,
 synopsis: '', publication_year: null, cover_image_url: '' // Tambahkan cover_image_url
});
const submittingForm = ref(false); // Untuk submit buku
const formMessage = ref('');
const formSuccess = ref(false);
const bookImageFileInput = ref(null); // Ref untuk input file buku

const showEditUserFormModal = ref(false);
const userForm = ref({
  id: null, username: '', email: '', full_name: '', phone_number: '', is_librarian: false, password: ''
});
const submittingUserForm = ref(false);
const userFormMessage = ref('');
const userFormSuccess = ref(false);

const showAddNewsForm = ref(false);
const showEditNewsForm = ref(false);
const isEditNewsMode = ref(false); // Untuk mode edit berita
const newsForm = ref({
 id: null, title: '', content: '', image_url: '' // Tambahkan image_url
});
const submittingNewsForm = ref(false); // Untuk submit berita
const newsFormMessage = ref('');
const newsFormSuccess = ref(false);
const newsImageFileInput = ref(null); // Ref untuk input file berita
const formatPrice = (value) => {
 return new Intl.NumberFormat('id-ID', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
};

const formatDate = (isoString) => {
 if (!isoString) return '-';
 const date = new Date(isoString);
 const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
 return date.toLocaleDateString('id-ID', options);
};

// --- FUNGSI UPLOAD GAMBAR UMUM ---
const uploadImage = async (file) => {
 // startLoading(); // Aktifkan jika pakai loading global
 const formData = new FormData();
 formData.append('file', file);

 try {
  const response = await fetch('/api/upload', {
   method: 'POST',
   body: formData,
   credentials: 'include'
  });

  if (response.status === 401 || response.status === 403) {
   showToast('Anda tidak memiliki izin untuk mengunggah gambar. Silakan login sebagai pustakawan.', 'warning');
   router.push('/login');
   return null;
  }

  const data = await response.json();

  if (!response.ok) {
   throw new Error(data.message || 'Gagal mengunggah gambar.');
  }

  showToast('Gambar berhasil diunggah!', 'success');
  return data.file_url; // Mengembalikan URL gambar yang diunggah
 } catch (err) {
  console.error('Error saat mengunggah gambar:', err);
  showToast(err.message || 'Terjadi kesalahan saat mengunggah gambar.', 'error');
  return null;
 } finally {
  // stopLoading(); // Aktifkan jika pakai loading global
 }
};

// --- FUNGSI MANAJEMEN BUKU (Modifikasi untuk Upload Gambar Sampul) ---
const fetchBooks = async () => {
  loadingBooks.value = true;
  errorBooks.value = null;

  try {
    let url = '/api/books';
    const params = new URLSearchParams();

    if (booksearchQuery.value) {
      params.append('q', booksearchQuery.value);
    }

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();
    books.value = data;
  } catch (err) {
    console.error("Gagal mengambil buku:", err);
    errorBooks.value = "Gagal memuat buku. Silakan coba lagi nanti.";
    showToast('Gagal memuat buku.', 'error');
  } finally {
    loadingBooks.value = false;
  }
};


const handleBookImageFileChange = async (event) => { // Fungsi untuk input file buku
 const file = event.target.files[0];
 if (file) {
  const uploadedUrl = await uploadImage(file);
  if (uploadedUrl) {
   bookForm.value.cover_image_url = uploadedUrl;
  }
 }
};

const submitBookForm = async () => {
 submittingForm.value = true; formMessage.value = ''; formSuccess.value = false;

 // Hapus password field jika ada (tidak relevan untuk buku)
 const dataToSend = { ...bookForm.value };
 delete dataToSend.password;

 const url = isEditMode.value ? `/api/books/${bookForm.value.id}` : '/api/books';
 const method = isEditMode.value ? 'PUT' : 'POST';
 try {
  const response = await fetch(url, {
   method: method,
   headers: { 'Content-Type': 'application/json' },
   body: JSON.stringify(dataToSend), // Menggunakan dataToSend
   credentials: 'include'
  });

  if (response.status === 401 || response.status === 403) { formMessage.value = "Anda tidak memiliki izin untuk melakukan aksi ini. Silakan login sebagai pustakawan."; formSuccess.value = false; showToast('Anda tidak memiliki izin untuk melakukan aksi ini. Silakan login sebagai pustakawan.', 'warning'); router.push('/login'); return; }
  const data = await response.json(); if (!response.ok) { throw new Error(`HTTP error! status: ${response.status}`); }
  formMessage.value = data.message || `Buku berhasil ${isEditMode.value ? 'diperbarui' : 'ditambahkan'}!`; formSuccess.value = true;
  showToast(`Buku berhasil ${isEditMode.value ? 'diperbarui' : 'ditambahkan'}!`, 'success'); fetchBooks(); setTimeout(() => { closeBookForm(); }, 1500);
} catch (err) { console.error(`Error saat ${isEditMode.value ? 'memperbarui' : 'menambahkan'} buku:`, err); formMessage.value = err.message || `Terjadi kesalahan saat ${isEditMode.value ? 'memperbarui' : 'menambahkan'} buku.`; showToast(err.message || `Terjadi kesalahan saat ${isEditMode.value ? 'memperbarui' : 'menambahkan'} buku.`, 'error'); } finally { submittingForm.value = false; }
};
const editBook = (book) => { /* ... kode sama ... */
 isEditMode.value = true; showAddBookForm.value = true; bookForm.value = { ...book };
 if (bookImageFileInput.value) { bookImageFileInput.value.value = ''; }
};
const deleteBook = async (id) => { /* ... kode sama ... */
 if (!confirm('Apakah Anda yakin ingin menghapus buku ini? Aksi ini tidak dapat dibatalkan.')) { return; }
 try {
  const response = await fetch(`/api/books/${id}`, { method: 'DELETE', credentials: 'include' });
  if (response.status === 401 || response.status === 403) { showToast('Anda tidak memiliki izin untuk menghapus buku. Silakan login sebagai pustakawan.', 'warning'); router.push('/login'); return; }
  if (!response.ok) { const data = await response.json(); throw new Error(data.message || 'Gagal menghapus buku.'); }
  showToast('Buku berhasil dihapus!', 'success'); fetchBooks();
 } catch (err) { console.error('Error saat menghapus buku:', err); showToast(err.message || 'Terjadi kesalahan saat menghapus buku.', 'error'); } finally { }
};
const closeBookForm = () => { /* ... kode sama ... */
 showAddBookForm.value = false; showEditBookForm.value = false; isEditMode.value = false;
 bookForm.value = { id: null, title: '', author: '', isbn: '', stock: 0, price: 0.0, synopsis: '', publication_year: null, cover_image_url: '' };
 formMessage.value = ''; formSuccess.value = false;
 if (bookImageFileInput.value) { bookImageFileInput.value.value = ''; }
};

// --- FUNGSI MANAJEMEN RESERVASI (Tidak Berubah) ---
const fetchReservations = async () => { /* ... kode sama ... */
  loadingReservations.value = true
  errorReservations.value = null
 try {
    let url = '/api/admin/reservations'
    const params = new URLSearchParams()

    if (reservationsearchQuery.value) {
      params.append('q', reservationsearchQuery.value)
    }

    if (params.toString()) {
      url += `?${params.toString()}`
    }

    const response = await fetch(url, { credentials: 'include' })

    if (response.status === 401 || response.status === 403) {
      errorReservations.value = "Anda tidak memiliki izin untuk melihat reservasi. Silakan login sebagai pustakawan."
      showToast('Anda tidak memiliki izin untuk melihat reservasi.', 'warning')
      router.push('/login')
      return
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    reservations.value = data
    
  } catch (err) {
    console.error("Gagal mengambil reservasi:", err)
    errorReservations.value = "Gagal memuat reservasi. Silakan coba lagi nanti."
    showToast('Gagal memuat reservasi.', 'error')
  } finally {
    console.log(reservations.value)
    loadingReservations.value = false
  }
};
const updateReservationStatus = async (reservation) => { /* ... kode sama ... */
 try {
  const response = await fetch(`/api/admin/reservations/${reservation.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: reservation.status }), credentials: 'include' });
  if (response.status === 401 || response.status === 403) { showToast('Anda tidak memiliki izin untuk mengubah status reservasi. Silakan login sebagai pustakawan.', 'warning'); router.push('/login'); return; }
  if (!response.ok) { const data = await response.json(); throw new Error(data.message || 'Gagal memperbarui status reservasi.'); }
  showToast(`Status reservasi ${reservation.id} berhasil diperbarui menjadi ${reservation.status}!`, 'success');
  fetchReservations(); fetchBooks();
 } catch (err) { console.error('Error saat update status reservasi:', err); showToast(err.message || 'Terjadi kesalahan saat memperbarui status reservasi.', 'error'); } finally { }
};

// --- FUNGSI MANAJEMEN PESANAN (Tidak Berubah) ---
const fetchOrders = async () => { /* ... kode sama ... */
 loadingOrders.value = true
 errorOrders.value = null
 try {
    let url = '/api/admin/orders'
    const params = new URLSearchParams()

    if (ordersearchQuery.value) {
      params.append('q', ordersearchQuery.value)
    }

    if (params.toString()) {
      url += `?${params.toString()}`
    }

    const response = await fetch(url, { credentials: 'include' })

    if (response.status === 401 || response.status === 403) {
      errorOrders.value = "Anda tidak memiliki izin untuk melihat pesanan. Silakan login sebagai pustakawan."
      showToast('Anda tidak memiliki izin untuk melihat pesanan.', 'warning')
      router.push('/login')
      return
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    orders.value = data
    
  } catch (err) {
    console.error("Gagal mengambil pesanan:", err)
    errorOrders.value = "Gagal memuat pesanan. Silakan coba lagi nanti."
    showToast('Gagal memuat reservasi.', 'error')
  } finally {
    console.log(orders.value)
    loadingOrders.value = false
  }
};

const updateOrderStatus = async (order) => { /* ... kode sama ... */
 try {
  const response = await fetch(`/api/admin/orders/${order.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: order.status }), credentials: 'include' });
  if (response.status === 401 || response.status === 403) { showToast('Anda tidak memiliki izin untuk mengubah status pesanan. Silakan login sebagai pustakawan.', 'warning'); router.push('/login'); return; }
  if (!response.ok) { const data = await response.json(); throw new Error(data.message || 'Gagal memperbarui status pesanan.'); }
  showToast(`Status pesanan ${order.id} berhasil diperbarui menjadi ${order.status}!`, 'success'); fetchOrders();
 } catch (err) { console.error('Error saat update status pesanan:', err); showToast(err.message || 'Terjadi kesalahan saat memperbarui status pesanan.', 'error'); } finally { }
};

// --- FUNGSI MANAJEMEN PENGGUNA ---
const fetchUsers = async () => { /* ... kode sama ... */
  loadingUsers.value = true
  errorUsers.value = null
 try {
    let url = '/api/admin/users'
    const params = new URLSearchParams()

    if (usersearchQuery.value) {
      params.append('q', usersearchQuery.value)
    }

    if (params.toString()) {
      url += `?${params.toString()}`
    }

    const response = await fetch(url, { credentials: 'include' })

    if (response.status === 401 || response.status === 403) {
      errorUsers.value = "Anda tidak memiliki izin untuk melihat pengguna. Silakan login sebagai pustakawan."
      showToast('Anda tidak memiliki izin untuk melihat pengguna.', 'warning')
      router.push('/login')
      return
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    users.value = data
    
  } catch (err) {
    console.error("Gagal mengambil pengguna:", err)
    errorUsers.value = "Gagal memuat pengguna. Silakan coba lagi nanti."
    showToast('Gagal memuat pengguna.', 'error')
  } finally {
    console.log(users.value)
    loadingUsers.value = false
  }
};
const showEditUserForm = (user) => { /* ... kode sama ... */
 showEditUserFormModal.value = true; userForm.value = { ...user, password: '' };
};
const submitUserForm = async () => { /* ... kode sama ... */
 submittingUserForm.value = true; userFormMessage.value = ''; userFormSuccess.value = false;
 try {
  const response = await fetch(`/api/admin/users/${userForm.value.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(userForm.value), credentials: 'include' });
  if (response.status === 401 || response.status === 403) { userFormMessage.value = "Anda tidak memiliki izin untuk mengedit pengguna."; userFormSuccess.value = false; showToast('Anda tidak memiliki izin untuk mengedit pengguna.', 'warning'); router.push('/login'); return; }
  const data = await response.json(); if (!response.ok) { throw new Error(data.message || 'Gagal memperbarui pengguna.'); }
  userFormMessage.value = data.message || "Pengguna berhasil diperbarui!"; userFormSuccess.value = true;
  showToast('Pengguna berhasil diperbarui!', 'success'); fetchUsers(); setTimeout(() => { closeUserForm(); }, 1500);
 } catch (err) { console.error('Error saat update pengguna:', err); userFormMessage.value = err.message || 'Terjadi kesalahan saat memperbarui pengguna.'; showToast(err.message || 'Terjadi kesalahan saat memperbarui pengguna.', 'error'); } finally { submittingUserForm.value = false; }
};
const deleteUser = async (id) => { /* ... kode sama ... */
 if (!confirm('Apakah Anda yakin ingin menghapus pengguna ini? Aksi ini tidak dapat dibatalkan.')) { return; }
 try {
  const response = await fetch(`/api/admin/users/${id}`, { method: 'DELETE', credentials: 'include' });
  if (response.status === 401 || response.status === 403) { showToast('Anda tidak memiliki izin untuk menghapus pengguna.', 'warning'); router.push('/login'); return; }
  if (!response.ok) { const data = await response.json(); throw new Error(data.message || 'Gagal menghapus pengguna.'); }
  showToast('Pengguna berhasil dihapus!', 'success'); fetchUsers();
 } catch (err) { console.error('Error saat menghapus pengguna:', err); showToast(err.message || 'Terjadi kesalahan saat menghapus pengguna.', 'error'); } finally { }
};
const closeUserForm = () => { /* ... kode sama ... */
 showEditUserFormModal.value = false; userForm.value = { id: null, username: '', email: '', full_name: '', phone_number: '', is_librarian: false, password: '' };
 userFormMessage.value = ''; userFormSuccess.value = false;
};

// --- FUNGSI MANAJEMEN BERITA ---
const fetchNewsArticles = async () => {
 loadingNews.value = true
  errorNews.value = null
 try {
    let url = '/api/news'
    const params = new URLSearchParams()

    if (newssearchQuery.value) {
      params.append('q', newssearchQuery.value)
    }

    if (params.toString()) {
      url += `?${params.toString()}`
    }

    const response = await fetch(url, { credentials: 'include' })

    if (response.status === 401 || response.status === 403) {
      errorNews.value = "Anda tidak memiliki izin untuk melihat berita. Silakan login sebagai pustakawan."
      showToast('Anda tidak memiliki izin untuk melihat berita.', 'warning')
      router.push('/login')
      return
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    newsArticles.value = data
    
  } catch (err) {
    console.error("Gagal mengambil berita:", err)
    errorNews.value = "Gagal memuat berita. Silakan coba lagi nanti."
    showToast('Gagal memuat berita.', 'error')
  } finally {
    console.log(newsArticles.value)
    loadingNews.value = false
  }
};

const handleNewsImageFileChange = async (event) => { // Fungsi untuk input file berita
 const file = event.target.files[0];
 if (file) {
  const uploadedUrl = await uploadImage(file);
  if (uploadedUrl) {
   newsForm.value.image_url = uploadedUrl;
  }
 }
};

const submitNewsForm = async () => {
 submittingNewsForm.value = true; newsFormMessage.value = ''; newsFormSuccess.value = false;

 const url = isEditNewsMode.value ? `/api/admin/news/${newsForm.value.id}` : '/api/admin/news';
 const method = isEditNewsMode.value ? 'PUT' : 'POST';

 try {
  // --- PENTING: Panggil uploadImage dan tunggu hasilnya di sini ---
  if (newsImageFileInput.value && newsImageFileInput.value.files[0]) {
   const file = newsImageFileInput.value.files[0];
   const uploadedUrl = await uploadImage(file);
   if (uploadedUrl) {
    newsForm.value.image_url = uploadedUrl; // Pastikan newsForm.image_url terupdate
   } else {
    // Jika upload gagal, hentikan proses submit form berita
    newsFormMessage.value = "Gagal mengunggah gambar, tidak dapat menyimpan berita.";
    newsFormSuccess.value = false;
    submittingNewsForm.value = false;
    return;
   }
  } else if (newsForm.value.image_url === '') {
   // Jika tidak ada file baru dan image_url kosong, set ke null agar tidak ada string kosong di DB
   newsForm.value.image_url = null;
  }
  // --- AKHIR LOGIKA PENTING ---

  const response = await fetch(url, {
   method: method,
   headers: { 'Content-Type': 'application/json' },
   body: JSON.stringify(newsForm.value), // newsForm.value sekarang dijamin memiliki image_url yang benar
   credentials: 'include'
  });

  if (response.status === 401 || response.status === 403) {
   newsFormMessage.value = "Anda tidak memiliki izin untuk mengelola berita. Silakan login sebagai pustakawan.";
   newsFormSuccess.value = false; showToast('Anda tidak memiliki izin untuk mengelola berita.', 'warning'); router.push('/login'); return;
  }

  const data = await response.json();

  if (!response.ok) {
   throw new Error(data.message || 'Operasi gagal.');
  }

  newsFormMessage.value = data.message || `Berita berhasil ${isEditNewsMode.value ? 'diperbarui' : 'ditambahkan'}!`;
  newsFormSuccess.value = true;
  showToast('Berita berhasil diperbarui!', 'success'); fetchNewsArticles(); setTimeout(() => { closeNewsForm(); }, 1500);
 } catch (err) { console.error(`Error saat ${isEditNewsMode.value ? 'memperbarui' : 'menambahkan'} berita:`, err); newsFormMessage.value = err.message || `Terjadi kesalahan saat ${isEditNewsMode.value ? 'memperbarui' : 'menambahkan'} berita.`; showToast(err.message || `Terjadi kesalahan saat ${isEditMode.value ? 'memperbarui' : 'menambahkan'} berita.`, 'error'); } finally { submittingNewsForm.value = false; }
};

const editNews = (news) => {
 isEditNewsMode.value = true; showEditNewsForm.value = true; newsForm.value = { ...news };
 if (newsImageFileInput.value) { newsImageFileInput.value.value = ''; }
};

const deleteNews = async (id) => {
 if (!confirm('Apakah Anda yakin ingin menghapus berita ini? Aksi ini tidak dapat dibatalkan.')) { return; }
 try {
  const response = await fetch(`/api/admin/news/${id}`, { method: 'DELETE', credentials: 'include' });
  if (response.status === 401 || response.status === 403) { showToast('Anda tidak memiliki izin untuk menghapus berita.', 'warning'); router.push('/login'); return; }
  if (!response.ok) { const data = await response.json(); throw new Error(data.message || 'Gagal menghapus berita.'); }
  showToast('Berita berhasil dihapus!', 'success'); fetchNewsArticles();
 } catch (err) { console.error('Error saat menghapus berita:', err); showToast(err.message || 'Terjadi kesalahan saat menghapus berita.', 'error'); } finally { }
};

const closeNewsForm = () => {
 showAddNewsForm.value = false; showEditNewsForm.value = false; isEditNewsMode.value = false;
 newsForm.value = { id: null, title: '', content: '', image_url: '' };
 newsFormMessage.value = ''; newsFormSuccess.value = false;
 if (newsImageFileInput.value) {
  newsImageFileInput.value.value = '';
 }
};

// --- MENAMBIL INFO USER SAAT INI & MEMUTUSKAN FETCHER ---
watchEffect(async () => {
 try {
  const response = await fetch('/api/current_user', { credentials: 'include' });
  if (response.ok) {
   const data = await response.json();
   currentUser.value = data.user;
   if (currentUser.value && currentUser.value.is_librarian) {
    fetchBooks(); fetchReservations(); fetchOrders(); fetchUsers(); fetchNewsArticles();
   } else {
    books.value = []; reservations.value = []; orders.value = []; users.value = []; newsArticles.value = [];
    loadingBooks.value = false; loadingReservations.value = false; loadingOrders.value = false; loadingUsers.value = false; loadingNews.value = false;
   }
  } else {
   currentUser.value = null;
   books.value = []; reservations.value = []; orders.value = []; users.value = []; newsArticles.value = [];
   loadingBooks.value = false; loadingReservations.value = false; loadingOrders.value = false; loadingUsers.value = false; loadingNews.value = false;
  }
 } catch (error) {
  console.error("Gagal memuat user saat ini di dashboard admin:", error);
  currentUser.value = null;
  books.value = []; reservations.value = []; orders.value = []; users.value = []; newsArticles.value = [];
  loadingBooks.value = false; loadingReservations.value = false; loadingOrders.value = false; loadingUsers.value = false; loadingNews.value = false;
 }
});

const csvFile = ref(null)

function exportCSV() { // <--- Fungsi exportCSV() ada
  fetch("/api/admin/books/export", { // <-- Masalah URL ada di sini
    credentials: 'include'
  })
    .then(res => res.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "books.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch(err => {
      alert("Gagal mengekspor CSV.");
      console.error(err);
    });
}

function importCSV() { // <--- Fungsi importCSV() ada
  const file = csvFile.value?.files[0]
  if (!file) {
    alert("Pilih file CSV terlebih dahulu.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  fetch("/api/admin/books/import", { // <-- Masalah URL ada di sini
    method: "POST",
    body: formData,
    credentials: 'include'
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      location.reload();
    })
    .catch(err => {
      alert("Gagal mengimpor CSV.");
      console.error(err);
    });

}

onMounted(() => {
 // watchEffect akan menangani pemanggilan fetcher awal
});
</script>

<style scoped>
/* Semua styling dari sebelumnya */
.admin-dashboard-container {
 max-width: 1200px; margin: 20px auto; padding: 25px;
 background-color: #f9f9f9; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.admin-dashboard-container h1 { text-align: center; color: #333; margin-bottom: 20px; }
.admin-dashboard-container p { text-align: center; color: #555; margin-bottom: 30px; }

.admin-nav {
 display: flex; justify-content: center; gap: 10px; margin-bottom: 30px;
 background-color: #e9ecef; padding: 10px; border-radius: 8px; flex-wrap: wrap;
}
.admin-nav button {
 padding: 10px 15px; border: none; border-radius: 5px; background-color: #f8f9fa; cursor: pointer; font-size: 1em;
 transition: background-color 0.3s ease, color
 0.3s ease;
}
.admin-nav button.active { background-color: #007bff; color: white; box-shadow: 0 2px 5px rgba(0, 123, 255, 0.2); }
.admin-nav button:hover:not(.active) { background-color: #e2e6ea; }

.admin-section {
 background-color: #fff; padding: 25px; border-radius: 8px;
 box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); margin-bottom: 30px;
}
.admin-section h2 { color: #007bff; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.add-button {
 background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; margin-bottom: 20px; transition: background-color 0.3s ease;
}
.add-button:hover { background-color: #218838; }

.admin-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9em; }
.admin-table th, .admin-table td { border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }
.admin-table th { background-color: #f2f2f2; font-weight: bold; color: #333; }
.admin-table tr:nth-child(even) { background-color: #f9f9f9; }
.admin-table tr:hover { background-color: #eef; }
.admin-table td button {
 padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px; margin-bottom: 5px; transition: background-color
 0.3s ease;
}
.edit-button { background-color: #ffc107; color: #333; }
.edit-button:hover { background-color: #e0a800; }
.delete-button { background-color: #dc3545; color: white; }
.delete-button:hover { background-color: #c82333; }
.save-button { background-color: #007bff; color: white; }
.save-button:hover { background-color: #0056b3; }
.admin-table td select { padding: 6px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9em; width: 120px; }

/* Form Overlay/Modal Styles */
.form-overlay {
 position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5);
 display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.form-modal {
 background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
 width: 90%; max-width: 600px; box-sizing: border-box; max-height: 90vh; overflow-y: auto;
}
.form-modal h2 { text-align: center; color: #333; margin-bottom: 20px; margin-top: 0; }
.form-group { margin-bottom: 15px; text-align: left; }
.form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
.form-group input, .form-group textarea, .form-group select {
 width: calc(100% - 20px); padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; box-sizing: border-box;
}
.form-group input[type="checkbox"] { width: auto; margin-right: 8px; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.form-actions button {
 padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; transition: background-color 0.3s ease;
}
.form-actions button[type="submit"] { background-color: #007bff; color: white; }
.form-actions button[type="submit"]:hover:not(:disabled) { background-color: #0056b3; }
.form-actions button:disabled { background-color: #cccccc; cursor: not-allowed; }
.cancel-button { background-color: #6c757d; color: white; }
.cancel-button:hover { background-color: #5a6268; }

.success-message {
 color: #28a745; background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 5px; margin-top: 15px;
}
.error-message {
 color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 5px; margin-top: 15px;
}

.search-bar input {
  width: 100%;
  max-width: 400px;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 25px;
  font-size: 1em;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.search-bar button {
  padding: 10px 25px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease;
}

.search-bar button:hover {
  background-color: #0056b3;
}

/* Gambar preview di form */
.image-preview {
  max-width: 100px;
  max-height: 100px;
  margin-top: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
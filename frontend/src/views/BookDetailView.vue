<template>
  <div class="book-detail-container">
    <router-link to="/katalog" class="back-link">&lt; Kembali ke Katalog</router-link>

    <template v-if="loading">
      <p>Memuat detail buku...</p>
    </template>
    <template v-else-if="error">
      <p>{{ error }}</p>
    </template>
    <template v-else-if="book">
      <div class="book-detail-content">
        <div class="detail-header">
          <img :src="book.cover_image_url || 'https://via.placeholder.com/250x350?text=No+Image'" :alt="book.title" class="detail-cover-image">
          <div class="detail-info">
            <h1>{{ book.title }}</h1>
            <p><strong>Oleh:</strong> {{ book.author }}</p>
            <p><strong>Penerbit:</strong> {{ book.publisher || 'Tidak Diketahui' }}</p>
            <p><strong>Tahun Terbit:</strong> {{ book.publication_year || 'Tidak Diketahui' }}</p>
            <p><strong>ISBN:</strong> {{ book.isbn }}</p>
            <p><strong>Stok Tersedia:</strong> <span :class="{'stock-low': book.stock < 3, 'stock-zero': book.stock === 0}">{{ book.stock }}</span></p>
            <p class="price">Harga: Rp {{ formatPrice(book.price) }}</p>
          </div>
        </div>
        <div class="detail-synopsis">
          <h3>Sinopsis</h3>
          <p>{{ book.synopsis || 'Sinopsis belum tersedia.' }}</p>
        </div>

        <div class="action-buttons">
          <button 
            class="action-button reserve-button" 
            @click="showReservationForm = true" 
            :disabled="book.stock === 0"
          >
            {{ book.stock === 0 ? 'Stok Habis' : 'Reservasi Peminjaman' }}
          </button>
          <button 
            class="action-button buy-button" 
            @click="showPurchaseForm = true" 
            :disabled="book.stock === 0"
          >
            {{ book.stock === 0 ? 'Stok Habis' : 'Beli Buku' }}
          </button>
        </div>

        <div v-if="showReservationForm" class="reservation-form-overlay">
          <div class="reservation-form-modal">
            <h2>Reservasi Buku: {{ book.title }}</h2>
            <form @submit.prevent="submitReservation">
              <div class="form-group">
                <label for="userName">Nama Lengkap:</label>
                <input type="text" id="userName" v-model="reservationForm.userName" required>
              </div>
              <div class="form-group">
                <label for="userContact">Email / No. Telepon:</label>
                <input type="text" id="userContact" v-model="reservationForm.userContact" required>
              </div>
              <div class="form-group">
                <label for="pickupDate">Tanggal Pengambilan (Opsional):</label>
                <input type="date" id="pickupDate" v-model="reservationForm.pickupDate">
              </div>
              
              <div v-if="reservationMessage" :class="{'success-message': reservationSuccess, 'error-message': !reservationSuccess}">
                {{ reservationMessage }}
              </div>

              <div class="form-actions">
                <button type="submit" :disabled="submittingReservation">
                  {{ submittingReservation ? 'Mengirim...' : 'Kirim Reservasi' }}
                </button>
                <button type="button" @click="closeReservationForm" class="cancel-button">Batal</button>
              </div>
            </form>
          </div>
        </div>

        <div v-if="showPurchaseForm" class="purchase-form-overlay">
          <div class="purchase-form-modal">
            <h2>Beli Buku: {{ book.title }}</h2>
            <form @submit.prevent="submitPurchase">
              <div class="form-group">
                <label for="purchaseQuantity">Jumlah:</label>
                <input type="number" id="purchaseQuantity" v-model.number="purchaseForm.quantity" min="1" :max="book.stock" required>
                <p v-if="purchaseForm.quantity > book.stock" class="error-message-inline">Stok tidak cukup.</p>
              </div>
              <div class="form-group">
                <label for="shippingAddress">Alamat Pengiriman:</label>
                <textarea id="shippingAddress" v-model="purchaseForm.shippingAddress" required></textarea>
              </div>
              <div class="form-group">
                <label for="paymentMethod">Metode Pembayaran:</label>
                <select id="paymentMethod" v-model="purchaseForm.paymentMethod" required>
                  <option value="">Pilih Metode</option>
                  <option value="QRIS">QRIS</option>
                  <option value="Transfer Bank">Transfer Bank</option>
                  <option value="Dana">Dana</option>
                  <option value="OVO">OVO</option>
                </select>
              </div>
              
              <p class="total-price-display">Total Harga: Rp {{ formatPrice(book.price * purchaseForm.quantity) }}</p>

              <div v-if="purchaseMessage" :class="{'success-message': purchaseSuccess, 'error-message': !purchaseSuccess}">
                {{ purchaseMessage }}
              </div>

              <div v-if="purchaseSuccess && purchaseForm.paymentMethod === 'QRIS'" class="payment-info qris-info">
                  <h3>Scan untuk Pembayaran QRIS</h3>
                  <img src="https://via.placeholder.com/300x300?text=QRIS+CODE" alt="QRIS Code" class="qris-image">
                  <p>Jumlah yang harus dibayar: <strong>Rp {{ formatPrice(book.price * purchaseForm.quantity) }}</strong></p>
                  <p>Pastikan jumlah pembayaran sesuai.</p>
              </div>
              <div v-if="purchaseSuccess" class="payment-info whatsapp-info">
                  <h3>Konfirmasi Pesanan</h3>
                  <p>Untuk konfirmasi pembayaran atau pertanyaan lebih lanjut, silakan hubungi kami via WhatsApp:</p>
                  <a :href="whatsappLink" target="_blank" class="whatsapp-button">
                      <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/1200px-WhatsApp.svg.png" alt="WhatsApp Icon" style="width: 24px; vertical-align: middle; margin-right: 8px;">
                      Hubungi Pustakawan via WhatsApp
                  </a>
                  <p class="whatsapp-number">atau hubungi langsung: +62 812-3456-7890</p>
                  <p>Kode Pesanan Anda: <strong>#{{ lastOrderId }}</strong></p>
              </div>

              <div class="form-actions">
                <button type="submit" :disabled="submittingPurchase || purchaseForm.quantity > book.stock || purchaseForm.quantity <= 0 || purchaseSuccess">
                  {{ submittingPurchase ? 'Memproses...' : (purchaseSuccess ? 'Pesanan Dibuat' : 'Beli Sekarang') }}
                </button>
                <button type="button" @click="closePurchaseForm" class="cancel-button">Batal</button>
              </div>
            </form>
          </div>
        </div>

      </div>
    </template>
    <template v-else>
      <p>Buku tidak ditemukan.</p>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from '../composables/useToast'; // Tambahkan ini di script setup
const { showToast } = useToast(); // Tambahkan ini di script setup

const route = useRoute();
const router = useRouter();
const book = ref(null);
const loading = ref(true);
const error = ref(null);

const showReservationForm = ref(false);
const reservationForm = ref({
  userName: '',
  userContact: '',
  pickupDate: ''
});
const submittingReservation = ref(false);
const reservationMessage = ref('');
const reservationSuccess = ref(false);

const showPurchaseForm = ref(false);
const purchaseForm = ref({
  quantity: 1,
  shippingAddress: '',
  paymentMethod: ''
});
const submittingPurchase = ref(false);
const purchaseMessage = ref('');
const purchaseSuccess = ref(false);
const lastOrderId = ref(null); // Untuk menyimpan ID pesanan terakhir
const whatsappNumber = '6281234567890'; // Ganti dengan nomor WhatsApp pustakawan
const whatsappMessageTemplate = (orderId, bookTitle, quantity, totalPrice) => 
  `Halo Pustakawan, saya ingin mengonfirmasi pesanan buku saya.\n` +
  `Kode Pesanan: #${orderId}\n` +
  `Buku: ${bookTitle} (${quantity} buah)\n` +
  `Total Pembayaran: Rp ${formatPrice(totalPrice)}\n` +
  `Terima kasih.`;

const whatsappLink = ref('');


const formatPrice = (value) => {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value).replace('IDR', '');
};


const fetchBookDetail = async (id) => {
  loading.value = true;
  error.value = null;
  book.value = null;
  try {
    const response = await fetch(`/api/books/${id}`);
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("Buku tidak ditemukan.");
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    book.value = data;
    // Set default quantity berdasarkan stok jika stok ada
    if (book.value.stock > 0) {
      purchaseForm.value.quantity = 1;
    } else {
      purchaseForm.value.quantity = 0;
    }
  } catch (err) {
    console.error("Gagal mengambil detail buku:", err);
    error.value = err.message || "Gagal memuat detail buku. Silakan coba lagi nanti.";
  } finally {
    loading.value = false;
  }
};

const submitReservation = async () => {
  submittingReservation.value = true;
  reservationMessage.value = '';
  reservationSuccess.value = false;

  try {
    const response = await fetch('/api/reservations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        book_id: book.value.id,
        user_name: reservationForm.value.userName,
        user_contact: reservationForm.value.userContact,
        pickup_date: reservationForm.value.pickupDate || null
      }),
      credentials: 'include'
    });

    if (response.status === 401) {
      reservationMessage.value = "Anda perlu login untuk melakukan reservasi.";
      showToast('Anda perlu login untuk reservasi buku!', 'error')
      reservationSuccess.value = false;
      router.push('/login');
      return;
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || `HTTP error! status: ${response.status}`);
    }

    reservationMessage.value = data.message || "Reservasi berhasil diajukan!";
    reservationSuccess.value = true;
    fetchBookDetail(book.value.id); // Refresh data buku untuk update stok
    
  } catch (err) {
    console.error("Gagal mengirim reservasi:", err);
    reservationMessage.value = err.message || "Terjadi kesalahan saat reservasi.";
    reservationSuccess.value = false;
  } finally {
    submittingReservation.value = false;
  }
};

const closeReservationForm = () => {
  showReservationForm.value = false;
  reservationForm.value = { userName: '', userContact: '', pickupDate: '' };
  reservationMessage.value = '';
  reservationSuccess.value = false;
};

const submitPurchase = async () => {
  submittingPurchase.value = true;
  purchaseMessage.value = '';
  purchaseSuccess.value = false;

  if (purchaseForm.value.quantity <= 0 || purchaseForm.value.quantity > book.value.stock) {
    purchaseMessage.value = "Kuantitas tidak valid atau melebihi stok.";
    purchaseSuccess.value = false;
    submittingPurchase.value = false;
    return;
  }
  if (!purchaseForm.value.shippingAddress || !purchaseForm.value.paymentMethod) {
    purchaseMessage.value = "Alamat pengiriman dan metode pembayaran harus diisi.";
    purchaseSuccess.value = false;
    submittingPurchase.value = false;
    return;
  }

  try {
    const response = await fetch('/api/orders', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        book_id: book.value.id,
        quantity: purchaseForm.value.quantity,
        shipping_address: purchaseForm.value.shippingAddress,
        payment_method: purchaseForm.value.paymentMethod
      }),
      credentials: 'include'
    });

    if (response.status === 401) {
      purchaseMessage.value = "Anda perlu login untuk melakukan pembelian.";
      purchaseSuccess.value = false;
      router.push('/login');
      return;
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || `HTTP error! status: ${response.status}`);
    }

    purchaseMessage.value = data.message || "Pesanan berhasil dibuat!";
    purchaseSuccess.value = true;
    lastOrderId.value = data.order ? data.order.id : 'N/A'; // Ambil ID pesanan
    
    // Siapkan link WhatsApp setelah pesanan berhasil
    whatsappLink.value = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(
      whatsappMessageTemplate(
        lastOrderId.value,
        book.value.title,
        purchaseForm.value.quantity,
        book.value.price * purchaseForm.value.quantity
      )
    )}`;

    fetchBookDetail(book.value.id); // Refresh data buku untuk update stok

  } catch (err) {
    console.error("Gagal mengirim pesanan:", err);
    purchaseMessage.value = err.message || "Terjadi kesalahan saat membuat pesanan.";
    purchaseSuccess.value = false;
  } finally {
    submittingPurchase.value = false;
  }
};

const closePurchaseForm = () => {
  showPurchaseForm.value = false;
  purchaseForm.value = { quantity: 1, shippingAddress: '', paymentMethod: '' };
  purchaseMessage.value = '';
  purchaseSuccess.value = false;
  lastOrderId.value = null; // Reset ID pesanan
};

onMounted(() => {
  fetchBookDetail(route.params.id);
});

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchBookDetail(newId);
  }
});
</script>

<style scoped>
/* Semua styling dari sebelumnya */
.book-detail-container {
  max-width: 900px;
  margin: 20px auto;
  padding: 25px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}
.back-link {
  display: inline-block;
  margin-bottom: 20px;
  color: #007bff;
  text-decoration: none;
  font-weight: bold;
}
.back-link:hover { text-decoration: underline; }
.detail-header {
  display: flex; flex-direction: column; align-items: center; gap: 25px; margin-bottom: 30px;
}
.detail-cover-image {
  width: 250px; height: 350px; object-fit: cover; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
.detail-info { text-align: center; }
.detail-info h1 {
  font-size: 2.2em; color: #333; margin-bottom: 10px;
}
.detail-info p { font-size: 1.1em; color: #555; margin-bottom: 5px; }
.detail-info .price {
  font-size: 1.4em; color: #28a745; font-weight: bold; margin-top: 15px;
}
.stock-low { color: orange; font-weight: bold; }
.stock-zero { color: red; font-weight: bold; }
.detail-synopsis {
  background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); margin-bottom: 30px;
}
.detail-synopsis h3 {
  font-size: 1.5em; color: #333; margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;
}
.detail-synopsis p { line-height: 1.6; color: #444; }
.action-buttons {
  display: flex; justify-content: center; gap: 20px;
}
.action-button {
  padding: 12px 25px; font-size: 1.1em; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s ease, transform 0.2s ease;
}
.reserve-button { background-color: #007bff; color: white; }
.reserve-button:hover:not(:disabled) { background-color: #0056b3; transform: translateY(-2px); }
.buy-button { background-color: #28a745; color: white; }
.buy-button:hover:not(:disabled) { background-color: #218838; transform: translateY(-2px); }
@media (min-width: 768px) {
  .detail-header { flex-direction: row; text-align: left; align-items: flex-start; }
  .detail-info { text-align: left; }
}

.success-message {
  color: #28a745;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
}

/* Styling untuk formulir reservasi dan pembelian */
.reservation-form-overlay, .purchase-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.reservation-form-modal, .purchase-form-modal {
  background-color: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 500px;
  box-sizing: border-box;
}

.reservation-form-modal h2, .purchase-form-modal h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.reservation-form-modal .form-group, .purchase-form-modal .form-group {
  margin-bottom: 15px;
}

.reservation-form-modal .form-group label, .purchase-form-modal .form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.reservation-form-modal .form-group input,
.purchase-form-modal .form-group input[type="number"],
.purchase-form-modal .form-group textarea,
.purchase-form-modal .form-group select {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1em;
  box-sizing: border-box;
}

.reservation-form-modal .form-actions, .purchase-form-modal .form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.reservation-form-modal .form-actions button, .purchase-form-modal .form-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease;
}

.reservation-form-modal .form-actions button[type="submit"], .purchase-form-modal .form-actions button[type="submit"] {
  background-color: #007bff;
  color: white;
}

.purchase-form-modal .form-actions button[type="submit"] {
  background-color: #28a745;
  color: white;
}

.reservation-form-modal .form-actions button[type="submit"]:hover:not(:disabled),
.purchase-form-modal .form-actions button[type="submit"]:hover:not(:disabled) {
  background-color: #0056b3; /* Darker blue */
}

.purchase-form-modal .form-actions button[type="submit"]:hover:not(:disabled) {
  background-color: #218838; /* Darker green */
}


.reservation-form-modal .form-actions button:disabled, .purchase-form-modal .form-actions button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #5a6268;
}

.total-price-display {
    font-size: 1.2em;
    font-weight: bold;
    color: #007bff;
    text-align: right;
    margin-top: 15px;
    margin-bottom: 15px;
}

.error-message-inline {
    color: red;
    font-size: 0.85em;
    margin-top: 5px;
}

/* Style QRIS dan WA */
.payment-info {
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px dashed #ddd;
    text-align: center;
}

.qris-image {
    width: 100%;
    max-width: 250px;
    height: auto;
    border: 1px solid #eee;
    margin-bottom: 15px;
}

.whatsapp-button {
    display: inline-block;
    background-color: #25D366; /* WhatsApp green */
    color: white;
    padding: 10px 20px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: bold;
    margin-top: 15px;
    transition: background-color 0.3s ease;
}

.whatsapp-button:hover {
    background-color: #1DA851;
}

.whatsapp-number {
    font-size: 0.9em;
    color: #777;
    margin-top: 10px;
}


/* Responsive adjustment */
@media (min-width: 768px) {
  .detail-header {
    flex-direction: row;
    text-align: left;
    align-items: flex-start;
  }
  .detail-info {
    text-align: left;
  }
}
</style>
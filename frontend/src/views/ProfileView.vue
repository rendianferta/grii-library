<template>
  <div class="profile-container">
    <h1>Profil Pengguna</h1>
    <p v-if="currentUser">Selamat datang, {{ currentUser.full_name || currentUser.username }}!</p>
    <p v-else>Memuat informasi pengguna...</p>

    <div class="profile-nav">
      <button :class="{ active: currentSection === 'info' }" @click="currentSection = 'info'">Informasi Akun</button>
      <button :class="{ active: currentSection === 'reservations' }" @click="currentSection = 'reservations'">Riwayat Reservasi</button>
      <button :class="{ active: currentSection === 'orders' }" @click="currentSection = 'orders'">Riwayat Pesanan</button>
    </div>

    <div v-if="currentSection === 'info'" class="profile-section">
      <h2>Informasi Akun</h2>
      <div v-if="currentUser" class="user-info-display">
        <p><strong>Username:</strong> {{ currentUser.username }}</p>
        <p><strong>Email:</strong> {{ currentUser.email }}</p>
        <p><strong>Nama Lengkap:</strong> {{ currentUser.full_name || '-' }}</p>
        <p><strong>No. Telepon:</strong> {{ currentUser.phone_number || '-' }}</p>
        <p><strong>Status:</strong> {{ currentUser.is_librarian ? 'Pustakawan' : 'Anggota Biasa' }}</p>
      </div>
      <p v-else>Tidak ada informasi pengguna.</p>
    </div>

    <div v-else-if="currentSection === 'reservations'" class="profile-section">
      <h2>Riwayat Reservasi Anda</h2>
      <table class="profile-table reservation-table">
        <thead>
          <tr>
            <th>ID Res.</th>
            <th>Buku</th>
            <th>Tgl. Res.</th>
            <th>Tgl. Ambil</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingReservations">
            <td colspan="5">Memuat riwayat reservasi...</td>
          </tr>
          <tr v-else-if="errorReservations">
            <td colspan="5" class="error-message">{{ errorReservations }}</td>
          </tr>
          <tr v-else-if="userReservations.length === 0">
            <td colspan="5">Tidak ada riwayat reservasi.</td>
          </tr>
          <tr v-for="res in userReservations" :key="res.id">
            <td>{{ res.id }}</td>
            <td>{{ res.book_title }} ({{ res.book_author }})</td>
            <td>{{ formatDate(res.reservation_date) }}</td>
            <td>{{ res.pickup_date ? formatDate(res.pickup_date) : '-' }}</td>
            <td>{{ res.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="currentSection === 'orders'" class="profile-section">
      <h2>Riwayat Pesanan Anda</h2>
      <table class="profile-table order-table">
        <thead>
          <tr>
            <th>ID Pes.</th>
            <th>Buku</th>
            <th>Qty</th>
            <th>Total Harga</th>
            <th>Tgl. Pes.</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingOrders">
            <td colspan="6">Memuat riwayat pesanan...</td>
          </tr>
          <tr v-else-if="errorOrders">
            <td colspan="6" class="error-message">{{ errorOrders }}</td>
          </tr>
          <tr v-else-if="userOrders.length === 0">
            <td colspan="6">Tidak ada riwayat pesanan.</td>
          </tr>
          <tr v-for="order in userOrders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.book_title }} ({{ order.book_author }})</td>
            <td>{{ order.quantity }}</td>
            <td>Rp {{ formatPrice(order.total_price) }}</td>
            <td>{{ formatDate(order.order_date) }}</td>
            <td>{{ order.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watchEffect } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const currentUser = ref(null);
const currentSection = ref('info'); // Default tab

const userReservations = ref([]);
const loadingReservations = ref(true);
const errorReservations = ref(null);

const userOrders = ref([]);
const loadingOrders = ref(true);
const errorOrders = ref(null);

const formatPrice = (value) => {
  return new Intl.NumberFormat('id-ID', { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
};

const formatDate = (isoString) => {
  if (!isoString) return '-';
  const date = new Date(isoString);
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return date.toLocaleDateString('id-ID', options);
};

const fetchUserReservations = async () => {
  loadingReservations.value = true;
  errorReservations.value = null;
  try {
    const response = await fetch('/api/user/reservations', {
      credentials: 'include'
    });
    if (response.status === 401) {
      router.push('/login'); // Redirect to login if not authenticated
      return;
    }
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    userReservations.value = data;
  } catch (err) {
    console.error("Gagal mengambil riwayat reservasi:", err);
    errorReservations.value = "Gagal memuat riwayat reservasi. Silakan coba lagi nanti.";
  } finally {
    loadingReservations.value = false;
  }
};

const fetchUserOrders = async () => {
  loadingOrders.value = true;
  errorOrders.value = null;
  try {
    const response = await fetch('/api/user/orders', {
      credentials: 'include'
    });
    if (response.status === 401) {
      router.push('/login'); // Redirect to login if not authenticated
      return;
    }
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    userOrders.value = data;
  } catch (err) {
    console.error("Gagal mengambil riwayat pesanan:", err);
    errorOrders.value = "Gagal memuat riwayat pesanan. Silakan coba lagi nanti.";
  } finally {
    loadingOrders.value = false;
  }
};


// Ambil info user saat ini dan muat data yang relevan
watchEffect(async () => {
  try {
    const response = await fetch('/api/current_user', {
      credentials: 'include'
    });
    if (response.ok) {
      const data = await response.json();
      currentUser.value = data.user;
      // Jika user login, panggil fetcher riwayat
      if (currentUser.value) {
        fetchUserReservations();
        fetchUserOrders();
      }
    } else {
      currentUser.value = null;
      // Jika tidak login, kosongkan data riwayat
      userReservations.value = [];
      userOrders.value = [];
      loadingReservations.value = false;
      loadingOrders.value = false;
      router.push('/login'); // Arahkan ke login jika mencoba akses tanpa login
    }
  } catch (error) {
    console.error("Gagal memuat user saat ini di profil:", error);
    currentUser.value = null;
    userReservations.value = [];
    userOrders.value = [];
    loadingReservations.value = false;
    loadingOrders.value = false;
    router.push('/login');
  }
});

onMounted(() => {
  // watchEffect akan menangani pemanggilan fetcher awal
});
</script>

<style scoped>
.profile-container {
  max-width: 900px;
  margin: 20px auto;
  padding: 25px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.profile-container h1 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.profile-container p {
  text-align: center;
  color: #555;
  margin-bottom: 30px;
}

.profile-nav {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
  background-color: #e9ecef;
  padding: 10px;
  border-radius: 8px;
}

.profile-nav button {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  background-color: #f8f9fa;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.profile-nav button.active {
  background-color: #007bff;
  color: white;
  box-shadow: 0 2px 5px rgba(0, 123, 255, 0.2);
}

.profile-nav button:hover:not(.active) {
  background-color: #e2e6ea;
}

.profile-section {
  background-color: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.profile-section h2 {
  color: #007bff;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.user-info-display p {
  text-align: left;
  margin-bottom: 10px;
  color: #333;
}

.user-info-display strong {
  color: #000;
}

.profile-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  font-size: 0.9em;
}

.profile-table th, .profile-table td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: left;
  vertical-align: top;
}

.profile-table th {
  background-color: #f2f2f2;
  font-weight: bold;
  color: #333;
}

.profile-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.profile-table tr:hover {
  background-color: #eef;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
}
</style>
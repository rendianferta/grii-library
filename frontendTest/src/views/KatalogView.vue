<template>
  <div class="katalog-container">
    <h1>Katalog Buku</h1>

    <div class="search-bar">
      <input 
        type="text" 
        v-model="searchQuery" 
        @keyup.enter="performSearch" 
        placeholder="Cari judul, penulis, atau ISBN..."
      >
      <button @click="performSearch">Cari</button>
    </div>

    <p v-if="loading">Memuat daftar buku...</p>
    <p v-else-if="error">{{ error }}</p>
    <div v-else-if="books.length === 0">
      <p>Tidak ada buku yang ditemukan.</p>
    </div>
    <div v-else class="book-grid">
      <div v-for="book in books" :key="book.id" class="book-card">
        <img :src="book.cover_image_url || 'https://via.placeholder.com/150x200?text=No+Image'" :alt="book.title" class="book-cover">
        <div class="book-info">
          <h2>{{ book.title }}</h2>
          <p>Oleh: {{ book.author }}</p>
          <p>Stok: {{ book.stock }}</p>
          <p>Harga: Rp {{ formatPrice(book.price) }}</p>
          <router-link :to="{ name: 'book-detail', params: { id: book.id } }" class="detail-button">Lihat Detail</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// Hapus import useLoading
// import { useLoading } from '../composables/useLoading';

const books = ref([]);
const loading = ref(true); // Lokal loading
const error = ref(null);
const router = useRouter();

const searchQuery = ref('');
// Hapus inisialisasi useLoading
// const { startLoading, stopLoading } = useLoading();

const formatPrice = (value) => {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value).replace('IDR', '');
};

const fetchBooks = async () => {
  // Hapus startLoading()
  error.value = null;
  books.value = [];
  try {
    let url = '/api/books';
    const params = new URLSearchParams();
    if (searchQuery.value) { params.append('q', searchQuery.value); }
    if (params.toString()) { url += `?${params.toString()}`; }

    const response = await fetch(url);
    if (!response.ok) { throw new Error(`HTTP error! status: ${response.status}`); }
    const data = await response.json();
    books.value = data;
    loading.value = false; // Pastikan ini ada
    console.log("KatalogView - Buku yang diambil:", books.value);
  } catch (err) {
    console.error("KatalogView - Gagal mengambil buku:", err);
    error.value = "Gagal memuat buku. Silakan coba lagi nanti.";
    loading.value = false; // Pastikan ini ada
  } finally {
    // Hapus stopLoading()
  }
};

const performSearch = () => {
  fetchBooks();
};

onMounted(() => {
  fetchBooks();
});
</script>


<style scoped>
.katalog-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Style untuk search bar */
.search-bar {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  gap: 10px;
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


.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  justify-content: center;
}

.book-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 15px;
  background-color: #fff;
}

.book-cover {
  width: 150px;
  height: auto;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.book-info h2 {
  font-size: 1.2em;
  margin-top: 0;
  margin-bottom: 8px;
  color: #333;
}

.book-info p {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 5px;
}

.detail-button {
  display: inline-block;
  background-color: #007bff;
  color: white;
  padding: 8px 15px;
  border-radius: 5px;
  text-decoration: none;
  margin-top: 10px;
  transition: background-color 0.3s ease;
}

.detail-button:hover {
  background-color: #0056b3;
}
</style>
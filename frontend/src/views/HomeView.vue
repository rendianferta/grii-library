<template>
  <div class="home-container">
    <h1>Selamat Datang di Perpustakaan GRII Balikpapan</h1>
    <p>Jelajahi koleksi buku kami, reservasi untuk pinjaman, atau beli buku favorit Anda.</p>
    
    <section class="book-section">
      <h2>Buku Terbaru</h2>
      <p v-if="loadingBooks">Memuat buku...</p>
      <p v-else-if="errorBooks" class="error-message">{{ errorBooks }}</p>
      <div v-else-if="latestBooks.length === 0">
        <p>Tidak ada buku terbaru yang ditemukan.</p>
      </div>
      <div v-else class="book-grid">
        <div v-for="book in latestBooks" :key="book.id" class="book-card">
          <img :src="book.cover_image_url || 'https://via.placeholder.com/150x200?text=No+Image'" :alt="book.title" class="book-cover">
          <div class="book-info">
            <h3>{{ book.title }}</h3>
            <p>Oleh: {{ book.author }}</p>
            <router-link :to="{ name: 'book-detail', params: { id: book.id } }" class="detail-button">Lihat Detail</router-link>
          </div>
        </div>
      </div>
    </section>

    <section class="news-section">
      <h2>Berita Terbaru</h2>
      <p v-if="loadingNews">Memuat berita...</p>
      <p v-else-if="errorNews" class="error-message">{{ errorNews }}</p>
      <div v-else-if="newsArticles.length === 0">
        <p>Tidak ada berita terbaru yang tersedia.</p>
      </div>
      <div v-else class="news-grid">
        <div v-for="article in newsArticles" :key="article.id" class="news-card">
          <img v-if="article.image_url" :src="article.image_url" :alt="article.title" class="news-image">
          <div class="news-card-content">
            <h3>{{ article.title }}</h3>
            <p class="news-meta">Dipublikasikan: {{ formatDate(article.publication_date) }} oleh {{ article.author_username }}</p>
            <p class="news-preview">{{ truncateContent(article.content) }}</p>
            <router-link :to="{ name: 'news-detail', params: { id: article.id } }" class="read-more-link">Baca Selengkapnya</router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const latestBooks = ref([]);
const loadingBooks = ref(true);
const errorBooks = ref(null);

const newsArticles = ref([]);
const loadingNews = ref(true);
const errorNews = ref(null);

const formatPrice = (value) => {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value).replace('IDR', '');
};

const formatDate = (isoString) => {
  if (!isoString) return '-';
  const date = new Date(isoString);
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('id-ID', options);
};

const truncateContent = (content) => {
  const maxLength = 100;
  if (content.length > maxLength) {
    return content.substring(0, maxLength) + '...';
  }
  return content;
};

const fetchLatestBooks = async () => {
  loadingBooks.value = true;
  errorBooks.value = null;
  try {
    const response = await fetch('/api/books');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    latestBooks.value = data.sort((a, b) => {
      if (b.publication_year !== a.publication_year) {
        return b.publication_year - a.publication_year;
      }
      return a.title.localeCompare(b.title);
    }).slice(0, 3);
  } catch (err) {
    console.error("Gagal mengambil buku terbaru:", err);
    errorBooks.value = "Gagal memuat buku terbaru. Silakan coba lagi nanti.";
  } finally {
    loadingBooks.value = false;
  }
};

const fetchNews = async () => {
  loadingNews.value = true;
  errorNews.value = null;
  try {
    const response = await fetch('/api/news');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    newsArticles.value = data.slice(0, 3);
  } catch (err) {
    console.error("Gagal mengambil berita:", err);
    errorNews.value = "Gagal memuat berita. Silakan coba lagi nanti.";
  } finally {
    loadingNews.value = false;
  }
};

onMounted(() => {
  fetchLatestBooks();
  fetchNews();
});
</script>

<style scoped>
/* Semua styling yang sudah ada dari sebelumnya */
.home-container {
  max-width: 1200px; margin: 20px auto; padding: 25px;
  background-color: var(--color-bg-light); border-radius: 8px; box-shadow: var(--shadow-md);
}
.home-container h1 { text-align: center; color: var(--color-dark); margin-bottom: 40px; font-size: 2.5em; }
.book-section, .news-section {
  margin-bottom: 50px; padding-bottom: 30px; border-bottom: 1px dashed var(--color-secondary);
}
.book-section:last-of-type, .news-section:last-of-type { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
h2 {
  text-align: center; color: var(--color-primary); margin-bottom: 30px; font-size: 2em;
  position: relative; padding-bottom: 10px;
}
h2::after {
  content: ''; position: absolute; left: 50%; bottom: 0; transform: translateX(-50%);
  width: 60px; height: 3px; background-color: var(--color-accent); border-radius: 2px;
}
.book-grid, .news-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px; justify-content: center;
}
.book-card, .news-card {
  background-color: var(--color-card-bg); border-radius: 10px; box-shadow: var(--shadow-sm);
  overflow: hidden; display: flex; flex-direction: column; align-items: center; text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.book-card:hover, .news-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-md); }
.book-cover {
  width: 100%; max-width: 180px; height: 250px; object-fit: cover;
  border-radius: 8px; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.book-info, .news-card-content {
  padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; width: 100%;
}
.book-info h3, .news-card-content h3 { font-size: 1.3em; color: var(--color-dark); margin-top: 0; margin-bottom: 8px; }
.book-info p { font-size: 0.95em; color: var(--color-secondary); margin-bottom: 10px; }
.detail-button, .read-more-link {
  display: inline-block; background-color: var(--color-primary); color: var(--color-white);
  padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: 500;
  margin-top: 10px; transition: background-color 0.3s ease; align-self: center;
}
.detail-button:hover, .read-more-link:hover { background-color: var(--color-dark); }
.news-image {
  width: 100%; height: 200px; object-fit: cover; border-radius: 8px 8px 0 0;
}
.news-card-content h3 { font-size: 1.4em; color: var(--color-primary); text-align: left; }
.news-meta { font-size: 0.85em; color: var(--color-secondary); text-align: left; margin-bottom: 10px; }
.news-preview {
  font-size: 0.95em; color: var(--color-text); line-height: 1.5; text-align: left; flex-grow: 1; margin-bottom: 15px;
}
.error-message {
  color: var(--color-danger); background-color: #f8d7da; border: 1px solid #f5c6cb;
  padding: 10px; border-radius: 5px; margin: 20px auto; max-width: 600px; text-align: center;
}
@media (max-width: 768px) {
  .home-container { padding: 15px; }
  .book-grid, .news-grid { grid-template-columns: 1fr; }
  .book-card, .news-card { max-width: 300px; margin: 0 auto; }
}
</style>
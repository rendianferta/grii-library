<template>
  <div class="news-list-container">
    <h1>Berita & Informasi Perpustakaan</h1>
    <p v-if="loading">Memuat berita...</p>
    <p v-else-if="error">{{ error }}</p>
    <div v-else-if="newsArticles.length === 0">
      <p>Belum ada berita yang tersedia.</p>
    </div>
    <div v-else class="news-grid">
      <div v-for="article in newsArticles" :key="article.id" class="news-card">
        <h2>{{ article.title }}</h2>
        <p class="news-meta">Dipublikasikan: {{ formatDate(article.publication_date) }} oleh {{ article.author_username }}</p>
        <!-- <img :src="article.image_url || 'https://via.placeholder.com/250x350?text=No+Image'" :alt="article.title" class="detail-cover-image"> -->
        <img v-if="article.image_url" :src="article.image_url" :alt="article.title" class="news-detail-image">
        <p class="news-content-preview">{{ truncateContent(article.content) }}</p>
        <router-link :to="{ name: 'news-detail', params: { id: article.id } }" class="read-more-link">Baca Selengkapnya</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const newsArticles = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchNews = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch('/api/news');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    newsArticles.value = data;
  } catch (err) {
    console.error("Gagal mengambil berita:", err);
    error.value = "Gagal memuat berita. Silakan coba lagi nanti.";
  } finally {
    loading.value = false;
  }
};

const formatDate = (isoString) => {
  if (!isoString) return '-';
  const date = new Date(isoString);
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('id-ID', options);
};

const truncateContent = (content) => {
  const maxLength = 150;
  if (content.length > maxLength) {
    return content.substring(0, maxLength) + '...';
  }
  return content;
};

onMounted(() => {
  fetchNews();
});
</script>

<style scoped>
.news-list-container {
  max-width: 900px;
  margin: 20px auto;
  padding: 25px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.news-list-container h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

.news-card {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.news-card h2 {
  font-size: 1.5em;
  color: #007bff;
  margin-top: 0;
  margin-bottom: 10px;
}

.news-meta {
  font-size: 0.9em;
  color: #777;
  margin-bottom: 15px;
}

.news-content-preview {
  font-size: 1em;
  color: #444;
  line-height: 1.6;
  flex-grow: 1; /* Agar content preview mengisi ruang */
  margin-bottom: 15px;
}

.read-more-link {
  display: inline-block;
  background-color: #007bff;
  color: white;
  padding: 8px 15px;
  border-radius: 5px;
  text-decoration: none;
  align-self: flex-start; /* Agar tombol berada di kiri bawah */
  transition: background-color 0.3s ease;
}

.read-more-link:hover {
  background-color: #0056b3;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
  text-align: center;
}
</style>
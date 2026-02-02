<template>
  <div class="news-detail-container">
    <router-link to="/berita" class="back-link">&lt; Kembali ke Berita</router-link>

    <p v-if="loading">Memuat detail berita...</p>
    <p v-else-if="error">{{ error }}</p>
    <div v-else-if="article" class="news-article">
      <h1>{{ article.title }}</h1>
      <p class="news-meta">Dipublikasikan: {{ formatDate(article.publication_date) }} oleh {{ article.author_username }}</p>
      <img v-if="article.image_url" :src="article.image_url" :alt="article.title" class="news-detail-image">
      <div class="news-content" v-html="article.content"></div>
    </div>
    <p v-else>Berita tidak ditemukan.</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const article = ref(null);
const loading = ref(true);
const error = ref(null);

const formatDate = (isoString) => {
  if (!isoString) return '-';
  const date = new Date(isoString);
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return date.toLocaleDateString('id-ID', options);
};

const fetchNewsDetail = async (id) => {
  loading.value = true;
  error.value = null;
  article.value = null;
  try {
    const response = await fetch(`/api/news/${id}`);
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error("Berita tidak ditemukan.");
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    article.value = data;
  } catch (err) {
    console.error("Gagal mengambil detail berita:", err);
    error.value = err.message || "Gagal memuat detail berita. Silakan coba lagi nanti.";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchNewsDetail(route.params.id);
});

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchNewsDetail(newId);
  }
});
</script>

<style scoped>
/* Semua styling yang sudah ada dari sebelumnya */
.news-detail-container {
  max-width: 800px; margin: 20px auto; padding: 25px;
  background-color: #f9f9f9; border-radius: 8px; box-shadow: var(--shadow-md);
}
.back-link {
  display: inline-block; margin-bottom: 20px; color: var(--color-primary); text-decoration: none; font-weight: bold;
}
.back-link:hover { text-decoration: underline; }
.news-article h1 { font-size: 2.5em; color: #333; margin-bottom: 10px; }
.news-meta {
  font-size: 0.95em; color: #777; margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 10px;
}
.news-detail-image {
  width: 70%; height: auto;object-fit: cover;
  border-radius: 8px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: block;
  margin-left: auto;
  margin-right: auto;
}
.news-content { font-size: 1.1em; line-height: 1.8; color: #444; text-align: justify; }
.news-content p { margin-bottom: 1em; }
.news-content strong { font-weight: bold; }
.news-content em { font-style: italic; }
.error-message {
  color: var(--color-danger); background-color: #f8d7da; border: 1px solid #f5c6cb;
  padding: 10px; border-radius: 5px; margin-top: 15px; text-align: center;
}
</style>
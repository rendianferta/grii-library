<template>
  <div>
    <header>
      <nav class="navbar">
        <div class="nav-header">
          <router-link to="/" class="logo-link">
            <img src="/Logo_GRII_Balikpapan.png" alt="Logo Perpustakaan" class="header-logo">
          </router-link>

          <button class="mobile-menu-toggle" @click="toggleMobileMenu">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
          </button>
        </div>

        <transition name="slide-fade">
          <div class="nav-links" v-show="showMobileMenu || windowWidth > 768">
            <router-link to="/">Beranda</router-link>
            <router-link to="/katalog">Katalog Buku</router-link>
            <router-link to="/berita">Berita</router-link>
            <router-link to="/tentang">Tentang Kami</router-link>

            <template v-if="!isLoggedIn">
              <router-link to="/register">Daftar</router-link>
              <router-link to="/login">Login</router-link>
            </template>
            <template v-else>
              <router-link to="/profile" class="welcome-message">Halo, {{ currentUser.username }}!</router-link>
              <a href="#" @click.prevent="logout" class="logout-link">Logout</a>
            </template>

            <router-link v-if="isLoggedIn && currentUser && currentUser.is_librarian" to="/admin" class="admin-link">
              Admin Dashboard
            </router-link>
          </div>
        </transition>
      </nav>
    </header>

    <main>
      <router-view></router-view>
    </main>

    <footer class="main-footer">
      <div class="footer-content">
        <div class="footer-section footer-contact">
          <h3>Hubungi Kami</h3>
          <p><strong>Alamat:</strong> Kompleks Ruko Balikpapan Baru, Little China Blok AB-4 No. 19-20, Kel. Damai Baru, Kec. Balikpapan Kota, Kota Balikpapan, Kalimantan Timur</p>
          <p><strong>Telepon:</strong> (021) 1234567981011121131415</p>
          <p><strong>Email:</strong> info@perpustakaancontoh.com</p>
        </div>
        <div class="footer-section footer-social">
          <h3>Ikuti Kami</h3>
          <div class="social-icons">
            <a href="https://www.youtube.com/@GRIIBALIKPAPAN" target="_blank" rel="noopener noreferrer" title="Kunjungi YouTube Kami">
              <img src="/Logo_Youtube_Bulat.png" alt="YouTube Logo" class="youtube-icon">
            </a>
            <a href="https://www.instagram.com/griibalikpapan/" target="_blank" rel="noopener noreferrer" title="Ikuti Kami di Instagram">
              <img src="/Logo_Instagram_Bulat.png" alt="Instagram Logo" class="instagram-icon">
            </a>
            <a href="https://api.whatsapp.com/send?phone=6287740348431" target="_blank" rel="noopener noreferrer" title="Hubungi Kami via WhatsApp">
              <img src="/Logo_Whatsapp_Bulat.png" alt="WhatsApp Logo" class="whatsapp-icon">
            </a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2025 GRII Balikpapan. Hak Cipta Dilindungi.</p>
      </div>
    </footer>

    <ToastNotification />
  </div>
</template>

<script setup>
// Kode JavaScript tetap sama seperti sebelumnya
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import ToastNotification from './components/ToastNotification.vue';
import { useToast } from './composables/useToast';

const isLoggedIn = ref(false);
const currentUser = ref(null);
const showMobileMenu = ref(false);
const windowWidth = ref(window.innerWidth);
const router = useRouter();
const { showToast } = useToast();
const route = useRoute();

watch(() => route.fullPath, () => {
  checkLoginStatus();
});

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value;
};

const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
  if (window.innerWidth > 768) {
    showMobileMenu.value = false;
  }
};

const checkLoginStatus = async () => {
  try {
    const response = await fetch('/api/current_user', {
      credentials: 'include'
    });
    if (response.ok) {
      const data = await response.json();
      isLoggedIn.value = true;
      currentUser.value = data.user;
    } else {
      isLoggedIn.value = false;
      currentUser.value = null;
    }
  } catch (error) {
    console.error("Gagal memeriksa status login:", error);
    isLoggedIn.value = false;
    currentUser.value = null;
  }
};

const logout = async () => {
  try {
    const response = await fetch('/api/logout', {
      method: 'POST',
      credentials: 'include'
    });
    if (response.ok) {
      isLoggedIn.value = false;
      currentUser.value = null;
      showToast('Anda telah logout!', 'info');
      router.push('/login');
    } else {
      showToast('Gagal logout. Silakan coba lagi.', 'error');
    }
  } catch (error) {
    console.error('Error saat logout:', error);
    showToast('Terjadi kesalahan saat logout.', 'error');
  }
};

onMounted(() => {
  window.addEventListener('resize', updateWindowWidth);
  checkLoginStatus();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateWindowWidth);
});
</script>

<style>
/* --- Gaya CSS yang sudah ada --- */
header {
  background-color: var(--color-dark);
  color: var(--color-white);
  box-shadow: var(--shadow-sm);
}
.navbar {
  width: 100%;
  background-color: var(--color-dark);
  padding: 10px 20px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
}
.header-logo {
  height: 80px;
  width: auto;
  border-radius: 4px;
}
.mobile-menu-toggle {
  display: none;
  flex-direction: column;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
}
.mobile-menu-toggle .bar {
  width: 25px;
  height: 3px;
  background-color: var(--color-white);
  border-radius: 2px;
  transition: all 0.3s ease;
}
.nav-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 0;
}
.nav-links a {
  color: var(--color-light);
  background-color: rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  border-radius: 6px;
  text-decoration: none;
  transition: background-color 0.2s;
}
.nav-links a:hover {
  background-color: var(--color-primary);
  color: var(--color-white);
}
nav a.router-link-active {
  background-color: var(--color-primary);
  color: var(--color-white);
  font-weight: bold;
}
main {
  padding: 20px;
  flex-grow: 1;
}
.main-footer {
  background-color: var(--color-dark);
  color: var(--color-light);
  padding: 2rem 20px;
  box-shadow: 0 -1px 3px rgba(0,0,0,0.05);
}
.footer-content {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.footer-section {
  flex: 1;
  min-width: 250px;
  margin-right: 100px;
  text-align: left;
}
.footer-section h3 {
  color: var(--color-white);
  margin-bottom: 15px;
  font-size: 1.2rem;
}
.footer-section p {
  color: var(--color-light);
  line-height: 1.6;
}
.footer-social {
  /* Hapus flex: 1; agar kolom ini menyesuaikan kontennya */
  min-width: unset;
}


.social-icons {
  display: flex;
  gap: 15px;
  /* Atur agar ikon sejajar dengan teks di atasnya */
  align-items: center;
  justify-content: flex-start;
  margin-top: 5px; /* Sesuaikan margin untuk sejajar dengan header */
}
.youtube-icon {
  width: 55px;
  margin-right: 2px;
  height: auto;
  transition: transform 0.3s ease-in-out;
}
.youtube-icon:hover {
  transform: scale(1.1);
}

.instagram-icon {
  width: 60px;
  height: auto;
  transition: transform 0.3s ease-in-out;
}
.instagram-icon:hover {
  transform: scale(1.1);
}

.whatsapp-icon {
  width: 85px;
  height: auto;
  transition: transform 0.3s ease-in-out;
}
.whatsapp-icon:hover {
  transform: scale(1.1);
}

.footer-bottom {
  text-align: center;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.footer-bottom p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-light);
}

@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: flex;
  }
  .nav-links {
    flex-direction: column;
    align-items: center;
    padding: 10px 0;
    background-color: var(--color-dark);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }
  .nav-links a {
    width: 100%;
    text-align: center;
  }
  .header-logo {
    height: 60px;
  }
  .footer-content {
    flex-direction: column;
    text-align: left; /* Rata kiri untuk semua teks di mode handphone */
  }
  .footer-section {
    min-width: 100%;
    margin-bottom: 20px;
  }
  .social-icons {
    justify-content: flex-start; /* Rata kiri untuk ikon di mode handphone */
  }
}
.slide-fade-enter-active {
  transition: all 0.3s ease;
}
.slide-fade-leave-active {
  transition: all 0.2s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// --- IMPOR KOMPONEN VIEW ---
// Impor komponen untuk halaman umum
import HomeView from '../views/HomeView.vue'
import KatalogView from '../views/KatalogView.vue'
import BeritaView from '../views/BeritaView.vue' // Halaman daftar berita
import NewsDetailView from '../views/NewsDetailView.vue' // Halaman detail berita
import TentangView from '../views/TentangView.vue'
import KontakView from '../views/KontakView.vue'
import BookDetailView from '../views/BookDetailView.vue' // Pastikan ini adalah 'BookDetailView'

// Impor komponen untuk autentikasi
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'

// Impor komponen untuk profil pengguna
import ProfileView from '../views/ProfileView.vue'

// Impor komponen untuk dashboard admin
import AdminDashboardView from '../views/AdminDashboardView.vue'


// --- DEFINISI ROUTER ---
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Menggunakan HTML5 History mode untuk URL yang bersih
  routes: [
    // Rute Umum
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/katalog',
      name: 'katalog',
      component: KatalogView
    },
    {
      path: '/katalog/:id', // Rute dinamis untuk detail buku
      name: 'book-detail',
      component: BookDetailView // Pastikan ini adalah 'BookDetailView'
    },
    {
      path: '/berita',
      name: 'berita',
      component: BeritaView
    },
    {
      path: '/berita/:id', // Rute dinamis untuk detail berita
      name: 'news-detail',
      component: NewsDetailView
    },
    {
      path: '/tentang',
      name: 'tentang',
      component: TentangView
    },
    {
      path: '/kontak',
      name: 'kontak',
      component: KontakView
    },

    // Rute Autentikasi
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },

    // Rute Profil Pengguna (Membutuhkan Autentikasi)
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true } // Pengguna harus login untuk mengakses ini
    },

    // Rute Dashboard Admin (Membutuhkan Autentikasi & Otorisasi Pustakawan)
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboardView,
      meta: { requiresAuth: true, requiresLibrarian: true } // Hanya pustakawan yang login
    }
    // Anda bisa tambahkan rute 404 Not Found di sini di paling bawah jika ingin
    // { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundComponent },
  ]
})


// --- NAVIGASI PENJAGA (GLOBAL NAVIGATION GUARD) ---
// Ini adalah middleware yang dijalankan sebelum setiap navigasi rute
router.beforeEach(async (to, from, next) => {
  // Cek apakah rute yang dituju memiliki meta.requiresAuth atau meta.requiresLibrarian
  if (to.meta.requiresAuth || to.meta.requiresLibrarian) {
    try {
      // Panggil API backend untuk mengecek status user saat ini
      const response = await fetch('/api/current_user', {
        credentials: 'include' // Penting untuk mengirim cookie sesi
      });

      if (response.ok) {
        // Jika respons OK, berarti ada user yang login
        const data = await response.json();
        const currentUser = data.user;

        // Cek otorisasi pustakawan jika rute membutuhkannya
        if (to.meta.requiresLibrarian && !currentUser.is_librarian) {
          // Jika rute butuh pustakawan tapi user bukan pustakawan
          alert('Akses ditolak: Anda bukan pustakawan.');
          next('/login'); // Arahkan ke halaman login (atau halaman lain)
        } else {
          // Jika user login dan memiliki otorisasi yang cukup
          next(); // Lanjutkan ke rute yang dituju
        }
      } else {
        // Jika respons TIDAK OK (misal 401 Unauthorized)
        alert('Anda perlu login untuk mengakses halaman ini.');
        next('/login'); // Arahkan ke halaman login
      }
    } catch (error) {
      // Tangani kesalahan jaringan atau server saat mengecek status login
      console.error('Error saat cek status login di navigation guard:', error);
      alert('Terjadi kesalahan saat verifikasi login. Silakan login ulang.');
      next('/login'); // Arahkan ke halaman login
    }
  } else {
    // Jika rute tidak memerlukan otentikasi/otorisasi, lanjutkan
    next();
  }
});

export default router
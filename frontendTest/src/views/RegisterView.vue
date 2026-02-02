<template>
  <div class="auth-container">
    <div class="auth-box">
      <h1>Daftar Akun Baru</h1>
      <form @submit.prevent="register">
        <div class="form-group">
          <label for="username">Username:</label>
          <input type="text" id="username" v-model="form.username" required>
        </div>
        <div class="form-group">
          <label for="email">Email:</label>
          <input type="email" id="email" v-model="form.email" required>
        </div>
        <div class="form-group">
          <label for="password">Password:</label>
          <input type="password" id="password" v-model="form.password" required>
        </div>
        <div class="form-group">
          <label for="fullName">Nama Lengkap (Opsional):</label>
          <input type="text" id="fullName" v-model="form.full_name">
        </div>
        <div class="form-group">
          <label for="phoneNumber">No. Telepon (Opsional):</label>
          <input type="text" id="phoneNumber" v-model="form.phone_number">
        </div>
        
        <p v-if="message" :class="{'success-message': success, 'error-message': !success}">
          {{ message }}
        </p>
        
        <button type="submit" :disabled="loading">
          {{ loading ? 'Mendaftar...' : 'Daftar' }}
        </button>
      </form>
      <p class="auth-link">Sudah punya akun? <router-link to="/login">Login di sini</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const form = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  phone_number: ''
});
const loading = ref(false);
const message = ref('');
const success = ref(false);

const register = async () => {
  loading.value = true;
  message.value = '';
  success.value = false;

  try {
    const response = await fetch('/api/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Registrasi gagal.');
    }

    message.value = data.message || 'Registrasi berhasil! Silakan login.';
    success.value = true;
    
    // Opsional: Langsung arahkan ke halaman login setelah registrasi sukses
    setTimeout(() => {
      router.push('/login');
    }, 2000);

  } catch (err) {
    console.error('Error saat registrasi:', err);
    message.value = err.message || 'Terjadi kesalahan saat registrasi.';
    success.value = false;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 150px); /* Sesuaikan tinggi agar tidak menempel header/footer */
  background-color: #f0f2f5;
  padding: 20px;
}

.auth-box {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  text-align: center;
}

.auth-box h1 {
  font-size: 2em;
  margin-bottom: 25px;
  color: #333;
}

.form-group {
  text-align: left;
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.form-group input {
  width: calc(100% - 20px);
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1em;
  box-sizing: border-box;
}

button[type="submit"] {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1.1em;
  cursor: pointer;
  margin-top: 20px;
  transition: background-color 0.3s ease;
}

button[type="submit"]:hover:not(:disabled) {
  background-color: #0056b3;
}

button[type="submit"]:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.auth-link {
  margin-top: 20px;
  font-size: 0.95em;
  color: #666;
}

.auth-link a {
  color: #007bff;
  text-decoration: none;
  font-weight: bold;
}

.auth-link a:hover {
  text-decoration: underline;
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
</style>
<template>
  <div class="contact-section">
    <h1>Hubungi Kami</h1>
    <div class="contact-info">
      <p><strong>Alamat:</strong> Kompleks Ruko Balikpapan Baru, Little China Blok AB-4 No. 19-20, Kel. Damai Baru, Kec. Balikpapan Kota, Kota Balikpapan, Kalimantan Timur</p>
      <p><strong>Telepon:</strong> (021) 1234567981011121131415</p>
      <p><strong>Email:</strong> info@perpustakaancontoh.com</p>
    </div>

    <div class="social-links">
      <a href="https://www.youtube.com/@GRIIBALIKPAPAN" target="_blank" rel="noopener noreferrer" title="Kunjungi YouTube Kami">
        <img src="/Logo_Youtube_Bulat.png" alt="YouTube Logo" class="Youtube-icon">
      </a>
      <a href="https://www.instagram.com/griibalikpapan/" target="_blank" rel="noopener noreferrer" title="Ikuti Kami di Instagram">
        <img src="/Logo_Instagram_Bulat.png" alt="Instagram Logo" class="Instagram-icon">
      </a>
      <a href="https://api.whatsapp.com/send?phone=6287740348431" target="_blank" rel="noopener noreferrer" title="Hubungi Kami via WhatsApp">
        <img src="/Logo_Whatsapp_Bulat.png" alt="WhatsApp Logo" class="Whatsapp-icon">
      </a>
    </div>
  </div>
</template>

<script setup>
</script>

<style>
/* --- Styling untuk layout secara keseluruhan --- */
.contact-section {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h1, h2 {
  text-align: center;
  color: #333;
}

/* --- Styling untuk informasi kontak --- */
.contact-info {
  margin-bottom: 20px;
  text-align: center;
}
.contact-info p {
  line-height: 1.6;
  color: #555;
}
.contact-info strong {
  color: #333;
}

/* --- Styling untuk tautan media sosial --- */
.social-links {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}
.Youtube-icon {
  width: 60px;
  height: auto;
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}
.Youtube-icon:hover {
  transform: scale(1.2);
}

.Instagram-icon {
  margin-top: 4px;
  margin-left: 6px;
  width: 55px;
  height: auto;
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}
.Instagram-icon:hover {
  transform: scale(1.2);
}

.Whatsapp-icon {
  margin-top: 2px;
  width: 77px;
  height: auto;
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}
.Whatsapp-icon:hover {
  transform: scale(1.2);
}
</style>
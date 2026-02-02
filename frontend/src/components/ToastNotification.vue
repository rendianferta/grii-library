<template>
  <transition name="toast-fade">
    <div v-if="toast.show" :class="['toast-notification', `toast-${toast.type}`]">
      <p>{{ toast.message }}</p>
    </div>
  </transition>
</template>

<script setup>
import { useToast } from '../composables/useToast';

const { toast } = useToast();
</script>

<style scoped>
.toast-notification {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-weight: bold;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  z-index: 2000; /* Lebih tinggi dari modal */
  min-width: 250px;
  max-width: 90%;
}

.toast-success { background-color: var(--color-accent); } /* Hijau */
.toast-error { background-color: var(--color-danger); } /* Merah */
.toast-info { background-color: var(--color-primary); } /* Biru */
.toast-warning { background-color: var(--color-warning); } /* Kuning */

/* Transisi Fade */
.toast-fade-enter-active, .toast-fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.toast-fade-enter-from, .toast-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
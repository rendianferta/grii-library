// frontend/src/composables/useToast.js
import { ref } from 'vue';

const toast = ref({
  message: '',
  type: '', // 'success', 'error', 'info', 'warning'
  show: false,
  timeout: null
});

export function useToast() {
  const showToast = (message, type = 'info', duration = 3000) => {
    // Clear any existing timeout
    if (toast.value.timeout) {
      clearTimeout(toast.value.timeout);
    }

    toast.value.message = message;
    toast.value.type = type;
    toast.value.show = true;

    // Set timeout to hide toast
    toast.value.timeout = setTimeout(() => {
      toast.value.show = false;
      toast.value.message = '';
    }, duration);
  };

  return {
    toast,
    showToast
  };
}
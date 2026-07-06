import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../api';

export const useAuthStore = defineStore('auth', () => {
  // In-memory state only (never persisted) — protects the access token from XSS/localStorage theft.
  const token = ref(null);
  const isAdmin = ref(false);

  // Computed login status
  const isAuthenticated = computed(() => !!token.value);

  // Helpers for setting/clearing state
  function setToken(newToken) {
    token.value = newToken;
  }

  function clearAuth() {
    token.value = null;
    isAdmin.value = false;
  }

  // Login: sends credentials to the backend.
  // The backend responds with the access token + role, and sets the HttpOnly refresh cookie.
  async function login(username, password) {
    const response = await api.post('token/', { username, password });
    setToken(response.data.access);
    isAdmin.value = response.data.isAdmin;
  }

  // Logout: tells the backend to clear the cookie, then clears local state.
  async function logout() {
    try {
      await api.post('logout/');
    } finally {
      clearAuth();
    }
  }

  // Runs on app start (App.vue -> onMounted).
  // Tries to restore an existing session via the refresh cookie.
  async function attemptSilentRefresh() {
    try {
      const response = await api.post('token/refresh/');
      setToken(response.data.access);
      isAdmin.value = response.data.isAdmin;
    } catch (error) {
      // Catches the expected 400 when no cookie exists yet on first load.
      // Reset state defensively without crashing the app.
      clearAuth();
    }
  }

  return {
    token,
    isAdmin,
    isAuthenticated,
    login,
    logout,
    setToken,
    clearAuth,
    attemptSilentRefresh,
  };
});
import axios from 'axios';
import { useAuthStore } from './stores/auth';

// Configure via .env: VITE_API_BASE_URL=http://localhost:8000/api/
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/';

const api = axios.create({
  baseURL,
  withCredentials: true, // REQUIRED: allows the refresh cookie to be sent/received automatically
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attaches the access token to every API call, if present
api.interceptors.request.use(
  (config) => {
    const auth = useAuthStore();
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: catches expired access tokens (401) and silently renews them via the cookie
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If the server returns 401 (Unauthorized) and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Silent refresh: send an empty POST to the refresh route.
        // The browser attaches the HttpOnly cookie automatically in the background.
        const response = await axios.post(`${baseURL}token/refresh/`, {}, {
          withCredentials: true,
        });

        const auth = useAuthStore();
        auth.setToken(response.data.access);

        // Retry the original request with the new token
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh also failed (e.g. cookie expired or invalid) — force logout
        const auth = useAuthStore();
        auth.clearAuth();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
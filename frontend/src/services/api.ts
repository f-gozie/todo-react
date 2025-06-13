import axios from 'axios';
import { store } from '@/store';
import { logout } from '@/store/slices/authSlice';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
});

api.interceptors.request.use((config) => {
  const state = store.getState();
  const token = state.auth.accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // TODO: handle refresh token flow later
      store.dispatch(logout());
    }
    return Promise.reject(error);
  },
);

export default api; 
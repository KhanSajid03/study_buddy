import { create } from 'zustand';
import { authAPI } from '../services/api';

const useStore = create((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,

  login: async (credentials) => {
    try {
      set({ loading: true, error: null });
      const response = await authAPI.login(credentials);
      const { access_token } = response.data;

      localStorage.setItem('token', access_token);

      // Fetch user data
      const userResponse = await authAPI.getMe();

      set({
        token: access_token,
        user: userResponse.data,
        isAuthenticated: true,
        loading: false,
      });

      return true;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        loading: false
      });
      return false;
    }
  },

  register: async (userData) => {
    try {
      set({ loading: true, error: null });
      await authAPI.register(userData);
      set({ loading: false });
      return true;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        loading: false
      });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  fetchUser: async () => {
    try {
      const response = await authAPI.getMe();
      set({ user: response.data });
    } catch (error) {
      console.error('Failed to fetch user:', error);
      // If unauthorized, logout
      if (error.response?.status === 401) {
        set({ user: null, token: null, isAuthenticated: false });
        localStorage.removeItem('token');
      }
    }
  },

  clearError: () => set({ error: null }),
}));

export default useStore;

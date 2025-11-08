import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// Users API
export const usersAPI = {
  updateSettings: (data) => api.put('/users/me', data),
};

// Documents API
export const documentsAPI = {
  upload: (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },
  list: () => api.get('/documents/'),
  get: (id) => api.get(`/documents/${id}`),
  delete: (id) => api.delete(`/documents/${id}`),
};

// Query API
export const queryAPI = {
  query: (data) => api.post('/query/', data),
};

export default api;

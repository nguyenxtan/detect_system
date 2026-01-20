import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/api/auth/login', { username, password }),

  register: (userData) =>
    api.post('/api/auth/register', userData),

  getCurrentUser: () =>
    api.get('/api/auth/me/'),
};

// Defect API
export const defectAPI = {
  getProfiles: (params) =>
    api.get('/api/defects/profiles', { params }),

  getProfile: (id) =>
    api.get(`/api/defects/profiles/${id}`),

  createProfile: (formData) =>
    api.post('/api/defects/profiles', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  matchDefect: (formData) =>
    api.post('/api/defects/match', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  getIncidents: (params) =>
    api.get('/api/defects/incidents', { params }),
};

// User API
export const userAPI = {
  getAll: () =>
    api.get('/api/users/'),

  get: (id) =>
    api.get(`/api/users/${id}/`),

  create: (userData) =>
    api.post('/api/users/', userData),

  update: (id, userData) =>
    api.put(`/api/users/${id}`, userData),

  delete: (id) =>
    api.delete(`/api/users/${id}`),
};

// Customer API
export const customerAPI = {
  getAll: (params) =>
    api.get('/api/customers/', { params }),

  get: (id) =>
    api.get(`/api/customers/${id}`),

  create: (customerData) =>
    api.post('/api/customers/', customerData),

  update: (id, customerData) =>
    api.put(`/api/customers/${id}`, customerData),

  delete: (id) =>
    api.delete(`/api/customers/${id}`),
};

// Product API
export const productAPI = {
  getAll: (params) =>
    api.get('/api/products/', { params }),

  get: (id) =>
    api.get(`/api/products/${id}`),

  create: (productData) =>
    api.post('/api/products/', productData),

  update: (id, productData) =>
    api.put(`/api/products/${id}`, productData),

  delete: (id) =>
    api.delete(`/api/products/${id}`),
};

// DefectType API
export const defectTypeAPI = {
  getAll: (params) =>
    api.get('/api/defect-types/', { params }),

  get: (id) =>
    api.get(`/api/defect-types/${id}`),

  create: (defectTypeData) =>
    api.post('/api/defect-types/', defectTypeData),

  update: (id, defectTypeData) =>
    api.put(`/api/defect-types/${id}`, defectTypeData),

  delete: (id) =>
    api.delete(`/api/defect-types/${id}`),
};

// SeverityLevel API
export const severityLevelAPI = {
  getAll: (params) =>
    api.get('/api/severity-levels/', { params }),

  get: (id) =>
    api.get(`/api/severity-levels/${id}`),

  create: (severityLevelData) =>
    api.post('/api/severity-levels/', severityLevelData),

  update: (id, severityLevelData) =>
    api.put(`/api/severity-levels/${id}`, severityLevelData),

  delete: (id) =>
    api.delete(`/api/severity-levels/${id}`),
};

export default api;

import axios from 'axios';
import { getDeviceInfo, storeDeviceInfo, getStoredDeviceInfo } from './deviceFingerprint';

// Get API URL from environment variables
// For Google Cloud deployment, use environment variables
const API_URL = process.env.REACT_APP_BACKEND_URL || 
  (process.env.NODE_ENV === 'production' ? 'https://pentorasecbeta.mywire.org' : 'http://localhost:8001');
const BASE_URL = `${API_URL}/api`;

// Create centralized Axios instance
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Token management functions
const TOKEN_KEY = 'authToken';

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
};

export const getAuthToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

// Export for external use
api.getAuthToken = getAuthToken;

export const removeAuthToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

// Auto-connect function for device-specific authentication
export const autoConnect = async () => {
  try {
    const deviceInfo = getDeviceInfo();
    console.log('Device info:', deviceInfo);
    storeDeviceInfo(deviceInfo);
    
    const response = await api.post('/auth/auto-connect', deviceInfo);
    console.log('Auto-connect response:', response.data);
    
    if (response.data && response.data.access_token) {
      setAuthToken(response.data.access_token);
      return response.data;
    }
    
    throw new Error('No token received');
  } catch (error) {
    console.error('Auto-connect failed:', error);
    throw error;
  }
};

// Initialize authentication on app start
export const initializeAuth = async () => {
  try {
    // Check if we already have a valid token
    const existingToken = getAuthToken();
    if (existingToken) {
      // Verify token is still valid by making a test request
      try {
        await api.get('/auth/me');
        return true; // Token is valid
      } catch (error) {
        // Token is invalid, remove it
        removeAuthToken();
      }
    }
    
    // No valid token, auto-connect
    await autoConnect();
    return true;
  } catch (error) {
    console.error('Auth initialization failed:', error);
    return false;
  }
};

// Request interceptor to automatically add JWT token and debug
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('API Request:', config.method?.toUpperCase(), config.url, 'with token');
    } else {
      console.log('API Request:', config.method?.toUpperCase(), config.url, 'without token');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and debugging
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.config?.url, error.message);
    
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401) {
      console.warn('Authentication failed, token removed');
      removeAuthToken();
      
      // Try to re-authenticate automatically
      if (error.config?.url !== '/auth/auto-connect' && error.config?.url !== '/auth/me') {
        console.log('Attempting to re-authenticate...');
        autoConnect().catch(err => {
          console.error('Re-authentication failed:', err);
        });
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

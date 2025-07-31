import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock authentication token (in production, implement proper auth)
api.defaults.headers.common['Authorization'] = 'Bearer mock_token';

export const chatAPI = {
  sendMessage: async (message, customerId, sessionId = null) => {
    const response = await api.post('/chat', {
      message,
      customer_id: customerId,
      session_id: sessionId,
    });
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;

import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, 
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      return Promise.reject(new Error('Session expired. Please login again.'));
    }
    if (error.response?.status === 403) {
      return Promise.reject(new Error('You do not have permission to perform this action.'));
    }
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timed out. Please try again.'));
    }
    return Promise.reject(error.response?.data?.error || error.message || 'An unexpected error occurred');
  }
);

export const apiService = {
  async askQuestion(question, chatId = null) {
    const maxRetries = 3;
    let retries = 0;

    while (retries < maxRetries) {
      try {
        const response = await api.post('/ask', { 
          question, 
          chat_id: null 
        });
        
        if (!response.data) {
          throw new Error('Empty response received');
        }

        return {
          answer: response.data.answer,
          chatId: response.data.chat_id,
          references: response.data.references || [],
          recommendedLawyers: response.data.recommended_lawyers || []
        };
      } catch (error) {
        retries++;
        if (retries === maxRetries) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  },

  // Chat related endpoints
  async startChat(recipientId) {
    const response = await api.post('/chat/start', { recipient_id: recipientId });
    return response.data;
  },

  async getChatHistory(chatId) {
    const response = await api.get(`/chat/${chatId}/messages`);
    return response.data;
  },

  async getUserChats() {
    const response = await api.get('/user/chats');
    return response.data;
  },

  // Lawyer related endpoints
  async searchLawyers(query) {
    const response = await api.get(`/lawyers/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },

  async getLawyerDetails(lawyerId) {
    const response = await api.get(`/lawyers/${lawyerId}`);
    return response.data;
  },

  async getLawyersBySpecialization(specialization) {
    const response = await api.get(`/lawyers/specialization/${specialization}`);
    return response.data;
  },

  // Profile related endpoints
  async getUserProfile() {
    const response = await api.get('/user-profile');
    return response.data;
  },

  async updateProfile(profileData) {
    const response = await api.put('/user-profile', profileData);
    return response.data;
  },

  // System health check
  async checkHealth() {
    const response = await api.get('/health');
    return response.data;
  }
};

export default apiService;
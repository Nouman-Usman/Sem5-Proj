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
      const currentRole = apiService.getUserRole();
      if (currentRole) {
        window.location.href = '/user-home';
      } else {
        window.location.href = '/login';
      }
      return Promise.reject(new Error('Access denied: Insufficient permissions'));
    }
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timed out. Please try again.'));
    }
    return Promise.reject(error.response?.data?.error || error.message || 'An unexpected error occurred');
  }
);

export const apiService = {
  // Add this new utility function
  getUserRole() {
    const user = JSON.parse(localStorage.getItem('user'));
    return user?.role || null;
  },

  async askQuestion(question ) {
    const maxRetries = 3;
    let retries = 0;

    while (retries < maxRetries) {
      try {
        const response = await api.post('/ask', { 
          question,  
        });
        
        if (!response.data) {
          throw new Error('Empty response received');
        }

        return {
          answer: response.data.answer,
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

  async createClientProfile(formData) {
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    };
    const response = await api.post('/cl/profile', formData, config);
    return response.data;
  },

  async createLawyerProfile(profileData) {
    const response = await api.post('/lw/profile', profileData);
    return response.data;
  },

  async createSubscription(subscriptionData) {
    const token = localStorage.getItem('token');
    try {
      const response = await api.post('/subscribe', {
        access_token: token,
        ...subscriptionData
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create subscription');
    }
  },

  async getCurrentSubscription() {
    try {
      const response = await api.get('/subscription/current');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch subscription');
    }
  },

  async checkHealth() {
    const response = await api.get('/health');
    return response.data;
  }
};

export default apiService;
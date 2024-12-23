import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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

let SessionId = null;

export const apiService = {
  // Add this new utility function
  getUserRole() {
    const user = JSON.parse(localStorage.getItem('user'));
    return user?.role || null;
  },
  async getChatTopic() {
    const token = localStorage.getItem("token");
    try {
      const chatTopic = await api.get('/topics');
      return {
        topic: chatTopic.data.chat_topics,
        session_id: chatTopic.data.chat_sessions || null,
        time: chatTopic.data.Time || null
      };
    } catch (error) {
      console.error('Failed to fetch chat topic:', error.message);
      return null;
    }
  },

  async getChatsFromSessionId(sessionId) {
    try {
      const response = await api.get(`/chats/${sessionId}`);
      return response;
    } catch (error) {
      console.error('Failed to fetch session messages:', error);
      throw error; // Propagate error to be handled by the component
    }
  },

  async askQuestion(question, sessionId = null) {
    try {
      const response = await api.post('/ask', {
        question,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      console.error('Error asking question:', error);
      throw error;
    }
  },

  // Update the lawyer details fetch function
  async getLawyerDeatilsbyLawyerId(lawyerId) {
    try {
      
      // Ensure lawyerId is a number
      const id = typeof lawyerId === 'object' ? lawyerId.LawyerId : parseInt(lawyerId);
      if (!id || isNaN(id)) {
        throw new Error('Invalid lawyer ID');
      }
  
      const response = await api.get(`/getlawyer/${id}`);
      
      if (!response.data || !response.data.lawyer) {
        throw new Error('Invalid response format');
      }
  
      return response.data;
    } catch (error) {
      console.error('Error fetching lawyer details:', error);
      throw error;
    }
  },

  async startChat(recipientId) {
    const response = await api.post('/chat/start', { recipient_id: recipientId });
    return response.data;
  },

  async sendMessage(recipientId, message) {
    const response = await api.post(`/chat/${recipientId}/message`, { message });
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

  async isLawyerProfileCompleted(lawyerid) {
    const response = await api.get(`/lawyers/isCompleted/${lawyerid}`);
    return response.data;
  },

  async getLawyerDashboardData() {
    try {
      const response = await api.get('/lawyer/dashboard');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch lawyer dashboard data:', error.message);
      return null;
    }
  },
  async getUserCredits() {
    try {
      const response = await api.get('/get/credits/');
      if (!response.data || typeof response.data.credits !== 'number') {
        throw new Error('Invalid credits data received');
      }
      return response.data.credits;
    } catch (error) {
      console.error('Failed to fetch credits:', error);
      throw new Error('Failed to fetch credits');
    }
  },

  async updateCredits(credits) {
    try {
      if (typeof credits !== 'number' || credits < 0) {
        throw new Error('Invalid credits value');
      }
      const response = await api.put('/up/credits/', { credits });
      return response.data;
    } catch (error) {
      console.error('Failed to update credits:', error);
      throw new Error(error.response?.data?.error || 'Failed to update credits');
    }
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
    try {
      const response = await api.post('/lw/profile', profileData);

      localStorage.setItem('isProfileCompleted', true);
      return response.data;
    } catch (error) {
      console.error('Failed to create lawyer profile:', error.message);
      return null;
    }

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
  },

  updateChatTitle: async (sessionId, newTitle) => {
    const response = await fetch(`${API_BASE_URL}/chat/update-title/${sessionId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({ title: newTitle })
    });

    if (!response.ok) {
      throw new Error('Failed to update chat title');
    }

    return response.json();
  },

  deleteChat: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/chat/delete/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to delete chat');
    }

    return response.json();
  },
};

// Add this to your fetchPDFAsBlob function
const fetchPDFAsBlob = async (url) => {
  try {
    if (isGovtUrl(url)) {
      console.warn('Accessing government website, SSL verification might be required');
    }

    const proxyUrl = `${apiService.API_BASE_URL}/proxy-pdf?url=${encodeURIComponent(url)}`;

    const response = await fetch(proxyUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/pdf,*/*',
        'Cache-Control': 'no-cache',
      },
      credentials: 'same-origin',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    if (blob.size === 0) {
      throw new Error('Empty PDF received');
    }

    // Verify it's actually a PDF
    if (!blob.type.includes('pdf')) {
      throw new Error('Invalid PDF format received');
    }

    return URL.createObjectURL(blob);
  } catch (error) {
    console.error('Error fetching PDF:', error);
    throw new Error(
      isGovtUrl(url)
        ? 'Government website access restricted. Please try opening in browser.'
        : error.message
    );
  }
};

export default apiService;
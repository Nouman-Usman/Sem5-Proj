import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Add response interceptor for error handling
api.interceptors.response.use(
  response => {
    // Handle 204 responses
    if (response.status === 204) {
      console.warn('Received 204 No Content response, retrying request...');
      return Promise.reject(new Error('No content received, retrying...'));
    }
    return response;
  },
  error => {
    console.error('API Error:', error);
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. Please try again.');
    }
    if (error.response?.status === 503) {
      throw new Error('Service is currently unavailable. Please try again later.');
    }
    throw new Error(error.response?.data?.error || error.message || 'An unexpected error occurred');
  }
);

export const apiService = {
  async askQuestion(question, userId, chatId = null) {
    const maxRetries = 3;
    let retries = 0;

    while (retries < maxRetries) {
      try {
        const response = await api.post('/ask', { 
          question, 
          user_id: userId, 
          chat_id: chatId 
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
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  },
  getUserChats: (userId, chatId) => 
    api.get(`/user/${userId}/chats/${chatId}`),
  getChatMessages: (userId, chatId) => 
    api.get(`/user/${userId}/chat/${chatId}/messages`),
  clearChat: (userId, chatId) => 
    api.delete(`/user/${userId}/chat/${chatId}`),
  checkHealth: () => api.get('/health'),
};

export default apiService;
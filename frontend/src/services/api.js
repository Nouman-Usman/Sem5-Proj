import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  askQuestion: (question, userId, chatId = null) => 
    api.post('/ask', { question, user_id: userId, chat_id: chatId }),
  getUserChats: (userId,chatId ) => 
    api.get(`/user/${userId}/chats/${chatId}`),
  getChatMessages: (userId, chatId) => 
    api.get(`/user/${userId}/chat/${chatId}/messages`),
  clearChat: (userId, chatId) => 
    api.delete(`/user/${userId}/chat/${chatId}`),
  checkHealth: () => api.get('/health'),
};

export default apiService;
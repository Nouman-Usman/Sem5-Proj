import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

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
      // const chatTopic = await api.get('/topics');
      const chatTopic = {
        "data": {
            "Time": [
                "Sat, 14 Dec 2024 09:53:46 GMT",
                "Sat, 14 Dec 2024 09:44:23 GMT",
                "Sat, 14 Dec 2024 09:38:02 GMT",
                "Fri, 13 Dec 2024 16:01:14 GMT",
                "Fri, 13 Dec 2024 15:54:58 GMT",
                "Fri, 13 Dec 2024 15:30:55 GMT",
                "Fri, 13 Dec 2024 15:27:02 GMT",
                "Fri, 13 Dec 2024 15:23:34 GMT",
                "Fri, 13 Dec 2024 15:17:40 GMT",
                "Fri, 13 Dec 2024 15:12:18 GMT",
                "Fri, 13 Dec 2024 14:51:19 GMT",
                "Fri, 13 Dec 2024 14:47:53 GMT",
                "Fri, 13 Dec 2024 14:27:54 GMT",
                "Fri, 13 Dec 2024 14:27:19 GMT",
                "Fri, 13 Dec 2024 14:21:10 GMT",
                "Fri, 13 Dec 2024 14:19:39 GMT",
                "Fri, 13 Dec 2024 14:09:15 GMT",
                "Fri, 13 Dec 2024 13:58:50 GMT",
                "Fri, 13 Dec 2024 13:51:42 GMT",
                "Fri, 13 Dec 2024 13:02:41 GMT",
                "Fri, 13 Dec 2024 12:55:36 GMT",
                "Fri, 13 Dec 2024 12:54:13 GMT",
                "Fri, 13 Dec 2024 09:52:15 GMT",
                "Fri, 13 Dec 2024 09:47:03 GMT",
                "Fri, 13 Dec 2024 09:46:31 GMT",
                "Fri, 13 Dec 2024 09:45:59 GMT"
            ],
            "chat_sessions": [
                26,
                25,
                24,
                23,
                22,
                21,
                20,
                19,
                18,
                17,
                16,
                15,
                14,
                13,
                12,
                11,
                10,
                9,
                8,
                7,
                6,
                5,
                4,
                3,
                2,
                1
            ],
            "chat_topics": [
                "Pakistan Parliament Works",
                "Pakistan Parliament Works",
                "Know Law Order",
                "Alert Case Zainab",
                "Friend Stabbed",
                "Added Amendment Constitution Language Schedule",
                "Define Law",
                "Alert Case Know Zainab",
                "Alert Case Consequences Explain Zainab",
                "Alert Case Consequences Explain Zainab",
                "Legislation meant",
                "Definw law",
                "Ok",
                "Goof morning",
                "Ok",
                "Define law order",
                "Adn define law order",
                "America parliament working",
                "Australia parliament working",
                "Parliament working",
                "According explain legislation pakistan",
                "According explain legislation pakistan",
                "Friend stabbed",
                "2018 explain law",
                "2018 explain law",
                "2018 explain law"
            ]
        },
        "status": 200,
        "statusText": "OK",
        "headers": {
            "content-length": "1562",
            "content-type": "application/json"
        },
        "config": {
            "transitional": {
                "silentJSONParsing": true,
                "forcedJSONParsing": true,
                "clarifyTimeoutError": false
            },
            "adapter": [
                "xhr",
                "http",
                "fetch"
            ],
            "transformRequest": [
                null
            ],
            "transformResponse": [
                null
            ],
            "timeout": 0,
            "xsrfCookieName": "XSRF-TOKEN",
            "xsrfHeaderName": "X-XSRF-TOKEN",
            "maxContentLength": -1,
            "maxBodyLength": -1,
            "env": {},
            "headers": {
                "Accept": "application/json, text/plain, /",
                "Content-Type": "application/json",
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczNDE1MTA2MiwianRpIjoiYzk1MzMxZWItZWUxYi00MjExLWFhOTMtYzljNzQwZTJiMDE1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzM0MTUxMDYyLCJjc3JmIjoiNGY0NTI4OGEtZTc3OS00NTIxLWE1OWItMTZmNDBkMDcyOWZlIiwiZXhwIjoxNzM0MTY5MDYyLCJyb2xlIjoiY2xpZW50IiwiZW1haWwiOiJub3VtYW5tdWdoYWwwMTIzQGdtYWlsLmNvbSIsIm5hbWUiOiJOb3VtYW4iLCJ1c2VyX2lkIjoxfQ.vObfyIV5ZqIqOneRGbEozt4RknNkhPyAEUfXK06Uqw4"
            },
            "baseURL": "http://localhost:5000/api",
            "method": "get",
            "url": "/topics"
        },
        "request": {}
    }
      // console.log("chat topic is ", chatTopic)
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
  async askQuestion(question) {
    try {
      const response = await api.post('/ask', {
        question,
        SessionId,
      });

      if (!response.data) {
        throw new Error('Empty response received');
      }

      SessionId = response.data.session_id || SessionId;
      console.log('SessionId:', SessionId);

      return {
        answer: response.data.answer,
        references: response.data.references || [],
        recommendedLawyers: response.data.recommended_lawyers || [],
        session_id: response.data.session_id || null
      };
    } catch (error) {
      if (error.message.includes('Request timed out')) {
        console.error('Request timed out. Please try again.');
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
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
    console.log(profileData)
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
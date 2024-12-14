
import axios from 'axios';
import apiService from "@/services/api"


const API_URL = 'http://localhost:5000/api';

export const authService = {
  async login(email, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, { email, password });
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      if (response.data.user.role == 'lawyer'){
        const isProfileCompleted = (await apiService.isLawyerProfileCompleted(response.data.user.id)).is_completed;
        console.log(isProfileCompleted);
        localStorage.setItem('isProfileCompleted', isProfileCompleted);
      }
      else{
        localStorage.setItem('isProfileCompleted', true);
      }
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Login failed');
    }
  },

  async signup(name, email, password, role) {
    try {
      const response = await axios.post(`${API_URL}/signup`, {
        name,
        email,
        password,
        role: role.toLowerCase()
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Signup failed');
    }
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('isProfileCompleted');
  }
};
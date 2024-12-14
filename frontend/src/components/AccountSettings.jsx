import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FaUser, FaEnvelope, FaLock, FaUserTag } from 'react-icons/fa';

const AccountSettings = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const response = await apiService.getUser(user.id);
        setFormData({
          name: response.name,
          email: response.email,
          password: '',
          role: response.role
        });
      } catch (err) {
        setError('Failed to fetch user data');
      }
    };

    fetchUserData();
  }, []);

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const user = JSON.parse(localStorage.getItem('user'));
      await apiService.updateUser(user.id, formData);
      localStorage.setItem('user', JSON.stringify({ ...user, ...formData }));
      navigate('/user-home');
    } catch (err) {
      setError('Failed to update account settings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#030614] pt-24">
      <div className="max-w-4xl mx-auto p-6 relative">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px]"></div>
          <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px]"></div>
          <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px]"></div>
        </div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative bg-[#1A1A2E]/90 rounded-2xl shadow-xl backdrop-blur-lg border border-[#9333EA]/20"
        >
          {/* Header */}
          <div className="p-8 text-center border-b border-[#9333EA]/20">
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
              Account Settings
            </h2>
            <p className="text-gray-400 mt-2">Update your profile information</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-8 space-y-6">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-400 text-center"
              >
                {error}
              </motion.div>
            )}

            <div className="space-y-6">
              <div className="group">
                <Label htmlFor="name" className="flex items-center text-purple-300 mb-2">
                  <FaUser className="mr-2" />
                  Full Name
                </Label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                    focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                    hover:border-[#9333EA]/50"
                  required
                />
              </div>

              <div className="group">
                <Label htmlFor="email" className="flex items-center text-purple-300 mb-2">
                  <FaEnvelope className="mr-2" />
                  Email
                </Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                    focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                    hover:border-[#9333EA]/50"
                  required
                />
              </div>

              <div className="group">
                <Label htmlFor="password" className="flex items-center text-purple-300 mb-2">
                  <FaLock className="mr-2" />
                  Password
                </Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Leave blank to keep current password"
                  className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                    focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                    hover:border-[#9333EA]/50"
                />
              </div>

              <div className="group">
                <Label htmlFor="role" className="flex items-center text-purple-300 mb-2">
                  <FaUserTag className="mr-2" />
                  Role
                </Label>
                <Input
                  id="role"
                  name="role"
                  type="text"
                  value={formData.role}
                  disabled
                  className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white/50
                    focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all cursor-not-allowed"
                />
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-[#9333EA] to-[#7E22CE]
                text-white rounded-lg hover:opacity-90 transition-opacity duration-300
                disabled:opacity-50 disabled:cursor-not-allowed
                hover:shadow-[0_0_20px_rgba(147,51,234,0.5)]"
            >
              {loading ? "Updating..." : "Update Profile"}
            </motion.button>
          </form>
        </motion.div>
      </div>
    </div>
  );
};

export default AccountSettings;

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { FaUser, FaIdCard, FaMapMarkerAlt, FaBriefcase, FaGraduationCap, FaPhone, FaEnvelope } from 'react-icons/fa';

const LawyerProfile = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    cnic: '',
    licenseNumber: '',
    location: '',
    experience: '',
    specialization: '',
    contact: '',
    email: ''
  });

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const validateStep = (step) => {
    try {
      switch(step) {
        case 1:
          return formData.cnic && formData.licenseNumber;
        case 2:
          return formData.location && formData.experience;
        case 3:
          return formData.specialization && formData.contact && formData.email;
        default:
          return false;
      }
    } catch (err) {
      return false;
    }
  };

  const handleNext = () => {
    let hasError = false;
    setError('');

    try {
      // Validate current step fields
      switch (currentStep) {
        case 1:
          if (!formData.cnic || !formData.licenseNumber) {
            throw new Error('Please fill in all fields for this step');
          }
          if (formData.cnic && (formData.cnic.length !== 13 || !/^\d+$/.test(formData.cnic))) {
            throw new Error('CNIC must be 13 digits');
          }
          break;
        case 2:
          if (!formData.location || !formData.experience) {
            throw new Error('Please fill in all fields for this step');
          }
          if (parseInt(formData.experience) < 0) {
            throw new Error('Experience must be a positive number');
          }
          break;
        case 3:
          if (!formData.specialization || !formData.contact || !formData.email) {
            throw new Error('Please fill in all fields for this step');
          }
          if (formData.email && !formData.email.includes('@')) {
            throw new Error('Please enter a valid email address');
          }
          break;
      }

      if (!hasError) {
        setCurrentStep(currentStep + 1);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleBack = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Validate all required fields first
      if (!formData.cnic || !formData.licenseNumber || !formData.location || 
          !formData.experience || !formData.specialization || !formData.contact || 
          !formData.email) {
        throw new Error('Please complete all fields before submitting');
      }

      // Validate field formats
      if (formData.cnic.length !== 13 || !/^\d+$/.test(formData.cnic)) {
        throw new Error('CNIC must be 13 digits');
      }

      if (!formData.email.includes('@')) {
        throw new Error('Please enter a valid email address');
      }

      if (parseInt(formData.experience) < 0) {
        throw new Error('Experience must be a positive number');
      }

      // Only proceed if we're on the last step
      if (currentStep !== 3) {
        handleNext();
        return;
      }

      const response = await apiService.createLawyerProfile(formData);
      localStorage.setItem('isProfileCompleted', 'true');
      console.log('Profile created successfully:', response);
      navigate('/lawyer-dashboard');
    } catch (err) {
      console.error('Profile creation error:', err);
      setError(
        err.response?.data?.error || 
        err.message || 
        'Failed to create lawyer profile'
      );
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
              Complete Your Profile
            </h2>
            <p className="text-gray-400 mt-2">Step {currentStep} of 3</p>
          </div>

          {/* Progress Bar */}
          <div className="w-full h-2 bg-gray-700">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(currentStep / 3) * 100}%` }}
              className="h-full bg-gradient-to-r from-[#9333EA] to-[#7E22CE]"
              transition={{ duration: 0.5 }}
            />
          </div>

          {/* Form Content */}
          <form onSubmit={handleSubmit} className="p-8">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-400 text-center"
              >
                {error}
              </motion.div>
            )}

            {/* Form Steps */}
            <div className="space-y-6">
              {/* Existing form fields with updated styling */}
              {currentStep === 1 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  <div className="group">
                    <label className="flex items-center text-purple-300 mb-2">
                      <FaIdCard className="mr-2" />
                      CNIC
                    </label>
                    <input
                      type="text"
                      name="cnic"
                      value={formData.cnic}
                      onChange={handleChange}
                      className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                        focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                        hover:border-[#9333EA]/50"
                      placeholder="Enter 13-digit CNIC"
                    />
                  </div>
                  <div className="group">
                    <label className="flex items-center text-purple-300 mb-2">
                      <FaIdCard className="mr-2" />
                      License Number
                    </label>
                    <input
                      type="text"
                      name="licenseNumber"
                      value={formData.licenseNumber}
                      onChange={handleChange}
                      className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                        focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                        hover:border-[#9333EA]/50"
                      placeholder="Enter License Number"
                    />
                  </div>
                </motion.div>
              )}
              {currentStep === 2 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  <div className="group">
                    <label className="flex items-center text-purple-300 mb-2">
                      <FaMapMarkerAlt className="mr-2" />
                      Location
                    </label>
                    <input
                      type="text"
                      name="location"
                      value={formData.location}
                      onChange={handleChange}
                      className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                        focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                        hover:border-[#9333EA]/50"
                      placeholder="Enter Location"
                    />
                  </div>
                  <div className="group">
                    <label className="flex items-center text-purple-300 mb-2">
                      <FaBriefcase className="mr-2" />
                      Experience (years)
                    </label>
                    <input
                      type="number"
                      name="experience"
                      value={formData.experience}
                      onChange={handleChange}
                      className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                        focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                        hover:border-[#9333EA]/50"
                      placeholder="Enter Experience in Years"
                    />
                  </div>
                </motion.div>
              )}
              {currentStep === 3 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="space-y-6"
                >
                  <div className="group">
                    <label className="flex items-center text-purple-300 mb-2">
                      <FaGraduationCap className="mr-2" />
                      Specialization
                    </label>
                    <input
                      type="text"
                      name="specialization"
                      value={formData.specialization}
                      onChange={handleChange}
                      className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                        focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                        hover:border-[#9333EA]/50"
                      placeholder="Enter Specialization"
                    />
                  </div>
                  <div className="group">
                    <label className="flex items-center text-purple-300 mb-2">
                      <FaPhone className="mr-2" />
                      Contact
                    </label>
                    <input
                      type="tel"
                      name="contact"
                      value={formData.contact}
                      onChange={handleChange}
                      className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                        focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                        hover:border-[#9333EA]/50"
                      placeholder="Enter Contact Number"
                    />
                  </div>
                  <div className="group">
                    <label className="flex items-center text-purple-300 mb-2">
                      <FaEnvelope className="mr-2" />
                      Email
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      className="w-full bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg p-3 text-white
                        focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                        hover:border-[#9333EA]/50"
                      placeholder="Enter Email Address"
                    />
                  </div>
                </motion.div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-8">
              {currentStep > 1 && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="button"
                  onClick={handleBack}
                  className="px-6 py-2 bg-[#2E2E3A] text-purple-300 rounded-lg
                    hover:bg-[#3E3E4A] transition-colors duration-300"
                >
                  Back
                </motion.button>
              )}
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type={currentStep === 3 ? "submit" : "button"}
                onClick={currentStep === 3 ? undefined : handleNext}
                className="px-6 py-2 bg-gradient-to-r from-[#9333EA] to-[#7E22CE]
                  text-white rounded-lg hover:opacity-90 transition-opacity duration-300
                  ml-auto"
              >
                {currentStep === 3 ? "Submit" : "Next"}
              </motion.button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
};

export default LawyerProfile;

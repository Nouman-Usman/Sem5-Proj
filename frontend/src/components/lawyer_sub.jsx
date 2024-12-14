import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { motion } from 'framer-motion';

const LawyerSubscription = () => {
  const [isSelected, setIsSelected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubscribe = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const startDate = new Date();
      const endDate = new Date();
      endDate.setMonth(endDate.getMonth() + 1); // Add 1 month

      await apiService.createSubscription({
        plan: 'premium',
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        amount: 1000
      });

      setShowPopup(true);
      setTimeout(() => {
        setShowPopup(false);
        navigate('/lawyer-profile');
      }, 3000);
    } catch (err) {
      setError(err.message);
      setTimeout(() => setError(null), 5000);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#030614] pt-24 relative">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px]"></div>
        <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px]"></div>
        <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px]"></div>
      </div>

      <div className="max-w-7xl mx-auto p-8 relative z-10">
        <motion.h2 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-8"
        >
          Lawyer Subscription Plan
        </motion.h2>
        <div className="flex justify-center">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            className={`w-[320px] p-6 rounded-xl shadow-lg bg-[#1A1A2E]/90 border border-[#9333EA]/20 backdrop-blur-lg 
              hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300
              ${isSelected ? 'ring-2 ring-[#9333EA]' : ''}`}
          >
            <h3 className="text-2xl font-semibold text-white mb-4">Premium Plan</h3>
            <div className="text-4xl font-bold text-purple-400 mb-6">Rs. 1000/month</div>
            <ul className="space-y-3 mb-8 text-gray-300">
              {[
                'Profile Listing on Platform',
                'Client Case Matching',
                'Direct Client Communication',
                'Document Management Tools',
                'Priority Support',
                'Analytics Dashboard'
              ].map((feature, index) => (
                <li key={index} className="flex items-center">
                  <svg className="w-5 h-5 text-purple-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <button
              onClick={handleSubscribe}
              disabled={isLoading}
              className="w-full py-3 px-4 bg-gradient-to-r from-[#9333EA] to-[#7E22CE] text-white font-semibold rounded-lg 
                hover:shadow-[0_0_20px_rgba(147,51,234,0.5)] transition-all duration-300 flex items-center justify-center"
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
              ) : "Subscribe Now"}
            </button>
          </motion.div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="fixed top-20 right-4 bg-red-900/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg z-50">
            {error}
          </div>
        )}

        {/* Success Popup */}
        {showPopup && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
            <motion.div
              initial={{ scale: 0.5, y: 100 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.5, y: 100 }}
              transition={{ type: "spring", bounce: 0.4 }}
              className="relative bg-[#1A1A2E]/90 rounded-2xl overflow-hidden p-6 shadow-xl"
            >
              {/* Glowing border effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-[#9333EA] to-[#7E22CE] animate-borderGlow"></div>
              
              {/* Content container */}
              <div className="relative m-[1px] bg-[#1A1A2E] rounded-2xl p-8">
                {/* Purple orb background effects */}
                <div className="absolute inset-0 overflow-hidden">
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[200px] bg-[#9333EA]/20 rounded-full blur-[32px]"></div>
                  <div className="absolute top-0 right-0 w-[100px] h-[100px] bg-[#7E22CE]/20 rounded-full blur-[24px]"></div>
                </div>

                {/* Content */}
                <div className="relative z-10 text-center">
                  <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-2">
                    Congratulations! 🎉
                  </h3>
                  <p className="text-gray-300 mb-4">Your subscription is activated</p>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LawyerSubscription;

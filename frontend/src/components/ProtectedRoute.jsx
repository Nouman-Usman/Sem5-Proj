import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const [showProfilePopup, setShowProfilePopup] = useState(false);
  const user = JSON.parse(localStorage.getItem('user'));
  const location = useLocation();

  useEffect(() => {
    if (user && 
        user.role === 'lawyer' && 
        !JSON.parse(localStorage.getItem("isProfileCompleted")) && 
        location.pathname !== '/lawyer-profile') {
      setShowProfilePopup(true);
    }
  }, [user, location]);

  if (!user || !user.role) {
    return <Navigate to="/login" />;
  }

  if (!allowedRoles.includes(user.role)) {
    if (user.role === 'lawyer') {
      return <Navigate to="/lawyer-dashboard" />;
    } else if (user.role === 'client') {
      return <Navigate to="/user-home" />;
    }
  }

  const handleCompleteProfile = () => {
    setShowProfilePopup(false);
    window.location.href = '/lawyer-profile';
  };

  return (
    <>
      {children}
      <AnimatePresence>
        {showProfilePopup && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50"
            onClick={() => setShowProfilePopup(false)} // Close on backdrop click
          >
            <motion.div
              initial={{ scale: 0.5, y: 100 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.5, y: 100 }}
              transition={{ type: "spring", bounce: 0.4 }}
              className="relative bg-[#1A1A2E]/90 rounded-2xl overflow-hidden"
              onClick={e => e.stopPropagation()} // Prevent closing when clicking the popup
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
                <div className="relative z-10">
                  <motion.div
                    initial={{ y: -20 }}
                    animate={{ y: 0 }}
                    className="text-center"
                  >
                    <h3 className="text-3xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                      Complete Your Profile
                    </h3>
                    <p className="text-gray-300 mb-6 max-w-md">
                      Please complete your profile to unlock all features and start connecting with clients.
                    </p>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleCompleteProfile}
                      className="bg-gradient-to-r from-[#9333EA] to-[#7E22CE] text-white 
                        py-3 px-8 rounded-lg font-medium
                        hover:shadow-[0_0_20px_rgba(147,51,234,0.5)]
                        transition-all duration-300"
                    >
                      Complete Profile
                    </motion.button>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
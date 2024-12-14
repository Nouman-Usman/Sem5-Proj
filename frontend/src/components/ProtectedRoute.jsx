import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const [showProfilePopup, setShowProfilePopup] = useState(false);
  const user = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    if (user && user.role === 'lawyer' && !JSON.parse(localStorage.getItem("isProfileCompleted"))) {
      setShowProfilePopup(true);
    }
  }, [user]);

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

  return (
    <>
      {children}
      {showProfilePopup && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl">
            <h3 className="text-2xl font-bold text-purple-600 mb-2">Complete Your Profile</h3>
            <p className="text-gray-600 mb-4">Please complete your profile to access the dashboard.</p>
            <button
              onClick={() => window.location.href = '/lawyer-profile'}
              className="bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors"
            >
              Complete Profile
            </button>
          </div>
        </div>
      )}
    </>
  );
};
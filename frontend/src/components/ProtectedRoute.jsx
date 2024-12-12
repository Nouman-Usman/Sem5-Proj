
import React from 'react';
import { Navigate } from 'react-router-dom';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const user = JSON.parse(localStorage.getItem('user'));
  
  if (!user || !user.role) {
    return <Navigate to="/login" />;
  }

  if (!allowedRoles.includes(user.role)) {
    // Redirect based on their roles
    if (user.role === 'lawyer') {
      return <Navigate to="/lawyer-home" />;
    }
    else if (user.role === 'client') {
        return <Navigate to="/user-home" />;
  }
}

  return children;
};
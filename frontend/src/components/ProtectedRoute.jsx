
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
      return <Navigate to="/lawyer-dashboard" />;
    }
    else if (user.role === 'client') {
      return <Navigate to="/user-home" />;
    }
  }
  // console.log(window.location.pathname);
  if (window.location.pathname != "/lawyer-profile" && user.role == 'lawyer' && JSON.parse(localStorage.getItem("isProfileCompleted")) == false){
    return <Navigate to="/lawyer-profile" />; 
  }
  // if (window.location.pathname != "/client-profile" && user.role == 'client' && JSON.parse(localStorage.getItem("isProfileCompleted")) == false){
  //   return <Navigate to="/lawyer-profile" />; 
  // }
  return children;
};
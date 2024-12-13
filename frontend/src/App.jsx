// App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Home from './components/Home.jsx';
import About from './components/About.jsx';
import { LoginSignup } from './components/LoginSignup.jsx';
import { Navbar } from './components/navbar.jsx';
import { LawyerRecommendationPage } from './components/LawyerRecommendationPage.jsx';
import { UserHome } from './components/UserHome.jsx';
import { ChatbotPage } from './components/ChatbotPage.jsx';
import ClientProfile from './components/client_profile';
import LawyerProfile from './components/lawyer_profile.jsx';
import LawyerSubscription from './components/lawyer_sub.jsx';
import SubscriptionPlans from './components/cleint_sub.jsx';
import LawyerDashboard from './components/lawyer_dashboard';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (    
    <Router>
      <NavbarWithConditionalRender />
      <Routes>
        <Route path="/chatbot" element={
          <ProtectedRoute allowedRoles={['client', 'lawyer']}>
            <ChatbotPage />
          </ProtectedRoute>
        } />
        <Route path="/lawyers" element={
          <ProtectedRoute allowedRoles={['lawyer']}>
            <LawyerRecommendationPage />
          </ProtectedRoute>
        } />
        <Route path="/user-home" element={
          <ProtectedRoute allowedRoles={['client']}>
            <UserHome />
          </ProtectedRoute>
        } />
        <Route path="/client-profile" element={
          <ProtectedRoute allowedRoles={['client']}>
            <ClientProfile />
          </ProtectedRoute>
        } />
        <Route path="/lawyer-profile" element={
          <ProtectedRoute allowedRoles={['lawyer']}>
            <LawyerProfile />
          </ProtectedRoute>
        } />
        <Route path="/lawyer-subscription" element={
          <ProtectedRoute allowedRoles={['lawyer']}>
            <LawyerSubscription />
          </ProtectedRoute>
        } />
        <Route path="/lawyer-dashboard" element={
          <ProtectedRoute allowedRoles={['lawyer']}>
            <LawyerDashboard />
          </ProtectedRoute>
        } />
        <Route path="/subscription-plans" element={
          <ProtectedRoute allowedRoles={['client']}>
            <SubscriptionPlans />
          </ProtectedRoute>
        } />
        <Route path="/about" element={<About />} />
        <Route path="/Signup" element={<LoginSignup />} />
        <Route path="/login" element={<LoginSignup />} />
        <Route path="/" element={<Home />} />
      </Routes>
    </Router>
  );
}

function NavbarWithConditionalRender() {  
  const location = useLocation();
  // Update the condition to handle both cases and normalize the path
  const noNavbarPaths = ['/login', '/signup', '/'];
  const shouldHideNavbar = noNavbarPaths.includes(location.pathname.toLowerCase());

  return !shouldHideNavbar ? <Navbar /> : null;
}

export default App;

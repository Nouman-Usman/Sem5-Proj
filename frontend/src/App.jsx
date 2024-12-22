import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Home from './components/Home.jsx';
import About from './components/About.jsx';
import { LoginSignup } from './components/LoginSignup.jsx';
import { Navbar } from './components/Navbar.jsx';
import { LawyerRecommendationPage } from './components/LawyerRecommendationPage.jsx';
import { UserHome } from './components/UserHome.jsx';
import { ChatbotPage } from './components/ChatbotPage.jsx';
import ClientProfile from './components/client_profile';
import LawyerProfile from './components/lawyer_profile.jsx';
import LawyerSubscription from './components/lawyer_sub.jsx';
import SubscriptionPlans from './components/cleint_sub.jsx';
import LawyerDashboard from './components/lawyer_dashboard';
import { ProtectedRoute } from './components/ProtectedRoute';
import AccountSettings from './components/AccountSettings.jsx';
import AdminDashboard from './components/AdminDashboard.jsx';
import LawyerProfilePage from '@/views/LawyerProfilePage';
import LawyerChatbotPage from './components/LawyerChatbot.jsx';

function App() {
  const location = useLocation();
  const hideNavbarRoutes = ['/chatbot', '/login', '/signup', '/'];

  return (
    <div className="App">
      {!hideNavbarRoutes.includes(location.pathname) && <Navbar />}
      <Routes>
        <Route path="/chatbot" element={
          <ProtectedRoute allowedRoles={['client', 'lawyer']}>
            <ChatbotPage />
          </ProtectedRoute>
        } />
        <Route path="/lawyers" element={
          <ProtectedRoute allowedRoles={['client']}>  {/* Changed from 'lawyer' to 'client' */}
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
        <Route path="/lawyer-chatbot" element={
          <ProtectedRoute allowedRoles={['client']}>
            <LawyerChatbotPage />
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
        <Route path="/account-settings" element={
          <ProtectedRoute allowedRoles={['client', 'lawyer']}>
            <AccountSettings />
          </ProtectedRoute>
        } />
        <Route path="/about" element={<About />} />
        <Route path="/Signup" element={<LoginSignup />} />
        <Route path="/login" element={<LoginSignup />} />
        <Route path="/" element={<Home />} />
        <Route path="/admin-dashboard" element={<AdminDashboard />} />
        <Route path="/lawyer/:id" element={<LawyerProfilePage />} />
      </Routes>
    </div>
  );
}

export default function AppWrapper() {
  return (
    <Router>
      <App />
    </Router>
  );
}

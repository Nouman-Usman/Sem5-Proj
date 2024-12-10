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
function App() {
  return (    
    <Router>
      <NavbarWithConditionalRender />
      <Routes>
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="/lawyers" element={<LawyerRecommendationPage />} />
        <Route path="/user-home" element={<UserHome />} />
        <Route path="/about" element={<About />} />
        <Route path="/Signup" element={<LoginSignup />} />
        <Route path="/login" element={<LoginSignup />} />
        <Route path="/client-profile" element={<ClientProfile />} />
        <Route path="/lawyer-profile" element={<LawyerProfile />} />
        <Route path="/lawyer-subscription" element={<LawyerSubscription />} />
        <Route path="/subscription-plans" element={<SubscriptionPlans />} />
        <Route path="/lawyer-dashboard" element={<LawyerDashboard />} />
        <Route path="/" element={<Home />} />
      </Routes>
    </Router>
  );
}

function NavbarWithConditionalRender() {
  const location = useLocation(); 
  const shouldHideNavbar = location.pathname === '/Login' || location.pathname === '/Signup' || location.pathname === '/';

  return !shouldHideNavbar ? <Navbar /> : null; // Render Navbar conditionally
}

export default App;

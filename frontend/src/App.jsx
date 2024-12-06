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
        <Route path="/" element={<Home />} />
      </Routes>
    </Router>
  );
}

function NavbarWithConditionalRender() {
  const location = useLocation(); // This is now safe because it's inside the Router

  // Hide navbar on Login/Signup pages
  const shouldHideNavbar = (location.pathname).toLowerCase() === '/login' || (location.pathname).toLowerCase() === '/signup' || location.pathname === '/';

  return !shouldHideNavbar ? <Navbar /> : null; // Render Navbar conditionally
}

export default App;

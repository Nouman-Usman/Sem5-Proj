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
        {/* <Route path="/" element={<Home />} /> */}
        <Route path="/" element={<UserHome />} />
        <Route path="/about" element={<About />} />
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="/Lawyers" element={<LawyerRecommendationPage />} />
        <Route path="/Login" element={<LoginSignup />} />
        <Route path="/Signup" element={<LoginSignup />} />
        <Route path="/Account-settings" element={<UserHome />} />
        <Route path="/Dashboard" element={<UserHome />} />
        <Route path="/lawyer/:id" element={<div>Lawyer Profile Placeholder</div>} />
      </Routes>
    </Router>
  );
}

function NavbarWithConditionalRender() {
  const location = useLocation(); // This is now safe because it's inside the Router

  // Hide navbar on Login/Signup pages
  const shouldHideNavbar = location.pathname === '/Login' || location.pathname === '/Signup' ;

  return !shouldHideNavbar ? <Navbar /> : null; // Render Navbar conditionally
}

export default App;
